"""Dynamic forms for contract-driven operations."""

from __future__ import annotations

import json
from collections import OrderedDict
from typing import Any

from django import forms

from landing.forms import REGION_CHOICES
from landing.operation_invocation_contracts import OperationFieldSpec, OperationInvocationContract

LONG_TEXT_FIELDS = {"observation", "plan", "comments", "description"}
LABEL_TOKEN_MAP = {
    "ad": "AD",
    "ami": "AMI",
    "dns": "DNS",
    "ec2": "EC2",
    "gpo": "GPO",
    "id": "ID",
    "ids": "IDs",
    "poam": "POAM",
    "s3": "S3",
    "ssm": "SSM",
    "vpc": "VPC",
}


def _build_label(name: str) -> str:
    tokens = name.replace("-", "_").split("_")
    display_tokens = [LABEL_TOKEN_MAP.get(token.lower(), token.capitalize()) for token in tokens if token]
    return " ".join(display_tokens)


class OperationExecutionForm(forms.Form):
    """Render a generic operation form from the invocation contract."""

    def __init__(
        self,
        *args: Any,
        contract: OperationInvocationContract,
        initial_payload: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        self.contract = contract
        self.field_specs = {field.name: field for field in contract.all_fields}
        initial = dict(kwargs.pop("initial", {}))
        if initial_payload:
            initial.update(initial_payload)
        super().__init__(*args, initial=initial, **kwargs)
        self._build_fields()
        self._order_mode_first()

    def _build_fields(self) -> None:
        for field_spec in self.contract.all_fields:
            self.fields[field_spec.name] = self._build_field(field_spec)

    def _order_mode_first(self) -> None:
        if "mode" not in self.fields:
            return
        keys = list(self.fields.keys())
        keys.remove("mode")
        keys.insert(0, "mode")
        self.fields = OrderedDict((key, self.fields[key]) for key in keys)

    def _build_field(self, field_spec: OperationFieldSpec) -> forms.Field:
        name = field_spec.name
        label = _build_label(name)
        if field_spec.is_literal:
            return forms.CharField(
                required=field_spec.required,
                initial=str(field_spec.literal_value),
                widget=forms.HiddenInput(),
            )

        if field_spec.field_type == "choice":
            initial = field_spec.choices[1] if name == "mode" and len(field_spec.choices) > 1 else (
                field_spec.choices[0] if field_spec.choices else ""
            )
            return forms.ChoiceField(
                label=label,
                required=field_spec.required,
                choices=[(choice, choice) for choice in field_spec.choices],
                initial=initial,
                widget=forms.Select(attrs={"class": "form-select"}),
            )

        if name in {"source_region", "destination_region"}:
            return forms.ChoiceField(
                label=label,
                required=field_spec.required,
                choices=REGION_CHOICES,
                initial=REGION_CHOICES[0][0],
                widget=forms.Select(attrs={"class": "form-select"}),
            )

        if field_spec.field_type == "boolean":
            return forms.BooleanField(
                label=label,
                required=False,
                widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
            )

        if field_spec.field_type == "integer":
            return forms.IntegerField(
                label=label,
                required=field_spec.required,
                widget=forms.NumberInput(attrs={"class": "form-control"}),
            )

        if field_spec.field_type == "number":
            return forms.DecimalField(
                label=label,
                required=field_spec.required,
                widget=forms.NumberInput(attrs={"class": "form-control", "step": "any"}),
            )

        if name.endswith("_date"):
            return forms.DateField(
                label=label,
                required=field_spec.required,
                widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            )

        if field_spec.field_type in {"array", "object"} or name in LONG_TEXT_FIELDS:
            help_text = None
            if field_spec.field_type == "array":
                help_text = "Enter one value per line or comma-separated."
            elif field_spec.field_type == "object":
                help_text = "Enter valid JSON for this object payload."
            return forms.CharField(
                label=label,
                required=field_spec.required,
                help_text=help_text,
                widget=forms.Textarea(
                    attrs={
                        "class": "form-control",
                        "rows": 3 if field_spec.field_type == "array" else 4,
                        "spellcheck": "false",
                    }
                ),
            )

        return forms.CharField(
            label=label,
            required=field_spec.required,
            widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
        )

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        for field_spec in self.contract.all_fields:
            if field_spec.is_literal:
                continue
            value = cleaned_data.get(field_spec.name)
            if value in (None, ""):
                continue
            if field_spec.field_type == "array":
                if isinstance(value, str):
                    items = []
                    for line in value.splitlines():
                        for candidate in line.split(","):
                            cleaned = candidate.strip()
                            if cleaned:
                                items.append(cleaned)
                    cleaned_data[field_spec.name] = items
            elif field_spec.field_type == "object" and isinstance(value, str):
                try:
                    cleaned_data[field_spec.name] = json.loads(value)
                except json.JSONDecodeError as exc:
                    self.add_error(field_spec.name, f"Enter valid JSON. {exc.msg}.")
            elif field_spec.name.endswith("_date") and value:
                cleaned_data[field_spec.name] = value.isoformat()
        return cleaned_data

    def build_payload(self) -> dict[str, Any]:
        """Build a payload using only contract-defined fields."""
        payload: dict[str, Any] = {}
        for field_spec in self.contract.all_fields:
            if field_spec.is_literal:
                payload[field_spec.name] = field_spec.literal_value
                continue
            value = self.cleaned_data.get(field_spec.name)
            if isinstance(value, bool):
                if field_spec.required or value:
                    payload[field_spec.name] = value
                continue
            if value in (None, "", []):
                continue
            payload[field_spec.name] = value
        return payload
