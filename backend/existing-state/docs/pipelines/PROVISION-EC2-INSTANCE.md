# Provision EC2 Instance Pipeline

## Summary

The **provision-ec2-instance** Step Functions pipeline shares an AMI from the source account to a destination account, copies it there, waits for the copy to become available, and launches an EC2 instance with the specified instance type, storage, security groups, and tags. Optionally: create security groups from definitions first; domain-join the instance (managed-instance playbook then domain-join-ec2-instance); and apply the Duo Unix playbook for SSH MFA.

## Pipeline Steps

| Step | Function | Inputs | Outputs |
| ---- | -------- | ------ | ------- |
| NormalizeInput | Merge pipeline input with config | pipeline_input | normalized |
| ExtractNormalized | Pass normalized payload into state | normalized.Payload.normalized | — |
| CheckHasSecurityGroups | Branch on presence of security_groups | normalized.security_groups | Next: CreateSecurityGroupsMap or ShareAMI |
| CreateSecurityGroupsMap | create-security-group for each item | mode, destination_account_id, security_groups[] | createSecurityGroupsResult |
| ShareAMI | Share AMI and snapshots to destination (source account) | mode, ami_id, destination_account_id, source_region | shareResult |
| CopyAMI | Copy AMI into destination account | mode, ami_id, destination_account_id, copy_name | new_ami_id |
| CopyResultNextChoice | verify mode → skip wait | mode | Next: CheckWantDomainJoin or CheckAMIImageState |
| CheckAMIImageState | Poll until copied AMI available | new_ami_id, destination_account_id | ready |
| WaitForAMIImage | Wait 60s before re-check | — | — |
| CheckWantDomainJoin | Branch on domain_join_directory_name | domain_join_directory_name | PassSkipDomainJoinInLaunch |
| LaunchEC2Instance | Launch EC2 with AMI, storage, security groups, tags | image_id, instance_type, storage_settings, tag-resource-group, security_groups, etc., skip_domain_join_in_launch | instance_id |
| CheckWantDomainJoinAfterLaunch | If domain join requested → run playbook then domain join | domain_join_directory_name | Next: ApplyManagedInstancePlaybook or PipelineSucceeded |
| ApplyManagedInstancePlaybook | apply-ansible-playbook managed-instance.yaml | node_id (instance_id), playbook, output S3/CloudWatch | applyPlaybookResult |
| DomainJoinEC2Instance | domain-join-ec2-instance via SSM | instance_id, domain_join_*, destination_account_id | domainJoinResult |
| CheckWantDuoUnix | If duo_unix_secret_name set → apply Duo Unix playbook | duo_unix_secret_name | Next: ApplyDuoUnixPlaybook or PipelineSucceeded |
| ApplyDuoUnixPlaybook | apply-ansible-playbook duo-unix.yaml | node_id, secret_name | applyDuoUnixResult |
| PipelineSucceeded / PipelineFailed | Terminal state | — | — |

## Related

- **Contract:** [provision-ec2-instance.yaml](../../contracts/pipelines/provision-ec2-instance.yaml)
- **State machine:** `statemachine/provision_ec2_instance.asl.json`
- **Run:** `./scripts/sre-cli provision-ec2-instance events/example/provision-ec2-instance.json`
