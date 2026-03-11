import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_poam_list_defaults_to_open_entries(authenticated_client) -> None:
    response = authenticated_client.get(reverse("poam:list"))
    assert response.status_code == 200
    page = response.content.decode()
    assert "Plan of Actions and Milestones" in page
    assert "POAM-1001" in page
    assert "POAM-1002" not in page


@pytest.mark.django_db
def test_poam_list_can_filter_closed_entries(authenticated_client) -> None:
    response = authenticated_client.get(reverse("poam:list") + "?status=closed")
    assert response.status_code == 200
    page = response.content.decode()
    assert "POAM-1002" in page
    assert "POAM-1001" not in page


@pytest.mark.django_db
def test_create_poam_entry_persists_to_session_list(authenticated_client) -> None:
    response = authenticated_client.post(
        reverse("poam:new"),
        data={
            "mode": "modify",
            "poam_id": "POAM-2001",
            "status": "open",
            "owner": "Security Operations",
            "source": "Inspector",
            "enclave_names": "sre-research-enclave-01",
            "vulnerability_ids": "CVE-2026-2001",
            "resource_ids": "i-0a1b2c3d4e5f1111",
            "due_date": "2026-03-31",
            "observation": "Testing POAM creation.",
            "plan": "Create entry through the console.",
            "comments": "Created in test flow.",
        },
        follow=True,
    )
    assert response.status_code == 200
    page = response.content.decode()
    assert "POAM entry POAM-2001 saved." in page
    assert "POAM-2001" in page
