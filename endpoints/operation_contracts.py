"""Helpers for reading existing-state operation invocation contracts."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from django.conf import settings

EXISTING_OPERATIONS_DIR = settings.BASE_DIR / "backend" / "existing-state" / "contracts" / "operations"
SUPPORTED_ENDPOINT_OPERATION_IDS = ("apply-ansible-playbook", "apply-playbook-to-node")
SCALAR_TYPE_HINTS = {"string", "integer", "number", "boolean", "array", "object"}


@dataclass(frozen=True, slots=True)
class OperationInvocationContract:
    """Operation contract fields needed to build an invocation payload safely."""

    id: str
    label: str
    function: str
    required_payload_keys: tuple[str, ...]
    optional_payload_keys: tuple[str, ...]
    required_literal_values: dict[str, str | int | float | bool]
    mode_choices: tuple[str, ...]
    source_path: Path


def _coerce_payload_keys(raw_payload_fields: Any) -> tuple[str, ...]:
    if isinstance(raw_payload_fields, dict):
        return tuple(str(key).strip() for key in raw_payload_fields if str(key).strip())
    if isinstance(raw_payload_fields, list):
        return tuple(str(name).strip() for name in raw_payload_fields if str(name).strip())
    return ()


def _literal_required_values(raw_required: Any) -> dict[str, str | int | float | bool]:
    if not isinstance(raw_required, dict):
        return {}
    values: dict[str, str | int | float | bool] = {}
    for key, raw_value in raw_required.items():
        if isinstance(raw_value, bool | int | float):
            values[str(key)] = raw_value
            continue
        if not isinstance(raw_value, str):
            continue
        candidate = raw_value.strip()
        if not candidate:
            continue
        # Type hints and enum-like text are not literal payload defaults.
        if candidate.lower() in SCALAR_TYPE_HINTS or "|" in candidate:
            continue
        values[str(key)] = candidate
    return values


def _read_operation_contract(contract_path: Path) -> OperationInvocationContract:
    with contract_path.open(encoding="utf-8") as contract_file:
        raw_data: dict[str, Any] = yaml.safe_load(contract_file) or {}

    invocation = raw_data.get("invocation", {})
    payload = invocation.get("payload", {}) if isinstance(invocation, dict) else {}
    raw_required = payload.get("required", {})
    raw_optional = payload.get("optional", {})
    raw_modes = raw_data.get("modes", {})

    required_payload_keys = _coerce_payload_keys(raw_required)
    optional_payload_keys = _coerce_payload_keys(raw_optional)
    required_literal_values = _literal_required_values(raw_required)

    mode_choices: tuple[str, ...] = ()
    if isinstance(raw_modes, dict):
        mode_choices = tuple(str(mode).strip() for mode in raw_modes if str(mode).strip())

    contract_id = str(raw_data.get("id", contract_path.stem)).strip()
    label = str(raw_data.get("label", contract_id.replace("-", " ").title())).strip()

    return OperationInvocationContract(
        id=contract_id,
        label=label,
        function=str(raw_data.get("function", "")).strip(),
        required_payload_keys=required_payload_keys,
        optional_payload_keys=optional_payload_keys,
        required_literal_values=required_literal_values,
        mode_choices=mode_choices,
        source_path=contract_path,
    )


@lru_cache(maxsize=1)
def list_endpoint_operation_contracts() -> tuple[OperationInvocationContract, ...]:
    """Load endpoint-action operation contracts from existing-state contracts."""
    result: list[OperationInvocationContract] = []
    for operation_id in SUPPORTED_ENDPOINT_OPERATION_IDS:
        path = EXISTING_OPERATIONS_DIR / f"{operation_id}.yaml"
        if path.exists():
            result.append(_read_operation_contract(path))
    return tuple(result)


def get_endpoint_operation_contract(operation_id: str) -> OperationInvocationContract | None:
    for contract in list_endpoint_operation_contracts():
        if contract.id == operation_id:
            return contract
    return None
