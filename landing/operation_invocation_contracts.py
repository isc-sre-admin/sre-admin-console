"""Helpers for reading existing-state operation invocation contracts."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from django.conf import settings

EXISTING_OPERATIONS_DIR = settings.BASE_DIR / "backend" / "existing-state" / "contracts" / "operations"
SCALAR_TYPE_HINTS = {"string", "integer", "number", "boolean", "array", "object"}


@dataclass(frozen=True, slots=True)
class OperationFieldSpec:
    """One payload field from an operation invocation contract."""

    name: str
    required: bool
    field_type: str
    raw_spec: str
    choices: tuple[str, ...] = ()
    literal_value: str | int | float | bool | None = None

    @property
    def is_literal(self) -> bool:
        return self.literal_value is not None


@dataclass(frozen=True, slots=True)
class OperationInvocationContract:
    """Operation contract fields needed for generic form rendering."""

    id: str
    label: str
    function: str
    description: str
    required_fields: tuple[OperationFieldSpec, ...]
    optional_fields: tuple[OperationFieldSpec, ...]
    source_path: Path

    @property
    def all_fields(self) -> tuple[OperationFieldSpec, ...]:
        return (*self.required_fields, *self.optional_fields)


def _stringify_spec(raw_value: Any) -> str:
    if raw_value is None:
        return ""
    if isinstance(raw_value, bool | int | float):
        return str(raw_value)
    return str(raw_value).strip()


def _parse_choices(spec_text: str) -> tuple[str, ...]:
    if "|" not in spec_text:
        return ()
    return tuple(part.strip() for part in spec_text.split("|") if part.strip())


def _infer_field_type(spec_text: str) -> str:
    normalized = spec_text.lower()
    if "list of string" in normalized or "list[string]" in normalized or normalized == "array":
        return "array"
    if normalized == "object":
        return "object"
    if normalized == "boolean":
        return "boolean"
    if normalized == "integer":
        return "integer"
    if normalized == "number":
        return "number"
    if _parse_choices(spec_text):
        return "choice"
    return "string"


def _is_literal_value(spec_text: str, raw_value: Any) -> bool:
    if isinstance(raw_value, bool | int | float):
        return True
    normalized = spec_text.lower()
    if not spec_text:
        return False
    if normalized in SCALAR_TYPE_HINTS:
        return False
    if "list of " in normalized or "list[" in normalized or "|" in spec_text:
        return False
    return True


def _coerce_field_specs(raw_payload_fields: Any, *, required: bool) -> tuple[OperationFieldSpec, ...]:
    if not isinstance(raw_payload_fields, dict):
        return ()

    result: list[OperationFieldSpec] = []
    for key, raw_value in raw_payload_fields.items():
        name = str(key).strip()
        if not name:
            continue
        spec_text = _stringify_spec(raw_value)
        literal_value: str | int | float | bool | None = None
        if _is_literal_value(spec_text, raw_value):
            literal_value = raw_value if isinstance(raw_value, bool | int | float) else spec_text
        result.append(
            OperationFieldSpec(
                name=name,
                required=required,
                field_type=_infer_field_type(spec_text),
                raw_spec=spec_text,
                choices=_parse_choices(spec_text),
                literal_value=literal_value,
            )
        )
    return tuple(result)


def _read_operation_contract(contract_path: Path) -> OperationInvocationContract:
    with contract_path.open(encoding="utf-8") as contract_file:
        raw_data: dict[str, Any] = yaml.safe_load(contract_file) or {}

    invocation = raw_data.get("invocation", {})
    payload = invocation.get("payload", {}) if isinstance(invocation, dict) else {}
    required_fields = _coerce_field_specs(payload.get("required", {}), required=True)
    optional_fields = _coerce_field_specs(payload.get("optional", {}), required=False)

    contract_id = str(raw_data.get("id", contract_path.stem)).strip()
    label = str(raw_data.get("label", contract_id.replace("-", " ").title())).strip()

    return OperationInvocationContract(
        id=contract_id,
        label=label,
        function=str(raw_data.get("function", "")).strip(),
        description=str(raw_data.get("description", "")).strip(),
        required_fields=required_fields,
        optional_fields=optional_fields,
        source_path=contract_path,
    )


@lru_cache(maxsize=1)
def list_operation_contracts() -> tuple[OperationInvocationContract, ...]:
    """Load all existing-state operation contracts."""
    contracts = [
        _read_operation_contract(contract_path)
        for contract_path in sorted(EXISTING_OPERATIONS_DIR.glob("*.yaml"))
    ]
    return tuple(sorted(contracts, key=lambda contract: contract.id))


def get_operation_contract(operation_id: str) -> OperationInvocationContract | None:
    """Return a single existing-state operation contract by id."""
    for contract in list_operation_contracts():
        if contract.id == operation_id:
            return contract
    return None
