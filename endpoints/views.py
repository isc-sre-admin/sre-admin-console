import json
from dataclasses import dataclass
from typing import Any

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from endpoints.operation_contracts import get_endpoint_operation_contract
from landing.backend import get_backend
from landing.enclaves import SAMPLE_ENCLAVES
from landing.forms import DEFAULT_REGION, EnclaveOption

SUPPORTED_RESOURCE_TYPES = {"ec2", "workspace"}


@dataclass(frozen=True, slots=True)
class EndpointRecord:
    resource_type: str
    resource_id: str
    name: str
    region: str
    is_managed: bool
    node_id: str | None
    ssm_status: str
    last_patched_at: str | None = None
    patch_managed: bool = False


def _sample_endpoints_for_enclave(enclave_id: str, region: str) -> list[EndpointRecord]:
    suffix = enclave_id[-4:]
    return [
        EndpointRecord(
            resource_type="ec2",
            resource_id=f"i-0a1b2c3d4e5f{suffix}",
            name=f"analytics-node-{suffix}",
            region=region,
            is_managed=True,
            node_id=f"mi-0f1e2d3c4b5a{suffix}",
            ssm_status="Online",
            last_patched_at="2025-07-21 14:32 UTC",
            patch_managed=True,
        ),
        EndpointRecord(
            resource_type="workspace",
            resource_id=f"ws-01234567{suffix}",
            name=f"research-workspace-{suffix}",
            region=region,
            is_managed=True,
            node_id=f"mi-1234abcd5678{suffix}",
            ssm_status="Online",
            last_patched_at="2025-07-19 09:15 UTC",
            patch_managed=True,
        ),
        EndpointRecord(
            resource_type="ec2",
            resource_id=f"i-09f8e7d6c5b4{suffix}",
            name=f"batch-runner-{suffix}",
            region=region,
            is_managed=False,
            node_id=None,
            ssm_status="Not registered",
            last_patched_at=None,
            patch_managed=False,
        ),
    ]


def _coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _normalize_endpoint(item: dict[str, Any], *, region: str) -> EndpointRecord | None:
    raw_type = (item.get("resource_type") or item.get("type") or "").strip().lower()
    if raw_type not in SUPPORTED_RESOURCE_TYPES:
        if item.get("workspace_id"):
            raw_type = "workspace"
        elif item.get("instance_id"):
            raw_type = "ec2"
        else:
            return None

    resource_id = (
        item.get("resource_id")
        or item.get("instance_id")
        or item.get("workspace_id")
        or item.get("node_id")
        or ""
    )
    resource_id = str(resource_id).strip()
    if not resource_id:
        return None

    endpoint_region = str(item.get("region") or item.get("destination_region") or region).strip() or region
    node_id = str(item.get("node_id") or item.get("managed_instance_id") or "").strip() or None
    ping_status = str(item.get("ping_status") or item.get("ssm_status") or "").strip()
    is_managed = _coerce_bool(item.get("is_managed") or item.get("ssm_registered"))
    unmanaged_statuses = {"not registered", "unregistered", "not-managed"}
    if ping_status and ping_status.strip().lower() not in unmanaged_statuses:
        is_managed = True
    if is_managed and node_id is None and resource_id.startswith("mi-"):
        node_id = resource_id

    raw_last_patched = item.get("last_patched_at")
    last_patched_at = str(raw_last_patched).strip() if raw_last_patched else None
    patch_managed = _coerce_bool(item.get("patch_managed"))

    return EndpointRecord(
        resource_type=raw_type,
        resource_id=resource_id,
        name=str(item.get("name") or item.get("label") or resource_id).strip(),
        region=endpoint_region,
        is_managed=is_managed,
        node_id=node_id,
        ssm_status=ping_status or ("Online" if is_managed else "Not registered"),
        last_patched_at=last_patched_at,
        patch_managed=patch_managed,
    )


def _load_enclaves() -> tuple[tuple[EnclaveOption, ...], bool, str | None]:
    """Load enclave options from backend list-enclaves query, falling back to sample data.

    Returns (enclaves, using_backend_data, backend_note).
    """
    payload = {"query": "list-enclaves"}
    result = get_backend().run_query(payload)
    if result.get("status") == "success":
        enclaves: list[EnclaveOption] = []
        for item in result.get("result") or []:
            if not isinstance(item, dict):
                continue
            research_group = str(item.get("research_group") or "").strip()
            enclave_name = str(item.get("enclave_name") or "").strip()
            destination_account_id = str(item.get("destination_account_id") or "").strip()
            if not enclave_name or not destination_account_id:
                continue
            if not research_group:
                research_group = enclave_name
            enclaves.append(
                EnclaveOption(
                    research_group=research_group,
                    enclave_name=enclave_name,
                    destination_account_id=destination_account_id,
                )
            )
        if enclaves:
            return tuple(enclaves), True, None

    note = "Enclave list is not available from the backend yet. Showing sample enclaves for prototyping."
    return SAMPLE_ENCLAVES, False, note


def _load_endpoints_for_enclave(
    destination_account_id: str,
    *,
    region: str,
) -> tuple[list[EndpointRecord], bool, str | None]:
    payload = {
        "query": "list-endpoints",
        "destination_account_id": destination_account_id,
        "destination_region": region,
    }
    result = get_backend().run_query(payload)
    if result.get("status") == "success":
        records: list[EndpointRecord] = []
        for item in result.get("result") or []:
            if isinstance(item, dict):
                record = _normalize_endpoint(item, region=region)
                if record:
                    records.append(record)
        return records, True, None

    note = (
        "Endpoint query is not available from the backend yet. Showing sample data for prototyping."
    )
    return _sample_endpoints_for_enclave(destination_account_id, region), False, note


def _load_vulnerabilities_for_enclave(
    destination_account_id: str,
    *,
    region: str,
    resource_id: str | None = None,
    category: str | None = None,
    filters: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], bool, str | None]:
    payload: dict[str, Any] = {
        "query": "list-vulnerabilities",
        "destination_account_id": destination_account_id,
    }
    if region:
        payload["destination_region"] = region
    if resource_id:
        payload["resource_id"] = resource_id
    if category:
        payload["category"] = category
    if filters:
        payload["filters"] = filters

    result = get_backend().run_query(payload)
    if result.get("status") == "success":
        records: list[dict[str, Any]] = []
        for item in result.get("result") or []:
            if isinstance(item, dict):
                records.append(item)
        return records, True, None

    note = (
        "Vulnerability data is not available from the backend yet. The table will be empty "
        "until the list-vulnerabilities query is implemented."
    )
    return [], False, note


def _get_enclave_or_404(enclave_id: str) -> EnclaveOption:
    enclaves, _, _ = _load_enclaves()
    enclave = next((e for e in enclaves if e.destination_account_id == enclave_id), None)
    if enclave is None:
        raise Http404("Enclave not found.")
    return enclave


def _get_endpoint_or_404(
    *,
    enclave_id: str,
    resource_type: str,
    resource_id: str,
    region: str,
) -> EndpointRecord:
    endpoints, _, _ = _load_endpoints_for_enclave(enclave_id, region=region)
    for endpoint in endpoints:
        if endpoint.resource_type == resource_type and endpoint.resource_id == resource_id:
            return endpoint
    raise Http404("Endpoint not found.")


def _extract_optional_value(key: str, raw_value: str) -> Any:
    value = raw_value.strip()
    if value == "":
        return None
    if key == "install_dependencies":
        return _coerce_bool(value)
    if key in {"node_ids", "source_info"}:
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def _build_operation_payload(
    request: HttpRequest,
    *,
    endpoint: EndpointRecord,
    enclave: EnclaveOption,
    operation_id: str,
) -> tuple[dict[str, Any], list[str]]:
    contract = get_endpoint_operation_contract(operation_id)
    if contract is None:
        return {}, ["Unsupported operation."]

    payload: dict[str, Any] = {}
    errors: list[str] = []
    for key in contract.required_payload_keys:
        if key in contract.required_literal_values:
            payload[key] = contract.required_literal_values[key]
            continue
        if key == "destination_account_id":
            payload[key] = enclave.destination_account_id
            continue
        if key == "node_id":
            if endpoint.node_id:
                payload[key] = endpoint.node_id
            elif endpoint.resource_id.startswith("mi-"):
                payload[key] = endpoint.resource_id
            else:
                errors.append("This endpoint is not SSM-registered, so node actions are unavailable.")
            continue
        if key == "destination_region":
            payload[key] = (
                (request.POST.get("destination_region") or "").strip() or endpoint.region or DEFAULT_REGION
            )
            continue

        value = (request.POST.get(key) or "").strip()
        if not value:
            errors.append(f"{key.replace('_', ' ').capitalize()} is required.")
            continue
        payload[key] = value

    for key in contract.optional_payload_keys:
        if key == "install_dependencies":
            if key in request.POST:
                payload[key] = _coerce_bool(request.POST.get(key))
            continue
        raw_value = request.POST.get(key)
        if raw_value is None:
            continue
        parsed = _extract_optional_value(key, raw_value)
        if parsed is not None:
            payload[key] = parsed

    return payload, errors


@login_required
def endpoints_index(request: HttpRequest) -> HttpResponse:
    enclaves, using_backend_data, backend_note = _load_enclaves()
    context = {
        "enclaves": enclaves,
        "using_backend_data": using_backend_data,
        "backend_note": backend_note,
    }
    return render(request, "endpoints/index.html", context)


@login_required
def enclave_detail(request: HttpRequest, enclave_id: str) -> HttpResponse:
    enclave = _get_enclave_or_404(enclave_id)
    region = (request.GET.get("region") or "").strip() or DEFAULT_REGION
    endpoints, using_backend_data, backend_note = _load_endpoints_for_enclave(
        enclave.destination_account_id,
        region=region,
    )
    context = {
        "enclave": enclave,
        "region": region,
        "endpoints": endpoints,
        "using_backend_data": using_backend_data,
        "backend_note": backend_note,
    }
    return render(request, "endpoints/enclave_detail.html", context)


@login_required
def endpoint_detail(
    request: HttpRequest,
    enclave_id: str,
    resource_type: str,
    resource_id: str,
) -> HttpResponse:
    normalized_resource_type = resource_type.strip().lower()
    if normalized_resource_type not in SUPPORTED_RESOURCE_TYPES:
        raise Http404("Unsupported endpoint type.")

    enclave = _get_enclave_or_404(enclave_id)
    region = (request.GET.get("region") or "").strip() or DEFAULT_REGION
    endpoint = _get_endpoint_or_404(
        enclave_id=enclave.destination_account_id,
        resource_type=normalized_resource_type,
        resource_id=resource_id,
        region=region,
    )

    ansible_contract = get_endpoint_operation_contract("apply-ansible-playbook")
    rerun_contract = get_endpoint_operation_contract("apply-playbook-to-node")
    default_playbook = "managed-workspace.yaml" if endpoint.resource_type == "workspace" else "managed-instance.yaml"
    context = {
        "enclave": enclave,
        "endpoint": endpoint,
        "region": region,
        "ansible_contract": ansible_contract,
        "rerun_contract": rerun_contract,
        "default_playbook": default_playbook,
    }
    return render(request, "endpoints/endpoint_detail.html", context)


@login_required
def patch_detail(
    request: HttpRequest,
    enclave_id: str,
    resource_type: str,
    resource_id: str,
) -> HttpResponse:
    normalized_resource_type = resource_type.strip().lower()
    if normalized_resource_type not in SUPPORTED_RESOURCE_TYPES:
        raise Http404("Unsupported endpoint type.")

    enclave = _get_enclave_or_404(enclave_id)
    region = (request.GET.get("region") or "").strip() or DEFAULT_REGION
    endpoint = _get_endpoint_or_404(
        enclave_id=enclave.destination_account_id,
        resource_type=normalized_resource_type,
        resource_id=resource_id,
        region=region,
    )

    context = {
        "enclave": enclave,
        "endpoint": endpoint,
        "region": region,
    }
    return render(request, "endpoints/patch_detail.html", context)


@login_required
def enclave_vulnerabilities(request: HttpRequest, enclave_id: str) -> HttpResponse:
    enclave = _get_enclave_or_404(enclave_id)
    region = (request.GET.get("region") or "").strip() or DEFAULT_REGION
    category = (request.GET.get("category") or "").strip() or None
    resource_id = (request.GET.get("resource_id") or "").strip() or None

    filters_param = request.GET.get("filters")
    parsed_filters: dict[str, Any] | None = None
    if filters_param:
        try:
            maybe_filters = json.loads(filters_param)
        except json.JSONDecodeError:
            maybe_filters = None
        if isinstance(maybe_filters, dict):
            parsed_filters = maybe_filters

    vulnerabilities, using_backend_data, backend_note = _load_vulnerabilities_for_enclave(
        enclave.destination_account_id,
        region=region,
        resource_id=resource_id or None,
        category=category or None,
        filters=parsed_filters,
    )
    return JsonResponse(
        {
            "vulnerabilities": vulnerabilities,
            "using_backend_data": using_backend_data,
            "backend_note": backend_note,
        }
    )


@login_required
def execute_endpoint_operation(
    request: HttpRequest,
    enclave_id: str,
    resource_type: str,
    resource_id: str,
    operation_id: str,
) -> HttpResponse:
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Method not allowed."}, status=405)

    normalized_resource_type = resource_type.strip().lower()
    if normalized_resource_type not in SUPPORTED_RESOURCE_TYPES:
        return JsonResponse({"success": False, "error": "Unsupported endpoint type."}, status=404)
    if get_endpoint_operation_contract(operation_id) is None:
        return JsonResponse({"success": False, "error": "Unknown operation."}, status=404)

    enclave = _get_enclave_or_404(enclave_id)
    region = (request.POST.get("destination_region") or "").strip() or DEFAULT_REGION
    endpoint = _get_endpoint_or_404(
        enclave_id=enclave.destination_account_id,
        resource_type=normalized_resource_type,
        resource_id=resource_id,
        region=region,
    )
    if not endpoint.is_managed:
        return JsonResponse(
            {"success": False, "error": "Endpoint must be SSM-registered for node actions."},
            status=400,
        )

    payload, errors = _build_operation_payload(
        request,
        endpoint=endpoint,
        enclave=enclave,
        operation_id=operation_id,
    )
    if errors:
        return JsonResponse({"success": False, "error": " ".join(errors)}, status=400)

    result = get_backend().invoke_operation(payload)
    if result.get("status") == "error":
        return JsonResponse(
            {
                "success": False,
                "error": result.get("error", "OperationError"),
                "message": result.get("message", "The operation failed."),
            },
            status=400,
        )

    contract = get_endpoint_operation_contract(operation_id)
    message = result.get("message") or f"{contract.label if contract else operation_id} request accepted."
    return JsonResponse(
        {
            "success": True,
            "message": message,
            "status": result.get("status", "success"),
            "config_changed": result.get("config_changed"),
        }
    )
