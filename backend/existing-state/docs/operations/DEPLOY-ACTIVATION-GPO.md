# Deploy Activation GPO

## Summary

Creates a GPO on a Windows EC2 instance (with GPMC, domain-joined) that runs the SSM hybrid activation script at startup for WorkSpaces. Uses an existing Secrets Manager secret in the destination account for the domain-admin password. Verify mode runs OU guardrail and can report computer count and GPO status. OU guardrail rejects default Computers OU or domain root unless allow_broad_ou_override is set.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `deploy-activation-gpo` |
| mode | Yes | `verify` or `modify` |
| destination_account_id | Yes | Target account |
| instance_id | Yes (modify) | Windows EC2 with GPMC |
| domain_admin_username | Yes (modify) | Domain admin for GPO |
| domain_admin_password_secret_name | Yes (modify) | Secret in destination account (JSON "secret") |
| gpo_name | No | Default "WorkSpaces SSM activation" |
| startup_script_path | No | Default path to ssm-hybrid-activate.cmd |
| ou_path | No | OU to link GPO |
| destination_region | No | Region |
| allow_broad_ou_override | No | Skip OU guardrail |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| verified | In verify mode |
| computer_count_in_ou | Verify when instance_id and ou_path provided |
| error, message | On error |

## Related

- **Contract:** [deploy-activation-gpo.yaml](../../contracts/operations/deploy-activation-gpo.yaml)
