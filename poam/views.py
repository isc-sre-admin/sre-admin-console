"""Views for POAM list and create/edit workflows."""

from __future__ import annotations

from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from landing.backend import get_backend
from landing.operation_invocation_contracts import get_operation_contract
from poam.forms import PoamEntryForm
from poam.session_store import get_poam_entry, list_poam_entries, save_poam_entry


def _entry_to_initial(entry: dict[str, Any]) -> dict[str, Any]:
    initial = dict(entry)
    for key in ("enclave_ids", "enclave_names", "vulnerability_ids", "resource_ids"):
        values = initial.get(key)
        if isinstance(values, list):
            initial[key] = "\n".join(str(value) for value in values if value)
    initial.setdefault("mode", "modify")
    return initial


@login_required
def poam_list(request: HttpRequest) -> HttpResponse:
    active_filter = (request.GET.get("status") or "open").strip().lower()
    if active_filter not in {"open", "closed", "all"}:
        active_filter = "open"

    all_entries = list_poam_entries(request)
    if active_filter == "all":
        filtered_entries = all_entries
    else:
        filtered_entries = [entry for entry in all_entries if entry.get("status") == active_filter]

    context = {
        "entries": filtered_entries,
        "active_filter": active_filter,
        "open_count": len([entry for entry in all_entries if entry.get("status") == "open"]),
        "closed_count": len([entry for entry in all_entries if entry.get("status") == "closed"]),
    }
    return render(request, "poam/list.html", context)


@login_required
def poam_edit(request: HttpRequest, poam_id: str | None = None) -> HttpResponse:
    contract = get_operation_contract("create-poam-entry")
    if contract is None:
        raise Http404("POAM contract not found.")

    existing_entry = get_poam_entry(request, poam_id) if poam_id else None
    if poam_id and existing_entry is None:
        raise Http404("POAM entry not found.")

    form = PoamEntryForm(
        request.POST or None,
        initial=_entry_to_initial(existing_entry) if existing_entry and request.method != "POST" else None,
    )
    if request.method == "POST" and form.is_valid():
        payload = form.build_payload()
        result = get_backend().invoke_operation(payload)
        if result.get("status") == "error":
            form.add_error(
                None,
                result.get("message") or result.get("error", "The POAM operation failed."),
            )
        else:
            if payload["mode"] == "modify":
                save_poam_entry(request, payload)
            messages.success(
                request,
                result.get("message")
                or (
                    f"POAM entry {payload['poam_id']} verified successfully."
                    if payload["mode"] == "verify"
                    else f"POAM entry {payload['poam_id']} saved successfully."
                ),
            )
            return redirect(reverse("poam:list"))

    context: dict[str, Any] = {
        "contract": contract,
        "form": form,
        "existing_entry": existing_entry,
    }
    return render(request, "poam/edit.html", context)
