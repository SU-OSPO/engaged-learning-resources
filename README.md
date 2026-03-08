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

