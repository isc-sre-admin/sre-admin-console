# Create Workspace Image

## Summary

Creates a new WorkSpace image from an existing WorkSpace in the destination account. In **modify** mode the workspace must be AVAILABLE (pipelines run check-workspace-state first); the operation does not start or wait. In **verify** mode checks that an image with the given name exists and returns image_id. Idempotent: if image with same name exists, returns success.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `create-workspace-image` |
| mode | Yes | `verify` or `modify` |
| destination_account_id | Yes | Target account |
| image_name | Yes | Name for the image |
| workspace_id | Yes (modify) | Source WorkSpace (must be AVAILABLE) |
| destination_region / source_region | No | Region |
| tag-research-group, tag-enclave-id | No | Tags on created image |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| image_id | Created or existing image ID |
| already_exists | When image already existed |
| verified | In verify mode |
| error, message | On error |

## Related

- **Contract:** [create-workspace-image.yaml](../../contracts/operations/create-workspace-image.yaml)
