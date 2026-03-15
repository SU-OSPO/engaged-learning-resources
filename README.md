# Teaching Activities Platform

Django + PostgreSQL app for faculty to browse teaching activities. Profs manage content via admin; faculty search by tag/name and view activity files.

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
- **Root** : `/` redirects to `/activities/`
- **Activities** : `GET /activities/` (list), `GET /activities/<id>/` (detail with materials)
- **Search & filter** : `?q=`, `?tag=`, `?category=`
- **Pagination** : `?page=1&limit=20`
- **Sorting** : `?sort=title`, `?sort=-created_at`, etc.
- **Tags** : `GET /tags/`
- **Categories** : `GET /categories/`
- **Materials** : `file_url` in activity detail returns absolute URLs for download

### Media & performance
- **Media serving** : files at `/media/` in development
- **Indexes** : category name, activity created_at, title, category, material_type

### Tests
- **ModelTests** : create category, create tag, tag unique name (DB), activity with category and tags, material linked to activity
- **ActivityListTests** : list returns all activities, search by title (`?q=`), filter by tag (`?tag=`), filter by category (`?category=`), pagination (`?page=`, `?limit=`), sort by title (`?sort=title`)
- **ActivityDetailTests** : detail returns activity with materials, 404 for invalid id
- **TagListTests** : list returns all tags
- **CategoryListTests** : list returns all categories

