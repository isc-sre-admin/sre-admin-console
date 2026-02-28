# Create SSM Hybrid Activation

## Summary

Creates or verifies a Systems Manager hybrid activation in a destination account for on-prem or other managed instances. When `iam_role` is "default", uses **AmazonEC2RunCommandRoleForManagedInstances**. Idempotent: reuses active activation with matching DefaultInstanceName and capacity. Optional ssm_default_instance_name to look up existing activation from Secrets Manager (e.g. rerun path). New activations are stored in Secrets Manager at `/upenn/ssm/activation/{instance_name}` in the destination account.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `create-ssm-hybrid-activation` |
| mode | Yes | `verify` or `modify` |
| destination_account_id | Yes | Target account |
| instance_limit | Yes | Registration limit |
| iam_role | Yes | e.g. "default" |
| activation_description | No | Default derived |
| activation_expiry_date | No | ISO 8601; default 24h |
| instance_name | No | Default hybrid-{account}-{username} when username provided |
| username / user_name | No | For default instance_name |
| ssm_default_instance_name | No | Look up existing activation from Secrets Manager |
| destination_region / source_region | No | Region |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| activation_id | Created or existing |
| instance_name | Default instance name for registration |
| verified | In verify mode |
| error, message | On error |

## Related

- **Contract:** [create-ssm-hybrid-activation.yaml](../../contracts/operations/create-ssm-hybrid-activation.yaml)
