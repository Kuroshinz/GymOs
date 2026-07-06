# ADR-013: Planning Optimizer

**Status**: Accepted  
**Date**: 2026-07-04  
**Deciders**: GymOS Architecture Team  
**Priority**: High  

## Context

RFC-021 delivered a deterministic Planning Engine that generates training plans from intent parameters. While the engine produces valid, scientifically-grounded plans, it offers no mechanism to explore the design space, trade off competing goals, or adapt to user-specific constraints. Users with different equipment, schedules, or recovery capacities receive identical plans for identical intents.

The Planning Optimizer addresses this gap by transforming planning from deterministic generation into intelligent multi-objective optimization.

## Decision

Create `shared/planning_optimizer/` as an evolutionary multi-objective optimization engine for training plans.

### Key Design Decisions

1. **Evolutionary approach over gradient-based**: Training plan parameters are discrete (sessions/week, mesocycle count, etc.) and the objective landscape is non-differentiable. Evolutionary algorithms naturally handle these characteristics.

2. **Simulation pipeline mirrors real architecture**: Rather than hard-coding fitness functions, the optimizer simulates the Prediction → Recovery → Nutrition → Decision pipeline that real GymOS modules would provide. This ensures optimization quality reflects the actual system.

3. **Frozen domain models, mutable scoring**: All domain models are immutable frozen dataclasses. Scoring functions are pure stateless methods.

4. **Composite score over Pareto front**: A single weighted composite score is used for ranking. This simplifies the algorithm, makes results directly comparable, and allows users to express preferences via objective weights. True Pareto optimization was considered but rejected for v1 — the composite approach is simpler and sufficient for the current use case.

5. **Seeded determinism**: A fixed random seed (42) ensures reproducibility. The same input always produces the same output, matching the deterministic guarantees of the Planning Engine.

6. **Constraint penalty in scoring**: Rather than hard-filtering infeasible candidates (which collapses the population), constraints are applied as score penalties. Hard constraint violations reduce the score enough that feasible candidates dominate, but infeasible candidates still contribute genetic diversity.

## Consequences

### Positive
- Users receive plans optimized for their specific objectives and constraints
- The optimizer can explore thousands of plan variants in seconds
- Objective weights give users control over the trade-off between competing goals
- The simulation pipeline evolves independently as real engine implementations improve
- All 299 tests pass, confirming correctness

### Negative
- Evolutionary optimization is non-trivial to debug compared to deterministic generation
- The composite score approach can conceal trade-offs visible in a true Pareto front
- Seeded reproducibility requires careful management of random state across all operations

### Mitigations
- The `OptimizationResult.score_improvement` and `success_rate` metrics expose optimization quality
- Component scores (scientific, recovery, hypertrophy, compliance, risk) are always available for inspection
- The `PlanMutator` class provides isolated, testable mutation operations

## Alternatives Considered

1. **Grid search**: Enumerate all combinations of parameters. Rejected — combinatorial explosion makes this infeasible for 10+ parameters.

2. **Bayesian optimization**: Model the objective function and sample efficiently. Rejected — requires continuous parameter spaces and smooth objectives.

3. **Simulated annealing**: Single-solution optimization with random perturbations. Rejected — cannot maintain population diversity or handle multiple constraints effectively.

4. **LLM-based generation**: Use an LLM to propose and evaluate plans. Rejected — violates the deterministic requirement; introduces non-reproducibility, cost, and latency.

## Implementation Details

| Module | Lines | Description |
|--------|-------|-------------|
| `domain.py` | ~220 | 10 domain models, 4 enums, config |
| `engine.py` | ~395 | OptimizationEngine + PlanMutator |
| `objectives.py` | ~355 | 10 scoring functions |
| `constraints.py` | ~225 | 10 constraint checkers |
| `scoring.py` | ~125 | 6-dimension composite scorer |
| `simulation.py` | ~215 | Prediction/Recovery/Nutrition/Decision pipeline |
| `__init__.py` | ~250 | Orchestrator facade |
| Tests (12 files) | ~299 tests | 299/299 passing |

## Verification

```powershell
python -m pytest shared/planning_optimizer/tests/ -q
# 299 passed in 0.88s

python -m pytest shared/planning/tests/ shared/planning_optimizer/tests/ -q
# 678 passed in 1.64s
```
