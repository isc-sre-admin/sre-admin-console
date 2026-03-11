"""Template context processors for shared shell navigation."""

from __future__ import annotations

from django.http import HttpRequest

from landing.navigation import (
    get_common_operation_items,
    get_operation_nav_categories,
    get_workflow_nav_items,
)
from landing.operation_contracts import list_quick_operations


def quick_operations(request: object) -> dict[str, object]:
    """Add quick_operations to template context for the Operations nav dropdown."""
    return {"quick_operations": list_quick_operations()}


def shell_navigation(request: HttpRequest) -> dict[str, object]:
    """Add sidebar navigation metadata to template context."""
    resolver_match = getattr(request, "resolver_match", None)
    return {
        "workflow_nav_items": get_workflow_nav_items(),
        "common_operation_items": get_common_operation_items(),
        "operation_nav_categories": get_operation_nav_categories(),
        "current_app_name": getattr(resolver_match, "app_name", ""),
        "current_url_name": getattr(resolver_match, "url_name", ""),
    }
