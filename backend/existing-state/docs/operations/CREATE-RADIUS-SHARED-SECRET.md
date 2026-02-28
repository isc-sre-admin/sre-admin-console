# Create Radius Shared Secret

## Summary

Generates a RADIUS shared secret and adds an enclave entry to the radius-secrets JSON in Secrets Manager (source account), using the AD Connector's two node IPs from the destination account. Idempotent: if enclave with same enclave_name exists, returns success.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `create-radius-shared-secret` |
| mode | Yes | `verify` or `modify` |
| destination_account_id | Yes | Account with AD Connector (for IPs) |
| enclave_name | Yes | Enclave name in radius-secrets |
| secret_name | Yes | Secrets Manager secret (source) with "enclaves" array |
| directory_dns_name | No | When destination has multiple AD Connectors |
| destination_region / source_region | No | Region |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| verified | In verify mode (enclave exists, IPs match) |
| error, message | On error |

## Related

- **Contract:** [create-radius-shared-secret.yaml](../../contracts/operations/create-radius-shared-secret.yaml)
