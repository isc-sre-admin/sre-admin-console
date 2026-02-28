# Launch EC2 Instance

## Summary

Launches an EC2 instance in the destination account using an AMI and RunInstances parameters from the event. Supports storage_settings (BlockDeviceMappings), tag-resource-group, instance_name (Name tag), security groups, key pair, IAM instance profile. When domain join is requested without skip_domain_join_in_launch, the operation can run managed-instance playbook and domain join; the provision-ec2-instance pipeline uses skip_domain_join_in_launch and runs those in separate steps. Idempotent: when instance_name is set, returns existing instance if found.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `launch-ec2-instance` |
| mode | Yes | `verify` or `modify` |
| image_id / ami_id | Yes | AMI ID |
| instance_type | Yes | Instance type |
| destination_account_id | Yes | Target account |
| destination_region / source_region | No | Region |
| instance_name | No | EC2 Name tag; used for idempotency |
| storage_settings | No | RootVolume.Size, VolumeType |
| tag-resource-group | No | ResearchGroup tag |
| subnet_id / subnet_names | No | Subnet |
| security_group_ids / security_groups | No | Security groups |
| keypair_name / key_name | No | Key pair |
| iam_instance_profile_name | No | IAM profile for instance |
| domain_join_* | No | Domain join (optional; pipeline may set skip_domain_join_in_launch) |
| ssm_registration_timeout_seconds | No | Wait for SSM (default 600) |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| instance_id | Launched or existing instance |
| error, message | On error |

## Related

- **Contract:** [launch-ec2-instance.yaml](../../contracts/operations/launch-ec2-instance.yaml)
