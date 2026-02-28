# Remove Activation GPO

## Summary

Backout for **deploy-activation-gpo**: unlinks the GPO from an OU (or all OUs) and optionally deletes the GPO via SSM on the same Windows instance.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `remove-activation-gpo` |
| mode | Yes | `verify` or `modify` |
| destination_account_id | Yes | Target account |
| instance_id | Yes | Windows EC2 with GPMC |
| gpo_name | No | Default "WorkSpaces SSM activation" |
| ou_path | No | Unlink only from this OU; omit to unlink from all |
| delete_gpo | No | Default false; true to delete GPO after unlink |
| destination_region | No | Region |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| verified | In verify mode |
| error, message | On error |

## Related

- **Contract:** [remove-activation-gpo.yaml](../../contracts/operations/remove-activation-gpo.yaml)
