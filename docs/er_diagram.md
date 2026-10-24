# Entity-Relationship Diagram

## Teaching Activities Platform : Database Schema

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           ENTITY-RELATIONSHIP DIAGRAM                            │
└─────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│      Category         │
├──────────────────────┤
│ PK  id                │
│     name              │
│     description       │
└──────────┬───────────┘
           │
           │ 1
           │
           │ has many
           │
           │ N
           ▼
┌──────────────────────┐         ┌──────────────────────┐
│      Activity         │         │    ActivityTag        │
├──────────────────────┤         ├──────────────────────┤
│ PK  id                │◄────────│ PK  id                │
│ UQ  slug              │    N    │ FK  activity_id       │
│ FK  category_id       │────────►│ FK  tag_id            │
│     title             │    N    └──────────┬───────────┘
│     description       │
│     created_at        │                    │
│     updated_at        │                    │ N
└──────────┬───────────┘                    │
           │                                │
           │ 1                              │ belongs to
           │                                │
           │ has many                       │ 1
           │                                ▼
           │ N                    ┌──────────────────────┐
           ▼                      │        Tag           │
┌──────────────────────┐         ├──────────────────────┤
│      Material         │         │ PK  id                │
├──────────────────────┤         │     name (unique)     │
│ PK  id                │         └──────────────────────┘
│ FK  activity_id       │
│     title             │
│     file_path         │
│     material_type     │
│     uploaded_at       │
└──────────────────────┘

material_type: ENUM('worksheet', 'instructions', 'example', 'video')
```

## Relationships Summary

| From       | To         | Cardinality | Description                          |
|------------|------------|-------------|--------------------------------------|
| Category   | Activity   | 1 : N       | One category groups many activities   |
| Activity   | Material   | 1 : N       | One activity has many materials       |
| Activity   | Tag        | N : N       | Activities and tags are many-to-many via ActivityTag |
| ActivityTag| Activity   | N : 1       | Many activity-tag pairs per activity  |
| ActivityTag| Tag        | N : 1       | Many activity-tag pairs per tag       |

## Fields added after this diagram was drawn

The ASCII art above reflects the original schema. Two fields have been added since,
and are included in `schema.sql`:

| Model | Field | Added by | Purpose |
|---|---|---|---|
| `Activity` | `slug` (unique) | `0004_add_activity_slug` | Public URL key — `/activities/<slug>/` |
| `Material` | `preview_pdf` | `0005_material_preview_pdf` | Optional PDF rendering, used when `file` is not itself a PDF |

`0006_add_curriculum_categories` also seeds 10 `Category` rows as data; it changes
no schema. Tests must therefore not assume the `Category` table starts empty.

To regenerate the authoritative field list at any time:

```bash
python manage.py inspectdb          # from the live database
python manage.py sqlmigrate activities 0001   # DDL for a given migration
```
