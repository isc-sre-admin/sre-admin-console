# Launch WorkSpace

## Summary

Launches a WorkSpace in the destination account from a bundle. Optional directory_id (if omitted, first WorkSpaces directory in the account is used). Supports running_mode, encryption options, encryption_key_alias.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `launch-workspace` |
| mode | Yes | `verify` or `modify` |
| bundle_id | Yes | WorkSpaces bundle ID |
| destination_account_id | Yes | Target account |
| username | Yes | WorkSpace user |
| running_mode | Yes | e.g. ALWAYS_ON |
| encrypt_root_volume | Yes | Boolean |
| encrypt_user_volume | Yes | Boolean |
| directory_id | No | Default first directory |
| encryption_key_alias | No | KMS alias |
| source_region | No | Region |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| workspace_id | Launched WorkSpace ID |
| error, message | On error |

## Related

- **Contract:** [launch-workspace.yaml](../../contracts/operations/launch-workspace.yaml)
