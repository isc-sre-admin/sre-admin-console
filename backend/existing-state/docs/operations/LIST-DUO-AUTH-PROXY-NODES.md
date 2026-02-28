# List Duo Auth Proxy Nodes

## Summary

Returns EC2 instance IDs in the source account (config `source_account_id`) with tag **Function: duo-auth-proxy** that are SSM-managed and **Online**. Used by the provision-ad-connector pipeline; returns node_account_id so apply-ansible-playbook runs in the correct account.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `list-duo-auth-proxy-nodes` |
| destination_account_id | Yes | Account to query (often same as source) |
| destination_region / source_region | No | Region |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| node_ids | Array of EC2 instance IDs |
| node_account_id | Account where nodes were found |
| tagged_count, ssm_online_count, message | When node_ids empty (troubleshooting) |
| error, message | On error |

## Related

- **Contract:** [list-duo-auth-proxy-nodes.yaml](../../contracts/operations/list-duo-auth-proxy-nodes.yaml)
