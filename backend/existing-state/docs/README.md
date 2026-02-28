# SRE Management Documentation

Detailed documentation for pipelines and operations supported by the sre-management Lambda and Step Functions.

## Documentation index

| Topic | Description |
|-------|-------------|
| [Project structure](PROJECT-STRUCTURE.md) | Repository layout and main folders. |
| [Configuration](CONFIGURATION.md) | config.yaml, operation defaults, and examples. |
| [Building and deploying](BUILDING-AND-DEPLOYING.md) | Build, SAM deploy, SystemManagementRole in destination accounts. |
| [Local testing](LOCAL-TESTING.md) | Invoking Lambda, unit tests, Bandit, pre-commit. |
| [CI/CD](CI-CD.md) | CodePipeline (CDK) for dev and prod. |
| [Playbooks and S3](PLAYBOOKS-AND-S3.md) | Syncing playbooks, cross-account delivery. |
| [Troubleshooting](TROUBLESHOOTING.md) | Command output, apply-ansible-playbook, list-duo-auth-proxy-nodes. |
| [Response format and utilities](RESPONSE-AND-UTILITIES.md) | Success/error shape, sanitize script. |
| [Useful commands](COMMANDS.md) | Quick reference table of common commands. |

## Pipelines

Step Functions state machines that orchestrate multiple operations in sequence.

| Pipeline | Description | Doc | Contract |
| -------- | ----------- | --- | -------- |
| [Provision AD Connector](pipelines/PROVISION-AD-CONNECTOR.md) | Deploy AD Connector, RADIUS/MFA, Duo Auth Proxy, register directory, branding, SSM activation | [PROVISION-AD-CONNECTOR.md](pipelines/PROVISION-AD-CONNECTOR.md) | [provision-ad-connector.yaml](../contracts/pipelines/provision-ad-connector.yaml) |
| [Provision Linux WorkSpace](pipelines/PROVISION-LINUX-WORKSPACE.md) | Image → share → copy → bundle → launch Linux WorkSpace → SSM tag → managed-workspace playbook | [PROVISION-LINUX-WORKSPACE.md](pipelines/PROVISION-LINUX-WORKSPACE.md) | [provision-linux-workspace.yaml](../contracts/pipelines/provision-linux-workspace.yaml) |
| [Provision Windows WorkSpace](pipelines/PROVISION-WINDOWS-WORKSPACE.md) | Same as Linux; optionally run PowerShell scripts (e.g. RStudio) after tag | [PROVISION-WINDOWS-WORKSPACE.md](pipelines/PROVISION-WINDOWS-WORKSPACE.md) | [provision-windows-workspace.yaml](../contracts/pipelines/provision-windows-workspace.yaml) |
| [Provision EC2 Instance](pipelines/PROVISION-EC2-INSTANCE.md) | Share AMI → copy AMI → launch EC2 → optional domain join and Duo Unix | [PROVISION-EC2-INSTANCE.md](pipelines/PROVISION-EC2-INSTANCE.md) | [provision-ec2-instance.yaml](../contracts/pipelines/provision-ec2-instance.yaml) |

## Operations

Lambda operations invoked by pipelines or directly.

| Operation | Description | Doc | Contract |
| --------- | ----------- | --- | -------- |
| [Apply Ansible Playbook](operations/APPLY-ANSIBLE-PLAYBOOK.md) | Deploy Ansible playbook to an EC2/SSM node | [APPLY-ANSIBLE-PLAYBOOK.md](operations/APPLY-ANSIBLE-PLAYBOOK.md) | [apply-ansible-playbook.yaml](../contracts/operations/apply-ansible-playbook.yaml) |
| [Apply Playbook to Node](operations/APPLY-PLAYBOOK-TO-NODE.md) | Apply playbook to a specific node (used in workspace rerun path) | [APPLY-PLAYBOOK-TO-NODE.md](operations/APPLY-PLAYBOOK-TO-NODE.md) | [apply-playbook-to-node.yaml](../contracts/operations/apply-playbook-to-node.yaml) |
| [Assign Domain Name](operations/ASSIGN-DOMAIN-NAME.md) | Route 53 A record for subdomain → instance IP | [ASSIGN-DOMAIN-NAME.md](operations/ASSIGN-DOMAIN-NAME.md) | [assign-domain-name.yaml](../contracts/operations/assign-domain-name.yaml) |
| [Check AD Connector State](operations/CHECK-AD-CONNECTOR-STATE.md) | Poll directory stage until Active | [CHECK-AD-CONNECTOR-STATE.md](operations/CHECK-AD-CONNECTOR-STATE.md) | [check-ad-connector-state.yaml](../contracts/operations/check-ad-connector-state.yaml) |
| [Check AMI State](operations/CHECK-AMI-STATE.md) | Poll AMI until available | [CHECK-AMI-STATE.md](operations/CHECK-AMI-STATE.md) | [check-ami-state.yaml](../contracts/operations/check-ami-state.yaml) |
| [Check Bundle State](operations/CHECK-BUNDLE-STATE.md) | Poll WorkSpaces bundle until available | [CHECK-BUNDLE-STATE.md](operations/CHECK-BUNDLE-STATE.md) | [check-bundle-state.yaml](../contracts/operations/check-bundle-state.yaml) |
| [Check Image State](operations/CHECK-IMAGE-STATE.md) | Poll WorkSpaces image until available | [CHECK-IMAGE-STATE.md](operations/CHECK-IMAGE-STATE.md) | [check-image-state.yaml](../contracts/operations/check-image-state.yaml) |
| [Check SSM Registration](operations/CHECK-SSM-REGISTRATION.md) | Check if node_id is registered and Online in SSM | [CHECK-SSM-REGISTRATION.md](operations/CHECK-SSM-REGISTRATION.md) | [check-ssm-registration.yaml](../contracts/operations/check-ssm-registration.yaml) |
| [Check Workspace State](operations/CHECK-WORKSPACE-STATE.md) | Return workspace state; start if STOPPED | [CHECK-WORKSPACE-STATE.md](operations/CHECK-WORKSPACE-STATE.md) | [check-workspace-state.yaml](../contracts/operations/check-workspace-state.yaml) |
| [Configure Windows WorkSpace](operations/CONFIGURE-WINDOWS-WORKSPACE.md) | Run PowerShell scripts on Windows WorkSpace via SSM | [CONFIGURE-WINDOWS-WORKSPACE.md](operations/CONFIGURE-WINDOWS-WORKSPACE.md) | [configure-windows-workspace.yaml](../contracts/operations/configure-windows-workspace.yaml) |
| [Configure WorkSpace Branding](operations/CONFIGURE-WORKSPACE-BRANDING.md) | Deploy Penn client branding (logo, support link) | [CONFIGURE-WORKSPACE-BRANDING.md](operations/CONFIGURE-WORKSPACE-BRANDING.md) | [configure-workspace-branding.yaml](../contracts/operations/configure-workspace-branding.yaml) |
| [Copy AMI](operations/COPY-AMI.md) | Copy shared AMI into destination account | [COPY-AMI.md](operations/COPY-AMI.md) | [copy-ami.yaml](../contracts/operations/copy-ami.yaml) |
| [Copy Image](operations/COPY-IMAGE.md) | Copy shared WorkSpaces image into destination account | [COPY-IMAGE.md](operations/COPY-IMAGE.md) | [copy-image.yaml](../contracts/operations/copy-image.yaml) |
| [Create AD Connector](operations/CREATE-AD-CONNECTOR.md) | Deploy AD Connector in destination account | [CREATE-AD-CONNECTOR.md](operations/CREATE-AD-CONNECTOR.md) | [create-ad-connector.yaml](../contracts/operations/create-ad-connector.yaml) |
| [Create AD Group](operations/CREATE-AD-GROUP.md) | Create AD group in AWS Managed Microsoft AD | [CREATE-AD-GROUP.md](operations/CREATE-AD-GROUP.md) | [create-ad-group.yaml](../contracts/operations/create-ad-group.yaml) |
| [Create AD Users](operations/CREATE-AD-USERS.md) | Create AD groups/users; store passwords in Secrets Manager | [CREATE-AD-USERS.md](operations/CREATE-AD-USERS.md) | [create-ad-users.yaml](../contracts/operations/create-ad-users.yaml) |
| [Create Bundle](operations/CREATE-BUNDLE.md) | Create WorkSpaces bundle from image | [CREATE-BUNDLE.md](operations/CREATE-BUNDLE.md) | [create-bundle.yaml](../contracts/operations/create-bundle.yaml) |
| [Create Data Exports](operations/CREATE-DATA-EXPORTS.md) | Create/verify BCM Data Exports (org management account) | [CREATE-DATA-EXPORTS.md](operations/CREATE-DATA-EXPORTS.md) | [create-data-exports.yaml](../contracts/operations/create-data-exports.yaml) |
| [Create Radius Shared Secret](operations/CREATE-RADIUS-SHARED-SECRET.md) | Add enclave to radius-secrets JSON with AD Connector IPs | [CREATE-RADIUS-SHARED-SECRET.md](operations/CREATE-RADIUS-SHARED-SECRET.md) | [create-radius-shared-secret.yaml](../contracts/operations/create-radius-shared-secret.yaml) |
| [Create Security Group](operations/CREATE-SECURITY-GROUP.md) | Create EC2 security group with ingress/egress rules | [CREATE-SECURITY-GROUP.md](operations/CREATE-SECURITY-GROUP.md) | [create-security-group.yaml](../contracts/operations/create-security-group.yaml) |
| [Create SSM Hybrid Activation](operations/CREATE-SSM-HYBRID-ACTIVATION.md) | Create/verify SSM hybrid activation for managed instances | [CREATE-SSM-HYBRID-ACTIVATION.md](operations/CREATE-SSM-HYBRID-ACTIVATION.md) | [create-ssm-hybrid-activation.yaml](../contracts/operations/create-ssm-hybrid-activation.yaml) |
| [Create Workspace Image](operations/CREATE-WORKSPACE-IMAGE.md) | Create WorkSpace image from existing WorkSpace | [CREATE-WORKSPACE-IMAGE.md](operations/CREATE-WORKSPACE-IMAGE.md) | [create-workspace-image.yaml](../contracts/operations/create-workspace-image.yaml) |
| [Deploy Activation GPO](operations/DEPLOY-ACTIVATION-GPO.md) | GPO to run SSM hybrid activation script at startup | [DEPLOY-ACTIVATION-GPO.md](operations/DEPLOY-ACTIVATION-GPO.md) | [deploy-activation-gpo.yaml](../contracts/operations/deploy-activation-gpo.yaml) |
| [Domain Join EC2 Instance](operations/DOMAIN-JOIN-EC2-INSTANCE.md) | Domain join existing EC2 via SSM (realm or AWS document) | [DOMAIN-JOIN-EC2-INSTANCE.md](operations/DOMAIN-JOIN-EC2-INSTANCE.md) | [domain-join-ec2-instance.yaml](../contracts/operations/domain-join-ec2-instance.yaml) |
| [Enable AD Connector MFA](operations/ENABLE-AD-CONNECTOR-MFA.md) | Enable RADIUS MFA on AD Connector | [ENABLE-AD-CONNECTOR-MFA.md](operations/ENABLE-AD-CONNECTOR-MFA.md) | [enable-ad-connector-mfa.yaml](../contracts/operations/enable-ad-connector-mfa.yaml) |
| [Ensure Ansible on Node](operations/ENSURE-ANSIBLE-ON-NODE.md) | Ensure Ansible is installed on SSM node | [ENSURE-ANSIBLE-ON-NODE.md](operations/ENSURE-ANSIBLE-ON-NODE.md) | [ensure-ansible-on-node.yaml](../contracts/operations/ensure-ansible-on-node.yaml) |
| [Get Remaining Node Indices](operations/GET-REMAINING-NODE-INDICES.md) | Return indices of nodes not yet processed (provision-ad-connector) | [GET-REMAINING-NODE-INDICES.md](operations/GET-REMAINING-NODE-INDICES.md) | [get-remaining-node-indices.yaml](../contracts/operations/get-remaining-node-indices.yaml) |
| [Launch EC2 Instance](operations/LAUNCH-EC2-INSTANCE.md) | Launch EC2 instance with AMI, storage, security groups | [LAUNCH-EC2-INSTANCE.md](operations/LAUNCH-EC2-INSTANCE.md) | [launch-ec2-instance.yaml](../contracts/operations/launch-ec2-instance.yaml) |
| [Launch WorkSpace](operations/LAUNCH-WORKSPACE.md) | Launch WorkSpace in destination account | [LAUNCH-WORKSPACE.md](operations/LAUNCH-WORKSPACE.md) | [launch-workspace.yaml](../contracts/operations/launch-workspace.yaml) |
| [List Duo Auth Proxy Nodes](operations/LIST-DUO-AUTH-PROXY-NODES.md) | List EC2 instances tagged as duo-auth-proxy, SSM online | [LIST-DUO-AUTH-PROXY-NODES.md](operations/LIST-DUO-AUTH-PROXY-NODES.md) | [list-duo-auth-proxy-nodes.yaml](../contracts/operations/list-duo-auth-proxy-nodes.yaml) |
| [Register WorkSpace Directory](operations/REGISTER-WORKSPACE-DIRECTORY.md) | Register directory with WorkSpaces; apply directory defaults | [REGISTER-WORKSPACE-DIRECTORY.md](operations/REGISTER-WORKSPACE-DIRECTORY.md) | [register-workspace-directory.yaml](../contracts/operations/register-workspace-directory.yaml) |
| [Remove Activation GPO](operations/REMOVE-ACTIVATION-GPO.md) | Unlink/delete GPO from deploy-activation-gpo | [REMOVE-ACTIVATION-GPO.md](operations/REMOVE-ACTIVATION-GPO.md) | [remove-activation-gpo.yaml](../contracts/operations/remove-activation-gpo.yaml) |
| [Share AMI](operations/SHARE-AMI.md) | Share AMI and snapshots with destination account | [SHARE-AMI.md](operations/SHARE-AMI.md) | [share-ami.yaml](../contracts/operations/share-ami.yaml) |
| [Share Image](operations/SHARE-IMAGE.md) | Share WorkSpaces image with destination account | [SHARE-IMAGE.md](operations/SHARE-IMAGE.md) | [share-image.yaml](../contracts/operations/share-image.yaml) |
| [Tag Managed Instance](operations/TAG-MANAGED-INSTANCE.md) | Tag SSM managed instance (EndUser, ResearchGroup, etc.) | [TAG-MANAGED-INSTANCE.md](operations/TAG-MANAGED-INSTANCE.md) | [tag-managed-instance.yaml](../contracts/operations/tag-managed-instance.yaml) |
