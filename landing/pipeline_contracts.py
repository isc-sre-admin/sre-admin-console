"""Helpers for reading backend pipeline contracts."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from django.conf import settings


@dataclass(frozen=True, slots=True)
class PipelineStepInfo:
    """One step from a pipeline contract (component_operations entry)."""

    operation: str
    step_id: str  # same as operation, for API use
    label: str  # human-readable, e.g. "Create AD Connector"


@dataclass(frozen=True, slots=True)
class PipelineContract:
    """A pipeline contract loaded from backend YAML files."""

    id: str
    label: str
    function: str
    description: str
    required_inputs: tuple[str, ...]
    optional_inputs: tuple[str, ...]
    source_path: Path
    component_operations: tuple[PipelineStepInfo, ...]

    @property
    def display_name(self) -> str:
        """Return a human-readable name for UI labels."""
        return self.label

    @property
    def all_inputs(self) -> tuple[str, ...]:
        """Return required inputs followed by optional inputs."""
        return (*self.required_inputs, *self.optional_inputs)


PIPELINE_CONTRACTS_DIR = settings.BASE_DIR / "backend" / "existing-state" / "contracts" / "pipelines"


def _coerce_input_names(raw_inputs: Any) -> tuple[str, ...]:
    if not isinstance(raw_inputs, list):
        return ()
    return tuple(str(name).strip() for name in raw_inputs if str(name).strip())


def _humanize_operation(operation: str) -> str:
    """Turn operation id like 'create-ad-connector' into 'Create AD Connector'."""
    return operation.replace("-", " ").title()


def _read_component_operations(raw_ops: Any) -> tuple[PipelineStepInfo, ...]:
    if not isinstance(raw_ops, list):
        return ()
    steps: list[PipelineStepInfo] = []
    for item in raw_ops:
        if isinstance(item, dict) and "operation" in item:
            op = str(item["operation"]).strip()
            if op:
                steps.append(
                    PipelineStepInfo(
                        operation=op,
                        step_id=op,
                        label=_humanize_operation(op),
                    )
                )
        elif isinstance(item, str) and item.strip():
            op = item.strip()
            steps.append(
                PipelineStepInfo(
                    operation=op,
                    step_id=op,
                    label=_humanize_operation(op),
                )
            )
    return tuple(steps)


def _read_pipeline_contract(contract_path: Path) -> PipelineContract:
    with contract_path.open(encoding="utf-8") as contract_file:
        raw_data: dict[str, Any] = yaml.safe_load(contract_file) or {}

    raw_inputs = raw_data.get("inputs", {})
    required_inputs = _coerce_input_names(raw_inputs.get("required"))
    optional_inputs = _coerce_input_names(raw_inputs.get("optional"))

    contract_id = str(raw_data.get("id", raw_data.get("name", contract_path.stem)))
    label = str(raw_data.get("label", "")).strip()
    if not label:
        # Fallback: derive from id (hyphens to spaces, title case)
        label = contract_id.replace("-", " ").title()

    component_operations = _read_component_operations(raw_data.get("component_operations"))

    return PipelineContract(
        id=contract_id,
        label=label,
        function=str(raw_data.get("function", "")).strip(),
        description=str(raw_data.get("description", "")).strip(),
        required_inputs=required_inputs,
        optional_inputs=optional_inputs,
        source_path=contract_path,
        component_operations=component_operations,
    )


@lru_cache(maxsize=1)
def list_pipeline_contracts() -> tuple[PipelineContract, ...]:
    """Load and cache all pipeline contracts from the backend directory."""
    contracts = [
        _read_pipeline_contract(contract_path)
        for contract_path in sorted(PIPELINE_CONTRACTS_DIR.glob("*.yaml"))
    ]
    return tuple(sorted(contracts, key=lambda contract: contract.id))


def get_pipeline_contract(pipeline_id: str) -> PipelineContract | None:
    """Return a single pipeline contract by id."""
    for contract in list_pipeline_contracts():
        if contract.id == pipeline_id:
            return contract
    return None
