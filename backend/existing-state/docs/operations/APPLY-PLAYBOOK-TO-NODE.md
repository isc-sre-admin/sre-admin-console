# Apply Playbook to Node

## Summary

Applies an Ansible playbook to a specific SSM node by node_id. Used by the provision-linux-workspace pipeline in the rerun path when re-applying the managed-workspace playbook to an existing WorkSpace without re-running image/bundle/launch steps.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `apply-ansible-playbook-to-node` |
| mode | Yes | `verify` or `modify` |
| destination_account_id | Yes | Target account |
| destination_region | Yes | Target region |
| node_id | Yes | SSM managed instance ID |
| username | No | Passed for CloudWatch log stream name |
| playbook | Yes | e.g. `managed-workspace.yaml` |
| install_dependencies | No | Default false in rerun path |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| error, message | On error |

## Related

- **Contract:** [apply-playbook-to-node.yaml](../../contracts/operations/apply-playbook-to-node.yaml)
