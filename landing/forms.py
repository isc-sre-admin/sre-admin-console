"""Dynamic forms for starting backend pipeline executions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django import forms

from landing.pipeline_contracts import PipelineContract

AUTOPOPULATED_INPUTS = {"destination_account_id", "enclave_name"}
JSON_LIKE_INPUTS = {"scripts", "security_groups", "security_group_ids", "storage_settings"}


@dataclass(frozen=True, slots=True)
class EnclaveOption:
    """Selectable enclave metadata used by the start form."""

    research_group: str
    enclave_name: str
    destination_account_id: str

    @property
    def label(self) -> str:
        return f"{self.research_group} - {self.enclave_name} ({self.destination_account_id})"


class PipelineStartForm(forms.Form):
    """Dynamically generated form based on a pipeline contract."""

    enclave = forms.ChoiceField(
        label="Research group / enclave",
        choices=(),
        help_text="Select the target enclave; destination account ID is filled automatically.",
    )

    def __init__(
        self,
        *args: Any,
        contract: PipelineContract,
        enclaves: tuple[EnclaveOption, ...],
        **kwargs: Any,
    ) -> None:
        self.contract = contract
        self._enclaves_by_account_id = {enclave.destination_account_id: enclave for enclave in enclaves}
        super().__init__(*args, **kwargs)
        self.fields["enclave"].choices = [
            ("", "Select an enclave"),
            *[(enclave.destination_account_id, enclave.label) for enclave in enclaves],
        ]
        self.fields["enclave"].widget.attrs.update({"class": "form-select", "autocomplete": "off"})
        self._build_dynamic_fields()

    def _build_dynamic_fields(self) -> None:
        required_inputs = [name for name in self.contract.required_inputs if name not in AUTOPOPULATED_INPUTS]
        optional_inputs = [name for name in self.contract.optional_inputs if name not in AUTOPOPULATED_INPUTS]

        for input_name in required_inputs:
            self.fields[input_name] = self._build_field(input_name=input_name, required=True)

        for input_name in optional_inputs:
            self.fields[input_name] = self._build_field(input_name=input_name, required=False)

    def _build_field(self, *, input_name: str, required: bool) -> forms.Field:
        label = input_name.replace("-", " ").replace("_", " ").capitalize()
        if input_name == "mode":
            return forms.ChoiceField(
                label=label,
                required=required,
                choices=[("modify", "modify"), ("verify", "verify")],
                initial="modify",
                help_text="Use modify to create/update resources or verify to validate existing resources.",
                widget=forms.Select(attrs={"class": "form-select"}),
            )

        if input_name in JSON_LIKE_INPUTS:
            return forms.CharField(
                label=label,
                required=required,
                help_text="Enter JSON text when passing lists or objects.",
                widget=forms.Textarea(attrs={"rows": 3, "class": "form-control", "spellcheck": "false"}),
            )

        return forms.CharField(
            label=label,
            required=required,
            widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
        )

    def clean_enclave(self) -> str:
        destination_account_id = self.cleaned_data["enclave"]
        if destination_account_id not in self._enclaves_by_account_id:
            raise forms.ValidationError("Select a valid research group / enclave.")
        return destination_account_id

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        destination_account_id = cleaned_data.get("enclave")
        if not destination_account_id:
            return cleaned_data

        enclave = self._enclaves_by_account_id[destination_account_id]
        cleaned_data["destination_account_id"] = enclave.destination_account_id
        cleaned_data["enclave_name"] = enclave.enclave_name
        return cleaned_data

    def build_pipeline_payload(self) -> dict[str, Any]:
        """Build payload limited to input names defined in the contract."""
        payload: dict[str, Any] = {}
        for input_name in self.contract.all_inputs:
            value = self.cleaned_data.get(input_name)
            if value in (None, ""):
                continue
            payload[input_name] = value
        return payload
