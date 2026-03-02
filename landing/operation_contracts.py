"""Helpers for reading quick-operation contracts (e.g. from proposed-changes)."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from django.conf import settings


@dataclass(frozen=True, slots=True)
class OperationContract:
    """An operation contract loaded from backend YAML (e.g. proposed-changes)."""

    id: str
    label: str
    function: str
    required_inputs: tuple[str, ...]
    optional_inputs: tuple[str, ...]
    source_path: Path

    @property
    def all_inputs(self) -> tuple[str, ...]:
        return (*self.required_inputs, *self.optional_inputs)


PROPOSED_OPERATIONS_DIR = settings.BASE_DIR / "backend" / "proposed-changes" / "operations"

# Operation IDs that are exposed as quick operations (modal dialog) in the nav.
QUICK_OPERATION_IDS = ("unlock-user",)


def _coerce_input_names(raw_inputs: Any) -> tuple[str, ...]:
    if not isinstance(raw_inputs, list):
        return ()
    return tuple(str(name).strip() for name in raw_inputs if str(name).strip())


def _read_operation_contract(contract_path: Path) -> OperationContract:
    with contract_path.open(encoding="utf-8") as f:
        raw_data: dict[str, Any] = yaml.safe_load(f) or {}

    raw_inputs = raw_data.get("inputs", {})
    required_inputs = _coerce_input_names(raw_inputs.get("required"))
    optional_inputs = _coerce_input_names(raw_inputs.get("optional"))

    contract_id = str(raw_data.get("id", raw_data.get("name", contract_path.stem)))
    label = str(raw_data.get("label", "")).strip()
    if not label:
        label = contract_id.replace("-", " ").title()

    return OperationContract(
        id=contract_id,
        label=label,
        function=str(raw_data.get("function", "")).strip(),
        required_inputs=required_inputs,
        optional_inputs=optional_inputs,
        source_path=contract_path,
    )


@lru_cache(maxsize=1)
def list_quick_operations() -> tuple[OperationContract, ...]:
    """Return operation contracts that are exposed as quick operations in the nav."""
    if not PROPOSED_OPERATIONS_DIR.exists():
        return ()
    result: list[OperationContract] = []
    for op_id in QUICK_OPERATION_IDS:
        path = PROPOSED_OPERATIONS_DIR / f"{op_id}.yaml"
        if path.exists():
            result.append(_read_operation_contract(path))
    return tuple(sorted(result, key=lambda c: c.id))


def get_operation_contract(operation_id: str) -> OperationContract | None:
    """Return a single operation contract by id."""
    for contract in list_quick_operations():
        if contract.id == operation_id:
            return contract
    return None
