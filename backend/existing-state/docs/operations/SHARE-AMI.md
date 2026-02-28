# Share AMI

## Summary

Shares an existing AMI in the source account (config `source_account_id`) with a destination account: adds launch permission on the AMI and createVolumePermission on its backing EBS snapshots (required for cross-account copy-ami). Runs in the source account with Lambda execution role.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `share-ami` |
| mode | Yes | `verify` or `modify` |
| ami_id | Yes | AMI ID in source account |
| destination_account_id | Yes | Account to share with |
| source_region | No | Region (or config copy_image_source_region) |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| verified | In verify mode (already shared) |
| error, message | On error |

## Related

- **Contract:** [share-ami.yaml](../../contracts/operations/share-ami.yaml)
