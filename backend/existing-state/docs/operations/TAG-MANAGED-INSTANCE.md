# Tag Managed Instance

## Summary

Tags SSM managed instances in the destination region. When **activation_default_instance_name** is provided (e.g. from provision-linux-workspace), targets only the managed instance whose SSM Name equals that value and adds EndUser, ResearchGroup, EnclaveID, Name tags; returns its managed instance ID as **tagged_instance_ids[0]** so pipelines can pass it to apply-ansible-playbook. Without that parameter, tags all untagged managed instances in the region. Uses SSM in the **source** account (config source_account_id) to tag instances in destination_region.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `tag-managed-instance` |
| destination_account_id | Yes | Account (for context) |
| destination_region | Yes | Region where instances live |
| tag-user-email | No | EndUser tag |
| tag-research-group | No | ResearchGroup tag |
| tag-enclave-id | No | EnclaveID tag |
| tag-username | No | Name tag component |
| activation_default_instance_name | No | When set, target only this SSM Name (pipeline path) |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| tagged_instance_ids | Managed instance IDs that were tagged |
| error, message | On error (e.g. ManagedInstanceNotFound) |

## Related

- **Contract:** [tag-managed-instance.yaml](../../contracts/operations/tag-managed-instance.yaml)
