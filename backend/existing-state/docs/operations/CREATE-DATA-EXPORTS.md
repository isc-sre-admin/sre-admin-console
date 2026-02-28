# Create Data Exports

## Summary

Creates or verifies BCM (Billing and Cost Management) Data Exports in the Organization Management account. Supports primary and billing_group views; optional billing_group_name to restrict to one group. Assumes SystemManagementBillingRole. Verify mode returns per-export verified status and exports_that_would_be_created.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `create-data-exports` |
| mode | Yes | `verify` or `modify` |
| export_name_suffix | Yes | Suffix for export names |
| export_type | Yes | e.g. legacy_cur |
| billing_view_type | Yes | primary or billing_group |
| s3_bucket | Yes | S3 bucket for exports |
| s3_path_prefix | Yes | Prefix (may include ${billing_group_name}) |
| destination_account_id | Yes | Org management account |
| billing_group_name | No | When billing_view_type is billing_group |
| s3_output_configuration, etc. | No | Override options |
| destination_region / source_region | No | Region |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| verified | Per-export in verify mode |
| exports_that_would_be_created | Verify mode payloads |
| error, message | On error |

## Related

- **Contract:** [create-data-exports.yaml](../../contracts/operations/create-data-exports.yaml)
