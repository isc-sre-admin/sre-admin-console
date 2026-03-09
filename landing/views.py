import json
import logging
from datetime import date, timedelta
from typing import Any

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from landing.backend import get_backend
from landing.backend.mock import (
    SAMPLE_ACTIVE_EXECUTION_IDS as MOCK_SAMPLE_ACTIVE_EXECUTION_IDS,
)
from landing.backend.mock import (
    SAMPLE_RECENT_EXECUTION_IDS as MOCK_SAMPLE_RECENT_EXECUTION_IDS,
)
from landing.enclaves import SAMPLE_ENCLAVES
from landing.forms import PipelineStartForm
from landing.operation_contracts import get_operation_contract
from landing.pipeline_contracts import get_pipeline_contract, list_pipeline_contracts

logger = logging.getLogger(__name__)

SESSION_STARTED_EXECUTIONS_KEY = "started_pipeline_executions"
SAMPLE_ACTIVE_EXECUTION_IDS = MOCK_SAMPLE_ACTIVE_EXECUTION_IDS
SAMPLE_RECENT_EXECUTION_IDS = MOCK_SAMPLE_RECENT_EXECUTION_IDS


def _pipeline_id_display(pipeline_id: str | None) -> str:
    """Return a short display value for pipeline_id (state machine name from ARN or as-is)."""
    if not pipeline_id:
        return ""
    if pipeline_id.startswith("arn:") and ":stateMachine:" in pipeline_id:
        return pipeline_id.split(":stateMachine:")[-1]
    return pipeline_id


def _get_ami_choices(source_region: str) -> list[tuple[str, str]]:
    """Return (ami_id, display_label) choices for the AMI dropdown via backend query."""
    result = get_backend().run_query({"query": "retrieve-ec2-source-images", "source_region": source_region})
    if result.get("status") != "success":
        return []
    items = result.get("result") or []
    return [(item["ami_id"], item.get("ami_name") or f"{item['ami_id']}") for item in items]


def _get_workspace_choices(source_region: str, os_type: str = "WINDOWS") -> list[tuple[str, str]]:
    """Return (workspace_id, display_label) choices for the Source workspace id dropdown via backend query."""
    result = get_backend().run_query({
        "query": "retrieve-workspace-source-workspaces",
        "source_region": source_region,
        "os_type": os_type,
    })
    if result.get("status") != "success":
        return []
    items = result.get("result") or []
    return [(item["workspace_id"], item.get("workspace_name") or item["workspace_id"]) for item in items]


def _get_hardware_type_choices(source_region: str | None = None) -> list[tuple[str, str]]:
    """Return (value, label) choices for the Hardware type dropdown via backend query."""
    payload: dict[str, Any] = {"query": "retrieve-workspace-hardware-types"}
    if source_region:
        payload["source_region"] = source_region
    result = get_backend().run_query(payload)
    if result.get("status") != "success":
        return []
    items = result.get("result") or []
    return [(item["value"], item.get("label") or item["value"]) for item in items]


def _get_directory_choices(destination_account_id: str | None = None) -> list[tuple[str, str]]:
    """Return (id, label) choices for the Directory id dropdown via backend query."""
    account_id = destination_account_id or ""
    result = get_backend().run_query({
        "query": "retrieve-workspace-directories",
        "destination_account_id": account_id,
    })
    if result.get("status") != "success":
        return []
    items = result.get("result") or []
    return [(item["id"], item.get("label") or item["id"]) for item in items]


def _get_encryption_key_alias_choices(destination_account_id: str | None = None) -> list[tuple[str, str]]:
    """Return (alias, label) choices for the Encryption key alias dropdown via backend query."""
    payload: dict[str, Any] = {"query": "retrieve-workspace-encryption-key-aliases"}
    if destination_account_id:
        payload["destination_account_id"] = destination_account_id
    result = get_backend().run_query(payload)
    if result.get("status") != "success":
        return []
    items = result.get("result") or []
    return [(item["alias"], item.get("label") or item["alias"]) for item in items]


def _get_username_choices(
    destination_account_id: str | None = None,
    directory_id: str | None = None,
) -> list[tuple[str, str]]:
    """Return (username, label) choices for the Username dropdown via backend query."""
    account_id = destination_account_id or ""
    payload: dict[str, Any] = {"query": "retrieve-workspace-usernames", "destination_account_id": account_id}
    if directory_id:
        payload["directory_id"] = directory_id
    result = get_backend().run_query(payload)
    if result.get("status") != "success":
        return []
    items = result.get("result") or []
    return [(item["username"], item.get("label") or item["username"]) for item in items]


def _get_running_mode_choices() -> list[tuple[str, str]]:
    """Return (value, label) choices for the Running mode radio buttons via backend query."""
    result = get_backend().run_query({"query": "retrieve-workspace-running-modes"})
    if result.get("status") != "success":
        return []
    items = result.get("result") or []
    return [(item["value"], item.get("label") or item["value"]) for item in items]


def _start_pipeline_execution(pipeline_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Start pipeline via backend (mock or real). Returns execution info or error dict."""
    return get_backend().start_pipeline(pipeline_id, payload)


def _save_execution_to_session(
    request: HttpRequest,
    execution: dict[str, Any],
    enclave_name: str,
    *,
    pipeline_id: str | None = None,
) -> None:
    started_executions = request.session.get(SESSION_STARTED_EXECUTIONS_KEY, [])
    record = {
        "execution_id": execution["execution_id"],
        "execution_arn": execution["execution_arn"],
        "name": execution["name"],
        "status": execution["status"],
        "enclave": enclave_name,
        "pipeline_id": pipeline_id or execution.get("name", ""),
        "started_at": execution["started_at_relative"],
        "started_at_full": execution["started_at"],
    }
    if "label" in execution:
        record["label"] = execution["label"]
    started_executions.insert(0, record)
    request.session[SESSION_STARTED_EXECUTIONS_KEY] = started_executions[:10]


def _execute_unlock_user(request: HttpRequest) -> HttpResponse:
    """Run unlock-user operation via backend (mock or real)."""
    username = (request.POST.get("username") or "").strip()
    if not username:
        return HttpResponse(
            json.dumps({"success": False, "error": "Username is required."}),
            content_type="application/json",
            status=400,
        )
    payload = {"operation": "unlock-user", "username": username}
    result = get_backend().invoke_operation(payload)
    if result.get("status") == "error":
        return HttpResponse(
            json.dumps({"success": False, "error": result.get("error", "Error"), "message": result.get("message", "")}),
            content_type="application/json",
            status=400,
        )
    return HttpResponse(
        json.dumps({"success": True, "message": result.get("message", "Unlock user request accepted.")}),
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


def _status_display(raw: str) -> str:
    """Map backend status (RUNNING/SUCCEEDED/FAILED) to template display (Running/Succeeded/Failed)."""
    u = (raw or "").upper()
    if u == "RUNNING":
        return "Running"
    if u == "SUCCEEDED":
        return "Succeeded"
    if u == "FAILED":
        return "Failed"
    return raw or "Unknown"


def _load_list_pipeline_executions_event() -> dict[str, Any] | None:
    """Load list-pipeline-executions event payload from landing/events/list-pipeline-executions.json."""
    path = settings.BASE_DIR / "landing" / "events" / "list-pipeline-executions.json"
    if not path.exists():
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def _list_pipeline_executions_payloads(
    status_filter: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[dict[str, Any]]:
    """Build payload(s) for list-pipeline-executions.

    When event file has pipeline_ids, return one payload (Lambda expects
    pipeline_ids in a single call). Otherwise one payload per pipeline_id
    from contracts. Optional status_filter/start_date/end_date are applied
    on top of the event file or base payload.
    """
    event = _load_list_pipeline_executions_event()
    if event and event.get("pipeline_ids"):
        # Lambda accepts the event-file shape with pipeline_ids (plural) in one invocation.
        payload = dict(event)
        if status_filter is not None:
            payload["status_filter"] = status_filter
        if start_date is not None:
            payload["start_date"] = start_date
        if end_date is not None:
            payload["end_date"] = end_date
        return [payload]
    base: dict[str, Any] = {"query": "list-pipeline-executions"}
    if status_filter is not None:
        base["status_filter"] = status_filter
    if start_date is not None:
        base["start_date"] = start_date
    if end_date is not None:
        base["end_date"] = end_date
    if event and event.get("max_results") is not None:
        base["max_results"] = event["max_results"]
    pipeline_ids = [c.id for c in list_pipeline_contracts()]
    return [{**base, "pipeline_id": pid} for pid in pipeline_ids]


def _executions_from_backend(request: HttpRequest) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Fetch pipeline executions from backend and merge with session-started; return (active, recent)."""
    backend = get_backend()
    scope = request.GET.get("scope") if request.method == "GET" else None
    start_date_param = request.GET.get("start_date") or None
    end_date_param = request.GET.get("end_date") or None
    status_filter = "NOT_RUNNING" if scope == "history" else None
    payloads = _list_pipeline_executions_payloads(
        status_filter=status_filter,
        start_date=start_date_param,
        end_date=end_date_param,
    )
    logger.info("pipeline-executions: using %s payload(s), backend=%s", len(payloads), type(backend).__name__)
    all_executions: list[dict[str, Any]] = []
    for i, payload in enumerate(payloads):
        result = backend.run_query(payload)
        status = result.get("status")
        result_list = result.get("result")
        count = len(result_list) if isinstance(result_list, list) else 0
        logger.info(
            "pipeline-executions: payload[%s] response status=%s, result_count=%s; keys=%s",
            i,
            status,
            count,
            list(result.keys()) if isinstance(result, dict) else None,
        )
        if status != "success":
            logger.warning(
                "pipeline-executions: payload[%s] non-success: error=%s message=%s",
                i,
                result.get("error"),
                result.get("message"),
            )
        if result.get("status") == "success":
            for e in result.get("result") or []:
                row = dict(e)
                row.setdefault("enclave", row.get("enclave_name", ""))
                row.setdefault("pipeline_id", row.get("pipeline_id", ""))
                row["pipeline_id_display"] = _pipeline_id_display(row.get("pipeline_id"))
                row.setdefault("started_at_full", row.get("started_at", ""))
                row.setdefault("completed_at", row.get("stopped_at"))
                row["status"] = _status_display(row.get("status", ""))
                all_executions.append(row)
    active = [e for e in all_executions if (e.get("status") or "").lower() == "running"]
    recent = [e for e in all_executions if e.get("status") in ("Succeeded", "Failed")]
    logger.info(
        "pipeline-executions: merged all=%s active=%s recent=%s",
        len(all_executions),
        len(active),
        len(recent),
    )
    started_executions = request.session.get(SESSION_STARTED_EXECUTIONS_KEY, [])
    for s in started_executions:
        r = dict(s)
        r.setdefault("enclave", r.get("enclave", ""))
        r.setdefault("pipeline_id", r.get("pipeline_id", ""))
        r.setdefault("pipeline_id_display", _pipeline_id_display(r.get("pipeline_id")))
        r.setdefault("status", "Running")
        if (r.get("status") or "").lower() != "running":
            continue
        if not any(a.get("execution_id") == r.get("execution_id") for a in active):
            active.insert(0, r)
    return active, recent


@login_required
def pipeline_executions_json(request: HttpRequest) -> HttpResponse:
    """Return active and recent pipeline executions as JSON for polling."""
    logger.info("pipeline-executions: GET /api/pipeline-executions/ request")
    active_executions, recent_executions = _executions_from_backend(request)
    poll_seconds = getattr(
        settings, "LANDING_PIPELINE_POLL_INTERVAL_SECONDS", 60
    )
    logger.info(
        "pipeline-executions: returning active=%s recent=%s",
        len(active_executions),
        len(recent_executions),
    )
    return JsonResponse(
        {
            "active_executions": active_executions,
            "recent_executions": recent_executions,
            "poll_interval_seconds": poll_seconds,
        }
    )


@login_required
def home(request: HttpRequest) -> HttpResponse:
    """Render the primary workflow-oriented landing page."""
    end_date = date.today()
    start_date = end_date - timedelta(days=7)
    active_executions, recent_executions = _executions_from_backend(request)
    poll_seconds = getattr(
        settings, "LANDING_PIPELINE_POLL_INTERVAL_SECONDS", 60
    )
    execution_detail_url_template = request.build_absolute_uri(
        reverse(
            "landing:pipeline-execution-detail",
            kwargs={"execution_id": "EXECUTION_ID"},
        )
    )
    context = {
        "active_executions": active_executions,
        "recent_executions": recent_executions,
        "relative_ranges": [7, 30, 60],
        "default_range_days": 7,
        "default_start_date": start_date.isoformat(),
        "default_end_date": end_date.isoformat(),
        "poll_interval_seconds": poll_seconds,
        "execution_detail_url_template": execution_detail_url_template,
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

    selected_enclave = (request.GET.get("enclave") or "").strip()
    valid_enclave_ids = {e.destination_account_id for e in SAMPLE_ENCLAVES}
    form_initial: dict[str, Any] = {}
    if selected_enclave and selected_enclave in valid_enclave_ids:
        form_initial["enclave"] = selected_enclave

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
        initial=form_initial,
    )
    if request.method == "POST":
        if form.is_valid():
            payload = form.build_pipeline_payload()
            started_execution = _start_pipeline_execution(contract.id, payload)
            if started_execution.get("status") == "error":
                form.add_error(
                    None,
                    started_execution.get("message") or started_execution.get("error", "Failed to start pipeline."),
                )
                started_execution = None
            else:
                if not started_execution.get("label"):
                    started_execution["label"] = contract.label
                started_execution["payload"] = payload
                _save_execution_to_session(
                    request,
                    started_execution,
                    form.cleaned_data["enclave_name"],
                    pipeline_id=contract.id,
                )
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


def _get_all_executions_from_backend() -> list[dict[str, Any]]:
    """Return merged list of executions from all pipelines (for lookup by execution_id)."""
    backend = get_backend()
    all_executions: list[dict[str, Any]] = []
    payloads = _list_pipeline_executions_payloads(status_filter="RUNNING")
    payloads += _list_pipeline_executions_payloads(status_filter="NOT_RUNNING")
    for payload in payloads:
        result = backend.run_query(payload)
        if result.get("status") == "success":
            for e in result.get("result") or []:
                row = dict(e)
                row.setdefault("enclave", row.get("enclave_name", ""))
                row.setdefault("pipeline_id", row.get("pipeline_id", ""))
                row["pipeline_id_display"] = _pipeline_id_display(row.get("pipeline_id"))
                row.setdefault("started_at_full", row.get("started_at", ""))
                row.setdefault("completed_at", row.get("stopped_at"))
                row["status"] = _status_display(row.get("status", ""))
                if not any(item.get("execution_id") == row.get("execution_id") for item in all_executions):
                    all_executions.append(row)
    return all_executions


def _get_execution_by_id(request: HttpRequest, execution_id: str) -> dict[str, Any] | None:
    """Resolve execution by id from session or backend."""
    started = request.session.get(SESSION_STARTED_EXECUTIONS_KEY, [])
    for item in started:
        if item.get("execution_id") == execution_id:
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
            record.setdefault("pipeline_id", record.get("pipeline_id", ""))
            record.setdefault("pipeline_id_display", _pipeline_id_display(record.get("pipeline_id")))
            return record
    for item in _get_all_executions_from_backend():
        if item.get("execution_id") == execution_id:
            return item
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

    execution_arn = execution.get("execution_arn")
    detail_result = None
    if execution_arn:
        detail_result = get_backend().run_query({
            "query": "get-pipeline-execution-detail",
            "execution_id": execution_id,
            "execution_arn": execution_arn,
        })
    if detail_result and detail_result.get("status") == "success":
        res = detail_result.get("result") or {}
        steps = res.get("steps") or []
        for s in steps:
            s["input_display"] = json.dumps(s.get("input") or {}, indent=2)
            s["output_display"] = json.dumps(s.get("output") or {}, indent=2)
        current_step_index = res.get("current_step_index")
        failure_step_index = res.get("failure_step_index")
        failure_cause = res.get("failure_cause")
        started_at_full = res.get("started_at") or execution.get("started_at_full") or execution.get("started_at", "")
        stopped_at = res.get("stopped_at")
    else:
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
            "pipeline_id": execution.get("pipeline_id"),
            "status": execution.get("status"),
            "started_at": started_at_full,
            "stopped_at": stopped_at,
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
