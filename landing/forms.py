"""Dynamic forms for starting backend pipeline executions."""

from __future__ import annotations

import json
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Sequence

from django import forms

from landing.pipeline_contracts import PipelineContract

AUTOPOPULATED_INPUTS = {"destination_account_id", "enclave_name"}
JSON_LIKE_INPUTS = {"scripts", "security_groups", "security_group_ids", "storage_settings"}

# Region dropdown: value is API region code, label is human-readable (default us-east-1).
REGION_CHOICES = [
    ("us-east-1", "Northern Virginia"),
    ("us-west-2", "Oregon"),
]
DEFAULT_REGION = "us-east-1"

# WorkSpace bundle hardware type: value is API constant (all caps), label is display.
HARDWARE_TYPE_CHOICES = [
    ("STANDARD", "Standard"),
    ("PERFORMANCE", "Performance"),
    ("POWER", "Power"),
    ("POWERPRO", "PowerPro"),
]

DEFAULT_OU_PATH = "OU=Computers,DC=upennsre,DC=local"

DEFAULT_INSTANCE_TYPE = "t3.small"

# Default security groups JSON for provision-ec2-instance (and similar) pipelines.
DEFAULT_SECURITY_GROUPS = """{
  "security_group_name": "enclave_instances_sg",
  "ingress_rules": [
    {
      "protocol": "TCP",
      "from_port": 22,
      "to_port": 22,
      "source_security_group_name": "enclave_workspaces_sg"
    }
  ],
  "egress_rules": [
    {
      "protocol": "TCP",
      "from_port": 443,
      "to_port": 443,
      "cidr_blocks": ["0.0.0.0/0"]
    }
  ]
}"""

# Default capacity (GB) for WorkSpaces storage; mapped to storage_settings JSON on submit.
DEFAULT_ROOT_VOLUME_GB = 80
DEFAULT_USER_VOLUME_GB = 50


class RunningModeRadioSelect(forms.RadioSelect):
    """RadioSelect rendered as a Bootstrap btn-group (one option template per choice)."""

    option_template_name = "landing/widgets/radio_button_option.html"


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
        ami_choices: Sequence[tuple[str, str]] | None = None,
        workspace_choices: Sequence[tuple[str, str]] | None = None,
        hardware_type_choices: Sequence[tuple[str, str]] | None = None,
        directory_choices: Sequence[tuple[str, str]] | None = None,
        encryption_key_alias_choices: Sequence[tuple[str, str]] | None = None,
        username_choices: Sequence[tuple[str, str]] | None = None,
        running_mode_choices: Sequence[tuple[str, str]] | None = None,
        **kwargs: Any,
    ) -> None:
        self.contract = contract
        self._enclaves_by_account_id = {enclave.destination_account_id: enclave for enclave in enclaves}
        self._ami_choices = list(ami_choices) if ami_choices else []
        self._workspace_choices = list(workspace_choices) if workspace_choices else []
        self._hardware_type_choices = list(hardware_type_choices) if hardware_type_choices else []
        self._directory_choices = list(directory_choices) if directory_choices else []
        self._encryption_key_alias_choices = list(encryption_key_alias_choices) if encryption_key_alias_choices else []
        self._username_choices = list(username_choices) if username_choices else []
        self._running_mode_choices = list(running_mode_choices) if running_mode_choices else []
        super().__init__(*args, **kwargs)
        enclave_choices = [
            ("", "Select an enclave"),
            *[(enclave.destination_account_id, enclave.label) for enclave in enclaves],
        ]
        self.fields["enclave"].choices = enclave_choices
        if enclaves:
            self.fields["enclave"].initial = enclaves[0].destination_account_id
        self.fields["enclave"].widget.attrs.update({"class": "form-select", "autocomplete": "off"})
        self._build_dynamic_fields()
        self._order_mode_first()

    def _build_dynamic_fields(self) -> None:
        required_inputs = [name for name in self.contract.required_inputs if name not in AUTOPOPULATED_INPUTS]
        optional_inputs = [name for name in self.contract.optional_inputs if name not in AUTOPOPULATED_INPUTS]

        for input_name in required_inputs:
            if input_name == "storage_settings":
                self._add_storage_volume_fields(required=True)
            else:
                self.fields[input_name] = self._build_field(input_name=input_name, required=True)

        for input_name in optional_inputs:
            if input_name == "storage_settings":
                self._add_storage_volume_fields(required=False)
            else:
                self.fields[input_name] = self._build_field(input_name=input_name, required=False)

    def _add_storage_volume_fields(self, *, required: bool) -> None:
        """Add Root volume and User volume fields; payload built in build_pipeline_payload."""
        if "root_volume" in self.fields:
            return
        self.fields["root_volume"] = forms.IntegerField(
            label="Root volume",
            required=required,
            min_value=1,
            max_value=2048,
            initial=DEFAULT_ROOT_VOLUME_GB,
            help_text="Root volume capacity (GB).",
            widget=forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 2048}),
        )
        self.fields["user_volume"] = forms.IntegerField(
            label="User volume",
            required=required,
            min_value=1,
            max_value=2048,
            initial=DEFAULT_USER_VOLUME_GB,
            help_text="User volume capacity (GB).",
            widget=forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 2048}),
        )

    def _order_mode_first(self) -> None:
        """Place the Mode dropdown first on all start pipeline pages."""
        if "mode" not in self.fields:
            return
        keys = list(self.fields.keys())
        keys.remove("mode")
        keys.insert(0, "mode")
        self.fields = OrderedDict((k, self.fields[k]) for k in keys)

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

        if input_name in ("source_region", "destination_region"):
            return forms.ChoiceField(
                label=label,
                required=required,
                choices=REGION_CHOICES,
                initial=DEFAULT_REGION,
                widget=forms.Select(attrs={"class": "form-select"}),
            )

        if input_name == "ami_id":
            choices = [("", "Select an AMI")] + self._ami_choices
            initial = self._ami_choices[0][0] if self._ami_choices else ""
            return forms.ChoiceField(
                label="AMI id",
                required=required,
                choices=choices,
                initial=initial,
                widget=forms.Select(attrs={"class": "form-select"}),
            )

        if input_name == "source_workspace_id":
            choices = [("", "Select a source workspace")] + self._workspace_choices
            initial = self._workspace_choices[0][0] if self._workspace_choices else ""
            return forms.ChoiceField(
                label="Source workspace id",
                required=required,
                choices=choices,
                initial=initial,
                widget=forms.Select(attrs={"class": "form-select"}),
            )

        if input_name == "hardware_type":
            choices = self._hardware_type_choices if self._hardware_type_choices else HARDWARE_TYPE_CHOICES
            return forms.ChoiceField(
                label="Hardware type",
                required=required,
                choices=[("", "Select hardware type")] + list(choices),
                initial="STANDARD",
                widget=forms.Select(attrs={"class": "form-select"}),
            )

        if input_name == "directory_id":
            choices = [("", "Select a directory")] + self._directory_choices
            initial = self._directory_choices[0][0] if self._directory_choices else ""
            return forms.ChoiceField(
                label="Directory id",
                required=required,
                choices=choices,
                initial=initial,
                widget=forms.Select(attrs={"class": "form-select"}),
            )

        if input_name == "username":
            choices = [("", "Select a user")] + self._username_choices
            initial = self._username_choices[0][0] if self._username_choices else ""
            return forms.ChoiceField(
                label="Username",
                required=required,
                choices=choices,
                initial=initial,
                widget=forms.Select(attrs={"class": "form-select"}),
            )

        if input_name == "running_mode":
            choices = self._running_mode_choices
            initial = self._running_mode_choices[0][0] if self._running_mode_choices else ""
            return forms.ChoiceField(
                label="Running mode",
                required=required,
                choices=choices,
                initial=initial,
                widget=RunningModeRadioSelect(),
            )

        if input_name in ("encrypt_root_volume", "encrypt_user_volume"):
            return forms.BooleanField(
                label=label,
                required=required,
                initial=True,
                widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
            )

        if input_name == "encryption_key_alias":
            choices = [("", "Select encryption key alias")] + self._encryption_key_alias_choices
            initial = (
                self._encryption_key_alias_choices[0][0]
                if self._encryption_key_alias_choices
                else "aws/workspaces"
            )
            return forms.ChoiceField(
                label="Encryption key alias",
                required=required,
                choices=choices,
                initial=initial,
                widget=forms.Select(attrs={"class": "form-select"}),
            )

        if input_name == "ou_path":
            return forms.CharField(
                label="OU path",
                required=required,
                initial=DEFAULT_OU_PATH,
                widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
            )

        if input_name == "instance_type":
            return forms.CharField(
                label=label,
                required=required,
                initial=DEFAULT_INSTANCE_TYPE,
                widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
            )

        if input_name == "security_groups":
            return forms.CharField(
                label=label,
                required=required,
                initial=DEFAULT_SECURITY_GROUPS,
                widget=forms.HiddenInput(attrs={"data-security-groups-json": ""}),
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
            if input_name == "storage_settings":
                if "root_volume" in self.cleaned_data and "user_volume" in self.cleaned_data:
                    payload["storage_settings"] = {
                        "RootStorage": {"Capacity": str(self.cleaned_data["root_volume"])},
                        "UserStorage": {"Capacity": str(self.cleaned_data["user_volume"])},
                    }
                continue
            if input_name == "security_groups":
                value = self.cleaned_data.get("security_groups")
                if value in (None, ""):
                    continue
                if isinstance(value, str):
                    try:
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        continue
                payload["security_groups"] = value
                continue
            value = self.cleaned_data.get(input_name)
            if value in (None, ""):
                continue
            payload[input_name] = value
        return payload
