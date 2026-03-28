# Teaching Activities Platform

Django + PostgreSQL app for faculty to browse teaching activities. Profs manage content via admin; faculty search by tag/name and view activity files.

## Setup

```bash
source venv/bin/activate   # activate virtual environment
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Done so far

### Setup & schema
- **Schema design** : ER diagram, SQL schema, indexes
- **Django project** : `config` + `activities` app
- **Models** : Category, Activity, Tag, ActivityTag, Material
- **Migrations** : applied
- **PostgreSQL** : configured, database created
- **.gitignore** : `media/` excluded from version control

### Admin
- **Admin panel** : models registered, tag assignment, activity management
- **File upload** : Material uses FileField, uploads stored in `media/`
- **Validation** : no duplicate tags (case-insensitive), required activity title, material linked to activity

### API
- **Root** : `GET /` — home page (HTML)
- **Activities** : `GET /activities/` (list), `GET /activities/<slug>/` (detail with materials, e.g. `/activities/scavenger-hunt/`)
- **Search & filter** : `?q=` (title, description, tags), `?tag=`, `?category=`
- **Error handling** : 400 (bad request), 404 (not found), 500 (server error) — JSON `{error, status, detail}`
- **Pagination** : `?page=1&limit=20`
- **Sorting** : `?sort=title`, `?sort=-created_at`, etc.
- **Tags** : `GET /tags/`
- **Categories** : `GET /categories/`
- **Materials** : JSON includes `file_open_url` (inline view) and `file_download_url` (attachment); both point at app routes under `/activities/materials/<id>/open/` and `.../download/`

### Media & performance
- **Media serving** : files at `/media/` in development
- **Indexes** : category name, activity created_at, title, category, material_type

### Tests
- **ModelTests** : create category, create tag, tag unique name (DB), activity with category and tags, material linked to activity
- **ActivityListTests** : list returns all activities, search by title/description/tags (`?q=`), filter by tag (`?tag=`), filter by category (`?category=`), pagination (`?page=`, `?limit=`), sort by title (`?sort=title`)
- **ActivityDetailTests** : detail returns activity with materials and slug, 404 for invalid slug (JSON), 400 for invalid category
- **TagListTests** : list returns all tags
- **CategoryListTests** : list returns all categories

### Frontend
- **Django templates** : Syracuse-inspired palette (navy `#0D2D4C`, orange `#F76900`), Source Sans 3, shared layout in `templates/base.html`
- **Home** : `GET /` — landing page (`templates/home.html`) with hero and links into browse
- **Activity list** : filter panel with search, category, tag, sort; **Apply filters** and optional **Clear all filters** when any filter is active; results count; pagination; activity cards with cover image, tags as chips, staggered entrance animation
- **Activity detail** : inline previews where the browser supports the type, plus **Download**; emoji-style icons per material type (`activities/templatetags/activity_icons.py`)
- **UI polish** : nav link underline on hover; button hover shadows; tag chips with hover lift; filter panel uses layered navy/orange gradients and a slow background drift (disabled when `prefers-reduced-motion`); reduced-motion respected across list/detail
- **Responsive** : HTML for browsers, JSON for API requests

#### Why a preview might not show
- **PDF, images, video, plain text** : Served from this app with `Content-Disposition: inline` so they usually preview on the activity page, including on `localhost`, as long as the file exists under `media/`.
- **Word, Excel, PowerPoint, ODF** : Preview uses **Microsoft Office Online** (`view.officeapps.live.com`) in an iframe. That service must **fetch your file’s URL from the public internet** over **HTTPS**, with **no login**. It cannot reach a dev server that only listens on your laptop, so on **`localhost`** the Office embed is **not shown** (you can still **Download**). After deployment to a real HTTPS URL, previews work if the open URL is world-readable.
- **Other file types** : No inline preview; use **Download**.

#### List card images (what we use)
All cover photos are **hotlinked from Unsplash** (`images.unsplash.com`) under the [Unsplash License](https://unsplash.com/license), with `auto=format&fit=crop&w=800&h=600&q=80` for consistent card size.

- **Default** : A fixed pool of **12 education-themed** photos. Each activity gets a **stable** image: `activity.id % 12` picks from that pool (see `activities/tile_images.py`).
- **Optional themed tiles** (same Unsplash source): if title, description, slug, category, or tags match certain phrases, the card uses a dedicated photo instead — e.g. scavenger / treasure / clues → map image; puzzle / jigsaw / riddle → jigsaw image; outdoor / hiking / team-building style phrases → outdoor group image. Copy that mentions **recruitment** / **recruiting** keeps the default pool image so tiles stay predictable.

Attribution: follow Unsplash’s guidelines when sharing; photographer names are listed on each photo’s page at unsplash.com.
