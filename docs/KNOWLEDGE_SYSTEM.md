# Knowledge System

## Overview

GymOS uses a static knowledge base to store all fitness domain data. This
knowledge is the single source of truth for exercise definitions, muscle
group characteristics, and program metadata.

**Principle:** No application logic should contain exercise-specific or
muscle-specific hard-coded data. Every module — including the future AI
Coach, analytics engine, and recommendation system — must access fitness
knowledge through the `KnowledgeLoader`.

## Directory Structure

```
knowledge/
├── aliases.yaml          # Exercise name → ID mapping for import normalization
├── exercises/            # Exercise definitions (105 files)
│   ├── _index.json       # Exercise library index
│   ├── chest_*.json      # Chest exercises
│   ├── back_*.json       # Back exercises
│   ├── shoulders_*.json  # Shoulder exercises
│   ├── quads_*.json      # Quad exercises
│   ├── hamstrings_*.json # Hamstring & glute exercises
│   ├── biceps_*.json     # Biceps exercises
│   ├── triceps_*.json    # Triceps exercises
│   ├── core_*.json       # Core & ab exercises
│   ├── calves_*.json     # Calf exercises
│   ├── forearms_*.json   # Forearm exercises
│   ├── full_body_*.json  # Full-body & compound exercises
│   ├── cardio_*.json     # Cardio exercises
│   └── warmup_*.json     # Warmup & mobility exercises
└── muscles/              # Muscle group definitions (53 files)
    ├── _index.json       # Muscle library index
    └── *.json            # Individual muscle definitions
```

## Loading Knowledge

```python
from shared.knowledge_loader import get_loader, get_exercise, resolve_alias

loader = get_loader()
loader.load_all()

# Get exercise by stable ID
exercise = loader.get_exercise("chest_bench_press")

# Resolve a name to exercise IDs (checks aliases, exercise names)
ids = loader.resolve_alias("Bench Press")
ids = loader.resolve_alias("DB Curl")

# Get muscle by stable ID
muscle = loader.get_muscle("pectoralis_major")

# Convenience functions
ex = get_exercise("quads_barbell_squat")
ids = resolve_alias("Squat")
```

## ID System

All knowledge files use stable, human-readable IDs:

- **Exercise IDs:** `{category}_{exercise_name}`, e.g. `chest_bench_press`
- **Muscle IDs:** `{muscle_name}`, e.g. `pectoralis_major`

IDs are lowercase, snake_case, and never change once assigned. New IDs may
be added but existing IDs must remain stable across versions.

### Alias Resolution

The `aliases.yaml` file maps common exercise names (from Excel imports,
user input) to canonical exercise IDs. The resolution order is:

1. Exact match against the alias map (case-insensitive)
2. Match against exercise display names
3. Match against exercise `aliases` array in the JSON definition

## Validation

The `KnowledgeLoader` provides validation methods:

- `validate_exercise_references()` — checks that all `exercise_id` values in
  the program point to valid exercise definitions
- `validate_muscle_references()` — checks that all `primary_muscles` and
  `secondary_muscles` values in exercises point to valid muscle definitions

## Schemas

JSON schemas for validation are in `schemas/`:

- `exercise.schema.json` — Exercise definition schema
- `muscle.schema.json` — Muscle definition schema
- `program.schema.json` — Workout program schema
