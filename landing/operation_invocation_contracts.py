"""Read operation invocation contracts from existing-state backend YAML files."""

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
class OperationField:
    """One operation payload field derived from contract invocation metadata."""

    key: str
    required: bool
    description: str
    value_type: str
    enum_choices: tuple[str, ...]
    literal_value: str | int | float | bool | None


@dataclass(frozen=True, slots=True)
class OperationInvocationContract:
    """Operation contract details needed for generic contract-driven forms."""

    id: str
    label: str
    function: str
    mode_choices: tuple[str, ...]
    fields: tuple[OperationField, ...]
    source_path: Path

    @property
    def required_fields(self) -> tuple[OperationField, ...]:
        return tuple(field for field in self.fields if field.required and field.literal_value is None)

    @property
    def optional_fields(self) -> tuple[OperationField, ...]:
        return tuple(field for field in self.fields if not field.required)

    @property
    def required_literal_values(self) -> dict[str, str | int | float | bool]:
        return {
            field.key: field.literal_value
            for field in self.fields
            if field.required and field.literal_value is not None
        }


def _coerce_modes(raw_modes: Any) -> tuple[str, ...]:
    if not isinstance(raw_modes, dict):
        return ()
    return tuple(str(mode).strip() for mode in raw_modes if str(mode).strip())


def _coerce_payload_mapping(raw_payload: Any) -> dict[str, str | int | float | bool]:
    if not isinstance(raw_payload, dict):
        return {}
    result: dict[str, str | int | float | bool] = {}
    for key, value in raw_payload.items():
        key_text = str(key).strip()
        if not key_text:
            continue
        if isinstance(value, bool | int | float):
            result[key_text] = value
            continue
        result[key_text] = str(value).strip()
    return result


def _infer_field_type(description: str) -> tuple[str, tuple[str, ...]]:
    text = description.strip().lower()
    if "|" in text:
        choices = tuple(part.strip() for part in description.split("|") if part.strip())
        return "enum", choices
    if "list of" in text or text.startswith("list[") or text.startswith("array"):
        return "array", ()
    if "object" in text:
        return "object", ()
    if "boolean" in text:
        return "boolean", ()
    if "integer" in text:
        return "integer", ()
    if "number" in text:
        return "number", ()
    return "string", ()


def _infer_literal_value(raw_value: str | int | float | bool) -> str | int | float | bool | None:
    if isinstance(raw_value, bool | int | float):
        return raw_value
    candidate = str(raw_value).strip()
    if not candidate:
        return None
    lowered = candidate.lower()
    if lowered in SCALAR_TYPE_HINTS or lowered.startswith("list of") or lowered.startswith("array"):
        return None
    if "|" in candidate:
        return None
    return candidate


def _build_fields(
    required_payload: dict[str, str | int | float | bool],
    optional_payload: dict[str, str | int | float | bool],
) -> tuple[OperationField, ...]:
    fields: list[OperationField] = []
    for key, raw_value in required_payload.items():
        description = str(raw_value)
        value_type, enum_choices = _infer_field_type(description)
        fields.append(
            OperationField(
                key=key,
                required=True,
                description=description,
                value_type=value_type,
                enum_choices=enum_choices,
                literal_value=_infer_literal_value(raw_value),
            )
        )
    for key, raw_value in optional_payload.items():
        description = str(raw_value)
        value_type, enum_choices = _infer_field_type(description)
        fields.append(
            OperationField(
                key=key,
                required=False,
                description=description,
                value_type=value_type,
                enum_choices=enum_choices,
                literal_value=None,
            )
        )
    return tuple(fields)


def _read_operation_contract(contract_path: Path) -> OperationInvocationContract:
    with contract_path.open(encoding="utf-8") as contract_file:
        raw_data: dict[str, Any] = yaml.safe_load(contract_file) or {}
    invocation = raw_data.get("invocation", {})
    payload = invocation.get("payload", {}) if isinstance(invocation, dict) else {}
    required_payload = _coerce_payload_mapping(payload.get("required", {}))
    optional_payload = _coerce_payload_mapping(payload.get("optional", {}))
    contract_id = str(raw_data.get("id", contract_path.stem)).strip()
    label = str(raw_data.get("label", contract_id.replace("-", " ").title())).strip()
    return OperationInvocationContract(
        id=contract_id,
        label=label,
        function=str(raw_data.get("function", "")).strip(),
        mode_choices=_coerce_modes(raw_data.get("modes")),
        fields=_build_fields(required_payload, optional_payload),
        source_path=contract_path,
    )


@lru_cache(maxsize=1)
def list_operation_contracts() -> tuple[OperationInvocationContract, ...]:
    """Load all existing operation contracts for generic operation forms."""
    if not EXISTING_OPERATIONS_DIR.exists():
        return ()
    contracts = [
        _read_operation_contract(contract_path)
        for contract_path in sorted(EXISTING_OPERATIONS_DIR.glob("*.yaml"))
    ]
    return tuple(sorted(contracts, key=lambda contract: contract.id))


def get_operation_contract(operation_id: str) -> OperationInvocationContract | None:
    """Return one operation contract by ID from existing operation contracts."""
    for contract in list_operation_contracts():
        if contract.id == operation_id:
            return contract
    return None
