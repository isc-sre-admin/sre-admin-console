# CI/CD (CodePipeline)

CI/CD for the SAM application is defined with **AWS CDK** in the `cdk/` directory. Two CodePipelines can be deployed:

- **Dev pipeline** (e.g. SRE Sandbox): Triggered by pushes to **develop**. Stages: Source (GitHub via CodeStar Connections) → BuildAndTest (unit tests, SAST, `sam build`) → Deploy (`sam deploy --config-env dev`). Stack: `sre-management-dev`.
- **Prod pipeline** (e.g. SRE Shared Services): Triggered by pushes to **main**. Stages: Source → BuildAndTest → **Manual Approval** → Deploy (`sam deploy --config-env prod`). Stack: `sre-management`.

## Prerequisites

1. **CodeStar connection** in each target account: Create a CodeStar connection to your GitHub org/repo; note the connection ARN per account.
2. **CDK bootstrap** (once per account/region):
   ```bash
   cd cdk
   pip install -r requirements.txt
   cdk bootstrap aws://ACCOUNT_ID/REGION
   ```

## Deploying the pipeline stacks

From `cdk/`, pass GitHub owner, repo name, and CodeStar connection ARN (use the connection ARN for the **same account** you are deploying to):

```bash
cdk synth -c githubOwner=YOUR_ORG -c githubRepo=sre-management -c codestarConnectionArn=arn:aws:codestar-connections:...
cdk deploy SreManagementPipelineDevStack -c githubOwner=... -c githubRepo=sre-management -c codestarConnectionArn=... --require-approval never
cdk deploy SreManagementPipelineProdStack -c ... --require-approval never
```

You can set context in `cdk.json` under `"context"` to avoid passing `-c` every time.

## Branch behavior

- **develop** → Dev pipeline: BuildAndTest and Deploy run automatically.
- **main** → Prod pipeline: BuildAndTest runs, then **Manual Approval** in CodePipeline; after approval, Deploy runs.
