# Register WorkSpace Directory

## Summary

Registers a Directory Service directory (e.g. AD Connector) with WorkSpaces so ImportClientBranding and other WorkSpaces APIs can use it. Polls until directory state is **REGISTERED**, then applies directory defaults (ModifyWorkspaceCreationProperties, ModifyWorkspaceAccessProperties, ModifyEndpointEncryptionMode). Optional ou_path sets DefaultOu for launched WorkSpaces. Idempotent: if already registered, returns success.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `register-workspace-directory` |
| destination_account_id | Yes | Target account |
| directory_id | Yes | Directory Service directory ID |
| subnet_ids | No | Two subnet IDs (default from directory) |
| ou_path | No | Default OU for WorkSpace machine accounts (LDAP DN) |
| security_group | No | Custom security group name for directory |
| destination_region / source_region | No | Region |
| workspace directory defaults | No | From config or pipeline (enable_internet_access, etc.) |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| error, message | On error |

## Related

- **Contract:** [register-workspace-directory.yaml](../../contracts/operations/register-workspace-directory.yaml)
