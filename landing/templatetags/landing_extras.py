"""Template helpers for dynamic dictionary access in landing templates."""

from __future__ import annotations

from django import template

register = template.Library()


@register.filter
def get_item(mapping: object, key: str) -> object:
    """Return mapping[key] if mapping is dict-like, otherwise empty string."""
    if isinstance(mapping, dict):
        return mapping.get(key, "")
    getter = getattr(mapping, "get", None)
    if callable(getter):
        return getter(key, "")
    return ""
