# Optimization Model

## Domain Models

### OptimizationRequest
The input to any optimization run. Contains the base plan (as JSON), objectives, constraints, and evolutionary parameters.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `request_id` | str | "" | Unique identifier |
| `base_plan_json` | str | "" | Serialized Macrocycle to optimize |
| `objectives` | list[OptimizationObjective] | [] | Weighted optimization goals |
| `constraints` | list[OptimizationConstraint] | [] | Hard/soft constraints |
| `population_size` | int | 20 | Candidates per generation |
| `max_generations` | int | 10 | Maximum evolutionary cycles |
| `mutation_rate` | float | 0.2 | Probability of mutation |
| `crossover_rate` | float | 0.5 | Probability of crossover |
| `elite_ratio` | float | 0.1 | Fraction of top candidates preserved |

### OptimizationObjective
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `objective_type` | ObjectiveType | HYPERTROPHY | Which goal to optimize |
| `weight` | float | 1.0 | Relative importance |
| `target_value` | float | None | Desired score threshold |
| `is_primary` | bool | False | Primary objective for tie-breaking |

### OptimizationConstraint
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `constraint_type` | ConstraintType | TIME | Which constraint to check |
| `max_value` | float | None | Upper bound |
| `min_value` | float | None | Lower bound |
| `value` | Any | None | Complex constraint data (e.g., equipment list) |
| `is_hard` | bool | True | Hard constraints invalidate candidates |
| `description` | str | "" | Human-readable description |

### OptimizationScore
| Field | Type | Description |
|-------|------|-------------|
| `scientific_score` | float | Progression and volume quality (0-1) |
| `recovery_score` | float | Recovery and fatigue management (0-1) |
| `hypertrophy_score` | float | Hypertrophy stimulus (0-1) |
| `compliance_score` | float | Adherence likelihood (0-1) |
| `risk_score` | float | Inverse of plateau/injury risk (0-1) |
| `overall` | float | Weighted composite (0-1) |

### OptimizationCandidate
| Field | Type | Description |
|-------|------|-------------|
| `candidate_id` | str | Unique identifier |
| `macrocycle_json` | str | Serialized candidate plan |
| `scores` | OptimizationScore | Computed quality scores |
| `mutations` | list[str] | Mutation history |
| `generation` | int | Which generation this belongs to |
| `rank` | int | Rank within population |
| `status` | CandidateStatus | active/dominated/infeasible/selected |
| `is_feasible` | bool | Passes all hard constraints |

### OptimizationResult
| Field | Type | Description |
|-------|------|-------------|
| `result_id` | str | Unique identifier |
| `request_id` | str | Associated request |
| `best_candidate` | OptimizationCandidate | Highest-scoring feasible plan |
| `all_candidates` | list[OptimizationCandidate] | Every generated candidate |
| `final_score` | float | Best candidate score |
| `total_generations` | int | Generations completed |
| `total_evaluated` | int | Total candidates evaluated |
| `feasible_count` | int | Number of feasible candidates |
| `success_rate` | float | Feasible / Total ratio |

## Enums

### ObjectiveType (10 values)
`MAXIMIZE_HYPERTROPHY`, `MINIMIZE_FATIGUE`, `MAXIMIZE_RECOVERY`, `MAXIMIZE_ADHERENCE`, `MINIMIZE_PLATEAU_RISK`, `MINIMIZE_INJURY_RISK`, `MAXIMIZE_STRENGTH`, `MAXIMIZE_ENDURANCE`, `BALANCE_VOLUME`, `MAXIMIZE_PROGRESSION`

### ConstraintType (10 values)
`EQUIPMENT`, `FREQUENCY`, `TIME`, `RECOVERY`, `INTENT`, `NUTRITION`, `SAFETY`, `EXPERIENCE`, `INJURY`, `SCHEDULE`

### CandidateStatus (4 values)
`ACTIVE`, `DOMINATED`, `INFEASIBLE`, `SELECTED`

### OptimizerStatus (5 values)
`PENDING`, `RUNNING`, `COMPLETED`, `FAILED`, `PARTIAL`

## Config

| Parameter | Default | Description |
|-----------|---------|-------------|
| `default_population_size` | 20 | Default candidates per generation |
| `default_max_generations` | 10 | Default max evolutionary cycles |
| `default_mutation_rate` | 0.2 | Default mutation probability |
| `default_crossover_rate` | 0.5 | Default crossover probability |
| `default_elite_ratio` | 0.1 | Default elite preservation |
| `max_candidates` | 500 | Hard cap on total candidates |
| `convergence_threshold` | 0.01 | Early stop when improvement stalls |
| `max_stall_generations` | 3 | Generations of stalling before early stop |
| `enable_early_stop` | True | Allow early convergence detection |
| `enable_diversity_maintenance` | True | Periodically inject random mutations |
| `constraint_penalty_factor` | 0.3 | How much violations reduce score |
