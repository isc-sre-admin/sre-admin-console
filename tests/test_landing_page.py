from django.urls import reverse


def test_landing_page_returns_200(client) -> None:
    response = client.get(reverse("landing:home"))
    assert response.status_code == 200


def test_landing_page_contains_primary_workflow_headings(client) -> None:
    response = client.get("/")
    page = response.content.decode()
    assert "Set up a new enclave" in page
    assert "Provision enclave resources" in page
    assert "Deploy software changes" in page
    assert "Pipeline activity" in page


def test_run_initial_setup_links_to_provision_ad_connector_start(client) -> None:
    """Run Initial Setup should go to Start Pipeline Execution for provision-ad-connector."""
    response = client.get(reverse("landing:home"))
    assert response.status_code == 200
    page = response.content.decode()
    start_url = reverse(
        "landing:start-pipeline-execution",
        kwargs={"pipeline_id": "provision-ad-connector"},
    )
    assert start_url in page
    assert "Run Initial Setup" in page
