"""POAM forms driven by the create-poam-entry contract."""

from __future__ import annotations

from typing import Any

from django import forms


def _parse_multivalue(value: str) -> list[str]:
    parts: list[str] = []
    for line in value.splitlines():
        for candidate in line.split(","):
            cleaned = candidate.strip()
            if cleaned:
                parts.append(cleaned)
    return parts


class PoamEntryForm(forms.Form):
    """Contract-aligned POAM create/edit form."""

    mode = forms.ChoiceField(
        choices=(("modify", "modify"), ("verify", "verify")),
        initial="modify",
        widget=forms.Select(attrs={"class": "form-select"}),
        help_text="Use modify to create or update an entry, or verify to validate an existing record.",
    )
    poam_id = forms.CharField(
        label="POAM ID",
        widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
    )
    status = forms.ChoiceField(
        choices=(("open", "open"), ("closed", "closed")),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    owner = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
    )
    source = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
    )
    enclave_ids = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2, "spellcheck": "false"}),
        help_text="Enter one enclave account ID per line or comma-separated.",
    )
    enclave_names = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2, "spellcheck": "false"}),
        help_text="Enter one enclave name per line or comma-separated.",
    )
    vulnerability_ids = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2, "spellcheck": "false"}),
        help_text="Enter one vulnerability ID per line or comma-separated.",
    )
    resource_ids = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 2, "spellcheck": "false"}),
        help_text="Enter one resource ID per line or comma-separated.",
    )
    create_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )
    due_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )
    completion_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )
    sequence_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
    )
    observation = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}),
    )
    plan = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}),
    )
    comments = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    )

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        for field_name in ("enclave_ids", "enclave_names", "vulnerability_ids", "resource_ids"):
            raw_value = cleaned_data.get(field_name)
            if isinstance(raw_value, str):
                cleaned_data[field_name] = _parse_multivalue(raw_value)
        return cleaned_data

    def build_payload(self) -> dict[str, Any]:
        """Build the Lambda payload exactly as required by the contract."""
        payload: dict[str, Any] = {
            "operation": "create-poam-entry",
            "mode": self.cleaned_data["mode"],
            "poam_id": self.cleaned_data["poam_id"].strip(),
            "status": self.cleaned_data["status"],
        }
        for key in ("owner", "source", "observation", "plan", "comments", "sequence_number"):
            value = (self.cleaned_data.get(key) or "").strip()
            if value:
                payload[key] = value
        for key in ("enclave_ids", "enclave_names", "vulnerability_ids", "resource_ids"):
            values = self.cleaned_data.get(key) or []
            if values:
                payload[key] = values
        for key in ("create_date", "due_date", "completion_date"):
            value = self.cleaned_data.get(key)
            if value:
                payload[key] = value.isoformat()
        return payload
