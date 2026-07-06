# Predictive Intelligence Engine (RFC-020)

## Overview
The Predictive Intelligence Engine (RFC-020) extends GymOS with forecasting capabilities across 9 prediction types and 4 time windows. All predictions are deterministic, stateless, and composable — they predict outcomes without modifying any plans.

## Architecture

```
modules/prediction/
  domain/           — Prediction entities, enums, value objects
  engines/          — 9 deterministic prediction engines
  infrastructure/   — SQLAlchemy models + PredictionRepository
  providers/        — IPredictionProvider + ProductionPredictionProvider
  application/      — PredictionService orchestrating engines + providers
  presentation/     — PredictionViewModel + PredictionFormatter
  tests/            — 113+ tests covering all layers
ui/prediction/      — PredictionDashboard widget
```

## 9 Prediction Types

| Type | Engine | Description |
|------|--------|-------------|
| PR Probability | PRPredictionEngine | Likelihood of new PR in forecast window |
| Plateau Risk | PlateauPredictionEngine | Probability of stalling progression |
| Recovery Decline | RecoveryPredictionEngine | Forecast recovery score trajectory |
| Bodyweight Trend | BodyweightPredictionEngine | Forecast bodyweight over time |
| Goal ETA | GoalEtaPredictionEngine | Estimated days to bodyweight goal |
| MRV Risk | VolumePredictionEngine | Risk of exceeding Max Recoverable Volume |
| Deload Risk | DeloadPredictionEngine | Probability deload will be needed |
| Consistency Decay | ConsistencyPredictionEngine | Forecast workout completion rate |
| Workout Completion | (via ConsistencyEngine) | Per-session completion probability |

## 4 Forecast Windows
- 3d: Short-term tactical forecasts
- 7d: Weekly planning horizon
- 14d: Bi-weekly trend analysis
- 28d: Long-term strategic outlook

## Key Design Decisions
- **Deterministic** — same inputs always produce same outputs
- **Stateless** — no internal state across calls
- **Pure** — no side effects during prediction
- **Composable** — PredictionService orchestrates all engines
- **Read-only** — engines never modify plans; GymBrain decides action

## Provider Interface
Consumed by GymBrain via `IPredictionProvider`:
- `get_next_pr_probability(window)` / `get_plateau_probability(window)` / etc.

## Events Published
- `prediction.updated` — when predictions are regenerated
- Shared events: `PredictionUpdated`, `PlateauPredicted`, `GoalEtaChanged`, `DeloadForecastUpdated`, `PredictionModelUpdated`
