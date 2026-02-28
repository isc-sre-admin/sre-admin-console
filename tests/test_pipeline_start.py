import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_start_pipeline_page_renders_contract_fields(client) -> None:
    response = client.get(
        reverse(
            "landing:start-pipeline-execution",
            kwargs={"pipeline_name": "provision-ad-connector"},
        )
    )

    assert response.status_code == 200
    page = response.content.decode()
    assert "Start pipeline execution" in page
    assert 'name="enclave"' in page
    assert 'name="mode"' in page
    assert 'name="ou_path"' in page
    assert 'name="destination_account_id"' not in page


@pytest.mark.django_db
def test_start_pipeline_page_renders_different_fields_for_ec2_pipeline(client) -> None:
    response = client.get(
        reverse(
            "landing:start-pipeline-execution",
            kwargs={"pipeline_name": "provision-ec2-instance"},
        )
    )

    assert response.status_code == 200
    page = response.content.decode()
    assert 'name="ami_id"' in page
    assert 'name="copy_name"' in page
    assert 'name="instance_type"' in page
    assert 'name="domain_join_username"' in page


@pytest.mark.django_db
def test_start_pipeline_shows_required_field_errors(client) -> None:
    response = client.post(
        reverse(
            "landing:start-pipeline-execution",
            kwargs={"pipeline_name": "provision-ad-connector"},
        ),
        data={"enclave": "111111111111"},
    )

    assert response.status_code == 200
    page = response.content.decode()
    assert "Please resolve the validation errors and submit again." in page
    assert "This field is required." in page


@pytest.mark.django_db
def test_start_pipeline_success_persists_execution_for_landing_and_detail_views(client) -> None:
    start_response = client.post(
        reverse(
            "landing:start-pipeline-execution",
            kwargs={"pipeline_name": "provision-ad-connector"},
        ),
        data={
            "enclave": "444444444444",
            "mode": "modify",
            "ou_path": "OU=Research,DC=example,DC=org",
        },
    )

    assert start_response.status_code == 200
    start_page = start_response.content.decode()
    assert "Pipeline execution started" in start_page
    assert "arn:aws:states:us-east-1:123456789012:execution:provision-ad-connector:" in start_page

    started_executions = client.session.get("started_pipeline_executions")
    assert started_executions is not None
    assert len(started_executions) == 1
    execution_id = started_executions[0]["execution_id"]

    landing_response = client.get(reverse("landing:home"))
    landing_page = landing_response.content.decode()
    assert landing_response.status_code == 200
    assert execution_id in landing_page
    assert "View details" in landing_page

    detail_response = client.get(
        reverse(
            "landing:pipeline-execution-detail",
            kwargs={"execution_id": execution_id},
        )
    )
    assert detail_response.status_code == 200
    detail_page = detail_response.content.decode()
    assert execution_id in detail_page
    assert "Execution detail" in detail_page


def test_unknown_pipeline_returns_404(client) -> None:
    response = client.get(
        reverse(
            "landing:start-pipeline-execution",
            kwargs={"pipeline_name": "missing-pipeline"},
        )
    )
    assert response.status_code == 404
