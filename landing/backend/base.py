"""Abstract backend interface for SRE operations, pipelines, and queries.

Implementations (mock or real) must match the contract request/response shapes
from backend/existing-state/contracts so the frontend can switch with minimal changes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Backend(ABC):
    """Abstract backend for Lambda operations, Step Functions pipelines, and queries."""

    @abstractmethod
    def invoke_operation(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Invoke a management operation (e.g. unlock-user). Payload includes 'operation' and inputs.

        Returns dict with either:
          success: {"status": "success", ...operation-specific fields (e.g. "message")}
          error:   {"status": "error", "error": str, "message": str}
        """
        ...

    @abstractmethod
    def start_pipeline(self, pipeline_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Start a Step Functions pipeline. Payload is the execution input per contract.

        Returns dict with:
          execution_id, execution_arn, name, status ("Running"), started_at (ISO or display).
        """
        ...

    @abstractmethod
    def run_query(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Run a query (e.g. list-pipeline-executions, retrieve-workspace-directories).

        Payload includes 'query' and query-specific inputs. Returns dict with either:
          success: {"status": "success", "result": ...}
          error:   {"status": "error", "error": str, "message": str}
        """
        ...
