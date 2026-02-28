# Ensure Ansible on Node

## Summary

Ensures Ansible is installed on an SSM managed node. Used by the provision-linux-workspace rerun path before applying the managed-workspace playbook to an existing WorkSpace when the node may not have Ansible yet.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `ensure-ansible-on-node` |
| destination_account_id | Yes | Target account |
| destination_region | Yes | Region |
| node_id | Yes | SSM managed instance ID |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| error, message | On error |

## Related

- **Contract:** [ensure-ansible-on-node.yaml](../../contracts/operations/ensure-ansible-on-node.yaml)
