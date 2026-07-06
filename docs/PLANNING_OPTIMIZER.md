# Planning Optimizer

## Overview

The Planning Optimizer is a multi-objective evolutionary optimization engine for training plans. It transforms planning from deterministic generation into intelligent optimization by generating, mutating, evaluating, ranking, and selecting optimal plan variants against configurable objectives and constraints.

## Architecture

```
Planning Optimizer Module (shared/planning_optimizer/)

├── domain.py         # Domain models: OptimizationRequest, OptimizationResult,
│                     # OptimizationCandidate, OptimizationScore, enums
├── engine.py         # OptimizationEngine + PlanMutator
├── objectives.py     # ObjectiveScorer — 10 pure scoring functions
├── constraints.py    # ConstraintChecker — 10 constraint types
├── scoring.py        # CompositeScorer — 6-dimension composite score
├── simulation.py     # SimulationPipeline — Candidate → Prediction → Recovery
│                     # → Nutrition → Decision → Score
├── metrics.py        # OptimizerMetrics + OptimizerMetricsCollector
├── reports.py        # PlanningOptimizerReports
├── serializer.py     # PlanningOptimizerSerializer
├── history.py        # PlanningOptimizerHistory
├── repository.py     # PlanningOptimizerRepository
├── events.py         # 8 domain events + PLANNING_OPTIMIZER_EVENT_REGISTRY
└── __init__.py       # PlanningOptimizerOrchestrator facade
```

## Key Concepts

### Optimization Request
- **Base Plan**: A serialized macrocycle JSON to optimize
- **Objectives**: Weighted goals (maximize hypertrophy, minimize fatigue, etc.)
- **Constraints**: Hard/soft limits (equipment, frequency, time, etc.)
- **Population Size**: Number of candidate plans per generation
- **Max Generations**: How many evolutionary cycles to run

### Optimization Cycle
1. **Initialize** — Generate initial population from base plan with random mutations
2. **Evaluate** — Run each candidate through Simulation Pipeline → Composite Score
3. **Rank** — Sort by score, feasible candidates first
4. **Select** — Tournament selection of parents
5. **Crossover** — Combine two parents into a child
6. **Mutate** — Random perturbation of child parameters
7. **Repeat** — Evolve for N generations

### Simulation Pipeline
Each candidate passes through simulated engines:
- **Prediction Engine**: Estimates hypertrophy/strength/endurance gains, plateau risk
- **Recovery Engine**: Estimates fatigue, rest adequacy, deload needs
- **Nutrition Engine**: Estimates caloric and macro requirements
- **Decision Engine**: Aggregates all signals into go/no-go recommendation

### Composite Score (6 Dimensions)
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Scientific | 25% | Progression quality, volume balance |
| Recovery | 15% | Fatigue management, rest adequacy |
| Hypertrophy | 25% | Volume stimulus, goal alignment |
| Compliance | 20% | Adherence likelihood, frequency fit |
| Risk | 15% | Plateau risk, injury risk |
| Constraint Penalty | — | Deduction for constraint violations |

## Usage

```python
from shared.planning_optimizer import PlanningOptimizerOrchestrator

orch = PlanningOptimizerOrchestrator()

# Optimize from existing plan
result = orch.optimize_from_plan(macrocycle_json)

# Access best candidate
best = result.best_candidate
print(f"Best score: {best.scores.overall:.2f}")

# Custom objectives and constraints
from shared.planning_optimizer.domain import (
    ObjectiveType, OptimizationObjective,
    ConstraintType, OptimizationConstraint,
)

objectives = [
    OptimizationObjective(ObjectiveType.MAXIMIZE_HYPERTROPHY, weight=1.0, is_primary=True),
    OptimizationObjective(ObjectiveType.MINIMIZE_FATIGUE, weight=0.7),
]
constraints = [
    OptimizationConstraint(ConstraintType.FREQUENCY, max_value=6.0, min_value=3.0),
]

result = orch.optimize_from_plan(plan_json, objectives, constraints)

# Evaluate a plan without optimization
score = orch.evaluate_plan({"total_sets": 480, ...})

# Check constraints
ok, violations, hard_count = orch.check_constraints(plan_data, constraints)
```

## Integration Points

| Platform | Integration |
|----------|-------------|
| **Capability** | `planning-optimizer` registered in `shared/capabilities/__init__.py` |
| **Events** | 8 events registered in `shared/events/domain_events.py` |
| **Planning Engine** | Consumes macrocycle JSON from PlanningEngine |
| **Intent** | Objectives derived from user intent |

## Determinism

The OptimizationEngine uses a fixed seed (42) for reproducibility. All scoring functions are pure — no randomness, no external state. The engine produces identical results for identical inputs.
