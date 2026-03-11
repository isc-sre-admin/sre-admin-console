"""Shared shell navigation metadata."""

from __future__ import annotations

from dataclasses import dataclass

from landing.operation_invocation_contracts import get_operation_contract, list_operation_contracts
from landing.pipeline_contracts import get_pipeline_contract

WORKFLOW_ORDER = (
    "provision-ad-connector",
    "provision-linux-workspace",
    "provision-windows-workspace",
    "provision-ec2-instance",
)

COMMON_OPERATION_IDS = ("unlock-user",)

OPERATION_CATEGORY_MAP = (
    (
        "user-management",
        "User Management",
        (
            "create-ad-users",
            "create-ad-group",
        ),
    ),
    (
        "enclave-setup",
        "Enclave Setup",
        (
            "create-ad-connector",
            "check-ad-connector-state",
            "assign-domain-name",
            "register-workspace-directory",
            "enable-ad-connector-mfa",
            "create-radius-shared-secret",
            "deploy-activation-gpo",
            "remove-activation-gpo",
            "create-security-group",
            "create-ssm-hybrid-activation",
            "create-data-exports",
            "configure-workspace-branding",
            "configure-windows-workspace",
            "domain-join-ec2-instance",
        ),
    ),
    (
        "image-and-ami",
        "Image and AMI",
        (
            "copy-ami",
            "share-ami",
            "check-ami-state",
            "copy-image",
            "share-image",
            "create-workspace-image",
            "check-image-state",
            "create-bundle",
            "check-bundle-state",
        ),
    ),
    (
        "maintenance-utilities",
        "Maintenance / Utilities",
        (
            "apply-ansible-playbook",
            "apply-playbook-to-node",
            "ensure-ansible-on-node",
            "tag-managed-instance",
            "check-ssm-registration",
            "launch-workspace",
            "launch-ec2-instance",
            "check-workspace-state",
            "list-duo-auth-proxy-nodes",
            "get-remaining-node-indices",
            "create-poam-entry",
        ),
    ),
)


@dataclass(frozen=True, slots=True)
class NavItem:
    """Sidebar navigation item."""

    id: str
    label: str


@dataclass(frozen=True, slots=True)
class NavCategory:
    """Collapsible sidebar category."""

    id: str
    label: str
    items: tuple[NavItem, ...]


def get_workflow_nav_items() -> tuple[NavItem, ...]:
    """Return major workflow links in feature order."""
    items: list[NavItem] = []
    for pipeline_id in WORKFLOW_ORDER:
        contract = get_pipeline_contract(pipeline_id)
        if contract:
            items.append(NavItem(id=contract.id, label=contract.label))
    return tuple(items)


def get_common_operation_items() -> tuple[NavItem, ...]:
    """Return high-visibility common operation links."""
    items: list[NavItem] = []
    for operation_id in COMMON_OPERATION_IDS:
        contract = get_operation_contract(operation_id)
        if contract:
            items.append(NavItem(id=contract.id, label=contract.label))
    return tuple(items)


def get_operation_nav_categories() -> tuple[NavCategory, ...]:
    """Return grouped operation navigation items."""
    contracts_by_id = {contract.id: contract for contract in list_operation_contracts()}
    categories: list[NavCategory] = []
    for category_id, label, operation_ids in OPERATION_CATEGORY_MAP:
        items: list[NavItem] = []
        for operation_id in operation_ids:
            if operation_id in COMMON_OPERATION_IDS:
                continue
            contract = contracts_by_id.get(operation_id)
            if contract is None:
                continue
            items.append(NavItem(id=operation_id, label=contract.label))
        if items:
            categories.append(NavCategory(id=category_id, label=label, items=tuple(items)))
    return tuple(categories)
