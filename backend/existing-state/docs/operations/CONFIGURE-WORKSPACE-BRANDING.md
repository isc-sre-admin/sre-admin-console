# Configure WorkSpace Branding

## Summary

Deploys Penn WorkSpaces client branding (logo, support link, login message) to a destination account using **ImportClientBranding**. Logo file `PennLogo.png` is bundled under `src/assets/`. Apply to a directory_id (e.g. AD Connector); if directory_id is omitted, the first directory in the account is used.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `configure-workspace-branding` |
| mode | Yes | `verify` or `modify` |
| destination_account_id | Yes | Target account |
| directory_id | No | WorkSpaces directory; default first directory |
| destination_region / source_region | No | Region |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| verified | In verify mode (true if branding present) |
| error, message | On error |

## Related

- **Contract:** [configure-workspace-branding.yaml](../../contracts/operations/configure-workspace-branding.yaml)
