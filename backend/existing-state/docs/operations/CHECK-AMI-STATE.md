# Check AMI State

## Summary

Checks whether an AMI in a destination account has reached **available** state. Used by the provision-ec2-instance pipeline to poll after copy-ami before launching the instance.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `check-ami-state` |
| ami_id | Yes | AMI ID in destination account |
| destination_account_id | Yes | Target account |
| destination_region / source_region | No | Region |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| ready | true when AMI state is available |
| state | AMI state (e.g. pending, available) |

## Related

- **Contract:** [check-ami-state.yaml](../../contracts/operations/check-ami-state.yaml)
