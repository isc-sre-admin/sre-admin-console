"""Helpers for reading backend pipeline contracts."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from django.conf import settings


@dataclass(frozen=True, slots=True)
class PipelineContract:
    """A pipeline contract loaded from backend YAML files."""

    name: str
    function: str
    description: str
    required_inputs: tuple[str, ...]
    optional_inputs: tuple[str, ...]
    source_path: Path

    @property
    def display_name(self) -> str:
        """Return a human-readable name for UI labels."""
        return self.name.replace("-", " ").title()

    @property
    def all_inputs(self) -> tuple[str, ...]:
        """Return required inputs followed by optional inputs."""
        return (*self.required_inputs, *self.optional_inputs)


PIPELINE_CONTRACTS_DIR = settings.BASE_DIR / "backend" / "existing-state" / "contracts" / "pipelines"


def _coerce_input_names(raw_inputs: Any) -> tuple[str, ...]:
    if not isinstance(raw_inputs, list):
        return ()
    return tuple(str(name).strip() for name in raw_inputs if str(name).strip())


def _read_pipeline_contract(contract_path: Path) -> PipelineContract:
    with contract_path.open(encoding="utf-8") as contract_file:
        raw_data: dict[str, Any] = yaml.safe_load(contract_file) or {}

    raw_inputs = raw_data.get("inputs", {})
    required_inputs = _coerce_input_names(raw_inputs.get("required"))
    optional_inputs = _coerce_input_names(raw_inputs.get("optional"))

    return PipelineContract(
        name=str(raw_data.get("name", contract_path.stem)),
        function=str(raw_data.get("function", "")).strip(),
        description=str(raw_data.get("description", "")).strip(),
        required_inputs=required_inputs,
        optional_inputs=optional_inputs,
        source_path=contract_path,
    )


@lru_cache(maxsize=1)
def list_pipeline_contracts() -> tuple[PipelineContract, ...]:
    """Load and cache all pipeline contracts from the backend directory."""
    contracts = [
        _read_pipeline_contract(contract_path)
        for contract_path in sorted(PIPELINE_CONTRACTS_DIR.glob("*.yaml"))
    ]
    return tuple(sorted(contracts, key=lambda contract: contract.name))


def get_pipeline_contract(pipeline_name: str) -> PipelineContract | None:
    """Return a single pipeline contract by name."""
    for contract in list_pipeline_contracts():
        if contract.name == pipeline_name:
            return contract
    return None
