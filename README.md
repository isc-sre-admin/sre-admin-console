# SRE Operations Console

Django-based administrative console for AWS Secure Research Enclave (SRE) operational workflows.

## Application shell and navigation

Authenticated pages now use a consistent three-region shell:

- **Left navigation pane** with links for Workflows, Endpoint Management, Plan of Actions and Milestones, and grouped Operations.
- **Center content pane** where workflow forms, endpoint pages, operation forms, and POAM pages render.
- **Right contextual pane pattern** for feature-specific side panels, starting with Vulnerability Management on enclave and endpoint detail pages.

On small screens, the left navigation can be expanded/collapsed using the **Nav** button in the header.

## Landing page

The root route (`/`) provides a workflow-oriented landing page for operations engineers:

- **Set up a new enclave** with the `provision-ad-connector` workflow.
- **Provision enclave resources** such as Linux/Windows WorkSpaces and EC2 instances.
- **Deploy software changes** using Ansible playbooks and PowerShell scripts.
- **Monitor pipeline activity** using tabs for currently executing and historical runs, with relative and absolute date filters. The list-pipeline-executions query is driven by `landing/events/list-pipeline-executions.json` (pipeline IDs, optional status_filter and max_results). The tables refresh on page load and then periodically (every `LANDING_PIPELINE_POLL_INTERVAL_SECONDS` seconds, default 60; set to 0 in settings to disable polling).
- **Start pipelines directly** from workflow cards and open a contract-driven start screen for each pipeline.
- **Open execution details** by clicking a pipeline label in the "Currently executing" or "Execution history" table; each label links to the pipeline execution detail screen.

The page shows pipeline data from the backend (mock or real). When the real backend is configured, the pipeline activity tables stay up to date via the configurable poll interval.

## Quick operations

Short-running operations that need minimal input are available from an **Operations** dropdown in the header (when signed in). Each operation opens in a modal dialog.

- **Unlock user**: Enter a username and submit to run the unlock-user operation. The request is sent to `/operations/unlock-user/execute/` and returns JSON; the modal shows success or error. Backend invocation is stubbed until the API is available.

Quick operations are defined by YAML contracts under `backend/proposed-changes/operations/` (e.g. `unlock-user.yaml`). The console loads these and exposes them in the nav; the first supported operation is **Unlock user**.

In addition to quick actions, the left sidebar includes an **Operations** section with grouped operation links that open contract-driven full-page operation forms at `/operations/<operation_id>/`.

## Endpoint management

The route `/endpoints/` provides enclave drill-down and endpoint management screens:

- **Endpoints index**: List enclaves (research group, enclave, destination account) and open endpoint inventory by enclave.
- **Enclave detail**: Show EC2 and WorkSpace endpoints for the enclave, including region and SSM registration status.
- **Endpoint detail**: Show Session Manager connect guidance plus contract-driven node actions:
  - `apply-ansible-playbook`
  - `apply-playbook-to-node`
- **Contextual Vulnerability Management pane**:
  - Available on enclave detail and endpoint detail pages.
  - Toggled by a vertical **Vulnerability Management** control on the right edge of the main content.
  - Persists open/closed preference with local storage keys:
    - `sreConsole.vulnPaneOpen.enclave`
    - `sreConsole.vulnPaneOpen.endpoint`
- **Provisioning links**: Endpoint detail includes quick links to start the provision Linux/Windows WorkSpace and EC2 pipelines with `?enclave=<destination_account_id>` prefilled.

Endpoint inventory data is requested via the proposed `list-endpoints` query contract. If the backend query is not implemented yet, the page shows sample rows so the UI remains usable for prototyping.

## Plan of Actions and Milestones (POAM)

The route `/poam/` provides a POAM management surface:

- **POAM list view** with Open/Closed/All filters and a table of entries.
- **Add/Edit POAM entry** form at `/poam/new/` and `/poam/<poam_id>/<status>/`.
- Form sections are organized into Identification, Context, Timeline, and Details.
- Submission invokes the existing `create-poam-entry` operation contract payload shape (`operation`, `mode`, `poam_id`, `status`, and optional fields).

Until a dedicated POAM list query exists in the backend, the list view is backed by sample/session data for prototyping.

## Start pipeline execution

The route `/pipelines/<pipeline_id>/start/` renders a shared start-execution screen for all backend pipelines:

- Inputs are generated dynamically from YAML pipeline contracts under `backend/existing-state/contracts/pipelines`.
- Required and optional inputs are shown as separate validated fields.
- A required **research group / enclave** selector auto-populates `destination_account_id` (and `enclave_name` when needed).
- Missing required values show inline validation warnings on submit.
- A successful submit returns an execution confirmation with:
  - execution ARN
  - link to the pipeline execution detail screen (`/pipelines/executions/<execution_id>/`)
  - link back to the landing page so operators can continue other actions while the pipeline runs

Backend start-execution wiring is intentionally stubbed for now; the UI and payload shaping are implemented to match the existing contracts.

## Pipeline execution detail

The route `/pipelines/executions/<execution_id>/` shows a high-level view of a single pipeline run:

- **Execution header**: execution ID, pipeline name, enclave, started/stopped time, status.
- **Pipeline steps**: list of steps derived from the pipeline contract’s `component_operations`; each step shows status (pending, running, succeeded, failed).
- **Step detail**: clicking a step expands to show its input and output (JSON). For a failed step, the root cause is shown and the row is highlighted in red.
- **Dynamic updates**: while the execution is running, the page polls the same URL with `?format=json` every 10 seconds and reloads when the status becomes Succeeded or Failed.

Execution data is resolved from the session (for runs started in the current browser session) or from sample active/recent execution data. When backend APIs are available, the view can be wired to the proposed queries `get-pipeline-execution-detail` and `get-pipeline-step-logs` (see `backend/proposed-changes/queries/`).

## Authentication

The console requires users to sign in before using the landing page, pipeline start, or execution detail screens.

- **Sign in**: Unauthenticated users are redirected to `/accounts/login/`. After signing in, they are sent back to the page they requested (or the home page).
- **Sign out**: Authenticated users see their username and a "Sign out" link in the header; signing out redirects to the home page (login screen for anonymous users).
- **Backend**: Authentication uses Django’s built-in session-based auth. Integration with Amazon Cognito is planned for a later feature; the UI is structured so that the auth backend can be swapped without changing the sign-in/sign-out experience.

Development superuser (if created): username `admin`, password `admin`.

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

