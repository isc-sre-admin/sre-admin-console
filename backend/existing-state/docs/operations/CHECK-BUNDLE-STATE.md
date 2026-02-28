# Check Bundle State

## Summary

Returns the WorkSpaces bundle state in a destination account. Used by provision-linux-workspace and provision-windows-workspace pipelines to poll until the bundle is available before launching a WorkSpace.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `check-bundle-state` |
| bundle_id | Yes | WorkSpaces bundle ID |
| destination_account_id | Yes | Target account |
| source_region | No | Region |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| ready | true when bundle is available |
| state | Bundle state |

## Related

- **Contract:** [check-bundle-state.yaml](../../contracts/operations/check-bundle-state.yaml)
