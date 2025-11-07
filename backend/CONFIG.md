# Backend Configuration & Secrets

This document lists the environment variables used by the Tapin backend, recommended defaults for local development, and guidance for storing secrets in CI (GitHub Actions).

## Required / important environment variables

- `SECRET_KEY` — Flask secret key. Defaults to a dev value in code, but _must_ be set to a strong secret in production.
- `JWT_SECRET_KEY` — Key used to sign JWTs. Defaults to `SECRET_KEY` when not provided but should be unique in production.
- `SECURITY_PASSWORD_SALT` — Salt for password reset tokens. Replace the dev value in production.

Optional but recommended:
- `SQLALCHEMY_DATABASE_URI` — Connection string for the database. Defaults to `sqlite:///backend/data.db`.
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `SMTP_USE_TLS` — Mail server settings for sending password reset emails.

## Local development

1. Copy `.env.sample` to `.env` in the repository root and edit values.
2. Install dev dependencies: `pip install -r backend/requirements.txt`.
3. Start the app (from repo root):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
python backend/app.py
```

The app will automatically load `.env` (if `python-dotenv` is installed) and pick up values.

## GitHub Actions / CI

Store secrets in your repository or organization settings (`Settings > Secrets and variables > Actions`). Name them as follows (example):

- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `SECURITY_PASSWORD_SALT`
- `SMTP_USER`, `SMTP_PASS` (if you need SMTP in CI)

In workflow files, reference secrets via `${{ secrets.SECRET_KEY }}`. Example excerpt for `.github/workflows/backend-tests.yml`:

```yaml
env:
  SECRET_KEY: ${{ secrets.SECRET_KEY }}
  JWT_SECRET_KEY: ${{ secrets.JWT_SECRET_KEY }}
  SECURITY_PASSWORD_SALT: ${{ secrets.SECURITY_PASSWORD_SALT }}
  SQLALCHEMY_DATABASE_URI: sqlite:///backend/data.db
```

Notes:
- Do not commit real secrets into the repository.
- For production, prefer a managed secret store (cloud provider secrets, HashiCorp Vault, etc.).
