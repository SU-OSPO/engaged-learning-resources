# Development

Getting TeachOrange running locally, and the things worth knowing once it is.

## Requirements

- **Python 3.12** (production pins 3.12.8 — see `runtime.txt`)
- **PostgreSQL 16**. There is no SQLite fallback: `config/settings.py` always uses
  the `postgresql` backend unless `DATABASE_URL` says otherwise, and the migrations
  have been written against Postgres.

On macOS:

```bash
brew install postgresql@16
brew services start postgresql@16
createdb teaching_activities
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then edit - at minimum set the database values
python manage.py migrate
python manage.py runserver
```

The app is then at <http://127.0.0.1:8000>.

> Use **one** hostname consistently — `localhost` *or* `127.0.0.1`, not both.
> Mixing them breaks CSRF cookies, because the cookie is scoped to the host that set it.

### Configuration

Every environment variable is listed in [configuration.md](configuration.md).
Locally, `.env` is loaded automatically by `python-dotenv` and is gitignored.

Note `DJANGO_DEBUG` defaults to **`1`**, so a bare `manage.py runserver` with no
`.env` runs in debug mode. That is intentional for development and is also why the
test suite must not run with `DJANGO_DEBUG=0` (see **Testing** below).

## Demo data

```bash
python scripts/seed_demo.py
```

Creates 6 activities, 12 tags, 5 categories and 10 materials, including small
generated PDFs so the preview and download paths are exercisable. It **clears
existing activity data first**, so never point it at production.

To reach `/admin/`:

```bash
python manage.py createsuperuser
```

Any email works locally; the `.edu` rule applies to the public sign-up form, not to
`createsuperuser`.

## Testing

```bash
python manage.py test                      # all 47
python manage.py test activities accounts  # by app
python manage.py test activities.tests.ContactFormTests.test_valid_submission
```

Every test subclasses `django.test.TestCase` and needs a **real PostgreSQL server**;
the runner creates and drops `test_teaching_activities`, so the database user needs
`CREATEDB`. No test touches the network — email is exercised through the `locmem`
backend and SMTP failures are simulated with `mock.patch`.

> **Do not run the tests with `DJANGO_DEBUG=0`.** `settings.py` turns on
> `SECURE_SSL_REDIRECT` whenever `DEBUG` is false, so the test client receives a
> `301` to https instead of reaching any view, and roughly two thirds of the suite
> fails with confusing assertion errors. CI sets `DJANGO_DEBUG=1` for the test step
> and `0` only for `check --deploy`, for exactly this reason.

### What CI runs

`.github/workflows/ci.yml`, on every pull request and as a reusable workflow called
by the deploy:

1. `python manage.py test` against a `postgres:16` service container
2. `python manage.py check --deploy --fail-level ERROR`

The deploy check fails only on errors, not warnings. It still reports
`SECURE_HSTS_INCLUDE_SUBDOMAINS` (W005) and `SECURE_HSTS_PRELOAD` (W021) — those
are deliberate decisions about the domain, not things CI should force.

## Project layout

```
config/           settings, root urls, wsgi/asgi, protected media, error helpers
accounts/         registration, login, password reset (no models)
activities/       models, views, admin, templatetags, tests
templates/        all HTML; each page carries its own CSS in {% block extra_css %}
static/           source static files (collectstatic output goes to staticfiles/)
scripts/          seed_demo.py and a presentation generator
docs/             this documentation
deploy.sh         production deploy script - see docs/operations.md
```

## Conventions

- **CSS lives in the template** that uses it, inside `{% block extra_css %}`. Shared
  colours are CSS custom properties on `:root` in `templates/base.html`.
- **Client-side validation mirrors the server and is never stricter.** It exists to
  give faster feedback; the server is the authority. Before adding a rule, check the
  corresponding form — for instance the contact form accepts any email, while login
  and registration require `.edu`.
- **Migrations are forward-only in practice.** `0004_add_activity_slug` mixes raw
  SQL with a `RunPython` whose reverse is a no-op, so it cannot be cleanly reversed.
  Write new migrations assuming rollback means restoring a database dump.
- **New pages** need a template, a view in `activities/views.py`, a route in
  `config/urls.py`, and a nav entry in `templates/base.html`.

## Common problems

| Symptom | Cause |
|---|---|
| `connection refused` on 5432 | Postgres is not running — `brew services start postgresql@16` |
| `role "..." does not exist` | `POSTGRES_USER` is unset or wrong; it has no safe default |
| Dozens of tests fail with `301 != 200` | Tests running with `DJANGO_DEBUG=0` |
| `ImproperlyConfigured: DJANGO_SECRET_KEY must be set` | Running with `DEBUG=0` and no key — intentional, see configuration.md |
| CSRF failures when logging in | Mixing `localhost` and `127.0.0.1` |
| Styles or favicon missing after deploy | `collectstatic` did not run |
