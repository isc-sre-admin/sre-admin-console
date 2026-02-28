# Provision Linux WorkSpace Pipeline

## Summary

The **provision-linux-workspace** Step Functions pipeline creates or reuses a WorkSpace image in the source (Shared Services) account, shares and copies it to a destination account, creates a bundle, launches a Linux WorkSpace, waits for SSM registration, tags the managed instance, and optionally applies the **managed-workspace** Ansible playbook. Supports rerun with `node_id` to apply only the playbook to an existing WorkSpace.

## Pipeline Steps

| Step | Function | Inputs | Outputs |
| ---- | -------- | ------ | ------- |
| NormalizeInput | Merge pipeline input with config defaults | pipeline_input | normalized |
| ExtractNormalized | Pass normalized payload into state | normalized.Payload.normalized | — |
| RerunPlaybookChoice | If node_id set, skip to playbook/check path | normalized.node_id | Next: CreateSSMHybridActivation or CheckDestinationWorkspaceAvailableBeforePlaybook |
| CreateSSMHybridActivation | Create/verify SSM hybrid activation for WorkSpace | mode, source_account_id, username, etc. | createSsmHybridActivationResult (instance_name) |
| CheckImageExistsInSource | create-workspace-image verify: image exists by name? | image_name, source_account_id | image_id or image_found: false |
| ImageExistsChoice | Image exists → use it; else create from workspace | checkImageExistsResult | Next: SetExistingImageResult or CheckWorkspaceState |
| CheckWorkspaceState | Poll workspace until AVAILABLE; start if STOPPED | workspace_id, source_account_id | ready |
| CreateWorkspaceImage | Create image from source workspace | workspace_id, image_name, mode, source_account_id | image_id |
| CheckSourceImageState | Poll until source image AVAILABLE | image_id, source_account_id | ready |
| ShareImage | Share image to destination account | image_id, destination_account_id, mode | shareResult |
| CopyImage | Copy image into destination account | image_id, destination_account_id, mode, source_region | new_image_id |
| CheckImageState | Poll until copied image AVAILABLE | new_image_id, destination_account_id | ready |
| CreateBundle | Create bundle from image in destination | new_image_id, hardware_type, storage_settings, mode | bundle_id |
| CheckBundleState | Poll until bundle AVAILABLE | bundle_id, destination_account_id | ready |
| LaunchWorkspace | Launch WorkSpace in destination | bundle_id, directory_id, username, running_mode, encryption, etc. | workspace_id |
| CheckWorkspaceAvailableAfterLaunch | Poll launched workspace until AVAILABLE | workspace_id, destination_account_id | ready |
| WaitForSSMRegistration | Fixed 300s wait for SSM registration | — | — |
| TagManagedInstance | Tag SSM managed instance (EndUser, ResearchGroup, etc.) | activation_default_instance_name, tag-* | tagged_instance_ids |
| CheckWorkspaceAvailableBeforePlaybook | Poll workspace AVAILABLE before playbook | workspace_id | ready |
| ApplyAnsiblePlaybook | Apply managed-workspace.yaml to tagged instance | node_id, username, playbook | applyAnsiblePlaybookResult |
| ApplyManagedWorkspacePlaybookExistingWorkspace | Rerun path: apply playbook to existing node_id | node_id, username, playbook | applyAnsiblePlaybookExistingResult |
| PipelineSucceeded / PipelineFailed | Terminal state | — | — |

## Related

- **Contract:** [provision-linux-workspace.yaml](../../contracts/pipelines/provision-linux-workspace.yaml)
- **State machine:** `statemachine/provision_linux_workspace.asl.json`
- **Run:** `./scripts/start_provision_linux_workspace.sh events/<path>/provision-workspace.json`
