"""Tests for feature 010 contextual shell, POAM pages, and vulnerability pane wiring."""

from __future__ import annotations

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_sidebar_navigation_contains_workflows_endpoints_poam(authenticated_client) -> None:
    response = authenticated_client.get(reverse("landing:home"))
    assert response.status_code == 200
    page = response.content.decode()
    assert "Workflows" in page
    assert "Endpoint Management" in page
    assert "Plan of Actions and Milestones" in page
    assert reverse("poam:list") in page


@pytest.mark.django_db
def test_poam_list_defaults_to_open_entries(authenticated_client) -> None:
    response = authenticated_client.get(reverse("poam:list"))
    assert response.status_code == 200
    page = response.content.decode()
    assert "Plan of Actions and Milestones" in page
    assert "POAM-001" in page
    assert "POAM-002" not in page


@pytest.mark.django_db
def test_poam_create_submits_contract_required_fields(authenticated_client) -> None:
    response = authenticated_client.post(
        reverse("poam:create"),
        data={
            "mode": "modify",
            "poam_id": "POAM-NEW-100",
            "status": "open",
            "owner": "owner@example.org",
            "source": "Inspector2",
        },
    )
    assert response.status_code == 200
    page = response.content.decode()
    assert "POAM request accepted" in page or "completed (mock)" in page

    list_response = authenticated_client.get(reverse("poam:list") + "?status=open")
    assert list_response.status_code == 200
    assert "POAM-NEW-100" in list_response.content.decode()


@pytest.mark.django_db
def test_enclave_detail_has_contextual_vulnerability_toggle(authenticated_client) -> None:
    response = authenticated_client.get(
        reverse("endpoints:enclave-detail", kwargs={"enclave_id": "111111111111"})
    )
    assert response.status_code == 200
    page = response.content.decode()
    assert 'data-storage-key="sreConsole.vulnPaneOpen.enclave"' in page
    assert "Toggle Vulnerability Management pane" in page


@pytest.mark.django_db
def test_endpoint_detail_has_contextual_vulnerability_toggle(authenticated_client) -> None:
    response = authenticated_client.get(
        reverse(
            "endpoints:endpoint-detail",
            kwargs={
                "enclave_id": "111111111111",
                "resource_type": "ec2",
                "resource_id": "i-0a1b2c3d4e5f1111",
            },
        )
    )
    assert response.status_code == 200
    page = response.content.decode()
    assert 'data-storage-key="sreConsole.vulnPaneOpen.endpoint"' in page
    assert 'data-fixed-resource-id="i-0a1b2c3d4e5f1111"' in page
