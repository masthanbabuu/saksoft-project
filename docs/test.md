# Test Document

Audience: Developers and QA engineers.

## Commands
    uv run python -m pytest -q
    uv run ruff check app tests
    uv run ruff format --check app tests
    uv run pyright app tests
    uv run bandit -r app
    uv run python -m pip_audit

## Verified results
- Pytest: 64 passed.
- Ruff: passed.
- Pyright: zero errors.
- Bandit: zero issues.
- Pip-audit: no known vulnerabilities.
- Semgrep: zero findings.
- Gitleaks: no leaks.

## Coverage areas
- Configuration validation.
- Health and readiness.
- Answering and knowledge retrieval.
- Password security.
- Upload validation and security controls.
- Log analyser and word statistics.

## Container security
117 findings reduced to 53.
Zero remaining CRITICAL findings.
Zero fixable HIGH or CRITICAL findings in Trivy.

AI evaluation metrics and clean checkout verification
remain pending.
