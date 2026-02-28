# Check Image State

## Summary

Returns the WorkSpaces image state in an account. Used by workspace pipelines to poll until an image is **AVAILABLE** before sharing or creating a bundle.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `check-image-state` |
| image_id | Yes | WorkSpaces image ID |
| destination_account_id | Yes | Account where image lives |
| source_region | No | Region |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| ready | true when image state is AVAILABLE |
| state | Image state |

## Related

- **Contract:** [check-image-state.yaml](../../contracts/operations/check-image-state.yaml)
