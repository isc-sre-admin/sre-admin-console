"""Tests for authentication UI (feature 005)."""

import pytest
from django.urls import reverse


def test_login_page_returns_200(client) -> None:
    response = client.get(reverse("login"))
    assert response.status_code == 200


def test_login_page_contains_sign_in_form(client) -> None:
    response = client.get(reverse("login"))
    page = response.content.decode()
    assert "Sign in" in page
    assert 'name="username"' in page
    assert 'name="password"' in page
    assert 'name="next"' in page or "next" in page


def test_anonymous_user_redirected_to_login_for_home(client) -> None:
    response = client.get(reverse("landing:home"))
    assert response.status_code == 302
    assert response["Location"].startswith(reverse("login"))


def test_anonymous_user_redirected_to_login_for_pipeline_start(client) -> None:
    response = client.get(
        reverse(
            "landing:start-pipeline-execution",
            kwargs={"pipeline_id": "provision-ad-connector"},
        )
    )
    assert response.status_code == 302
    assert response["Location"].startswith(reverse("login"))


def test_anonymous_user_redirected_to_login_for_execution_detail(client) -> None:
    response = client.get(
        reverse(
            "landing:pipeline-execution-detail",
            kwargs={"execution_id": "some-id"},
        )
    )
    assert response.status_code == 302
    assert response["Location"].startswith(reverse("login"))


@pytest.mark.django_db
def test_login_success_redirects_to_home(client) -> None:
    from django.contrib.auth import get_user_model

    User = get_user_model()
    User.objects.create_user(username="testuser", password="testpass")
    response = client.post(
        reverse("login"),
        data={"username": "testuser", "password": "testpass", "next": reverse("landing:home")},
    )
    assert response.status_code == 302
    assert response["Location"] == reverse("landing:home")


@pytest.mark.django_db
def test_logout_redirects_to_home(client) -> None:
    from django.contrib.auth import get_user_model

    User = get_user_model()
    User.objects.create_user(username="testuser", password="testpass")
    client.force_login(User.objects.get(username="testuser"))
    response = client.post(reverse("logout"))
    assert response.status_code == 302
    assert response["Location"] == reverse("landing:home")


@pytest.mark.django_db
def test_authenticated_user_sees_sign_out_in_header(authenticated_client) -> None:
    response = authenticated_client.get(reverse("landing:home"))
    assert response.status_code == 200
    page = response.content.decode()
    assert "Sign out" in page
    assert reverse("logout") in page


def test_anonymous_user_sees_sign_in_in_header(client) -> None:
    response = client.get(reverse("login"))
    assert response.status_code == 200
    page = response.content.decode()
    assert "Sign in" in page
    assert reverse("login") in page
