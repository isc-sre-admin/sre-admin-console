"""Mock backend returning realistic data from contract shapes for prototyping."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from django.utils import timezone as django_tz

from landing.backend.base import Backend
from landing.pipeline_contracts import get_pipeline_contract

# Stable fake execution IDs for sample rows (match views.py sample data).
_SAMPLE_ACTIVE_IDS = (
    "a1b2c3d4-active-ad-connector",
    "a2b3c4d5-active-linux-ws",
)
_SAMPLE_RECENT_IDS = (
    "b1c2d3e4-recent-windows-ws",
    "b2c3d4e5-recent-ec2-failed",
    "b3c4d5e6-recent-ad-connector",
)
SAMPLE_ACTIVE_EXECUTION_IDS = _SAMPLE_ACTIVE_IDS
SAMPLE_RECENT_EXECUTION_IDS = _SAMPLE_RECENT_IDS

def _state_machine_arn_from_execution_arn(execution_arn: str) -> str:
    """Derive state machine ARN from execution ARN (execution:name:id -> stateMachine:name)."""
    if ":execution:" in execution_arn:
        prefix, _, rest = execution_arn.partition(":execution:")
        name_part = rest.rsplit(":", 1)[0]
        return f"{prefix}:stateMachine:{name_part}"
    return execution_arn


MOCK_ACTIVE_EXECUTIONS = [
    {
        "execution_id": _SAMPLE_ACTIVE_IDS[0],
        "execution_arn": (
            "arn:aws:states:us-east-1:123456789012:execution:"
            f"provision-ad-connector:{_SAMPLE_ACTIVE_IDS[0]}"
        ),
        "name": "provision-ad-connector",
        "label": "Provision AD Connector",
        "pipeline_id": "arn:aws:states:us-east-1:123456789012:stateMachine:provision-ad-connector",
        "enclave_name": "sre-dev-enclave-01",
        "started_at": "6 minutes ago",
        "stopped_at": None,
        "status": "RUNNING",
    },
    {
        "execution_id": _SAMPLE_ACTIVE_IDS[1],
        "execution_arn": (
            "arn:aws:states:us-east-1:123456789012:execution:"
            f"provision-linux-workspace:{_SAMPLE_ACTIVE_IDS[1]}"
        ),
        "name": "provision-linux-workspace",
        "label": "Provision Linux Workspace",
        "pipeline_id": "arn:aws:states:us-east-1:123456789012:stateMachine:provision-linux-workspace",
        "enclave_name": "sre-research-enclave-02",
        "started_at": "18 minutes ago",
        "stopped_at": None,
        "status": "RUNNING",
    },
]

MOCK_RECENT_EXECUTIONS = [
    {
        "execution_id": _SAMPLE_RECENT_IDS[0],
        "execution_arn": (
            "arn:aws:states:us-east-1:123456789012:execution:"
            f"provision-windows-workspace:{_SAMPLE_RECENT_IDS[0]}"
        ),
        "name": "provision-windows-workspace",
        "label": "Provision Windows Workspace",
        "pipeline_id": "arn:aws:states:us-east-1:123456789012:stateMachine:provision-windows-workspace",
        "enclave_name": "sre-research-enclave-01",
        "started_at": "Today, 09:15 UTC",
        "stopped_at": "Today, 09:42 UTC",
        "status": "SUCCEEDED",
    },
    {
        "execution_id": _SAMPLE_RECENT_IDS[1],
        "execution_arn": (
            "arn:aws:states:us-east-1:123456789012:execution:"
            f"provision-ec2-instance:{_SAMPLE_RECENT_IDS[1]}"
        ),
        "name": "provision-ec2-instance",
        "label": "Provision EC2 Instance",
        "pipeline_id": "arn:aws:states:us-east-1:123456789012:stateMachine:provision-ec2-instance",
        "enclave_name": "sre-research-enclave-03",
        "started_at": "Today, 08:00 UTC",
        "stopped_at": "Today, 08:17 UTC",
        "status": "FAILED",
    },
    {
        "execution_id": _SAMPLE_RECENT_IDS[2],
        "execution_arn": (
            "arn:aws:states:us-east-1:123456789012:execution:"
            f"provision-ad-connector:{_SAMPLE_RECENT_IDS[2]}"
        ),
        "name": "provision-ad-connector",
        "label": "Provision AD Connector",
        "pipeline_id": "arn:aws:states:us-east-1:123456789012:stateMachine:provision-ad-connector",
        "enclave_name": "sre-dev-enclave-01",
        "started_at": "Yesterday, 19:30 UTC",
        "stopped_at": "Yesterday, 20:06 UTC",
        "status": "SUCCEEDED",
    },
]

MOCK_EC2_SOURCE_IMAGES = [
    {"ami_id": "ami-091898c3a03efa550", "ami_name": "SRE-Rocky9-Base-CUI-2026-02-27 (ami-091898c3a03efa550)"},
]

MOCK_WORKSPACE_SOURCE_WORKSPACES = [
    {"workspace_id": "ws-0123456789abcdef0", "workspace_name": "Windows - testuser (ws-0123456789abcdef0)"},
]

MOCK_HARDWARE_TYPES = [
    {"value": "STANDARD", "label": "Standard"},
    {"value": "PERFORMANCE", "label": "Performance"},
    {"value": "POWER", "label": "Power"},
    {"value": "POWERPRO", "label": "PowerPro"},
]

MOCK_DIRECTORIES = [
    {"id": "d-906603250f", "label": "testsre.local"},
]

MOCK_ENCRYPTION_KEY_ALIASES = [
    {"alias": "aws/workspaces", "label": "aws/workspaces"},
]

MOCK_USERNAMES = [
    {"username": "testuser", "label": "testuser (testuser@testsre.local)"},
]

MOCK_RUNNING_MODES = [
    {"value": "AUTO_STOP", "label": "Auto stop"},
    {"value": "ALWAYS_ON", "label": "Always on"},
]

MOCK_ENCLAVES = [
    {
        "research_group": "Neuroimaging",
        "enclave_name": "sre-research-enclave-01",
        "destination_account_id": "111111111111",
    },
    {
        "research_group": "Genomics",
        "enclave_name": "sre-research-enclave-02",
        "destination_account_id": "222222222222",
    },
]

MOCK_ENDPOINTS = [
    {
        "resource_type": "ec2",
        "resource_id": "i-0a1b2c3d4e5f1111",
        "name": "analytics-node-1111",
        "region": "us-east-1",
        "is_managed": True,
        "node_id": "mi-0f1e2d3c4b5a1111",
        "ssm_status": "Online",
        "destination_account_id": "111111111111",
    },
    {
        "resource_type": "workspace",
        "resource_id": "ws-012345671111",
        "name": "research-workspace-1111",
        "region": "us-east-1",
        "is_managed": True,
        "node_id": "mi-1234abcd56781111",
        "ssm_status": "Online",
        "destination_account_id": "111111111111",
    },
    {
        "resource_type": "ec2",
        "resource_id": "i-09f8e7d6c5b41111",
        "name": "batch-runner-1111",
        "region": "us-east-1",
        "is_managed": False,
        "node_id": None,
        "ssm_status": "Not registered",
        "destination_account_id": "111111111111",
    },
]

MOCK_VULNERABILITIES = [
    {
        "destination_account_id": "111111111111",
        "category": "actionable",
        "assessed_criticality": "High",
        "status": "Open",
        "days_open": "12",
        "days_actionable": "9",
        "account_id": "111111111111",
        "finding_type": "Package",
        "package_name": "openssl",
        "installed_version": "3.0.7",
        "fixed_version": "3.0.12",
        "vulnerability_id": "CVE-2026-1001",
        "vulnerability_source": "Inspector",
        "vulnerability_reported_at": "2026-03-01",
        "fix_available": "true",
        "exploit_available": "false",
        "resource_type": "ec2",
        "resource_id": "i-0a1b2c3d4e5f1111",
        "tag_name": "analytics-node-1111",
        "comments": "Patch during next enclave window.",
    },
    {
        "destination_account_id": "111111111111",
        "category": "planned",
        "assessed_criticality": "Medium",
        "status": "Open",
        "days_open": "5",
        "days_actionable": "3",
        "account_id": "111111111111",
        "finding_type": "Package",
        "package_name": "curl",
        "installed_version": "8.5.0",
        "fixed_version": "8.6.1",
        "vulnerability_id": "CVE-2026-1055",
        "vulnerability_source": "Inspector",
        "vulnerability_reported_at": "2026-03-06",
        "fix_available": "true",
        "exploit_available": "false",
        "resource_type": "workspace",
        "resource_id": "ws-012345671111",
        "tag_name": "research-workspace-1111",
        "comments": "Track with March workstation image refresh.",
    },
    {
        "destination_account_id": "111111111111",
        "category": "informational",
        "assessed_criticality": "Low",
        "status": "Observed",
        "days_open": "2",
        "days_actionable": "0",
        "account_id": "111111111111",
        "finding_type": "Configuration",
        "package_name": "",
        "installed_version": "",
        "fixed_version": "",
        "vulnerability_id": "CFG-2026-0201",
        "vulnerability_source": "Security Hub",
        "vulnerability_reported_at": "2026-03-09",
        "fix_available": "false",
        "exploit_available": "false",
        "resource_type": "ec2",
        "resource_id": "i-09f8e7d6c5b41111",
        "tag_name": "batch-runner-1111",
        "comments": "Manual observation captured for follow-up.",
    },
]

# Execution detail mock: steps and failure cause for demo.
MOCK_FAILURE_CAUSE = (
    "SSM Run Command failed: Instance i-0123456789abcdef0 is not in target state. "
    "Check SSM agent and IAM permissions."
)


def _mock_steps_for_execution(
    name: str,
    status: str,
) -> tuple[list[dict[str, Any]], int | None, int | None, str | None]:
    """Build steps list and current/failure index and cause for get-pipeline-execution-detail."""
    contract = get_pipeline_contract(name)
    if not contract or not contract.component_operations:
        return [], None, None, None
    current_index: int | None = 2 if status == "RUNNING" else None
    failure_index: int | None = 1 if status == "FAILED" else None
    failure_cause: str | None = MOCK_FAILURE_CAUSE if status == "FAILED" else None
    steps: list[dict[str, Any]] = []
    for i, step_info in enumerate(contract.component_operations):
        step_status = "pending"
        if status == "SUCCEEDED":
            step_status = "succeeded"
        elif status == "RUNNING":
            if current_index is not None:
                if i < current_index:
                    step_status = "succeeded"
                elif i == current_index:
                    step_status = "running"
        elif status == "FAILED" and failure_index is not None:
            if i < failure_index:
                step_status = "succeeded"
            elif i == failure_index:
                step_status = "failed"
        step_input: dict[str, Any] = {}
        step_output: dict[str, Any] = {}
        if step_status in ("succeeded", "running"):
            step_input = {"destination_account_id": "333333333333", "enclave_name": name}
        if step_status == "succeeded":
            step_output = {"status": "success"}
            if step_info.operation == "create-ad-connector":
                step_output["directory_id"] = "d-906603250f"
        if step_status == "failed":
            step_output = {"error": "SSM.RunCommandFailed", "cause": failure_cause}
        steps.append({
            "step_id": step_info.step_id,
            "step_name": step_info.label,
            "status": step_status,
            "input": step_input,
            "output": step_output,
            "error": step_output.get("error"),
            "cause": step_output.get("cause"),
        })
    return steps, current_index, failure_index, failure_cause


def _execution_by_id(execution_id: str) -> dict[str, Any] | None:
    """Return mock execution record by id from active + recent."""
    for e in MOCK_ACTIVE_EXECUTIONS + MOCK_RECENT_EXECUTIONS:
        if e.get("execution_id") == execution_id:
            return e
    return None


class MockBackend(Backend):
    """Backend that returns realistic mock data aligned with contract response shapes."""

    def invoke_operation(self, payload: dict[str, Any]) -> dict[str, Any]:
        operation = payload.get("operation")
        if operation == "unlock-user":
            username = (payload.get("username") or "").strip()
            if not username:
                return {"status": "error", "error": "ValidationError", "message": "Username is required."}
            return {"status": "success", "message": f"User {username} has been unlocked."}
        if operation == "create-poam-entry":
            mode = str(payload.get("mode") or "").strip().lower()
            poam_id = str(payload.get("poam_id") or "").strip()
            status = str(payload.get("status") or "").strip().lower()
            if not poam_id or status not in {"open", "closed"}:
                return {
                    "status": "error",
                    "error": "ValidationError",
                    "message": "poam_id and status are required.",
                }
            if mode == "verify":
                return {
                    "status": "success",
                    "verified": True,
                    "poam_id": poam_id,
                    "message": f"POAM entry {poam_id} verified.",
                }
            return {
                "status": "success",
                "poam_id": poam_id,
                "entry_status": status,
                "message": f"POAM entry {poam_id} saved.",
            }
        # Generic success for any other operation in contracts
        return {"status": "success", "message": f"Operation {operation} completed (mock)."}

    def start_pipeline(self, pipeline_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        execution_id = str(uuid4())
        now = django_tz.now()
        contract = get_pipeline_contract(pipeline_id)
        label = contract.label if contract else pipeline_id.replace("-", " ").title()
        return {
            "execution_id": execution_id,
            "execution_arn": f"arn:aws:states:us-east-1:123456789012:execution:{pipeline_id}:{execution_id}",
            "name": pipeline_id,
            "label": label,
            "status": "Running",
            "started_at": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "started_at_relative": "Just now",
        }

    def run_query(self, payload: dict[str, Any]) -> dict[str, Any]:
        query = payload.get("query")
        if not query:
            return {"status": "error", "error": "ValidationError", "message": "query is required."}

        if query == "list-pipeline-executions":
            pipeline_id = payload.get("pipeline_id")
            # Accept state machine ARN or short name: extract name after :stateMachine: for filtering
            pipeline_name = None
            if pipeline_id:
                if ":stateMachine:" in pipeline_id:
                    pipeline_name = pipeline_id.split(":stateMachine:")[-1].split(":")[0]
                else:
                    pipeline_name = pipeline_id
            status_filter = (payload.get("status_filter") or "").strip().upper()
            combined = []
            for e in MOCK_ACTIVE_EXECUTIONS + MOCK_RECENT_EXECUTIONS:
                if pipeline_name and e.get("name") != pipeline_name:
                    continue
                s = e.get("status", "")
                if status_filter == "NOT_RUNNING":
                    if s == "RUNNING":
                        continue
                elif status_filter and s != status_filter:
                    continue
                combined.append({
                    "execution_id": e["execution_id"],
                    "execution_arn": e["execution_arn"],
                    "name": e["name"],
                    "label": e["label"],
                    "pipeline_id": e.get("pipeline_id") or _state_machine_arn_from_execution_arn(e["execution_arn"]),
                    "status": e["status"],
                    "started_at": e["started_at"],
                    "stopped_at": e.get("stopped_at"),
                    "enclave_name": e["enclave_name"],
                })
            max_results = payload.get("max_results")
            if max_results is not None:
                combined = combined[: max_results]
            return {"status": "success", "result": combined}

        if query == "get-pipeline-execution-detail":
            execution_id = payload.get("execution_id")
            execution_arn = payload.get("execution_arn")
            if not execution_id or not execution_arn:
                return {
                    "status": "error",
                    "error": "ValidationError",
                    "message": "execution_id and execution_arn required.",
                }
            rec = _execution_by_id(execution_id)
            if not rec:
                return {"status": "error", "error": "NotFound", "message": f"Execution {execution_id} not found."}
            name = rec.get("name", "")
            status = rec.get("status", "RUNNING")
            steps, current_index, failure_index, failure_cause = _mock_steps_for_execution(name, status)
            pipeline_id_val = rec.get("pipeline_id") or _state_machine_arn_from_execution_arn(
                rec["execution_arn"]
            )
            return {
                "status": "success",
                "result": {
                    "execution_id": rec["execution_id"],
                    "execution_arn": rec["execution_arn"],
                    "name": rec["name"],
                    "label": rec["label"],
                    "pipeline_id": pipeline_id_val,
                    "status": rec["status"],
                    "started_at": rec["started_at"],
                    "stopped_at": rec.get("stopped_at"),
                    "enclave_name": rec["enclave_name"],
                    "steps": steps,
                    "current_step_index": current_index,
                    "failure_step_index": failure_index,
                    "failure_cause": failure_cause,
                },
            }

        if query == "get-pipeline-step-logs":
            return {
                "status": "success",
                "result": {"logs": ["[Mock] Step logs not available in mock backend."]},
            }

        if query == "retrieve-ec2-source-images":
            return {"status": "success", "result": list(MOCK_EC2_SOURCE_IMAGES)}

        if query == "retrieve-workspace-source-workspaces":
            return {"status": "success", "result": list(MOCK_WORKSPACE_SOURCE_WORKSPACES)}

        if query == "retrieve-workspace-hardware-types":
            return {"status": "success", "result": list(MOCK_HARDWARE_TYPES)}

        if query == "retrieve-workspace-directories":
            return {"status": "success", "result": list(MOCK_DIRECTORIES)}

        if query == "retrieve-workspace-encryption-key-aliases":
            return {"status": "success", "result": list(MOCK_ENCRYPTION_KEY_ALIASES)}

        if query == "retrieve-workspace-usernames":
            return {"status": "success", "result": list(MOCK_USERNAMES)}

        if query == "retrieve-workspace-running-modes":
            return {"status": "success", "result": list(MOCK_RUNNING_MODES)}

        if query == "list-enclaves":
            return {"status": "success", "result": list(MOCK_ENCLAVES)}

        if query == "list-endpoints":
            destination_account_id = payload.get("destination_account_id")
            destination_region = payload.get("destination_region")
            result = [
                item
                for item in MOCK_ENDPOINTS
                if (
                    (destination_account_id is None or item.get("destination_account_id") == destination_account_id)
                    and (destination_region is None or item.get("region") == destination_region)
                )
            ]
            return {"status": "success", "result": result}

        if query == "list-vulnerabilities":
            destination_account_id = payload.get("destination_account_id")
            resource_id = payload.get("resource_id")
            category = payload.get("category")
            result = [
                item
                for item in MOCK_VULNERABILITIES
                if (
                    (destination_account_id is None or item.get("destination_account_id") == destination_account_id)
                    and (resource_id is None or item.get("resource_id") == resource_id)
                    and (category is None or item.get("category") == category)
                )
            ]
            return {"status": "success", "result": result}

        return {"status": "error", "error": "UnknownQuery", "message": f"Unknown query: {query}"}
