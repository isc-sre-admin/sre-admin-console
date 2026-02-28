# Project Structure

A short, scannable overview of the repository layout.

## Top-level

| Path | Purpose |
|------|--------|
| `template.yaml` | SAM template: Lambda (`SreManagementFunction`) and Step Functions state machines (provision-linux-workspace, provision-windows-workspace, provision-ad-connector, provision-ec2-instance). |
| `statemachine/` | Amazon States Language (ASL) definitions for each pipeline. |
| `src/` | Application and config (see below). |
| `events/` | Sample event payloads for operations and pipelines. |
| `docs/` | Detailed documentation. [README](README.md) indexes pipelines and operations. |
| `contracts/` | YAML contracts (name, function, inputs, outputs) for pipelines and operations. |
| `scripts/` | Helper scripts (invoke Lambda, start pipelines, etc.). `scripts/workspaces/` has PowerShell and config for SSM hybrid activation on Windows; see `scripts/workspaces/README.md`. |
| `cloudformation/` | Standalone CloudFormation and deploy script for **SystemManagementRoleStack** in destination accounts. |
| `cdk/` | CDK app for CI/CD CodePipelines (dev/prod). |

## src/

| Path | Purpose |
|------|--------|
| `Dockerfile` | Builds the Lambda container image (Python 3.14). |
| `app/` | Application code: `handler.py` (dispatches by `operation`), `config.py`, `utility.py`, and `operations/` with subfolders: |
| `app/operations/directory/` | AD connector, AD group, AD users, RADIUS secret, MFA, register-workspace-directory. |
| `app/operations/workspaces/` | WorkSpaces image share/copy, bundle, launch, check states, create-workspace-image, branding. |
| `app/operations/ssm/` | Ansible playbook, configure-windows-workspace, SSM registration, tag-managed-instance, hybrid activation. |
| `app/operations/ec2/` | share-ami, copy-ami, check-ami-state, launch-ec2-instance, domain-join, assign-domain-name. |
| `app/operations/cost/` | create-data-exports. |
| `app/assets/playbooks/` | Ansible playbooks (e.g. `managed-workspace.yaml`, `managed-instance.yaml`, `duoauthproxy.yaml`, `duo-unix.yaml`) and assets; bundled into the Lambda image. |
| `app/assets/powershell/` | PowerShell scripts for Windows WorkSpaces (e.g. RStudio); bundled into the Lambda image. |
| `config/config.yaml` | Main configuration: `source_account_id`, region defaults, operation defaults, operation-specific defaults. |

## Playbooks (high level)

- **managed-workspace.yaml** / **managed-instance.yaml**: CloudWatch agent, ClamAV, CrowdStrike Falcon, ACLs for logs; managed-instance also deploys Kerberos crypto-policies for domain join.
- **duoauthproxy.yaml**: Configures Duo Auth Proxy on nodes; used by provision-ad-connector pipeline.
- **duo-unix.yaml**: Installs Duo Unix (pam_duo) for SSH MFA on EC2; uses a Duo **Unix** application secret, distinct from RADIUS Duo Auth Proxy.

See `src/assets/playbooks/` and per-operation docs under [docs/operations/](operations/) for details.
