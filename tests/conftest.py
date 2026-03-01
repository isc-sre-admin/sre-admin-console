"""Pytest fixtures for SRE Admin Console tests."""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def authenticated_client(client):
    """Return a Django test client with a logged-in user for protected views."""
    user = User.objects.create_user(username="testuser", password="testpass")
    client.force_login(user)
    return client
