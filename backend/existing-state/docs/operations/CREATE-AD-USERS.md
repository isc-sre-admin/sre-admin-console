# Create AD Users

## Summary

Creates AD groups (if missing) and AD users in AWS Managed Microsoft AD in the source account. Stores user passwords in a single Secrets Manager secret. Ensures displayName and retries for password eventual consistency. Idempotent: existing users/groups are skipped.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `create-ad-users` |
| mode | Yes | `verify` or `modify` |
| directory_id | Yes | Directory ID |
| ad_users | Yes | List of user_logon_name, email, first_name, last_name |
| ad_users_secret_name | Yes | Secret to store user/password JSON |
| ad_groups | No | Groups to create/ensure; optional parent_group_name |
| password_policy | No | minimum_length, require_uppercase, etc. |
| source_region | No | Region |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| groups_would_be_created, groups_already_exist | Verify summary |
| users_would_be_created, users_already_exist | Verify summary |
| verified | In verify mode |
| error, message | On error |

## Related

- **Contract:** [create-ad-users.yaml](../../contracts/operations/create-ad-users.yaml)
