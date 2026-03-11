import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_landing_page_returns_200(authenticated_client) -> None:
    response = authenticated_client.get(reverse("landing:home"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_landing_page_contains_primary_workflow_headings(authenticated_client) -> None:
    response = authenticated_client.get("/")
    page = response.content.decode()
    assert "Set up a new enclave" in page
    assert "Provision enclave resources" in page
    assert "Deploy software changes" in page
    assert "Pipeline activity" in page


@pytest.mark.django_db
def test_authenticated_shell_sidebar_contains_core_navigation(authenticated_client) -> None:
    response = authenticated_client.get(reverse("landing:home"))
    assert response.status_code == 200
    page = response.content.decode()
    assert "Workflows" in page
    assert "Endpoint Management" in page
    assert "Plan of Actions and Milestones" in page
    assert "Operations" in page
    assert reverse("poam:list") in page
    assert reverse("landing:operation-detail", kwargs={"operation_id": "unlock-user"}) in page


@pytest.mark.django_db
def test_run_initial_setup_links_to_provision_ad_connector_start(authenticated_client) -> None:
    """Run Initial Setup should go to Start Pipeline Execution for provision-ad-connector."""
    response = authenticated_client.get(reverse("landing:home"))
    assert response.status_code == 200
    page = response.content.decode()
    start_url = reverse(
        "landing:start-pipeline-execution",
        kwargs={"pipeline_id": "provision-ad-connector"},
    )
    assert start_url in page
    assert "Run Initial Setup" in page
