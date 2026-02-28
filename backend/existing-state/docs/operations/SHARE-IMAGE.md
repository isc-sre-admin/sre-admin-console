# Share Image

## Summary

Shares a WorkSpaces image with a destination account. The image must exist in the source (Lambda) account or in an account where the Lambda can perform the share. Used by workspace pipelines before copy-image.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `share-image` |
| image_id | Yes | WorkSpaces image ID |
| destination_account_id | Yes | Account to share with |
| mode | No | `verify` or `modify` (when used from pipeline) |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| error, message | On error |

## Related

- **Contract:** [share-image.yaml](../../contracts/operations/share-image.yaml)
