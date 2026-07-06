# Multi-Objective Optimization

## Overview

The Planning Optimizer uses evolutionary multi-objective optimization to find the best trade-off between competing training goals. Unlike single-objective optimization, multi-objective handles the natural tension between goals like "maximize hypertrophy" and "minimize fatigue."

## Objective Types

### Maximization Objectives (higher is better)
| Objective | Default Weight | Description |
|-----------|---------------|-------------|
| Maximize Hypertrophy | 1.0 | Volume stimulus, goal alignment |
| Maximize Recovery | 0.7 | Rest adequacy, deload scheduling |
| Maximize Adherence | 0.9 | Frequency fit, plan duration |
| Maximize Strength | 0.8 | Low-rep work, strength blocks |
| Maximize Endurance | 0.6 | High-rep work, conditioning |
| Maximize Progression | 0.7 | Volume increase over time |
| Balance Volume | 0.5 | Even weekly distribution |

### Minimization Objectives (lower is better, inverted in scoring)
| Objective | Default Weight | Description |
|-----------|---------------|-------------|
| Minimize Fatigue | 0.8 | Volume burden, rest days |
| Minimize Plateau Risk | 0.6 | Goal variety, deload frequency |
| Minimize Injury Risk | 0.8 | Volume ceilings, session spikes |

## Composite Score Formula

```
Overall = (Scientific × 0.25) + (Recovery × 0.15) + (Hypertrophy × 0.25)
        + (Compliance × 0.20) + (Risk × 0.15)
        
Final = Overall × (1 - Constraint_Penalty)
```

Where `Constraint_Penalty` is computed as:
```
Penalty = min(1.0, (hard_violations × 0.5 + soft_violations × 0.1) × penalty_factor)
```

## Evolutionary Algorithm

### Selection: Tournament Selection
- Pick `k=3` random candidates from the feasible pool
- Select the highest-scoring as a parent
- If no feasible candidates exist, select from the full pool

### Crossover: Uniform + List Crossover
- Scalar parameters: randomly inherit from either parent
- List parameters (mesocycles, weeks): single-point crossover at random split point

### Mutation: Random Perturbation
| Parameter | Mutation Delta |
|-----------|---------------|
| Sessions per week | ±1 (bounds: 1-7) |
| Total weeks | ±2-4 (bounds: 4-52) |
| Total sets | ±10-20 avg/week (bounds: 10-200) |
| Mesocycle goal | Random different goal |
| Mesocycle weeks | ±1 (bounds: 2-8) |
| Deload flag | Toggle |

### Elite Preservation
The top `elite_ratio × population_size` candidates are copied unchanged to the next generation.

### Convergence Detection
If the score range among the top 25% of candidates stays below `convergence_threshold` for `max_stall_generations`, the algorithm terminates early.

## Constraint Handling

### Hard Constraints
Violations make a candidate infeasible — it cannot be selected as the final solution but still participates in evolution.

### Soft Constraints
Violations add penalty to the composite score but don't disqualify the candidate.

### Constraint Types
| Type | Hard Check | Soft Check |
|------|-----------|------------|
| Equipment | Exercise equipment not available | — |
| Frequency | Sessions/week outside range | — |
| Time | Session duration outside range | — |
| Recovery | Rest ratio or consecutive days | — |
| Intent | No mesocycle matches goal | — |
| Nutrition | Calories/protein outside range | — |
| Safety | Volume/week > ceiling | High-volume session ratio |
| Experience | Sets/session > skill limit | — |
| Injury | Targets injured muscle | — |
| Schedule | Total weeks outside range | — |

## Score Interpretation

| Score Range | Label | Meaning |
|-------------|-------|---------|
| 0.80-1.00 | Optimal | Ready for execution |
| 0.50-0.79 | Good | Viable with minor adjustments |
| 0.30-0.49 | Adequate | Plan works but has trade-offs |
| 0.00-0.29 | Poor | Needs redesign or constraint relaxation |

## Planning vs Optimization

| Aspect | Planning Engine | Optimization Engine |
|--------|----------------|-------------------|
| Input | Intent parameters | Macrocycle JSON |
| Output | Single deterministic plan | Multiple candidates, best selected |
| Approach | Rule-based generation | Evolutionary search |
| Objectives | Fixed by design | Configurable weights |
| Constraints | Fixed in validator | Configurable per run |
| Runtime | Instant | Generations × population |
| Determinism | Fully deterministic | Seeded pseudo-random for evolution |
