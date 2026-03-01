from datetime import date, timedelta
from typing import Any
from uuid import uuid4

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from landing.forms import EnclaveOption, PipelineStartForm
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

SAMPLE_ACTIVE_EXECUTIONS = [
    {
        "name": "provision-ad-connector",
        "label": "Provision AD Connector",
        "enclave": "sre-dev-enclave-01",
        "started_at": "6 minutes ago",
        "status": "Running",
    },
    {
        "name": "provision-linux-workspace",
        "label": "Provision Linux Workspace",
        "enclave": "sre-research-enclave-02",
        "started_at": "18 minutes ago",
        "status": "Waiting for workspace registration",
    },
]

SAMPLE_RECENT_EXECUTIONS = [
    {
        "name": "provision-windows-workspace",
        "label": "Provision Windows Workspace",
        "enclave": "sre-research-enclave-01",
        "completed_at": "Today, 09:42 UTC",
        "status": "Succeeded",
    },
    {
        "name": "provision-ec2-instance",
        "label": "Provision EC2 Instance",
        "enclave": "sre-research-enclave-03",
        "completed_at": "Today, 08:17 UTC",
        "status": "Failed",
    },
    {
        "name": "provision-ad-connector",
        "label": "Provision AD Connector",
        "enclave": "sre-dev-enclave-01",
        "completed_at": "Yesterday, 20:06 UTC",
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


def pipeline_execution_detail(request: HttpRequest, execution_id: str) -> HttpResponse:
    """Display a minimal execution detail stub until feature 003 is implemented."""
    started_executions = request.session.get(SESSION_STARTED_EXECUTIONS_KEY, [])
    execution = next((item for item in started_executions if item.get("execution_id") == execution_id), None)
    context = {
        "execution": execution,
        "execution_id": execution_id,
    }
    return render(request, "landing/pipeline_execution_detail.html", context)
