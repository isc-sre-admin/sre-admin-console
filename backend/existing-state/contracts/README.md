# Contracts

Human- and machine-readable YAML contracts for pipelines and operations. Each file describes **name**, **function**, **inputs**, and **outputs**; pipeline contracts also list **component_operations** with their inputs and outputs.

## Structure

- **pipelines/** — One YAML per Step Functions pipeline (e.g. `provision-ad-connector.yaml`, `provision-linux-workspace.yaml`).
- **operations/** — One YAML per Lambda operation (e.g. `apply-ansible-playbook.yaml`, `create-ad-connector.yaml`).

## Naming

- Pipeline files: lowercase with hyphens (e.g. `provision-ad-connector.yaml`).
- Operation files: lowercase with hyphens matching the `operation` value (e.g. `apply-ansible-playbook.yaml`).

## Related

- **Documentation:** [docs/README.md](../docs/README.md) — Markdown docs with summaries and pipeline step tables.
- **Operations and pipelines:** See main [README.md](../README.md) and [docs/README.md](../docs/README.md).
