# Check SSM Registration

## Summary

Checks whether a specific SSM managed instance (node_id) is registered and **Online** in Systems Manager for a destination account/region. Used by the provision-linux-workspace rerun path before applying the managed-workspace playbook to an existing WorkSpace.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `check-ssm-registration` |
| node_id | Yes | SSM managed instance ID |
| destination_account_id | Yes | Target account |
| destination_region | No | Region |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| ready | true when instance is registered and Online |

## Related

- **Contract:** [check-ssm-registration.yaml](../../contracts/operations/check-ssm-registration.yaml)
