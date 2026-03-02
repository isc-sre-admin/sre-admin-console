import json
from datetime import date, timedelta
from typing import Any
from uuid import uuid4

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from landing.forms import EnclaveOption, PipelineStartForm
from landing.operation_contracts import get_operation_contract
from landing.pipeline_contracts import get_pipeline_contract, list_pipeline_contracts

SESSION_STARTED_EXECUTIONS_KEY = "started_pipeline_executions"

SAMPLE_ENCLAVES: tuple[EnclaveOption, ...] = (
    EnclaveOption(
        research_group="Neuroimaging",
        enclave_name="sre-research-enclave-01",
        destination_account_id="111111111111",
    ),
    EnclaveOption(
        research_group="Genomics",
        enclave_name="sre-research-enclave-02",
        destination_account_id="222222222222",
    ),
    EnclaveOption(
        research_group="Clinical Trials",
        enclave_name="sre-research-enclave-03",
        destination_account_id="333333333333",
    ),
    EnclaveOption(
        research_group="Platform Engineering",
        enclave_name="sre-dev-enclave-01",
        destination_account_id="444444444444",
    ),
)

# Stable fake execution IDs for sample rows so each pipeline label can link to detail.
SAMPLE_ACTIVE_EXECUTION_IDS = (
    "a1b2c3d4-active-ad-connector",
    "a2b3c4d5-active-linux-ws",
)
SAMPLE_RECENT_EXECUTION_IDS = (
    "b1c2d3e4-recent-windows-ws",
    "b2c3d4e5-recent-ec2-failed",
    "b3c4d5e6-recent-ad-connector",
)

SAMPLE_ACTIVE_EXECUTIONS = [
    {
        "execution_id": SAMPLE_ACTIVE_EXECUTION_IDS[0],
        "execution_arn": (
            f"arn:aws:states:us-east-1:123456789012:execution:provision-ad-connector:{SAMPLE_ACTIVE_EXECUTION_IDS[0]}"
        ),
        "name": "provision-ad-connector",
        "label": "Provision AD Connector",
        "enclave": "sre-dev-enclave-01",
        "started_at": "6 minutes ago",
        "status": "Running",
    },
    {
        "execution_id": SAMPLE_ACTIVE_EXECUTION_IDS[1],
        "execution_arn": (
            f"arn:aws:states:us-east-1:123456789012:execution:provision-linux-workspace:{SAMPLE_ACTIVE_EXECUTION_IDS[1]}"
        ),
        "name": "provision-linux-workspace",
        "label": "Provision Linux Workspace",
        "enclave": "sre-research-enclave-02",
        "started_at": "18 minutes ago",
        "status": "Waiting for workspace registration",
    },
]

SAMPLE_RECENT_EXECUTIONS = [
    {
        "execution_id": SAMPLE_RECENT_EXECUTION_IDS[0],
        "execution_arn": (
            f"arn:aws:states:us-east-1:123456789012:execution:provision-windows-workspace:{SAMPLE_RECENT_EXECUTION_IDS[0]}"
        ),
        "name": "provision-windows-workspace",
        "label": "Provision Windows Workspace",
        "enclave": "sre-research-enclave-01",
        "completed_at": "Today, 09:42 UTC",
        "started_at_full": "Today, 09:15 UTC",
        "status": "Succeeded",
    },
    {
        "execution_id": SAMPLE_RECENT_EXECUTION_IDS[1],
        "execution_arn": (
            f"arn:aws:states:us-east-1:123456789012:execution:provision-ec2-instance:{SAMPLE_RECENT_EXECUTION_IDS[1]}"
        ),
        "name": "provision-ec2-instance",
        "label": "Provision EC2 Instance",
        "enclave": "sre-research-enclave-03",
        "completed_at": "Today, 08:17 UTC",
        "started_at_full": "Today, 08:00 UTC",
        "status": "Failed",
    },
    {
        "execution_id": SAMPLE_RECENT_EXECUTION_IDS[2],
        "execution_arn": (
            f"arn:aws:states:us-east-1:123456789012:execution:provision-ad-connector:{SAMPLE_RECENT_EXECUTION_IDS[2]}"
        ),
        "name": "provision-ad-connector",
        "label": "Provision AD Connector",
        "enclave": "sre-dev-enclave-01",
        "completed_at": "Yesterday, 20:06 UTC",
        "started_at_full": "Yesterday, 19:30 UTC",
        "status": "Succeeded",
    },
]


def _get_ami_choices(source_region: str) -> list[tuple[str, str]]:
    """Return (ami_id, display_label) choices for the AMI dropdown.

    When the retrieve-ec2-source-images query is implemented, call it with
    source_region and map the response list to (ami_id, f"{ami_name} ({ami_id})").
    """
    # Sample data until backend query retrieve-ec2-source-images is available.
    _ = source_region
    return [
        ("ami-091898c3a03efa550", "SRE-Rocky9-Base-CUI-2026-02-27 (ami-091898c3a03efa550)"),
    ]


def _get_workspace_choices(source_region: str) -> list[tuple[str, str]]:
    """Return (workspace_id, display_label) choices for the Source workspace id dropdown.

    When the retrieve-workspace-source-workspaces query is implemented, call it
    with source_region and map the response list to
    (workspace_id, f"{workspace_name} ({workspace_id})").
    """
    # Sample data until backend query retrieve-workspace-source-workspaces is available.
    _ = source_region
    return [
        ("ws-0123456789abcdef0", "Windows - testuser (ws-0123456789abcdef0)"),
    ]


def _get_hardware_type_choices(source_region: str | None = None) -> list[tuple[str, str]]:
    """Return (value, label) choices for the Hardware type dropdown.

    When the retrieve-workspace-hardware-types query is implemented, call it
    with source_region (optional) and map the response list to (value, label).
    """
    # Sample data until backend query retrieve-workspace-hardware-types is available.
    _ = source_region
    return [
        ("STANDARD", "Standard"),
        ("PERFORMANCE", "Performance"),
        ("POWER", "Power"),
        ("POWERPRO", "PowerPro"),
    ]


def _get_directory_choices(destination_account_id: str | None = None) -> list[tuple[str, str]]:
    """Return (id, label) choices for the Directory id dropdown.

    When the retrieve-workspace-directories query is implemented, call it with
    destination_account_id and map the response list to (id, label).
    """
    # Sample data until backend query retrieve-workspace-directories is available.
    _ = destination_account_id
    return [
        ("d-906603250f", "testsre.local"),
    ]


def _get_encryption_key_alias_choices(destination_account_id: str | None = None) -> list[tuple[str, str]]:
    """Return (alias, label) choices for the Encryption key alias dropdown.

    When the retrieve-workspace-encryption-key-aliases query is implemented,
    call it with destination_account_id and map the response list to (alias, label).
    """
    # Sample data until backend query retrieve-workspace-encryption-key-aliases is available.
    _ = destination_account_id
    return [
        ("aws/workspaces", "aws/workspaces"),
    ]


def _get_username_choices(
    destination_account_id: str | None = None,
    directory_id: str | None = None,
) -> list[tuple[str, str]]:
    """Return (username, label) choices for the Username dropdown.

    When the retrieve-workspace-usernames query is implemented, call it with
    destination_account_id (and optionally directory_id) and map the response
    list to (username, label).
    """
    # Sample data until backend query retrieve-workspace-usernames is available.
    _ = destination_account_id
    _ = directory_id
    return [
        ("testuser", "testuser (testuser@testsre.local)"),
    ]


def _get_running_mode_choices() -> list[tuple[str, str]]:
    """Return (value, label) choices for the Running mode radio buttons.

    When the retrieve-workspace-running-modes query is implemented, call it
    and map the response list to (value, label). Labels are human-readable
    (e.g. Auto stop, Always on).
    """
    # Sample data until backend query retrieve-workspace-running-modes is available.
    return [
        ("AUTO_STOP", "Auto stop"),
        ("ALWAYS_ON", "Always on"),
    ]


def _start_pipeline_execution(pipeline_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Simulate pipeline start while backend API wiring is not yet implemented."""
    execution_id = str(uuid4())
    started_at = timezone.now()
    return {
        "execution_id": execution_id,
        "execution_arn": f"arn:aws:states:us-east-1:123456789012:execution:{pipeline_id}:{execution_id}",
        "name": pipeline_id,
        "status": "Running",
        "started_at": started_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "started_at_relative": "Just now",
        "payload": payload,
    }


def _save_execution_to_session(request: HttpRequest, execution: dict[str, Any], enclave_name: str) -> None:
    started_executions = request.session.get(SESSION_STARTED_EXECUTIONS_KEY, [])
    record = {
        "execution_id": execution["execution_id"],
        "execution_arn": execution["execution_arn"],
        "name": execution["name"],
        "status": execution["status"],
        "enclave": enclave_name,
        "started_at": execution["started_at_relative"],
        "started_at_full": execution["started_at"],
    }
    if "label" in execution:
        record["label"] = execution["label"]
    started_executions.insert(0, record)
    request.session[SESSION_STARTED_EXECUTIONS_KEY] = started_executions[:10]


def _execute_unlock_user(request: HttpRequest) -> HttpResponse:
    """Run unlock-user operation (stub until backend API is available)."""
    username = (request.POST.get("username") or "").strip()
    if not username:
        return HttpResponse(
            json.dumps({"success": False, "error": "Username is required."}),
            content_type="application/json",
            status=400,
        )
    # Stub: backend invoke would go here. Payload matches proposed contract.
    _payload = {"operation": "unlock-user", "username": username}
    return HttpResponse(
        json.dumps({
            "success": True,
            "message": "Unlock user request accepted. (Backend not yet connected.)",
        }),
        content_type="application/json",
    )


@login_required
def execute_operation(request: HttpRequest, operation_id: str) -> HttpResponse:
    """Execute a quick operation (e.g. unlock-user) and return JSON."""
    if request.method != "POST":
        return HttpResponse(
            json.dumps({"success": False, "error": "Method not allowed."}),
            content_type="application/json",
            status=405,
        )
    contract = get_operation_contract(operation_id)
    if contract is None:
        return HttpResponse(
            json.dumps({"success": False, "error": "Unknown operation."}),
            content_type="application/json",
            status=404,
        )
    if operation_id == "unlock-user":
        return _execute_unlock_user(request)
    return HttpResponse(
        json.dumps({"success": False, "error": "Operation not implemented."}),
        content_type="application/json",
        status=501,
    )


@login_required
def home(request: HttpRequest) -> HttpResponse:
    """Render the primary workflow-oriented landing page."""
    end_date = date.today()
    start_date = end_date - timedelta(days=7)
    started_executions = request.session.get(SESSION_STARTED_EXECUTIONS_KEY, [])
    active_executions = [*started_executions, *SAMPLE_ACTIVE_EXECUTIONS]
    context = {
        "active_executions": active_executions,
        "recent_executions": SAMPLE_RECENT_EXECUTIONS,
        "relative_ranges": [7, 30, 60],
        "default_range_days": 7,
        "default_start_date": start_date.isoformat(),
        "default_end_date": end_date.isoformat(),
    }
    return render(request, "landing/home.html", context)


@login_required
def start_pipeline_execution(request: HttpRequest, pipeline_id: str) -> HttpResponse:
    """Render and process the generic start-pipeline execution form."""
    contract = get_pipeline_contract(pipeline_id)
    if contract is None:
        raise Http404("Unknown pipeline.")

    ami_choices: list[tuple[str, str]] = []
    if "ami_id" in contract.all_inputs:
        ami_choices = _get_ami_choices("us-east-1")

    workspace_choices: list[tuple[str, str]] = []
    if "source_workspace_id" in contract.all_inputs:
        workspace_choices = _get_workspace_choices("us-east-1")

    hardware_type_choices: list[tuple[str, str]] = []
    if "hardware_type" in contract.all_inputs:
        hardware_type_choices = _get_hardware_type_choices("us-east-1")

    directory_choices: list[tuple[str, str]] = []
    if "directory_id" in contract.all_inputs:
        directory_choices = _get_directory_choices()

    encryption_key_alias_choices: list[tuple[str, str]] = []
    if "encryption_key_alias" in contract.all_inputs:
        encryption_key_alias_choices = _get_encryption_key_alias_choices()

    username_choices: list[tuple[str, str]] = []
    if "username" in contract.all_inputs:
        username_choices = _get_username_choices()

    running_mode_choices: list[tuple[str, str]] = []
    if "running_mode" in contract.all_inputs:
        running_mode_choices = _get_running_mode_choices()

    started_execution: dict[str, Any] | None = None
    form = PipelineStartForm(
        request.POST or None,
        contract=contract,
        enclaves=SAMPLE_ENCLAVES,
        ami_choices=ami_choices,
        workspace_choices=workspace_choices,
        hardware_type_choices=hardware_type_choices,
        directory_choices=directory_choices,
        encryption_key_alias_choices=encryption_key_alias_choices,
        username_choices=username_choices,
        running_mode_choices=running_mode_choices,
    )
    if request.method == "POST":
        if form.is_valid():
            payload = form.build_pipeline_payload()
            started_execution = _start_pipeline_execution(contract.id, payload)
            started_execution["label"] = contract.label
            _save_execution_to_session(request, started_execution, form.cleaned_data["enclave_name"])
            form = PipelineStartForm(
                contract=contract,
                enclaves=SAMPLE_ENCLAVES,
                ami_choices=ami_choices,
                workspace_choices=workspace_choices,
                hardware_type_choices=hardware_type_choices,
                directory_choices=directory_choices,
                encryption_key_alias_choices=encryption_key_alias_choices,
                username_choices=username_choices,
                running_mode_choices=running_mode_choices,
                initial={"mode": "modify"},
            )
        else:
            form.add_error(None, "Please resolve the validation errors and submit again.")

    context = {
        "contract": contract,
        "available_contracts": list_pipeline_contracts(),
        "form": form,
        "started_execution": started_execution,
    }
    return render(request, "landing/start_pipeline_execution.html", context)


def _get_execution_by_id(request: HttpRequest, execution_id: str) -> dict[str, Any] | None:
    """Resolve execution by id from session or sample data."""
    started = request.session.get(SESSION_STARTED_EXECUTIONS_KEY, [])
    for item in started:
        if item.get("execution_id") == execution_id:
            # Session record may lack execution_arn and label
            record = dict(item)
            if "execution_arn" not in record and "name" in record:
                record["execution_arn"] = (
                    f"arn:aws:states:us-east-1:123456789012:execution:{record['name']}:{execution_id}"
                )
            if "label" not in record and "name" in record:
                contract = get_pipeline_contract(record["name"])
                record["label"] = contract.label if contract else record["name"]
            if "started_at_full" not in record:
                record["started_at_full"] = record.get("started_at", "")
            return record
    for item in SAMPLE_ACTIVE_EXECUTIONS + SAMPLE_RECENT_EXECUTIONS:
        if item.get("execution_id") == execution_id:
            return dict(item)
    return None


def _build_execution_steps(
    execution: dict[str, Any],
) -> tuple[list[dict[str, Any]], int | None, int | None, str | None]:
    """Build steps list and optional current/failure index and cause from contract and execution status."""
    contract = get_pipeline_contract(execution.get("name", ""))
    if not contract or not contract.component_operations:
        return [], None, None, None

    steps: list[dict[str, Any]] = []
    status = execution.get("status", "")
    # For demo: Running -> current at step index 2; Failed -> fail at step index 1 with cause
    current_index: int | None = 2 if status in ("Running", "Waiting for workspace registration") else None
    failure_index: int | None = 1 if status == "Failed" else None
    failure_cause: str | None = (
        "SSM Run Command failed: Instance i-0123456789abcdef0 is not in target state. "
        "Check SSM agent and IAM permissions."
        if status == "Failed"
        else None
    )

    for i, step_info in enumerate(contract.component_operations):
        step_status = "pending"
        if status == "Succeeded" or (status not in ("Running", "Waiting for workspace registration", "Failed")):
            step_status = "succeeded"
        if status == "Running" or status == "Waiting for workspace registration":
            if current_index is not None:
                if i < current_index:
                    step_status = "succeeded"
                elif i == current_index:
                    step_status = "running"
        if status == "Failed":
            if failure_index is not None:
                if i < failure_index:
                    step_status = "succeeded"
                elif i == failure_index:
                    step_status = "failed"
                else:
                    step_status = "pending"

        step_input: dict[str, Any] = {}
        step_output: dict[str, Any] = {}
        if step_status in ("succeeded", "running"):
            step_input = {"destination_account_id": "333333333333", "enclave_name": execution.get("enclave", "")}
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
            "input_display": json.dumps(step_input, indent=2) if step_input else "",
            "output_display": json.dumps(step_output, indent=2) if step_output else "",
            "error": step_output.get("error") if step_status == "failed" else None,
            "cause": step_output.get("cause") if step_status == "failed" else None,
        })

    return steps, current_index, failure_index, failure_cause


@login_required
def pipeline_execution_detail(request: HttpRequest, execution_id: str) -> HttpResponse:
    """Display pipeline execution detail: steps, current step, expand I/O, failure cause; supports JSON for polling."""
    execution = _get_execution_by_id(request, execution_id)
    if execution is None:
        raise Http404("Execution not found.")

    steps, current_step_index, failure_step_index, failure_cause = _build_execution_steps(execution)
    started_at_full = execution.get("started_at_full") or execution.get("started_at", "")
    stopped_at = execution.get("stopped_at") or (
        execution.get("completed_at") if execution.get("status") in ("Succeeded", "Failed") else None
    )

    context = {
        "execution": execution,
        "execution_id": execution_id,
        "steps": steps,
        "current_step_index": current_step_index,
        "failure_step_index": failure_step_index,
        "failure_cause": failure_cause,
        "started_at_full": started_at_full,
        "stopped_at": stopped_at,
    }

    wants_json = (
        request.GET.get("format") == "json"
        or request.headers.get("Accept", "").split(",")[0].strip() == "application/json"
    )
    if wants_json:
        payload = {
            "execution_id": execution_id,
            "execution_arn": execution.get("execution_arn"),
            "name": execution.get("name"),
            "label": execution.get("label"),
            "status": execution.get("status"),
            "started_at": started_at_full,
            "stopped_at": stopped_at,
            "enclave_name": execution.get("enclave"),
            "steps": steps,
            "current_step_index": current_step_index,
            "failure_step_index": failure_step_index,
            "failure_cause": failure_cause,
        }
        return HttpResponse(
            json.dumps(payload, indent=2),
            content_type="application/json",
        )

    return render(request, "landing/pipeline_execution_detail.html", context)
