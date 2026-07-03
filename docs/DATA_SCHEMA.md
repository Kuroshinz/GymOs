# Data Schema

## Knowledge Base Schemas

All JSON schemas live in `schemas/` and follow JSON Schema Draft 07.

### exercise.schema.json

Validates every exercise definition in `knowledge/exercises/`.

**Required fields:** `id`, `name`, `category`, `primary_muscles`,
`movement_pattern`, `equipment`, `difficulty`

**ID pattern:** `^[a-z]+(_[a-z0-9]+)+$` (e.g. `chest_bench_press`)

**Category enum:** chest, back, shoulders, quads, hamstrings_glutes,
biceps, triceps, core, full_body, calves, forearms, cardio, warmup_mobility

**Difficulty enum:** beginner, intermediate, advanced

### muscle.schema.json

Validates every muscle definition in `knowledge/muscles/`.

**Required fields:** `id`, `display_name`, `group`, `weekly_volume_landmarks`,
`recommended_frequency`, `recovery_characteristics`

**Volume landmarks structure:**
- `mev` (Minimum Effective Volume): `{min_sets, max_sets, description}`
- `mav` (Maximum Adaptive Volume): `{min_sets, max_sets, description}`
- `mrv` (Maximum Recoverable Volume): `{min_sets, max_sets, description}`

### program.schema.json

Validates workout program definitions (e.g. `data/program.json`).

**Required fields:** `name`, `days`

**Metadata fields:** version, author, goal, experience_level, split,
mesocycle_duration_weeks, deload_week, progression_strategy, priority_muscles

**Goal enum:** hypertrophy, strength, endurance, power, fat_loss,
general_fitness, rehabilitation

**Experience level enum:** beginner, intermediate, advanced

## Domain Models

The `modules/workout_program/domain.py` module defines the Python domain
models that mirror these schemas:

| Domain Class         | Schema                               | Description              |
|----------------------|--------------------------------------|--------------------------|
| `WorkoutProgram`     | `program.schema.json`                | Full workout program     |
| `ProgramDay`         | (inline in program schema)           | A single training day    |
| `ProgramExercise`    | (inline in program schema)           | An exercise within a day |
| `DeloadWeek`         | (inline in program schema)           | Deload configuration     |
| `ProgressionStrategy`| (inline in program schema)           | Progression method       |

## Database Schema

The SQLite database schema is documented in `docs/database/schema.md`.

## Migration Scripts

Migration scripts are in `scripts/`:

| Script                         | Purpose                                    |
|--------------------------------|--------------------------------------------|
| `generate_muscle_library.py`   | Generate muscle JSON files                 |
| `migrate_exercises.py`         | Add missing fields to exercise files       |
| `parse_excel_program.py`       | Convert Excel program to JSON              |
