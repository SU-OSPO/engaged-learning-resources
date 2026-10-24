# Configuration

Every environment variable TeachOrange reads, where it is read, and what happens
if it is missing.

- **Locally**: put these in `.env` at the repo root (gitignored, loaded by
  `python-dotenv`). Start from [`.env.example`](../.env.example).
- **In production**: they live in `.env` in the app directory on the server, owned
  by the site user and never committed.

All of them are read in `config/settings.py` unless noted. Variables marked
**SECRET** must never be committed or pasted into chat.

## Core

| Variable | Default | Notes |
|---|---|---|
| `DJANGO_SECRET_KEY` | *(dev only)* | **SECRET.** **Required when `DJANGO_DEBUG=0`** — the app raises `ImproperlyConfigured` and refuses to start. In debug it falls back to a well-known development key. |
| `DJANGO_DEBUG` | `1` | Truthy set: `1`, `true`, `yes`, `on`. **Must be `0` in production.** |
| `DJANGO_ALLOWED_HOSTS` | `127.0.0.1,localhost` | Comma-separated. Production: `teachorange.com,www.teachorange.com` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `http://127.0.0.1:8000,http://localhost:8000` | Comma-separated, **scheme required**. Production: `https://teachorange.com,https://www.teachorange.com` |

> The secret key deliberately fails loudly rather than falling back. With automated
> deploys, a silent fallback would ship a key that is published in this repository,
> making every session cookie and CSRF token forgeable with no error anywhere.
> Generate one with:
> ```
> python -c 'from django.core.management.utils import get_random_secret_key as k; print(k())'
> ```

### Turning off DEBUG changes behaviour

When `DEBUG` is false, `settings.py` also enables `SECURE_SSL_REDIRECT`,
`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_HSTS_SECONDS` and
`SECURE_PROXY_SSL_HEADER`.

> ⚠️ **Never run the test suite with `DJANGO_DEBUG=0`.** `SECURE_SSL_REDIRECT` makes
> the test client receive a `301` to https instead of reaching any view, and most of
> the suite fails with misleading assertion errors. CI sets `DJANGO_DEBUG=1` for the
> test step and `0` only for `check --deploy`.

## Database

Either set `DATABASE_URL`, **or** the discrete `POSTGRES_*` values. `DATABASE_URL`
wins when present.

| Variable | Default | Notes |
|---|---|---|
| `DATABASE_URL` | *(unset)* | **SECRET** (contains credentials). Parsed by `dj-database-url`. |
| `POSTGRES_DB` | `teaching_activities` | |
| `POSTGRES_USER` | `$USER` | No safe default — set it explicitly |
| `POSTGRES_PASSWORD` | `""` | **SECRET** |
| `POSTGRES_HOST` | `localhost` | |
| `POSTGRES_PORT` | `5432` | |

There is no SQLite fallback. The backend is always `postgresql` unless
`DATABASE_URL` says otherwise, and the migrations assume Postgres.

## Email

| Variable | Default | Notes |
|---|---|---|
| `DJANGO_EMAIL_HOST` | `""` | Selects the SMTP backend together with `..._HOST_USER` |
| `DJANGO_EMAIL_PORT` | `587` | Cast with `int()` — a non-numeric value crashes at import |
| `DJANGO_EMAIL_HOST_USER` | `""` | For Mailjet this is the **API key** |
| `DJANGO_EMAIL_HOST_PASSWORD` | `""` | **SECRET.** For Mailjet, the **secret key** |
| `DJANGO_EMAIL_USE_TLS` | `1` | |
| `DJANGO_EMAIL_USE_SSL` | `0` | If truthy **and `..._USE_TLS` is absent from the environment**, TLS is forced off |
| `DJANGO_DEFAULT_FROM_EMAIL` | `TeachOrange <noreply@teachorange.local>` | The visible From address |
| `DJANGO_CONTACT_EMAIL` | `mdbrockw@syr.edu` | Where contact-form submissions are delivered |
| `DJANGO_EMAIL_BACKEND` | *(auto)* | Overrides the selection below. Rarely needed |

### How the backend is chosen

1. `DJANGO_EMAIL_BACKEND` set → used verbatim
2. Else if **both** `DJANGO_EMAIL_HOST` and `DJANGO_EMAIL_HOST_USER` are non-empty → SMTP
3. Else → **console**

> ⚠️ Case 3 is the trap. With `DEBUG=0` and no SMTP settings, the backend falls back
> to console and `email_delivery_available()` (`config/email_status.py`) returns
> False, so **password reset and the contact form return HTTP 503** while every other
> page looks healthy. A homepage health check will not notice.

`DJANGO_CONTACT_EMAIL` is unset in production today, so the hardcoded default
applies — a personal address baked into a public repository. Set it in the server
`.env`.

## Inert variables

| Variable | Why it is still read |
|---|---|
| `RENDER_EXTERNAL_HOSTNAME` | Appended to `ALLOWED_HOSTS` when running on Render |
| `RENDER_EXTERNAL_URL` | Appended to `CSRF_TRUSTED_ORIGINS` when running on Render |

The site runs on a Hostinger VPS, not Render, so these are never set. They are
harmless, but do not rely on them — set `DJANGO_ALLOWED_HOSTS` and
`DJANGO_CSRF_TRUSTED_ORIGINS` explicitly.

## CI

`.github/workflows/ci.yml` sets its own values. Two are deliberate:

- `DJANGO_SECRET_KEY` is a long throwaway, specifically so `check --deploy` does not
  report `security.W009` about a value that only exists in CI.
- `DJANGO_DEBUG` is **per step**: `1` for tests, `0` for `check --deploy`.

## Deployment secrets

Not read by Django — used by `.github/workflows/deploy.yml`. See
[operations.md](operations.md#github-secrets).

`DEPLOY_HOST` · `DEPLOY_USER` · `DEPLOY_PATH` · `DEPLOY_SSH_KEY` *(SECRET)* · `DEPLOY_PORT`
