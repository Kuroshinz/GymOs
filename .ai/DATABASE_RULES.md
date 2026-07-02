# GymOS — Database Rules

## Technology

| Property | Value |
|----------|-------|
| Engine | SQLite 3.x with WAL mode |
| ORM | SQLAlchemy 2.0+ async |
| Migrations | Alembic |
| Location | `data/gymos.db` |

## Principles

1. **All access via repositories.** No raw SQL or direct ORM usage outside `infrastructure/`. Repository interfaces live in `domain/`, implementations in `infrastructure/`.
2. **UUIDs for all primary keys.** Use `uuid4` as string (36 chars).
3. **Timestamps in UTC.** Store as ISO 8601 strings or Unix timestamps.
4. **Soft deletes where applicable.** Add `deleted_at` column instead of hard delete for workout history.
5. **No business logic in queries.** Repositories return data; application layer processes it.

## MVP Tables

See `docs/database/schema.md` for full schema.

Key entities:
- `workout_plans` — templates with ordered exercises
- `workout_sessions` — completed workout instances
- `exercise_logs` — exercises within a session
- `exercise_sets` — individual sets (weight, reps, RPE, completed)
- `nutrition_logs` — daily macros from Cronometer import
- `weight_logs` — daily body weight
- `personal_records` — auto-detected PRs
- `settings` — key-value app configuration

## Query Patterns

- **History queries** are filtered by date range (indexed on `started_at`, `date`)
- **Previous session lookup** finds most recent session containing the same exercise
- **PR detection** compares new sets against all historical sets per exercise
- **Volume calculation** = SUM(weight × reps) per exercise/session/week

## Migrations

```bash
# Create new migration
alembic revision -m "description"

# Apply all pending
alembic upgrade head

# Rollback one step
alembic downgrade -1
```

Never edit existing migrations. Create new ones for schema changes.

## Future Tables (Post-MVP)

- `recovery_scores` — daily HRV, sleep, readiness
- `ai_recommendations` — AI Coach recommendation log
- `progress_photos` — body measurement tracking
- `deload_entries` — deload period tracking
