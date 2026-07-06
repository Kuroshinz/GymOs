# Planning Engine

**RFC-021** | Status: `Complete` | Version: `1.0`

## Overview

The Planning Engine is the deterministic periodization pipeline for GymOS. Workout generation no longer produces workouts directly — it consumes plans produced by this engine.

Planning is the **single source of truth** for every future program.

## Core Architecture

```
User Intent → Planning Engine → Macrocycle → Mesocycles → Microcycles → WeekPlans → SessionPlans
                                     ↓
                           Allocation Engine (Volume, Intensity, Frequency, RIR, Recovery)
                                     ↓
                           Planning Validator (Scientific, Volume, Recovery, Frequency, Constraint)
                                     ↓
                           Planning Metrics (Quality, Balance, Specificity, Adherence)
```

## Components

### PlanningEngine
- `generate_macrocycle()` — Full macrocycle from parameters
- `generate_mesocycle()` — Single mesocycle with microcycles
- `generate_weekly_split()` — Day type distribution
- `generate_daily_session()` — Single session scaffold
- `generate_progression_block()` — Volume progression across weeks
- `generate_deload_block()` — Recovery week generator
- `generate_recovery_budget()` — Recovery capacity estimation
- `generate_nutrition_budget()` — Nutrition target estimation

### AllocationEngine
- `distribute_volume()` — Sets, reps, RIR per session
- `distribute_intensity()` — Load zones by focus
- `distribute_frequency()` — Muscle group frequency
- `distribute_rir()` — RIR decrease across mesocycle
- `distribute_recovery()` — Rest days, deload timing
- `compute_fatigue_budget()` — Fatigue units from volume
- `compute_nutrition_budget()` — Macros from calories
- `allocate_exercises_to_session()` — Exercise placement
- `compute_volume_distribution()` — Aggregate stats

### PlanningValidator
- `ScientificValidator` — Periodization logic, progression, deload placement
- `VolumeValidator` — Min/max per session, week, muscle group
- `RecoveryValidator` — Rest days, deload frequency, capacity
- `FrequencyValidator` — Session count, muscle frequency
- `ConstraintValidator` — Hard constraints (duration, sets)

### PlanningMetricsScorer
- `score_plan_quality()` — Aggregate 8-dimension score
- `score_scientific()` — Periodization, progression, intensity zone accuracy
- `score_recovery_balance()` — Rest days, deload, sleep alignment
- `score_fatigue_balance()` — Weekly load, spikes, distribution
- `score_specificity()` — Goal-aligned exercise selection
- `score_adherence()` — Time commitment, sustainability, recovery buffer

## Periodization Model

### Macrocycle (24 weeks default)
- Duration: 12-52 weeks
- Contains 4-6 mesocycles
- Designed from user goal (hypertrophy, strength, fat loss)

### Mesocycle (3-8 weeks)
- Single training focus (hypertrophy, strength, power, etc.)
- Contains 1-2 microcycles
- Ends with optional deload week

### Microcycle (1-4 weeks)
- Contains weekly plans
- Progressive volume increase
- Consistent split structure

### WeekPlan (7 days)
- Session types: Push, Pull, Legs, Upper, Lower, Full Body, Rest, Active Recovery, Deload
- Fatigue budget per week
- Recovery and nutrition budgets

### SessionPlan
- Exercise allocations with sets/reps/RIR
- Volume allocation
- Fatigue budget per session

## Quality Dimensions

| Metric | Weight | Description |
|--------|--------|-------------|
| Scientific Score | 20% | Periodization validity, progression logic |
| Recovery Balance | 15% | Rest days, deload frequency, sleep |
| Fatigue Balance | 15% | Weekly load, session spikes, distribution |
| Specificity | 15% | Goal-aligned intensity and volume |
| Adherence Prediction | 15% | Time commitment, sustainability |
| Volume Distribution | 10% | CV across training weeks |
| Progression Quality | 10% | Progressive overload consistency |

## Usage

```python
from shared.planning import PlanningOrchestrator

orch = PlanningOrchestrator()
output = orch.generate_plan(
    duration_weeks=24,
    goal="hypertrophy",
    sessions_per_week=5,
    split_style="ppl_ul",
)
print(f"Quality: {orch.score_plan().overall:.0%}")
print(f"Errors: {output.validation.error_count}")
print(f"Warnings: {output.validation.warning_count}")
print(orch.report())
```

## Integration

### Intent Platform
`generate_from_intent(intent_config)` builds a UserIntent, extracts goals, timeline, and training preferences, then generates a plan.

### Event Platform
Publishes: `MacrocycleGenerated`, `MesocycleGenerated`, `WeekPlanGenerated`, `SessionPlanGenerated`, `PlanActivated`, `PlanProgressed`, `PlanCompleted`, `DeloadWeekGenerated`, `VolumeAllocationAdjusted`

### Recovery Intelligence
Consumes recovery scores to adjust fatigue budgets and deload timing.

### Prediction Engine
Consumes plan quality and adherence predictions for goal forecasting.

### Nutrition Intelligence
Consumes nutrition budgets from plan for macro target setting.
