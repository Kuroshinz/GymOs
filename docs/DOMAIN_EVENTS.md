# Domain Events Reference

## Event Index

| Event | Source | Version | Payload |
|-------|--------|---------|---------|
| WorkoutStarted | workout | 1.0 | workout_id, program_name, day_name, started_at |
| WorkoutCompleted | workout | 1.0 | workout_id, program_name, day_name, duration_minutes, total_volume_kg, exercise_count, total_sets |
| ExerciseCompleted | workout | 1.0 | workout_id, exercise_id, exercise_name, sets_completed, total_reps, total_volume_kg |
| SetCompleted | workout | 1.0 | workout_id, exercise_id, exercise_name, set_number, reps, weight_kg, rir, rpe |
| ProgramImported | workout_program | 1.0 | program_name, version, source_file, day_count, exercise_count |
| ProgramActivated | workout_program | 1.0 | program_name, version, previous_program |
| BodyWeightUpdated | workout | 1.0 | weight_kg, date, change_from_last |
| PersonalRecordUnlocked | pr_engine | 1.0 | exercise_id, exercise_name, pr_type, value, previous_value, unit |
| RecoveryScoreUpdated | recovery_engine | 1.0 | score, flags[], session_id |
| MealLogged | nutrition | 1.0 | meal_name, calories, protein_g, carbs_g, fat_g, date |
| ExerciseKnowledgeUpdated | knowledge | 1.0 | exercise_id, exercise_name, version, changed_fields[] |

## WorkoutStarted

Fired when a user begins a workout session.

| Field | Type | Description |
|-------|------|-------------|
| workout_id | str | Unique session identifier |
| program_name | str | Active program name |
| day_name | str | Day label (e.g. "Push A") |
| started_at | datetime | Session start time |

## WorkoutCompleted

Fired when a workout session is saved/completed.

| Field | Type | Description |
|-------|------|-------------|
| workout_id | str | Unique session identifier |
| program_name | str | Active program name |
| day_name | str | Day label |
| duration_minutes | float | Total session duration |
| total_volume_kg | float | Total volume (sets × reps × weight) |
| exercise_count | int | Number of exercises performed |
| total_sets | int | Total sets performed |

## ExerciseCompleted

Fired when all sets of an exercise are logged.

| Field | Type | Description |
|-------|------|-------------|
| workout_id | str | Session identifier |
| exercise_id | str | Knowledge base exercise ID |
| exercise_name | str | Display name |
| sets_completed | int | Sets performed |
| total_reps | int | Total reps across all sets |
| total_volume_kg | float | Volume for this exercise |

## SetCompleted

Fired when a single set is logged.

| Field | Type | Description |
|-------|------|-------------|
| workout_id | str | Session identifier |
| exercise_id | str | Knowledge base exercise ID |
| exercise_name | str | Display name |
| set_number | int | Set index |
| reps | int | Reps performed |
| weight_kg | float | Weight used |
| rir | float? | Reps in reserve |
| rpe | float? | Rate of perceived exertion |

## ProgramImported

Fired when a new program is imported from a file.

| Field | Type | Description |
|-------|------|-------------|
| program_name | str | Program display name |
| version | str | Program version |
| source_file | str | Import file path/name |
| day_count | int | Number of training days |
| exercise_count | int | Total exercise slots |

## ProgramActivated

Fired when the active program is switched.

| Field | Type | Description |
|-------|------|-------------|
| program_name | str | Newly activated program |
| version | str | Program version |
| previous_program | str | Previously active program |

## BodyWeightUpdated

Fired when the user logs a new body weight.

| Field | Type | Description |
|-------|------|-------------|
| weight_kg | float | Current body weight |
| date | str | Date of measurement (YYYY-MM-DD) |
| change_from_last | float? | Difference from previous measurement |

## PersonalRecordUnlocked

Fired when a new personal record is detected.

| Field | Type | Description |
|-------|------|-------------|
| exercise_id | str | Knowledge base exercise ID |
| exercise_name | str | Display name |
| pr_type | str | Type: "weight", "volume", "reps", "e1rm" |
| value | float | New record value |
| previous_value | float? | Previous record value |
| unit | str | Unit (default: "kg") |

## RecoveryScoreUpdated

Fired after recovery analysis following a workout.

| Field | Type | Description |
|-------|------|-------------|
| score | float | Recovery score (0-100) |
| flags | list[str] | Recovery flags (e.g. "high_volume", "low_sleep") |
| session_id | str | Workout session that triggered this |

## MealLogged

Fired when a meal is logged in the nutrition tracker.

| Field | Type | Description |
|-------|------|-------------|
| meal_name | str | Meal label (e.g. "Breakfast") |
| calories | float | Total calories |
| protein_g | float | Protein in grams |
| carbs_g | float | Carbohydrates in grams |
| fat_g | float | Fat in grams |
| date | str | Date (YYYY-MM-DD) |

## ExerciseKnowledgeUpdated

Fired when an exercise definition is updated in the knowledge base.

| Field | Type | Description |
|-------|------|-------------|
| exercise_id | str | Knowledge base exercise ID |
| exercise_name | str | Display name |
| version | str | New knowledge version |
| changed_fields | list[str] | Fields that were modified |
