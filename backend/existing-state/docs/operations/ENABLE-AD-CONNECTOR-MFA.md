# Enable AD Connector MFA

## Summary

Enables RADIUS MFA on an AD Connector in the destination account using the shared secret from the radius-secrets enclave (create-radius-shared-secret). Idempotent: if RADIUS already enabled with matching settings and RadiusStatus is not Failed, returns success. Verify mode checks that RADIUS is enabled and settings match.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `enable-ad-connector-mfa` |
| mode | Yes | `verify` or `modify` |
| destination_account_id | Yes | Target account |
| enclave_name | Yes | Enclave name in radius-secrets |
| radius_server_display_label | Yes | Display label |
| radius_server_dns_name | Yes | RADIUS server DNS |
| secret_name | Yes | Secrets Manager secret (source) with enclaves |
| radius_server_port | Yes | Port (e.g. 1812) |
| protocol | Yes | PAP, CHAP, MS-CHAPv1, MS-CHAPv2 |
| server_timeout | Yes | 1–50 seconds |
| max_radius_retry_requests | Yes | 0–10 |
| directory_dns_name | No | When multiple AD Connectors |
| destination_region / source_region | No | Region |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| verified | In verify mode |
| radius_status | e.g. Failed (verify suggests re-run modify) |
| error, message | On error |

## Related

- **Contract:** [enable-ad-connector-mfa.yaml](../../contracts/operations/enable-ad-connector-mfa.yaml)
