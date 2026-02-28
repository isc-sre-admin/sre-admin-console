# Create AD Group

## Summary

Creates an AD group in AWS Managed Microsoft AD in the source account (Directory Service Data API). Supports verify and modify modes. Optional parent_group_name adds the new group as a member of that group.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `create-ad-group` |
| mode | Yes | `verify` or `modify` |
| directory_id | Yes | Directory ID (source account) |
| group_name | Yes | Group name |
| group_display_name | No | Display name |
| parent_group_name | No | Add new group as member of this group |
| description | No | Description |
| group_type | Yes | security or distribution |
| group_scope | Yes | domain local, universal, or global |
| source_region | No | Region |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| verified | In verify mode |
| error, message | On error |

## Related

- **Contract:** [create-ad-group.yaml](../../contracts/operations/create-ad-group.yaml)
