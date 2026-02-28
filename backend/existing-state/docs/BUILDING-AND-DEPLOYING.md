# Building and Deploying

## Building

From the project root:

```bash
sam build --use-container
```

This builds the Lambda container image and outputs artifacts under `.aws-sam/`. Playbooks under `src/assets/playbooks/` are included in the image. **If you changed playbooks or other bundled files**, Docker may use cached layers; bump the `PLAYBOOKS_CACHEBUST` build arg in `template.yaml` (e.g. `"1"` → `"2"`), then run `sam build --use-container` again and deploy.

## Deploying the SAM application

**First-time deploy:**

```bash
sam deploy --guided
```

Provide stack name (e.g. `sre-management`), region, and confirm creation of IAM resources. Configuration is saved in `samconfig.toml`.

**Subsequent deploys:**

```bash
sam deploy
```

**Environments:** Use `--config-env`:

- **prod** (default): `stack_name = "sre-management"`.
- **dev**: `stack_name = "sre-management-dev"`. Use a profile that targets the account in `src/config/config-dev.yaml`:
  ```bash
  sam build && sam deploy --config-env dev
  ```
  On first dev deploy: `sam deploy --guided --config-env dev`.

## Deploying SystemManagementRole to destination accounts

The Lambda assumes **SystemManagementVerifierRole** or **SystemManagementModifierRole** in each destination account. Deploy **SystemManagementRoleStack** into every destination account using `cloudformation/`:

1. From a management account (or account that can assume `AWSControlTowerExecution` in member accounts):
   ```bash
   python cloudformation/deploy.py --profile <your-org-management-profile>
   ```
   This deploys the stack to all configured accounts.
2. To target specific accounts (by friendly name):
   ```bash
   python cloudformation/deploy.py --profile <profile> pngc acad ftdc-genomics
   ```
3. Ensure `cloudformation/deploy.py` uses the correct `SHARED_SERVICES_ACCOUNT_ID` for your environment.

**If `register-workspace-directory` returns AccessDeniedException:** The RegisterWorkspaceDirectory API is often denied for assumed roles. **Workaround:** In the destination account, open WorkSpaces → Directories, select the directory, choose the two subnets, and click Register (e.g. while assuming SystemManagementModifierRole). Then re-run the operation or pipeline; it will see the directory as already registered. For full debugging (CloudTrail, permissions boundary, SCP, testing from destination account, console vs API), see the top-level README or the version of this section in git history before the docs reorganization.
