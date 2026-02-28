# Domain Join EC2 Instance

## Summary

Performs domain join on an existing EC2 instance via SSM (realm join or **AWS-JoinDirectoryServiceDomain-V2**). Used by the provision-ec2-instance pipeline after the managed-instance playbook so Kerberos crypto-policies are applied before join. Idempotent: if already domain joined, returns success.

## Inputs

| Input | Required | Description |
| ----- | -------- | ----------- |
| operation | Yes | `domain-join-ec2-instance` |
| mode | Yes | `verify` or `modify` |
| instance_id | Yes | EC2 instance ID |
| destination_account_id | Yes | Target account |
| domain_join_directory_name | Yes | Directory DNS name |
| domain_join_username, domain_join_password_secret_name | Yes (realm) | Credentials from source account |
| domain_join_computer_ou | No | OU for computer object |
| domain_join_use_aws_document | No | Use AWS-JoinDirectoryServiceDomain-V2 when true |
| destination_region / source_region | No | Region |
| ssm_registration_timeout_seconds | No | Wait for SSM |
| source_account_id | No | For role assumption |

## Outputs

| Output | Description |
| ------ | ----------- |
| status | `success` or `error` |
| verified | In verify mode |
| error, message | On error |

## Related

- **Contract:** [domain-join-ec2-instance.yaml](../../contracts/operations/domain-join-ec2-instance.yaml)
