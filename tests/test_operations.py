"""Tests for quick operations (e.g. unlock user) and execute-operation view."""

import json

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_anonymous_user_redirected_to_login_on_execute_operation(client) -> None:
    response = client.post(
        reverse("landing:execute-operation", kwargs={"operation_id": "unlock-user"}),
        data={"username": "jdoe", "operation": "unlock-user"},
    )
    assert response.status_code == 302
    assert response["Location"].startswith(reverse("login"))


@pytest.mark.django_db
def test_execute_operation_get_returns_405(authenticated_client) -> None:
    response = authenticated_client.get(
        reverse("landing:execute-operation", kwargs={"operation_id": "unlock-user"})
    )
    assert response.status_code == 405
    data = json.loads(response.content)
    assert data.get("success") is False
    assert "error" in data


@pytest.mark.django_db
def test_execute_operation_unknown_returns_404(authenticated_client) -> None:
    response = authenticated_client.post(
        reverse("landing:execute-operation", kwargs={"operation_id": "unknown-op"}),
        data={"operation": "unknown-op"},
    )
    assert response.status_code == 404
    data = json.loads(response.content)
    assert data.get("success") is False
    assert "error" in data


@pytest.mark.django_db
def test_execute_unlock_user_success(authenticated_client) -> None:
    response = authenticated_client.post(
        reverse("landing:execute-operation", kwargs={"operation_id": "unlock-user"}),
        data={"username": "jdoe", "operation": "unlock-user"},
    )
    assert response.status_code == 200
    assert response["Content-Type"] == "application/json"
    data = json.loads(response.content)
    assert data.get("success") is True
    assert "message" in data


@pytest.mark.django_db
def test_execute_unlock_user_missing_username_returns_400(authenticated_client) -> None:
    response = authenticated_client.post(
        reverse("landing:execute-operation", kwargs={"operation_id": "unlock-user"}),
        data={"username": "  ", "operation": "unlock-user"},
    )
    assert response.status_code == 400
    data = json.loads(response.content)
    assert data.get("success") is False
    assert "error" in data


@pytest.mark.django_db
def test_authenticated_home_shows_operations_dropdown(authenticated_client) -> None:
    """Quick operations (e.g. Unlock user) appear in the nav for authenticated users."""
    response = authenticated_client.get(reverse("landing:home"))
    assert response.status_code == 200
    page = response.content.decode()
    assert "Operations" in page
    assert "Unlock User" in page
    assert "operation-modal-unlock-user" in page
