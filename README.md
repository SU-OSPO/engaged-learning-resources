# Teaching Activities Platform

Django + PostgreSQL app for faculty to browse teaching activities. Profs manage content via admin; faculty search by tag/name and view activity files.

## Done so far

- **Schema design** : ER diagram, SQL schema, indexes
- **Django project** : `config` + `activities` app
- **Models** : Category, Activity, Tag, ActivityTag, Material
- **Migrations** : applied
- **PostgreSQL** : configured, database created
- **Admin panel** : models registered, tag assignment, activity management
- **File upload** : Material uses FileField, uploads stored in `media/`
- **Media serving** : files served at `/media/` in development
- **.gitignore** : `media/` excluded from version control
- **Search & filter** : search by title, filter by tag, filter by category
- **API endpoints** : `GET /activities/` (list), `GET /activities/<id>/` (detail)
- **Pagination** : `?page=1&limit=20`
- **Sorting** : `?sort=title`, `?sort=-created_at`, etc.
- **Tag list** : `GET /tags/`
- **Category list** : `GET /categories/`
- **File URLs** : material `file_url` returns absolute URLs for download

