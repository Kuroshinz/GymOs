# ADR-010: Predictive Intelligence Engine

## Status
Accepted (RFC-020)

## Context
GymOS needs predictive capabilities to forecast athlete state across multiple time horizons. These forecasts enable proactive decision-making rather than reactive adjustments.

## Decision
Implement a deterministic, stateless, composable prediction engine module (`modules/prediction/`) with:

1. **9 prediction types** covering PR probability, plateau risk, recovery decline, bodyweight trend, goal ETA, MRV violation risk, deload probability, consistency decay, and workout completion.

2. **4 forecast windows** (3d, 7d, 14d, 28d) for tactical to strategic planning.

3. **Engine isolation** — each engine is independent, pure, and unit-testable. The `PredictionService` orchestrates all engines and feeds them data from canonical providers.

4. **Provider pattern** — `IPredictionProvider` is consumed by GymBrain but engines never modify plans.

5. **Rich output** — every prediction includes confidence scores, explanations, evidence chains, scenarios, and point-by-point forecasts with confidence intervals.

## Consequences
- Predictions are deterministic and explainable
- No changes to existing module boundaries
- GymBrain consumes predictions via provider but makes its own decisions
- 113+ tests ensure correctness
