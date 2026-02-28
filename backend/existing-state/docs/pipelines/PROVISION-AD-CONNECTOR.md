# Provision AD Connector Pipeline

## Summary

The **provision-ad-connector** Step Functions pipeline deploys an AD Connector in a destination account, configures RADIUS shared secrets and Duo Auth Proxy on tagged EC2 nodes, enables RADIUS MFA on the AD Connector, registers the directory with WorkSpaces, applies Penn client branding, and creates an SSM hybrid activation. Optional: create one or more security groups before the AD Connector; when exactly one security group is created, it is used as the WorkSpaces custom security group.

## Pipeline Steps

| Step | Function | Inputs | Outputs |
| ---- | -------- | ------ | ------- |
| CheckHasSecurityGroupsPresent | Branch on presence of `security_groups` in input | Pipeline input | Next: CreateSecurityGroupsMap or CreateADConnectorNoSG |
| CreateSecurityGroupsMap | Create security groups (create-security-group) for each item | mode, destination_account_id, security_groups[] | createSecurityGroupsResult |
| CreateADConnector / CreateADConnectorNoSG | Create AD Connector in destination account | mode, destination_account_id, optional security_group_name | createAdConnectorResult (directory_id) |
| CheckADConnectorState | Poll until directory Stage is Active | destination_account_id, directory_id | ready, state |
| WaitForADConnector | Wait 120s before re-checking | — | — |
| CreateRadiusSharedSecret | Add enclave to radius-secrets JSON in source account | mode, destination_account_id, enclave_name | createRadiusSharedSecretResult |
| ListDuoAuthProxyNodes | Get duo-auth-proxy EC2 instance IDs (source account) | destination_account_id | node_ids, node_account_id |
| ApplyPlaybookSingleNode / ApplyPlaybookFirstNode / ApplyPlaybookRemainingMap | Apply duoauthproxy.yaml to node(s); multi-node: first then remaining if config_changed | node_id(s), playbook, secret_name, destination_region, etc. | applyFirstNodeResult, applyPlaybookResults, config_changed |
| GetRemainingNodeIndices | Indices of nodes not yet processed | node_ids | remaining_indices |
| EnableADConnectorMFA | Enable RADIUS MFA on AD Connector | mode, destination_account_id, enclave_name | enableMfaResult |
| RegisterWorkspaceDirectory | Register directory with WorkSpaces; apply ou_path, security_group | destination_account_id, directory_id, ou_path, optional security_group | registerWorkspaceDirectoryResult |
| ConfigureWorkspaceBranding | Deploy Penn branding to directory | mode, destination_account_id, directory_id | configureBrandingResult |
| CreateSSMHybridActivation | Create/verify SSM hybrid activation | mode, destination_account_id, iam_role, instance_limit | createSsmHybridActivationResult |
| PipelineSucceeded / PipelineFailed | Terminal state | — | — |

## Related

- **Contract:** [provision-ad-connector.yaml](../../contracts/pipelines/provision-ad-connector.yaml)
- **State machine:** `statemachine/provision_ad_connector.asl.json`
- **Run:** `./scripts/start_provision_ad_connector.sh events/<path>/provision-ad-connector.json`
