"""Shared enclave options used across app screens."""

from __future__ import annotations

from landing.forms import EnclaveOption

SAMPLE_ENCLAVES: tuple[EnclaveOption, ...] = (
    EnclaveOption(
        research_group="Neuroimaging",
        enclave_name="sre-research-enclave-01",
        destination_account_id="111111111111",
    ),
    EnclaveOption(
        research_group="Genomics",
        enclave_name="sre-research-enclave-02",
        destination_account_id="222222222222",
    ),
    EnclaveOption(
        research_group="Clinical Trials",
        enclave_name="sre-research-enclave-03",
        destination_account_id="333333333333",
    ),
    EnclaveOption(
        research_group="Platform Engineering",
        enclave_name="sre-dev-enclave-01",
        destination_account_id="444444444444",
    ),
)


def get_enclave_by_account_id(destination_account_id: str) -> EnclaveOption | None:
    """Resolve enclave metadata by destination account id."""
    for enclave in SAMPLE_ENCLAVES:
        if enclave.destination_account_id == destination_account_id:
            return enclave
    return None
