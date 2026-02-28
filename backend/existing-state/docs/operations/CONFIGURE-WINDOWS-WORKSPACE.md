# Configure Windows WorkSpace

## Summary

Runs a list of PowerShell scripts (e.g. RStudio installer) on a Windows WorkSpace via SSM **AWS-RunPowerShellScript**. Scripts are relative paths under `src/assets/powershell/windows-workspace` and are bundled into the Lambda image; they are uploaded to S3 and executed on the target managed instance (node_id).

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `configure-windows-workspace` |
| mode | Yes | `verify` or `modify` |
| destination_account_id | Yes | Target account |
| node_id | Yes | SSM managed instance ID (WorkSpace) |
| node_name | Yes | Used for logging (e.g. username) |
| scripts | Yes | List of relative paths (e.g. `["rinstall.ps1", "rstudio.ps1"]`) |
| destination_region / source_region | No | Region |
| timeout_seconds | No | Default 1200 |
| installer_url, installer_urls | No | Passed to scripts (e.g. RStudio URL) |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| command_id, scripts | For CloudWatch/SSM inspection |
| verified | In verify mode |
| error, message | On error |

## Related

- **Contract:** [configure-windows-workspace.yaml](../../contracts/operations/configure-windows-workspace.yaml)
