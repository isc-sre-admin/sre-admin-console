"""Session-backed POAM storage for prototype list/edit flows."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from django.http import HttpRequest

SESSION_POAM_ENTRIES_KEY = "poam_entries"

SAMPLE_POAM_ENTRIES: tuple[dict[str, Any], ...] = (
    {
        "poam_id": "POAM-1001",
        "status": "open",
        "owner": "Endpoint Operations",
        "source": "Inspector",
        "enclave_names": ["sre-research-enclave-01"],
        "vulnerability_ids": ["CVE-2026-1001"],
        "resource_ids": ["i-0a1b2c3d4e5f1111"],
        "observation": "OpenSSL library on analytics node is behind approved baseline.",
        "plan": "Patch package during the next maintenance window and verify version drift is cleared.",
        "due_date": "2026-03-20",
        "create_date": "2026-03-01",
        "comments": "Change ticket CHG-1042 approved.",
    },
    {
        "poam_id": "POAM-1002",
        "status": "closed",
        "owner": "Identity Services",
        "source": "Manual review",
        "enclave_names": ["sre-research-enclave-02"],
        "vulnerability_ids": [],
        "resource_ids": ["ws-012345671111"],
        "observation": "Legacy Duo proxy host lacked current hardening checklist evidence.",
        "plan": "Completed configuration review and attached evidence to control record.",
        "due_date": "2026-02-18",
        "completion_date": "2026-02-12",
        "create_date": "2026-01-30",
        "comments": "Closed after security review sign-off.",
    },
)


def _entry_key(entry: dict[str, Any]) -> tuple[str, str]:
    return str(entry.get("poam_id", "")).strip(), str(entry.get("status", "")).strip()


def list_poam_entries(request: HttpRequest) -> list[dict[str, Any]]:
    """Return sample entries merged with session-created prototype entries."""
    merged: dict[tuple[str, str], dict[str, Any]] = {
        _entry_key(entry): deepcopy(entry) for entry in SAMPLE_POAM_ENTRIES
    }
    for entry in request.session.get(SESSION_POAM_ENTRIES_KEY, []):
        if isinstance(entry, dict):
            merged[_entry_key(entry)] = deepcopy(entry)
    return sorted(
        (entry for entry in merged.values() if entry.get("poam_id")),
        key=lambda entry: (entry.get("status") != "open", entry.get("due_date") or "", entry.get("poam_id") or ""),
    )


def get_poam_entry(request: HttpRequest, poam_id: str) -> dict[str, Any] | None:
    """Return the first matching entry by POAM ID."""
    for entry in list_poam_entries(request):
        if entry.get("poam_id") == poam_id:
            return entry
    return None


def save_poam_entry(request: HttpRequest, entry: dict[str, Any]) -> None:
    """Persist a POAM entry in the current session."""
    existing_entries = [
        deepcopy(item)
        for item in request.session.get(SESSION_POAM_ENTRIES_KEY, [])
        if isinstance(item, dict)
    ]
    target_key = _entry_key(entry)
    updated = False
    for index, existing in enumerate(existing_entries):
        if _entry_key(existing) == target_key:
            existing_entries[index] = deepcopy(entry)
            updated = True
            break
    if not updated:
        existing_entries.insert(0, deepcopy(entry))
    request.session[SESSION_POAM_ENTRIES_KEY] = existing_entries
