# Decision Engine

## Central Orchestrator

`DecisionEngine` (in `modules/gymbrain/services/decision_engine.py`) is the primary API for GymBrain.

It instantiates all analyzers and registers all 15 default rules, then exposes simple methods for the application layer.

## Dashboard Integration API

| Method | Returns | Description |
|--------|---------|-------------|
| `get_today_recommendations(max_recs=10)` | `list[Recommendation]` | Evaluates all rules, returns sorted recommendations |
| `get_weekly_review()` | `WeeklyReview` | Generates structured weekly training summary |
| `get_goal_progress(goal_weight=None)` | `GoalProgress` | Tracks bodyweight goals and bulking quality |
| `get_priority_muscles()` | `list[MuscleAnalysisResult]` | Analyzes each priority muscle's status |
| `get_recovery_status()` | `FatigueResult` | Multi-factor fatigue analysis |
| `get_plateau_analysis()` | `list[PlateauResult]` | Detects plateaus on compound lifts |
| `get_muscle_analysis(muscle_ids=None)` | `list[MuscleAnalysisResult]` | Detailed muscle-by-muscle analysis |
| `evaluate_rules(max_recommendations=20)` | `list[Recommendation]` | Raw rule evaluation (no analysis wrappers) |

## Default Rules (15 total)

Registered in priority order:

| Rule | Priority | Trigger |
|------|----------|---------|
| FatigueRule | 95 | Systemic fatigue HIGH or VERY_HIGH |
| ProgressionRule | 90 | Target reps reached with adequate RIR |
| DeloadRule | 85 | Recovery flags indicate overreaching |
| VolumeRule | 80 | Priority muscle below MEV |
| RecoveryRule | 80 | Recovery flags present |
| VolumeExcessRule | 75 | Muscle above MRV |
| WeightPlateauRule | 70 | Bodyweight unchanged 14+ days |
| StrengthPlateauRule | 65 | e1rm stuck 3+ weeks |
| FrequencyRule | 60 | Muscle trained below recommended frequency |
| NutritionRule | 60 | Bodyweight trend outside optimal range |
| RestRule | 60 | RIR consistently 0 across sets |
| BodyweightStallRule | 55 | Bodyweight stalled 14+ days |
| RepPlateauRule | 55 | Rep count stalled 3+ weeks |
| ConsistencyRule | 50 | Missed sessions detected |
| TechniqueRule | 50 | Rep drop indicates form degradation |

## Priority × Confidence Sorting

Recommendations are sorted by `(priority * confidence)` descending.

- A CRITICAL (90) rule with 0.95 confidence scores 85.5
- A MEDIUM (50) rule with 0.95 confidence scores 47.5
- Within same score, higher priority wins

## Dependency Injection

GymBrain uses manual injection via `DataProvider`:

```python
provider = DataProvider(
    exercise_repo=exercise_repo,
    muscle_repo=muscle_repo,
    program_repo=program_repo,
    db=db,
    volume_engine=volume_engine,
    pr_engine=pr_engine,
    recovery_engine=recovery_engine,
    progression_engine=progression_engine,
)
engine = DecisionEngine(provider=provider)
recs = engine.get_today_recommendations()
```
