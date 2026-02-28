# Apply Ansible Playbook

## Summary

Deploys an Ansible playbook to an EC2 instance (SSM managed node) in a destination account via AWS Systems Manager **AWS-ApplyAnsiblePlaybooks**. Supports verify mode (check/dry run) and modify mode. Playbook and optional secrets (e.g. Duo config) can come from config bucket, S3 URL, or source_type/source_info. Optional `username` is passed as CloudWatch log stream name for managed-workspace playbook.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `apply-ansible-playbook` |
| mode | Yes | `verify` or `modify` |
| destination_account_id | Yes | Target AWS account |
| node_id | Yes* | EC2 instance ID (or use node_ids + node_index) |
| playbook | Yes | Playbook filename (e.g. `duoauthproxy.yaml`, `managed-workspace.yaml`) |
| secret_name | No | Secrets Manager secret (source account) passed as `secret_json_b64` |
| destination_region | No | Target region |
| username | No | CloudWatch log stream name for managed-workspace |
| playbook_s3_url / source_type/source_info | No | Override playbook source |
| install_dependencies | No | Default true |
| output_s3_bucket_name, output_s3_key_prefix | No | Capture output to S3 |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| config_changed | When playbook emits PLAYBOOK_CONFIG_CHANGED (e.g. duoauthproxy) |
| error, message | On error |

## Related

- **Contract:** [apply-ansible-playbook.yaml](../../contracts/operations/apply-ansible-playbook.yaml)
