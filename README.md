# TeachOrange 🍊

Django + PostgreSQL app for faculty to browse teaching activities (**TeachOrange** branding, domain **teachorange.com**). Profs manage content via admin; faculty register with a **`.edu`** email, then search by tag/name, **preview** supported files in a **new tab**, and download materials.

## Setup

```bash
source venv/bin/activate   # activate virtual environment
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Create a Django superuser for the admin site: `python manage.py createsuperuser` (use any email you like for local dev).

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
