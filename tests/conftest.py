"""Pytest fixtures for SRE Admin Console tests."""

import pytest
from django.contrib.auth import get_user_model

from landing.backend import reset_backend

User = get_user_model()


@pytest.fixture(autouse=True)
def use_mock_backend(settings):
    """Keep tests deterministic by using the in-process mock backend."""
    settings.USE_MOCK_BACKEND = True
    reset_backend()
    yield
    reset_backend()


@pytest.fixture
def authenticated_client(client):
    """Return a Django test client with a logged-in user for protected views."""
    user = User.objects.create_user(username="testuser", password="testpass")
    client.force_login(user)
    return client
