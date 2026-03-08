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
│ FK  category_id       │    N    │ FK  activity_id       │
│     title             │────────►│ FK  tag_id            │
│     description       │    N    └──────────┬───────────┘
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

