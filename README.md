# TeachOrange 🍊

Django + PostgreSQL app for faculty to browse teaching activities (**TeachOrange** branding, domain **teachorange.com**). Profs manage content via admin; faculty register with a **`.edu`** email, then search by tag/name, **preview** supported files in a **new tab**, and download materials.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Create a Django superuser for the admin site: `python manage.py createsuperuser` (use any email you like for local dev).

## Deployment

Production runs on a Hostinger VPS managed by **CloudPanel** (Python site type): nginx
terminates TLS and serves `/static/` from disk, reverse-proxying everything else to **gunicorn**
on port **8090**. The app process is managed by **supervisor**.

| | |
|---|---|
| Site user | `teachorange` |
| App directory | `/home/teachorange/htdocs/www.teachorange.com` |
| Python | 3.12 |
| App port | 8090 |

**Pushing to `main` deploys automatically.** `.github/workflows/deploy.yml` waits for the test
suite to pass, then runs [`deploy.sh`](deploy.sh) on the server over SSH.

### What a deploy does

`deploy.sh` is idempotent and safe to run by hand. In order:

1. Records the current commit so a failure can be undone
2. `git reset --hard origin/main`
3. Installs pinned dependencies
4. **Dumps the database** to `../db-backups/` (keeps the last 10)
5. `manage.py migrate --noinput`
6. `manage.py collectstatic --noinput` — `staticfiles/` is gitignored and must be rebuilt every deploy
7. Restarts gunicorn
8. Polls the site for HTTP 200; on failure, restores the previous commit and exits non-zero

### Required GitHub secrets

Settings → Secrets and variables → Actions:

| Secret | Value |
|---|---|
| `DEPLOY_HOST` | server hostname or IP |
| `DEPLOY_USER` | `teachorange` |
| `DEPLOY_SSH_KEY` | private key whose public half is added in CloudPanel → Sites → Settings → **SSH Keys** |
| `DEPLOY_PATH` | `/home/teachorange/htdocs/www.teachorange.com` |
| `DEPLOY_PORT` | optional, defaults to `22` |

### One-time server setup

1. Generate a deploy keypair locally and add the **public** half in CloudPanel →
   Sites → `www.teachorange.com` → Settings → **SSH Keys** (currently empty). Put the
   **private** half in the `DEPLOY_SSH_KEY` GitHub secret.
2. Confirm the repo is cloned at the app directory with a virtualenv at `.venv`.
3. Set the production environment variables (see [`.env.example`](.env.example)). `DJANGO_DEBUG=0`
   and `DJANGO_SECRET_KEY` are **required** — the app refuses to start in production without a secret.
4. Find the supervisor program name: `sudo supervisorctl status`. If it is not `teachorange`,
   set `APP_SERVICE` in the server environment.
5. Allow the site user to restart it without a password, via `visudo`:
   `teachorange ALL=(root) NOPASSWD: /usr/bin/supervisorctl restart teachorange`

### Rolling back

Code only — `deploy.sh` does this automatically on a failed health check:

```bash
cd <app-dir> && git reset --hard <previous-sha> && ./deploy.sh
```

**Migrations are never rolled back automatically.** Migration `0004_add_activity_slug` is not
safely reversible (raw SQL inside `SeparateDatabaseAndState`, plus a `RunPython` whose reverse is
a no-op), so restoring schema means restoring the dump from `../db-backups/`.

### Gotchas

- **Email fails quietly.** With `DJANGO_DEBUG=0` and no `DJANGO_EMAIL_HOST`/`DJANGO_EMAIL_HOST_USER`,
  the backend falls back to console and password reset plus the contact form return **HTTP 503**
  while the rest of the site looks healthy. The homepage health check will not catch this.
- **`/media/` must stay behind Django.** Uploads are gated by `@login_required` in
  `config/media_serve.py`. An nginx `location /media/` alias would serve them to anonymous users.

## Done so far

### Setup & schema
- **Schema design** : ER diagram, SQL schema, indexes
- **Django project** : `config` + `accounts` + `activities` apps
- **Models** : Category, Activity, Tag, ActivityTag, Material
- **Migrations** : applied
- **PostgreSQL** : configured, database created
- **.gitignore** : `media/` excluded from version control

### Admin
- **Admin panel** : models registered, tag assignment, activity management
- **File upload** : Material has **File** (main download, e.g. Word or PDF) and optional **Preview (PDF)** in admin when the main file is not a PDF (faculty open preview in a new tab); uploads under `media/`
- **Validation** : no duplicate tags (case-insensitive), required activity title, material linked to activity

### Accounts
- **Register** : `GET/POST /accounts/register/`: sign up with a **`.edu`** email (suffixes configurable via `ALLOWED_EMAIL_SUFFIXES` in `config/settings.py`)
- **Login / logout** : `/accounts/login/`, `POST /accounts/logout/`
- **Protected** : Browsing activities, activity detail, and material **open** / **download** require login (redirects to login with `?next=`)

### API
- **Root** : `GET /`: home page (HTML), public
- **Activities** : `GET /activities/` (list), `GET /activities/<slug>/` (detail with materials). **Require login** for HTML and JSON
- **Search & filter** : `?q=` (title, description, tags), `?tag=`, `?category=`
- **Error handling** : 400 (bad request), 404 (not found), 500 (server error). JSON `{error, status, detail}`
- **Pagination** : `?page=1&limit=20`
- **Sorting** : `?sort=title`, `?sort=-created_at`, etc.
- **Tags** : `GET /tags/`
- **Categories** : `GET /categories/`
- **Materials** : JSON includes `file_open_url` (new-tab preview) and `file_download_url` (attachment); both require login and map to `/activities/materials/<id>/open/` and `.../download/`

### Media & performance
- **Media serving** : files at `/media/` in development
- **Indexes** : category name, activity created_at, title, category, material_type

### Tests
- **ModelTests** : create category, create tag, tag unique name (DB), activity with category and tags, material linked to activity
- **ActivityListTests** : authenticated user; list, search (`?q=`), tag/category filters, pagination, sort; anonymous → redirect to login
- **ActivityDetailTests** : authenticated user; detail JSON + slug; anonymous → redirect to login
- **accounts** : `.edu` sign-up validation, register + login
- **TagListTests** : list returns all tags
- **CategoryListTests** : list returns all categories

### Frontend
- **Django templates** : TeachOrange 🍊, navy/orange palette (`#0D2D4C`, `#F76900`), Source Sans 3, shared layout in `templates/base.html`
- **Home** : `GET /`: landing page (`templates/home.html`) with hero and links into browse
- **Activity list** : filter panel with search, category, tag, sort; **Apply filters** and optional **Clear all filters** when any filter is active; results count; pagination; activity cards with cover image, tags as chips, staggered entrance animation
- **Activity detail** : **Preview** opens PDF/image/video/text in a **new tab**; no embedded viewer on the page; **Download** for the main file; emoji-style icons per material type (`activities/templatetags/activity_icons.py`)
- **UI polish** : nav link underline on hover; button hover shadows; tag chips with hover lift; filter panel uses layered navy/orange gradients and a slow background drift (disabled when `prefers-reduced-motion`); reduced-motion respected across list/detail
- **Responsive** : HTML for browsers, JSON for API requests

#### List card images (what we use)
All cover photos are **hotlinked from Unsplash** (`images.unsplash.com`) under the [Unsplash License](https://unsplash.com/license), with `auto=format&fit=crop&w=800&h=600&q=80` for consistent card size.

- **Default** : A fixed pool of **12 education-themed** photos. Each activity gets a **stable** image: `activity.id % 12` picks from that pool (see `activities/tile_images.py`).
- **Optional themed tiles** (same Unsplash source): if title, description, slug, category, or tags match certain phrases, the card uses a dedicated photo instead (e.g. scavenger / treasure / clues → map image; puzzle / jigsaw / riddle → jigsaw image; outdoor / hiking / team-building style phrases → outdoor group image). Copy that mentions **recruitment** / **recruiting** keeps the default pool image so tiles stay predictable.

Attribution: follow Unsplash’s guidelines when sharing; photographer names are listed on each photo’s page at unsplash.com.
