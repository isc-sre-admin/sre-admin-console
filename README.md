# SRE Operations Console

Django-based administrative console for AWS Secure Research Enclave (SRE) operational workflows.

## Landing page

The root route (`/`) provides a workflow-oriented landing page for operations engineers:

- **Set up a new enclave** with the `provision-ad-connector` workflow.
- **Provision enclave resources** such as Linux/Windows WorkSpaces and EC2 instances.
- **Deploy software changes** using Ansible playbooks and PowerShell scripts.
- **Monitor pipeline activity** using tabs for currently executing and historical runs, with relative and absolute date filters.

The page currently shows sample pipeline data and UI controls that are ready to be wired to backend APIs.

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
