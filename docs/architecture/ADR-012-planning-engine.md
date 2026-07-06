# ADR-012: Planning Engine

**Status:** Accepted | **Date:** 2026-07-04 | **RFC:** RFC-021

## Context

Workout generation in GymOS was producing workouts directly, without a deterministic planning layer. This caused:

1. **Non-deterministic output** — same inputs could produce different workouts
2. **No periodization** — no macro-to-micro structure
3. **No validation** — no way to verify scientific validity
4. **No quality metrics** — no objective assessment of plan quality
5. **No integration** — Recovery, Nutrition, and Prediction had no planning context
6. **No history** — plan versions and adherence tracking absent

The Intent Platform (ADR-011) now captures what the user wants. The Planning Engine is the missing step that translates intent into a structured, deterministic training plan.

## Decision

Create `shared/planning/` as a new platform within the Shared layer with:

### 1. Domain Models
- `Macrocycle` → `Mesocycle` → `Microcycle` → `WeekPlan` → `SessionPlan`
- Budget models: `FatigueBudget`, `RecoveryBudget`, `NutritionBudget`
- Value objects: `VolumeAllocation`, `ExerciseAllocation`
- Enums: `CyclePhase`, `TrainingFocus`, `DayType`, `MesocycleGoal`, `IntensityDomain`, `ProgressionModel`, `SplitStyle`

### 2. Planning Engine
Deterministic plan generation with no random or LLM components:
- `generate_macrocycle()` — Full macrocycle from parameters
- `generate_mesocycle()` — Single mesocycle with microcycles
- `generate_weekly_split()` — Day type distribution
- `generate_daily_session()` — Session scaffold
- `generate_progression_block()` — Volume ramp
- `generate_deload_block()` — Recovery week
- `generate_recovery_budget()`, `generate_nutrition_budget()`

### 3. Allocation Engine
Deterministic distribution of training variables:
- Volume, intensity, frequency, RIR, recovery
- Exercise-to-session allocation
- Fatigue and nutrition budget computation

### 4. Planning Validator
Five sub-validators merged into one result:
- Scientific (periodization, progression, deload placement, intensity accuracy)
- Volume (session/week/muscle min/max)
- Recovery (rest days, deload frequency, capacity)
- Frequency (session count, muscle frequency)
- Constraint (hard boundaries)

### 5. Planning Metrics
Eight-dimension quality scoring:
- Scientific Score (20%), Recovery Balance (15%), Fatigue Balance (15%)
- Specificity (15%), Adherence Prediction (15%)
- Volume Distribution (10%), Progression Quality (10%)

### 6. Repository, Reports, Serializer, History
- In-memory CRUD repository
- Human-readable report generation
- Dict/JSON serialization round-trips
- Plan versioning and change tracking

### 7. Orchestrator
`PlanningOrchestrator` is the single entry point for all planning operations.

## Consequences

### Positive
1. **Deterministic** — Same inputs always produce the same plan
2. **Verifiable** — Every plan is validated against scientific guidelines
3. **Measurable** — Objective quality scores for every plan
4. **Traceable** — Full version history and change tracking
5. **Integratable** — Event publishing, Intent integration, Recovery/Nutrition budget inputs
6. **Testable** — Pure functions, no external dependencies

### Negative
1. **Increased complexity** — New subsystem with ~15 files
2. **Migration cost** — Existing workout generation must be updated to consume plans
3. **Maintenance** — Scientific guidelines must be kept current

### Neutral
1. **Opinionated** — Prescribes periodization model (block periodization)
2. **Defaults required** — Many parameters have sensible defaults

## Technical Notes

- All domain models are frozen dataclasses (immutable)
- Engine produces `PlanningOutput` containing macrocycle + validation
- Validator returns `ValidationResult` with errors and warnings
- Metrics use weighted scoring with configurable dimensions
- History stores snapshots and changes per plan version
- Events are published for every major lifecycle transition

## References

- ADR-011: Intent Platform
- ADR-010: Predictive Intelligence
- docs/PLANNING_ENGINE.md
- docs/PLANNING_MODEL.md
- docs/PERIODIZATION.md
