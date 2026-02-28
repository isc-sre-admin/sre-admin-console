# Create Bundle

## Summary

Creates a WorkSpaces bundle from an image in the destination account. Used by workspace pipelines after the image is copied and available.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `create-bundle` |
| mode | Yes | `verify` or `modify` |
| image_id | Yes | WorkSpaces image ID |
| destination_account_id | Yes | Target account |
| hardware_type | Yes | Bundle hardware type |
| storage_settings | Yes | Root/user volume settings |
| source_region | No | Region |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| bundle_id | Created or existing bundle ID |
| error, message | On error |

## Related

- **Contract:** [create-bundle.yaml](../../contracts/operations/create-bundle.yaml)
