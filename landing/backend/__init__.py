"""Backend abstraction for SRE console: mock or real Lambda/Step Functions."""

from __future__ import annotations

from django.conf import settings

from landing.backend.base import Backend
from landing.backend.mock import MockBackend
from landing.backend.real import RealBackend

_backend_instance: Backend | None = None


def get_backend() -> Backend:
    """Return the configured backend (mock or real). Toggle via USE_MOCK_BACKEND setting."""
    global _backend_instance
    if _backend_instance is None:
        if getattr(settings, "USE_MOCK_BACKEND", True):
            _backend_instance = MockBackend()
        else:
            _backend_instance = RealBackend()
    return _backend_instance


def reset_backend() -> None:
    """Clear the cached backend instance (for tests)."""
    global _backend_instance
    _backend_instance = None
