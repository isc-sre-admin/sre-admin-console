"""Tests for feature 008 endpoints app."""

import json

import pytest
from django.test import override_settings
from django.urls import reverse

from landing.backend import reset_backend


@pytest.mark.django_db
def test_anonymous_user_redirected_to_login_for_endpoints_index(client) -> None:
    response = client.get(reverse("endpoints:index"))
    assert response.status_code == 302
    assert response["Location"].startswith(reverse("login"))


@pytest.mark.django_db
def test_endpoints_index_renders_enclave_rows(authenticated_client) -> None:
    response = authenticated_client.get(reverse("endpoints:index"))
    assert response.status_code == 200
    page = response.content.decode()
    assert "Endpoints by enclave" in page
    assert "sre-research-enclave-01" in page
    assert reverse("endpoints:enclave-detail", kwargs={"enclave_id": "111111111111"}) in page


@pytest.mark.django_db
def test_enclave_detail_renders_endpoint_table(authenticated_client) -> None:
    response = authenticated_client.get(
        reverse("endpoints:enclave-detail", kwargs={"enclave_id": "111111111111"})
    )
    assert response.status_code == 200
    page = response.content.decode()
    assert "analytics-node-1111" in page
    assert "research-workspace-1111" in page
    assert "Vulnerability Management" in page
    assert 'data-pane-storage-key="sreConsole.vulnPaneOpen.enclave"' in page


@pytest.mark.django_db
def test_endpoint_detail_managed_shows_session_manager_and_actions(authenticated_client) -> None:
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
    assert "Connect via Session Manager" in page
    assert "aws ssm start-session --target" in page
    assert "apply-ansible-playbook" in page
    assert "apply-playbook-to-node" in page
    assert "?enclave=111111111111" in page
    assert "Vulnerability Management" in page
    assert 'data-pane-storage-key="sreConsole.vulnPaneOpen.endpoint"' in page


@pytest.mark.django_db
def test_endpoint_detail_unmanaged_disables_node_actions(authenticated_client) -> None:
    response = authenticated_client.get(
        reverse(
            "endpoints:endpoint-detail",
            kwargs={
                "enclave_id": "111111111111",
                "resource_type": "ec2",
                "resource_id": "i-09f8e7d6c5b41111",
            },
        )
    )
    assert response.status_code == 200
    page = response.content.decode()
    assert "Register this endpoint with SSM to enable Session Manager and node operations." in page
    assert 'disabled aria-disabled="true"' in page


@pytest.mark.django_db
def test_execute_endpoint_operation_get_returns_405(authenticated_client) -> None:
    response = authenticated_client.get(
        reverse(
            "endpoints:execute-operation",
            kwargs={
                "enclave_id": "111111111111",
                "resource_type": "ec2",
                "resource_id": "i-0a1b2c3d4e5f1111",
                "operation_id": "apply-playbook-to-node",
            },
        )
    )
    assert response.status_code == 405
    data = json.loads(response.content)
    assert data.get("success") is False


@pytest.mark.django_db
@override_settings(USE_MOCK_BACKEND=True)
def test_execute_endpoint_operation_success_with_mock_backend(authenticated_client) -> None:
    reset_backend()
    response = authenticated_client.post(
        reverse(
            "endpoints:execute-operation",
            kwargs={
                "enclave_id": "111111111111",
                "resource_type": "ec2",
                "resource_id": "i-0a1b2c3d4e5f1111",
                "operation_id": "apply-playbook-to-node",
            },
        ),
        data={
            "mode": "modify",
            "destination_region": "us-east-1",
            "playbook": "managed-instance.yaml",
            "install_dependencies": "on",
        },
    )
    assert response.status_code == 200
    data = json.loads(response.content)
    assert data.get("success") is True
    reset_backend()


@pytest.mark.django_db
def test_start_pipeline_prefills_enclave_from_query(authenticated_client) -> None:
    response = authenticated_client.get(
        reverse("landing:start-pipeline-execution", kwargs={"pipeline_id": "provision-ad-connector"})
        + "?enclave=222222222222"
    )
    assert response.status_code == 200
    page = response.content.decode()
    assert 'value="222222222222" selected' in page or 'value="222222222222" selected="selected"' in page
