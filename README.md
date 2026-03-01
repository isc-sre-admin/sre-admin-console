# SRE Operations Console

Django-based administrative console for AWS Secure Research Enclave (SRE) operational workflows.

## Landing page

The root route (`/`) provides a workflow-oriented landing page for operations engineers:

- **Set up a new enclave** with the `provision-ad-connector` workflow.
- **Provision enclave resources** such as Linux/Windows WorkSpaces and EC2 instances.
- **Deploy software changes** using Ansible playbooks and PowerShell scripts.
- **Monitor pipeline activity** using tabs for currently executing and historical runs, with relative and absolute date filters.
- **Start pipelines directly** from workflow cards and open a contract-driven start screen for each pipeline.

The page currently shows sample pipeline data and UI controls that are ready to be wired to backend APIs.

## Start pipeline execution

The route `/pipelines/<pipeline_name>/start/` renders a shared start-execution screen for all backend pipelines:

- Inputs are generated dynamically from YAML pipeline contracts under `backend/existing-state/contracts/pipelines`.
- Required and optional inputs are shown as separate validated fields.
- A required **research group / enclave** selector auto-populates `destination_account_id` (and `enclave_name` when needed).
- Missing required values show inline validation warnings on submit.
- A successful submit returns an execution confirmation with:
  - execution ARN
  - link to a session-backed execution detail stub (`/pipelines/executions/<execution_id>/`)
  - link back to the landing page so operators can continue other actions while the pipeline runs

Backend start-execution wiring is intentionally stubbed for now; the UI and payload shaping are implemented to match the existing contracts.

## Local development

From `/workspace`:

1. Activate the virtual environment:
  - `source .venv/bin/activate`
2. Run migrations (if needed):
  - `python manage.py migrate`
3. Start the dev server:
  - `python manage.py runserver 0.0.0.0:8000`

## Quality checks

- Run tests: `pytest`
- Run linting: `ruff check .`
- Run SAST: `bandit -r . -c pyproject.toml`
- Run Django checks: `python manage.py check`

