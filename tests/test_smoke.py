import pytest
from django.test import Client


@pytest.mark.django_db
def test_admin_login_page_returns_200() -> None:
    client = Client()
    response = client.get("/admin/login/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_admin_requires_auth() -> None:
    client = Client()
    response = client.get("/admin/")
    assert response.status_code == 302
