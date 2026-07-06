# Intent Model — Domain Entities & Enumerations

**RFC-020.9** | Intent Platform | Core Domain

## Overview

The Intent Model defines the canonical user intent specification — a declarative,
immutable representation of what a user wants to achieve and how they want to
achieve it. Every GymOS decision path begins with an Intent.

## Core Entity: `UserIntent`

```python
@dataclass(frozen=True)
class UserIntent:
    intent_id: str
    version: str
    status: IntentStatus
    goals: list[GoalIntent]
    constraints: list[Constraint]
    timeline: Timeline
    equipment: EquipmentProfile
    lifestyle: LifestyleProfile
    compliance: ComplianceProfile
    risk_tolerance: RiskTolerance
    training: TrainingPreference
    nutrition: NutritionPreference
    recovery: RecoveryPreference
    adaptive: AdaptivePreference
    priorities: Priority
    conflicts: list[IntentConflict]
```

All fields are frozen — an intent cannot be mutated after construction.
`IntentBuilder` provides the single deterministic construction path.

## Sub-Entities (14)

| Entity | Purpose |
|--------|---------|
| `GoalIntent` | Training/nutrition goal with target, current, unit, priority |
| `Constraint` | Time/equipment/health/lifestyle/injury constraint |
| `Timeline` | Weekly schedule, session duration, preferred days/times |
| `EquipmentProfile` | Gym access level + available/missing/home items |
| `LifestyleProfile` | Occupation hours, commute, sleep, stress, children |
| `ComplianceProfile` | Historical adherence rates (training, nutrition, recovery) |
| `RiskTolerance` | Per-dimension and overall risk appetite |
| `TrainingPreference` | Style, focus muscles, volume ranges, RPE, progression |
| `NutritionPreference` | Approach, macros, meal timing, hydration |
| `RecoveryPreference` | Sleep targets, HRV tracking, deload triggers |
| `AdaptivePreference` | Which scopes auto-adapt, approval gate, speed |
| `Priority` | 1-10 priority per dimension |
| `IntentConflict` | Detected conflict between two dimensions |
| `IntentSnapshot` | Versioned snapshot of intent + score + change description |

## Enumerations (15)

| Enum | Values |
|------|--------|
| `TrainingStyle` | PPL_UL, PUSH_PULL_LEGS, FULL_BODY, UPPER_LOWER, BRO_SPLIT |
| `NutritionApproach` | LEAN_BULK, MAINTENANCE, CUT, REVERSE_DIET |
| `RecoveryPriority` | MAXIMIZE_PERFORMANCE, BALANCE_LIFESTYLE, MINIMIZE_EFFORT |
| `RiskLevel` | CONSERVATIVE, MODERATE, AGGRESSIVE |
| `GoalType` | WEIGHT, STRENGTH, HYPERTROPHY, ENDURANCE, BODY_COMPOSITION, MAINTENANCE |
| `EquipmentLevel` | NONE, MINIMAL, HOME_GYM, COMMERCIAL, FULL |
| `DayPreference` | WEEKDAYS, WEEKENDS, EVERYDAY, CUSTOM |
| `TimeOfDay` | MORNING, AFTERNOON, EVENING, FLEXIBLE |
| `AdaptiveScope` | VOLUME, EXERCISE_SELECTION, DELOAD_TIMING, NUTRITION, RECOVERY, ALL |
| `IntentDimension` | TRAINING, NUTRITION, RECOVERY, CONSISTENCY, LIFESTYLE |
| `ConstraintType` | TIME, EQUIPMENT, HEALTH, LIFESTYLE, INJURY |
| `IntentConflictSeverity` | LOW, MEDIUM, HIGH, CRITICAL |
| `IntentStatus` | ACTIVE, ARCHIVED, SUPERSEDED, DRAFT |

## Design Decisions

- **Immutable by default**: All domain entities are frozen dataclasses. Modification means constructing a new instance.
- **Strong typing**: Enums for all categorical fields prevent invalid states.
- **Defaults are sensible**: Every field has a safe default, enabling construction from partial data.
- **Self-describing**: `GoalType`, `TrainingStyle`, etc. have `.label` properties for UI display.
