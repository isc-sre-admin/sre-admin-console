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
        "enclave": "sre-dev-enclave-01",
        "started_at": "6 minutes ago",
        "status": "Running",
    },
    {
        "name": "provision-linux-workspace",
        "enclave": "sre-research-enclave-02",
        "started_at": "18 minutes ago",
        "status": "Waiting for workspace registration",
    },
]

SAMPLE_RECENT_EXECUTIONS = [
    {
        "name": "provision-windows-workspace",
        "enclave": "sre-research-enclave-01",
        "completed_at": "Today, 09:42 UTC",
        "status": "Succeeded",
    },
    {
        "name": "provision-ec2-instance",
        "enclave": "sre-research-enclave-03",
        "completed_at": "Today, 08:17 UTC",
        "status": "Failed",
    },
    {
        "name": "provision-ad-connector",
        "enclave": "sre-dev-enclave-01",
        "completed_at": "Yesterday, 20:06 UTC",
        "status": "Succeeded",
    },
]


def _start_pipeline_execution(pipeline_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Simulate pipeline start while backend API wiring is not yet implemented."""
    execution_id = str(uuid4())
    started_at = timezone.now()
    return {
        "execution_id": execution_id,
        "execution_arn": f"arn:aws:states:us-east-1:123456789012:execution:{pipeline_name}:{execution_id}",
        "name": pipeline_name,
        "status": "Running",
        "started_at": started_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "started_at_relative": "Just now",
        "payload": payload,
    }


def _save_execution_to_session(request: HttpRequest, execution: dict[str, Any], enclave_name: str) -> None:
    started_executions = request.session.get(SESSION_STARTED_EXECUTIONS_KEY, [])
    started_executions.insert(
        0,
        {
            "execution_id": execution["execution_id"],
            "execution_arn": execution["execution_arn"],
            "name": execution["name"],
            "status": execution["status"],
            "enclave": enclave_name,
            "started_at": execution["started_at_relative"],
            "started_at_full": execution["started_at"],
        },
    )
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


def start_pipeline_execution(request: HttpRequest, pipeline_name: str) -> HttpResponse:
    """Render and process the generic start-pipeline execution form."""
    contract = get_pipeline_contract(pipeline_name)
    if contract is None:
        raise Http404("Unknown pipeline name.")

    started_execution: dict[str, Any] | None = None
    form = PipelineStartForm(request.POST or None, contract=contract, enclaves=SAMPLE_ENCLAVES)
    if request.method == "POST":
        if form.is_valid():
            payload = form.build_pipeline_payload()
            started_execution = _start_pipeline_execution(contract.name, payload)
            _save_execution_to_session(request, started_execution, form.cleaned_data["enclave_name"])
            form = PipelineStartForm(contract=contract, enclaves=SAMPLE_ENCLAVES, initial={"mode": "modify"})
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
