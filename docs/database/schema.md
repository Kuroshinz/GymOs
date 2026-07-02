# Database Schema

## Overview

Database: SQLite (default: `data/nexus.db`)
Migration tool: Alembic
ORM: SQLAlchemy (async)

## Tables

### workouts
| Column | Type | Notes |
|--------|------|-------|
| id | VARCHAR(36) | UUID |
| name | VARCHAR(255) | |
| started_at | DATETIME | |
| completed_at | DATETIME | Nullable |
| notes | TEXT | |
| created_at | DATETIME | Auto |
| updated_at | DATETIME | Auto |

### workout_exercises
| Column | Type | Notes |
|--------|------|-------|
| id | VARCHAR(36) | UUID |
| workout_id | VARCHAR(36) | FK → workouts |
| name | VARCHAR(255) | |
| muscle_group | VARCHAR(50) | Enum |
| exercise_type | VARCHAR(50) | Enum |
| sort_order | INTEGER | |

### exercise_sets
| Column | Type | Notes |
|--------|------|-------|
| id | VARCHAR(36) | UUID |
| exercise_id | VARCHAR(36) | FK → workout_exercises |
| reps | INTEGER | |
| weight | FLOAT | kg |
| rpe | FLOAT | Nullable |
| completed | BOOLEAN | |

### meals
| Column | Type | Notes |
|--------|------|-------|
| id | VARCHAR(36) | UUID |
| name | VARCHAR(255) | |
| eaten_at | DATETIME | |
| notes | TEXT | |

### meal_items
| Column | Type | Notes |
|--------|------|-------|
| id | VARCHAR(36) | UUID |
| meal_id | VARCHAR(36) | FK → meals |
| name | VARCHAR(255) | |
| calories | FLOAT | |
| protein_g | FLOAT | |
| carbs_g | FLOAT | |
| fat_g | FLOAT | |
| quantity | FLOAT | Default 1.0 |
| unit | VARCHAR(50) | Default "serving" |

### plugin_config
| Column | Type | Notes |
|--------|------|-------|
| id | VARCHAR(36) | UUID |
| plugin_name | VARCHAR(100) | Unique |
| enabled | BOOLEAN | Default true |
| settings | TEXT | JSON |
| credentials | TEXT | JSON (encrypted) |

## Migrations

```bash
# Create new migration
alembic revision -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```
