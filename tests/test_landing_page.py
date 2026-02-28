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
