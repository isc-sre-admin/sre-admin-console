from __future__ import annotations

from typing import Any

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render

from landing.backend import get_backend
from landing.operation_invocation_contracts import get_operation_contract

SESSION_POAM_ENTRIES_KEY = "poam_entries"
POAM_OPERATION_ID = "create-poam-entry"
STATUS_FILTERS = ("open", "closed", "all")

SAMPLE_POAM_ENTRIES = (
    {
        "poam_id": "POAM-001",
        "status": "open",
        "owner": "secops@example.org",
        "source": "Inspector2",
        "enclave_names": ["sre-research-enclave-01"],
        "due_date": "2026-04-15",
        "observation": "Outdated OpenSSL package on analytics nodes.",
        "plan": "Patch endpoints during next maintenance window.",
    },
    {
        "poam_id": "POAM-002",
        "status": "closed",
        "owner": "platform@example.org",
        "source": "Manual review",
        "enclave_names": ["sre-research-enclave-02"],
        "due_date": "2026-02-20",
        "completion_date": "2026-02-18",
        "observation": "Unencrypted S3 export bucket policy gap.",
        "plan": "Applied baseline bucket policy and verified encryption settings.",
    },
)

LIST_FIELDS = {"enclave_ids", "enclave_names", "vulnerability_ids", "resource_ids"}


def _load_poam_entries(request: HttpRequest) -> list[dict[str, Any]]:
    raw_entries = request.session.get(SESSION_POAM_ENTRIES_KEY)
    if isinstance(raw_entries, list):
        return [dict(entry) for entry in raw_entries if isinstance(entry, dict)]
    return [dict(entry) for entry in SAMPLE_POAM_ENTRIES]


def _save_poam_entries(request: HttpRequest, entries: list[dict[str, Any]]) -> None:
    request.session[SESSION_POAM_ENTRIES_KEY] = entries


def _split_list_values(raw_value: str) -> list[str]:
    normalized = raw_value.replace("\r", "\n")
    values = [item.strip() for chunk in normalized.split("\n") for item in chunk.split(",")]
    return [value for value in values if value]


def _find_poam_entry(
    entries: list[dict[str, Any]],
    *,
    poam_id: str,
    entry_status: str,
) -> dict[str, Any] | None:
    for entry in entries:
        if str(entry.get("poam_id")) == poam_id and str(entry.get("status")) == entry_status:
            return dict(entry)
    return None


def _entry_form_data(entry: dict[str, Any] | None) -> dict[str, str]:
    if entry is None:
        return {}
    form_data: dict[str, str] = {}
    for key, value in entry.items():
        if key in LIST_FIELDS and isinstance(value, list):
            form_data[key] = ", ".join(str(item) for item in value)
        elif value is not None:
            form_data[key] = str(value)
    return form_data


def _upsert_entry(entries: list[dict[str, Any]], payload: dict[str, Any]) -> list[dict[str, Any]]:
    updated_entries = [dict(entry) for entry in entries]
    poam_id = str(payload.get("poam_id", ""))
    entry_status = str(payload.get("status", ""))
    replacement = {
        key: value
        for key, value in payload.items()
        if key not in {"operation", "mode"}
    }
    for idx, existing in enumerate(updated_entries):
        if str(existing.get("poam_id")) == poam_id and str(existing.get("status")) == entry_status:
            updated_entries[idx] = {**existing, **replacement}
            return updated_entries
    updated_entries.insert(0, replacement)
    return updated_entries


def _build_payload(
    request: HttpRequest,
    *,
    mode_choices: tuple[str, ...],
) -> tuple[dict[str, Any], list[str]]:
    payload: dict[str, Any] = {"operation": POAM_OPERATION_ID}
    errors: list[str] = []

    mode = (request.POST.get("mode") or "").strip()
    if not mode:
        errors.append("Mode is required.")
    elif mode_choices and mode not in mode_choices:
        errors.append("Mode must be one of: " + ", ".join(mode_choices))
    else:
        payload["mode"] = mode

    poam_id = (request.POST.get("poam_id") or "").strip()
    if not poam_id:
        errors.append("POAM ID is required.")
    else:
        payload["poam_id"] = poam_id

    status = (request.POST.get("status") or "").strip()
    if status not in {"open", "closed"}:
        errors.append("Status must be open or closed.")
    else:
        payload["status"] = status

    for key in (
        "source",
        "observation",
        "plan",
        "owner",
        "create_date",
        "due_date",
        "completion_date",
        "comments",
    ):
        value = (request.POST.get(key) or "").strip()
        if value:
            payload[key] = value

    sequence_number = (request.POST.get("sequence_number") or "").strip()
    if sequence_number:
        if sequence_number.isdigit():
            payload["sequence_number"] = int(sequence_number)
        else:
            payload["sequence_number"] = sequence_number

    for key in LIST_FIELDS:
        values = _split_list_values(request.POST.get(key, ""))
        if values:
            payload[key] = values

    return payload, errors


@login_required
def list_poam_entries(request: HttpRequest) -> HttpResponse:
    selected_status = (request.GET.get("status") or "open").strip().lower()
    if selected_status not in STATUS_FILTERS:
        selected_status = "open"

    entries = _load_poam_entries(request)
    if selected_status == "all":
        filtered_entries = entries
    else:
        filtered_entries = [entry for entry in entries if str(entry.get("status")).lower() == selected_status]

    context = {
        "selected_status": selected_status,
        "entries": filtered_entries,
    }
    return render(request, "poam/list.html", context)


@login_required
def edit_poam_entry(
    request: HttpRequest,
    poam_id: str | None = None,
    entry_status: str | None = None,
) -> HttpResponse:
    contract = get_operation_contract(POAM_OPERATION_ID)
    if contract is None:
        raise Http404("POAM operation contract not found.")

    mode_choices = contract.mode_choices or ("verify", "modify")
    entries = _load_poam_entries(request)
    existing_entry = None
    if poam_id and entry_status:
        existing_entry = _find_poam_entry(entries, poam_id=poam_id, entry_status=entry_status)

    form_data = _entry_form_data(existing_entry)
    if not form_data:
        form_data = {
            "mode": "modify",
            "status": "open",
        }

    errors: list[str] = []
    backend_result: dict[str, Any] | None = None
    submitted_payload: dict[str, Any] | None = None

    if request.method == "POST":
        form_data = {key: str(value) for key, value in request.POST.items()}
        submitted_payload, errors = _build_payload(request, mode_choices=mode_choices)
        if not errors:
            backend_result = get_backend().invoke_operation(submitted_payload)
            if backend_result.get("status") == "error":
                errors.append(
                    backend_result.get("message")
                    or backend_result.get("error")
                    or "POAM operation failed."
                )
            elif submitted_payload.get("mode") == "modify":
                _save_poam_entries(request, _upsert_entry(entries, submitted_payload))

    context = {
        "contract": contract,
        "mode_choices": mode_choices,
        "status_choices": ("open", "closed"),
        "errors": errors,
        "backend_result": backend_result,
        "submitted_payload": submitted_payload,
        "form_data": form_data,
        "is_edit": existing_entry is not None,
    }
    return render(request, "poam/edit.html", context)
