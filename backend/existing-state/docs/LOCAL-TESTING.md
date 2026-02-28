# Local Testing

## Invoking the Lambda

**Locally (no deploy):**

```bash
sam local invoke SreManagementFunction -e events/share-image.json
sam local invoke SreManagementFunction -e events/create-ad-connector.json
```

**Against deployed Lambda:**

```bash
sam remote invoke SreManagementFunction --event-file events/share-image.json --stack-name sre-management
```

Or use the helper scripts:

```bash
./scripts/invoke_lambda.sh events/share-image.json
./scripts/invoke_lambda.sh events/share-image.json sre-management-dev
./scripts/sre-cli events/apply-ansible-playbook.json
```

For `apply-ansible-playbook`, the scripts can print commands to tail CloudWatch logs (destination account). Use `AWS_PROFILE` as needed for the destination account.

## Unit tests and coverage

Install coverage and pytest-cov (e.g. in a venv):

```bash
pip install coverage pytest-cov
```

Run tests:

```bash
pytest tests/unit/ -v
# or
make test
```

With coverage (target ≥ 90%):

```bash
pytest tests/unit/ --cov=app --cov-report=term-missing --cov-fail-under=90
# or
make test-cov
```

HTML report: `pytest tests/unit/ --cov=app --cov-report=html` (output under `htmlcov/`).

## Bandit (SAST)

Run Bandit on `src/`:

```bash
bandit -r src -c pyproject.toml
# or
make bandit
# or
make sast
```

Install: `pip install bandit[toml]`.

## Pre-commit hook

A [pre-commit](https://pre-commit.com/) hook can run tests (with 90% coverage) and Bandit on every commit:

1. Install: `pip install pre-commit coverage pytest-cov bandit[toml]`
2. Install the hook: `pre-commit install`
3. On each `git commit`: pytest (coverage) and bandit run; commit is blocked if either fails.

Run all hooks manually: `pre-commit run --all-files`. Skip once: `git commit --no-verify`.
