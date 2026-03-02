"""Template context processors for the landing app."""

from __future__ import annotations

from landing.operation_contracts import list_quick_operations


def quick_operations(request: object) -> dict[str, object]:
    """Add quick_operations to template context for the Operations nav dropdown."""
    return {"quick_operations": list_quick_operations()}
