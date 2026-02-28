# Create AD Connector

## Summary

Deploys an AD Connector in a destination account. Password is read from Secrets Manager in the source account (config `source_account_id`). Supports **verify** mode (check that connector with directory_dns_name exists) and **modify** mode (create via STS assume role). Optional security_group_name; VPC/subnet by vpc_id/vpc_name and subnet_ids or subnet_names.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `create-ad-connector` |
| mode | Yes | `verify` or `modify` |
| destination_account_id | Yes | Target account |
| directory_size | Yes | `small` or `large` |
| directory_dns_name | Yes | DNS name for directory |
| dns_ip_addresses | Yes | DNS IPs for the domain |
| service_account_username | Yes | Domain service account |
| service_account_password_secret_name | Yes | Secret in source account (JSON key "secret") |
| vpc_id / vpc_name, subnet_ids / subnet_names | No | Network; defaults when omitted |
| security_group_name | No | Passed to register-workspace-directory when one SG created in pipeline |
| source_region / destination_region | No | Region |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| directory_id | Created or existing directory ID |
| verified | In verify mode |
| error, message | On error |

## Related

- **Contract:** [create-ad-connector.yaml](../../contracts/operations/create-ad-connector.yaml)
