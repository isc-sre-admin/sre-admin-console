# Check AD Connector State

## Summary

Returns the directory stage (e.g. Creating, Active) for an AD Connector in a destination account. Used by the provision-ad-connector pipeline to poll until the directory is Active before proceeding to RADIUS secret and MFA steps.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `check-ad-connector-state` |
| destination_account_id | Yes | Target account |
| directory_id or directory_dns_name | Yes | Directory identifier |
| destination_region / source_region | No | Region |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| ready | true when directory Stage is Active |
| state | Directory stage (e.g. Creating, Active) |
| directory_id | When looked up by directory_dns_name |

## Related

- **Contract:** [check-ad-connector-state.yaml](../../contracts/operations/check-ad-connector-state.yaml)
