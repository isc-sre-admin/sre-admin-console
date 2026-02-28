# Check Workspace State

## Summary

Returns the WorkSpace state (e.g. PENDING, AVAILABLE, STOPPED). If the workspace is STOPPED, the operation starts it. Used by workspace pipelines to poll until a workspace is **AVAILABLE** before create-workspace-image or before running playbooks/scripts.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `check-workspace-state` |
| workspace_id | Yes | WorkSpace ID |
| destination_account_id | Yes | Target account |
| source_region | No | Region |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| ready | true when state is AVAILABLE |
| state | WorkSpace state |

## Related

- **Contract:** [check-workspace-state.yaml](../../contracts/operations/check-workspace-state.yaml)
