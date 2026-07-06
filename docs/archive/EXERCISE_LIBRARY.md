# Exercise Library

## Overview

The exercise library contains 105 exercise definitions across 13 categories.
Each exercise is defined in a JSON file at `knowledge/exercises/<id>.json`.

## Categories

| Category           | Count | Prefix     |
|--------------------|-------|------------|
| Back               | 12    | `back_`    |
| Biceps             | 6     | `biceps_`  |
| Calves             | 4     | `calves_`  |
| Cardio             | 6     | `cardio_`  |
| Chest              | 10    | `chest_`   |
| Core               | 11    | `core_`    |
| Forearms           | 4     | `forearms_`|
| Full Body          | 8     | `full_body_`|
| Hamstrings & Glutes| 10    | `hamstrings_`|
| Quads              | 10    | `quads_`   |
| Shoulders          | 11    | `shoulders_`|
| Triceps            | 6     | `triceps_` |
| Warmup & Mobility  | 8     | `warmup_`  |

## Exercise Schema

Every exercise definition includes the following fields:

| Field                  | Required | Description                                   |
|------------------------|----------|-----------------------------------------------|
| `id`                   | Yes      | Stable unique identifier                      |
| `name`                 | Yes      | Display name                                  |
| `aliases`              | No       | Common alternative names                      |
| `category`             | Yes      | Muscle category                               |
| `primary_muscles`      | Yes      | Target muscles (min 1)                        |
| `secondary_muscles`    | No       | Synergist / stabilizer muscles                |
| `equipment`            | Yes      | Required equipment                            |
| `difficulty`           | Yes      | beginner / intermediate / advanced             |
| `movement_pattern`     | Yes      | Fundamental movement pattern                  |
| `mechanics`            | No       | compound / isolation / isometric              |
| `hypertrophy_rep_range`| No       | Optimal rep range for hypertrophy             |
| `rest_time`            | No       | Recommended rest between sets                 |
| `tempo`                | No       | Eccentric-pause-concentric notation           |
| `setup`                | No       | Setup instructions                            |
| `execution`            | No       | Execution instructions                        |
| `cues`                 | No       | Coach cues for form                           |
| `breathing`            | No       | Breathing pattern guidance                    |
| `common_mistakes`      | No       | Frequent form errors                          |
| `alternatives`         | No       | Alternative exercise IDs                      |
| `variations`           | No       | Variation exercise IDs                        |
| `progression`          | No       | Progression path                              |
| `spotting`             | No       | Spotting instructions                         |

## Full Schema Reference

See `schemas/exercise.schema.json` for the authoritative JSON Schema.

## Adding New Exercises

1. Create `<category>_<name>.json` in `knowledge/exercises/`
2. Ensure `id` follows the pattern `{category}_{unique_name}`
3. Fill all required fields
4. Add aliases to `knowledge/aliases.yaml`
5. Update `_index.json` total and category counts
6. Run the knowledge loader validation

## PPL-UL v6 Exercise Mapping

Every exercise in the canonical PPL-UL program
(`data/program.json`) is mapped to a knowledge base ID via the
`exercise_id` field. See the program file for the full mapping.
