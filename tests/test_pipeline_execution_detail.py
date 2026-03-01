"""Tests for pipeline execution detail view (feature 003)."""

import json

import pytest
from django.urls import reverse

from landing.views import SAMPLE_ACTIVE_EXECUTION_IDS, SAMPLE_RECENT_EXECUTION_IDS


@pytest.mark.django_db
def test_execution_detail_unknown_id_returns_404(authenticated_client) -> None:
    response = authenticated_client.get(
        reverse(
            "landing:pipeline-execution-detail",
            kwargs={"execution_id": "unknown-execution-id"},
        )
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_execution_detail_from_session_shows_steps(authenticated_client) -> None:
    authenticated_client.post(
        reverse(
            "landing:start-pipeline-execution",
            kwargs={"pipeline_id": "provision-ad-connector"},
        ),
        data={
            "enclave": "444444444444",
            "mode": "modify",
            "ou_path": "OU=Research,DC=example,DC=org",
        },
    )
    started = authenticated_client.session.get("started_pipeline_executions")
    assert started and len(started) == 1
    execution_id = started[0]["execution_id"]

    response = authenticated_client.get(
        reverse(
            "landing:pipeline-execution-detail",
            kwargs={"execution_id": execution_id},
        )
    )
    assert response.status_code == 200
    page = response.content.decode()
    assert "Execution detail" in page
    assert "Pipeline steps" in page
    assert "Create Ad Connector" in page
    assert execution_id in page


@pytest.mark.django_db
def test_execution_detail_sample_failed_shows_failure_cause(authenticated_client) -> None:
    failed_id = SAMPLE_RECENT_EXECUTION_IDS[1]
    response = authenticated_client.get(
        reverse(
            "landing:pipeline-execution-detail",
            kwargs={"execution_id": failed_id},
        )
    )
    assert response.status_code == 200
    page = response.content.decode()
    assert "Failed" in page
    assert "Root cause" in page
    assert "SSM Run Command failed" in page or "SSM" in page


@pytest.mark.django_db
def test_execution_detail_json_format_returns_application_json(authenticated_client) -> None:
    execution_id = SAMPLE_ACTIVE_EXECUTION_IDS[0]
    response = authenticated_client.get(
        reverse(
            "landing:pipeline-execution-detail",
            kwargs={"execution_id": execution_id},
        ),
        data={"format": "json"},
    )
    assert response.status_code == 200
    assert response.get("Content-Type", "").startswith("application/json")
    data = json.loads(response.content.decode())
    assert data["execution_id"] == execution_id
    assert data["status"] == "Running"
    assert "steps" in data
    assert "current_step_index" in data


@pytest.mark.django_db
def test_landing_page_pipeline_labels_link_to_execution_detail(authenticated_client) -> None:
    response = authenticated_client.get(reverse("landing:home"))
    assert response.status_code == 200
    page = response.content.decode()
    assert "pipeline-execution-detail" in page or "executions/" in page
    assert SAMPLE_RECENT_EXECUTION_IDS[1] in page or "View details" in page
