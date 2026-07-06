# Planning Model

**RFC-021** | Data Model Reference

## Entity Hierarchy

```
Macrocycle (1)
  ├── Mesocycle (4-6)
  │     ├── Microcycle (1-2)
  │     │     └── WeekPlan (3-7)
  │     │           ├── SessionPlan (1-7)
  │     │           │     ├── ExerciseAllocation (3-8)
  │     │           │     ├── VolumeAllocation (1)
  │     │           │     └── FatigueBudget (1)
  │     │           ├── RecoveryBudget (1)
  │     │           └── NutritionBudget (1)
  │     ├── IntensityDomain (1)
  │     └── Volume targets (min/max)
  ├── Progress tracking
  └── Quality metrics
```

## Domain Models

### Macrocycle
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| macrocycle_id | str | "" | Unique identifier |
| name | str | "" | Human-readable name |
| duration_weeks | int | 24 | Total plan duration |
| start_date | str | "" | ISO date |
| end_date | str | "" | ISO date |
| mesocycles | list[Mesocycle] | [] | Contained mesocycles |
| overall_goal | str | "" | User's primary goal |
| user_intent_id | str | "" | Link to Intent Platform |
| version | str | "1.0" | Plan version |

### Mesocycle
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| mesocycle_id | str | "" | Unique identifier |
| name | str | "" | Human-readable name |
| goal | MesocycleGoal | HYPERTROPHY | Training goal |
| focus | TrainingFocus | HYPERTROPHY | Training focus |
| phase | CyclePhase | HYPERTROPHY_I | Periodization phase |
| microcycles | list[Microcycle] | [] | Contained microcycles |
| week_count | int | 5 | Total weeks |
| start_week | int | 0 | Week offset in macrocycle |
| target_rir | float | 1.0 | Reps in reserve target |
| target_rpe | float | 8.0 | RPE target |
| min_volume_per_muscle | int | 8 | Minimum weekly sets |
| max_volume_per_muscle | int | 22 | Maximum weekly sets |
| intensity_zone | IntensityDomain | HYPERTROPHY | Load zone |
| deload_after | bool | True | Add deload week |

### SessionPlan
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| session_id | str | "" | Unique identifier |
| week | int | 0 | Week number |
| day_of_week | int | 0 | 0=Monday, 6=Sunday |
| day_type | DayType | REST | Push/Pull/Legs/etc |
| training_focus | TrainingFocus | HYPERTROPHY | Focus |
| exercises | list[ExerciseAllocation] | [] | Allocated exercises |
| volume_allocation | VolumeAllocation | default | Volume targets |
| fatigue_budget | FatigueBudget | default | Fatigue tracking |
| estimated_duration_minutes | int | 60 | Expected duration |
| is_deload | bool | False | Deload session flag |
| is_recovery | bool | False | Recovery session flag |

### ExerciseAllocation
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| exercise_id | str | "" | Exercise identifier |
| exercise_name | str | "" | Human-readable name |
| target_muscle_group | str | "" | Primary muscle group |
| sets | int | 0 | Working sets |
| reps | int | 0 | Reps per set |
| rir | float | 1.0 | Reps in reserve |
| rpe | float or None | None | RPE target |
| load_percent | float | 0.0 | % of 1RM |
| rest_seconds | int | 90 | Rest between sets |
| is_warmup | bool | False | Warmup set flag |
| is_primary | bool | False | Primary exercise flag |
| order_in_session | int | 0 | Execution order |

## Enums

### CyclePhase
Preparatory, Hypertrophy I, Hypertrophy II, Strength I, Strength II, Peaking, Deload, Transition, Maintenance

### TrainingFocus
Strength, Hypertrophy, Endurance, Power, Conditioning, Recovery, Maintenance

### DayType
Push, Pull, Legs, Upper, Lower, Full Body, Conditioning, Rest, Active Recovery, Deload

### MesocycleGoal
Max Strength, Hypertrophy, Strength Endurance, Power, Conditioning, Fat Loss, Maintenance, Rehab

### IntensityDomain
Strength (1-6 reps @ 80-100%), Hypertrophy (6-15 @ 60-80%), Endurance (15-30 @ 40-60%), Power (1-5 @ 75-90%)

### ProgressionModel
Double Progression, Linear Progression, Ramping, Periodization Block, Wave Loading, RPE-Based, Auto-Regulation

## Budget Models

### FatigueBudget
| Field | Description |
|-------|-------------|
| total_fatigue_units | Available fatigue capacity |
| used_fatigue_units | Consumed fatigue |
| max_per_session | Per-session cap |
| max_per_muscle_group | Per-muscle cap |
| recovery_rate_per_day | Daily recovery rate |
| current_fatigue_level | Current accumulated fatigue |

### RecoveryBudget
| Field | Description |
|-------|-------------|
| available_hours_per_night | Sleep target |
| target_hrv_score | HRV goal |
| current_hrv_score | Current HRV |
| sleep_quality_score | 0.0-1.0 |
| nutrition_score | 0.0-1.0 |
| stress_level | 1-10 |
| readiness_score | 0.0-1.0 |
| recovery_capacity | Computed: 0.0-1.0 |

### NutritionBudget
| Field | Description |
|-------|-------------|
| target_calories | Daily calorie target |
| protein_g | Daily protein |
| carbs_g | Daily carbs |
| fat_g | Daily fat |
| fiber_g | Daily fiber |
| hydration_ml | Daily hydration |
| pre_workout_carbs_g | Pre-workout carbs |
| post_workout_protein_g | Post-workout protein |
| meal_count | Number of meals |
