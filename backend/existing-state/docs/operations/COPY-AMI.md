# Copy AMI

## Summary

Creates a local copy of a shared AMI in the destination account. The source AMI must already be shared via **share-ami** (which shares both the AMI and its EBS snapshots). Assumes SystemManagementModifierRole (modify) or SystemManagementVerifierRole (verify) in the destination account. Idempotent: if a copy with the same name exists, returns success.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `copy-ami` |
| mode | Yes | `verify` or `modify` |
| ami_id | Yes | Source AMI ID (shared to destination) |
| destination_account_id | Yes | Target account |
| source_region | No | Source region (or config) |
| copy_name | No | Name for copy (default: source name + "-local") |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| new_ami_id | ID of the copied AMI (modify) |
| error, message | On error |

## Related

- **Contract:** [copy-ami.yaml](../../contracts/operations/copy-ami.yaml)
