# Copy Image

## Summary

Copies a shared WorkSpaces image into the destination account (local copy with `-local` suffix). Used by workspace pipelines after **share-image**. Assumes modifier/verifier role in destination when account differs from Lambda account.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `copy-image` |
| mode | Yes | `verify` or `modify` |
| image_id | Yes | WorkSpaces image ID (shared to destination) |
| destination_account_id | Yes | Target account |
| source_region | No | Region (or config) |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| new_image_id | ID of copied image (modify) |
| error, message | On error |

## Related

- **Contract:** [copy-image.yaml](../../contracts/operations/copy-image.yaml)
