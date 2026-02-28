# Summary of Useful Commands

| Action | Command |
|--------|---------|
| Build | `sam build --use-container` |
| Deploy SAM app | `sam deploy` |
| Run all tests | `make test` or `pytest tests/unit/ -v` |
| Run tests + coverage (≥90%) | `make test-cov` or `pytest tests/unit/ --cov=app --cov-report=term-missing --cov-fail-under=90` |
| Run Bandit (SAST) | `make bandit` or `make sast` or `bandit -r src -c pyproject.toml` |
| Install pre-commit hook | `pre-commit install` (after `pip install pre-commit coverage pytest-cov bandit[toml]`) |
| Invoke Lambda locally | `sam local invoke SreManagementFunction -e events/<event>.json` |
| Invoke deployed Lambda | `sam remote invoke SreManagementFunction --event-file events/<event>.json --stack-name sre-management` or `./scripts/invoke_lambda.sh <event-file> [stack-name]` or `./scripts/sre-cli <event-file> [stack-name]` |
| Start provision-linux-workspace | `./scripts/start_provision_linux_workspace.sh <event-file> [stack-name]` or `./scripts/sre-cli provision-linux-workspace <event-file> [stack-name] [--wait]` |
| See failed step (provision-linux-workspace) | `./scripts/get_provision_linux_workspace_failure.sh <execution-arn>` |
| Start provision-windows-workspace | `./scripts/sre-cli provision-windows-workspace <event-file> [stack-name] [--wait]` |
| Start provision-ad-connector | `./scripts/start_provision_ad_connector.sh <event-file> [stack-name]` or `./scripts/sre-cli provision-ad-connector <event-file> [stack-name] [--wait]` |
| See failed step (provision-ad-connector) | `./scripts/get_provision_ad_connector_failure.sh <execution-arn>` |
| Start provision-ec2-instance | `./scripts/sre-cli provision-ec2-instance <event-file> [stack-name] [--wait]` |
| Deploy role to destinations | `python cloudformation/deploy.py --profile <profile>` |
| Sync playbooks to S3 | `make sync-playbooks` |
| Sanitize output | `python scripts/sanitize.py --file <file>` or `python scripts/sanitize.py "<string>"` |
