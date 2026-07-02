# Database Schema

## Overview

| Property | Value |
|----------|-------|
| Engine | SQLite (WAL mode) |
| ORM | SQLAlchemy 2.0+ (async) |
| Migration | Alembic |
| Default path | `data/nexus.db` |

## Principles

- All access via repositories (no raw SQL in application/presentation)
- UUIDs for all primary keys
- Timestamps in UTC
- Soft deletes where applicable

## MVP Entities

### workout_plans

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | VARCHAR(36) | PK | UUID |
| name | VARCHAR(255) | NOT NULL | |
| description | TEXT | | |
| created_at | DATETIME | NOT NULL | Auto |
| updated_at | DATETIME | NOT NULL | Auto |

### workout_plan_exercises

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | VARCHAR(36) | PK | UUID |
| plan_id | VARCHAR(36) | FK → workout_plans | |
| exercise_id | VARCHAR(100) | NOT NULL | References knowledge/exercises/ |
| sort_order | INTEGER | NOT NULL | |
| target_sets | INTEGER | | Default 3 |
| target_reps | VARCHAR(20) | | e.g., "8-12" |
| rest_seconds | INTEGER | | Default 90 |

### workout_sessions

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | VARCHAR(36) | PK | UUID |
| plan_id | VARCHAR(36) | FK → workout_plans | Nullable (free form) |
| name | VARCHAR(255) | | |
| started_at | DATETIME | NOT NULL | |
| completed_at | DATETIME | | Nullable |
| duration_minutes | INTEGER | | |
| notes | TEXT | | |
| created_at | DATETIME | NOT NULL | Auto |

### exercise_logs

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | VARCHAR(36) | PK | UUID |
| session_id | VARCHAR(36) | FK → workout_sessions | |
| exercise_id | VARCHAR(100) | NOT NULL | References knowledge/ |
| sort_order | INTEGER | NOT NULL | |
| notes | TEXT | | |

### exercise_sets

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | VARCHAR(36) | PK | UUID |
| exercise_log_id | VARCHAR(36) | FK → exercise_logs | |
| set_number | INTEGER | NOT NULL | |
| weight_kg | FLOAT | | |
| reps | INTEGER | | |
| rpe | FLOAT | | Nullable, 1-10 |
| is_completed | BOOLEAN | DEFAULT 1 | |
| is_warmup | BOOLEAN | DEFAULT 0 | |
| created_at | DATETIME | NOT NULL | Auto |

### nutrition_logs

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | VARCHAR(36) | PK | UUID |
| date | DATE | NOT NULL | |
| calories | FLOAT | | |
| protein_g | FLOAT | | |
| carbs_g | FLOAT | | |
| fat_g | FLOAT | | |
| source | VARCHAR(50) | | "cronometer_import" |
| created_at | DATETIME | NOT NULL | Auto |

### weight_logs

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | VARCHAR(36) | PK | UUID |
| date | DATE | NOT NULL | |
| weight_kg | FLOAT | NOT NULL | |
| notes | TEXT | | |
| created_at | DATETIME | NOT NULL | Auto |

### personal_records

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | VARCHAR(36) | PK | UUID |
| exercise_id | VARCHAR(100) | NOT NULL | |
| pr_type | VARCHAR(20) | NOT NULL | "weight", "volume", "estimated_1rm" |
| value | FLOAT | NOT NULL | |
| achieved_at | DATETIME | NOT NULL | |
| session_id | VARCHAR(36) | FK → workout_sessions | |

### settings

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| key | VARCHAR(100) | PK | |
| value | TEXT | NOT NULL | JSON-encoded |
| updated_at | DATETIME | NOT NULL | Auto |

## Indexes

| Table | Index | Columns | Purpose |
|-------|-------|---------|---------|
| workout_sessions | idx_sessions_started | started_at | History queries |
| workout_sessions | idx_sessions_plan | plan_id | Plan sessions |
| exercise_logs | idx_logs_session | session_id | Session exercises |
| exercise_sets | idx_sets_log | exercise_log_id | Exercise sets |
| nutrition_logs | idx_nutrition_date | date | Daily nutrition |
| weight_logs | idx_weight_date | date | Weight trend |
| personal_records | idx_pr_exercise | exercise_id | PR per exercise |

## ERD (MVP)

```
workout_plans 1──* workout_plan_exercises
workout_plans 1──* workout_sessions
workout_sessions 1──* exercise_logs
exercise_logs 1──* exercise_sets
workout_sessions 1──* personal_records
```

## Migrations

```bash
# Create new migration
alembic revision -m "description"

# Apply all pending
alembic upgrade head

# Rollback one step
alembic downgrade -1

# View history
alembic history
```

## Future Tables (Post-MVP)

- `recovery_scores` — daily HRV, sleep, readiness
- `workout_templates` — shared/public plan templates
- `ai_recommendations` — AI Coach recommendation log
- `plugin_data` — per-plugin data storage
- `workout_routes` — GPS route data (outdoor)
