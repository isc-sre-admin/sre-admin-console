# Provision Windows WorkSpace Pipeline

## Summary

The **provision-windows-workspace** Step Functions pipeline mirrors the Linux WorkSpace flow: normalize input, optionally create image from source workspace, share and copy image, create bundle, launch Windows WorkSpace, wait for SSM registration, and tag the managed instance. After tagging, if the event includes a non-empty **scripts** array (e.g. PowerShell scripts like RStudio), the pipeline runs **configure-windows-workspace** on the node; otherwise it succeeds without running scripts.

## Pipeline Steps

| Step | Function | Inputs | Outputs |
| ---- | -------- | ------ | ------- |
| NormalizeInput | Merge pipeline input with config (includes scripts) | pipeline_input | normalized |
| ExtractNormalized | Pass normalized payload into state | normalized.Payload.normalized | — |
| RerunPlaybookChoice | If node_id set, skip to destination-workspace/scripts path | normalized.node_id | Next: CreateSSMHybridActivation or CheckDestinationWorkspaceAvailableBeforePlaybook |
| CreateSSMHybridActivation | Create/verify SSM hybrid activation | mode, source_account_id, username | createSsmHybridActivationResult |
| CheckImageExistsInSource | create-workspace-image verify: image exists? | image_name, source_account_id | image_id or image_found: false |
| CheckWorkspaceState | Poll workspace until AVAILABLE | workspace_id, source_account_id | ready |
| CreateWorkspaceImage | Create image from source workspace | workspace_id, image_name, mode | image_id |
| CheckSourceImageState | Poll until source image AVAILABLE | image_id | ready |
| ShareImage | Share image to destination | image_id, destination_account_id | shareResult |
| CopyImage | Copy image into destination | image_id, destination_account_id | new_image_id |
| CheckImageState | Poll until copied image AVAILABLE | new_image_id | ready |
| CreateBundle | Create bundle from image | new_image_id, hardware_type, storage_settings | bundle_id |
| CheckBundleState | Poll until bundle AVAILABLE | bundle_id | ready |
| LaunchWorkspace | Launch Windows WorkSpace | bundle_id, directory_id, username, encryption, etc. | workspace_id |
| CheckWorkspaceAvailableAfterLaunch | Poll until workspace AVAILABLE | workspace_id | ready |
| WaitForSSMRegistration | 300s wait for SSM registration | — | — |
| TagManagedInstance | Tag SSM managed instance | activation_default_instance_name, tag-* | tagged_instance_ids |
| ApplyPowerShellScriptsChoice | If tagged_instance_ids[0] and scripts[0] present → run scripts | tagged_instance_ids, normalized.scripts | Next: CheckWorkspaceAvailableBeforeScripts or PipelineSucceeded |
| ConfigureWindowsWorkspace | Run PowerShell scripts on Windows WorkSpace via SSM | node_id, scripts, node_name | configureWindowsWorkspaceResult |
| CheckDestinationWorkspaceAvailableBeforePlaybook | Rerun: poll destination workspace AVAILABLE | destination_workspace_id | ready |
| CheckSSMRegistrationExisting | Rerun: check node_id registered in SSM | node_id | ready |
| ConfigureWindowsWorkspaceExisting | Rerun: run scripts on existing node_id | node_id, scripts | configureWindowsWorkspaceExistingResult |
| PipelineSucceeded / PipelineFailed | Terminal state | — | — |

## Related

- **Contract:** [provision-windows-workspace.yaml](../../contracts/pipelines/provision-windows-workspace.yaml)
- **State machine:** `statemachine/provision_windows_workspace.asl.json`
- **Run:** `aws stepfunctions start-execution --state-machine-arn <ProvisionWindowsWorkspaceStateMachineArn> --input file://events/example/provision-windows-workspace.json`
