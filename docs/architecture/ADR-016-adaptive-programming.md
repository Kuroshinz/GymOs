# ADR-016: Adaptive Programming Engine

## Status

Accepted

## Context

The NexusOS ecosystem produces canonical platform outputs across multiple systems — Intent, Recovery, Prediction, Optimization Knowledge, Knowledge Evolution, Progress, and Compliance. However, these outputs were consumed in isolation without a unified mechanism to **continuously adapt the training strategy** based on the aggregate signal.

Key gaps identified:

1. **No real-time strategy adaptation** — The training strategy (volume, frequency, exercise selection, progression) was static between manual interventions
2. **No simulation before adaptation** — Changes were applied without simulating their expected impact
3. **No deterministic policy** — No rule-based system to evaluate, score, and approve/reject adaptations
4. **No evidence trail** — Adaptation decisions lacked explainable reasons, trigger sources, and supporting evidence
5. **No versioned adaptation history** — No immutable record of what changed, when, and why
6. **No cooldown or concurrency control** — No safeguards against rapid or overlapping adaptations
7. **No cross-platform integration** — Each platform's data was used in isolation, not synthesized into a unified adaptation decision

## Decision

Create a new `adaptive_programming` module within the `shared/` layer that provides a complete adaptation pipeline: monitor inputs → evaluate strategies → simulate outcomes → apply decisions → record history.

### Architecture

```
AdaptiveProgrammingOrchestrator
├── AdaptiveMonitorEngine       — Ingests platform outputs into AdaptiveContext
├── AdaptationStrategyEngine    — 8 strategy adapters → recommendations
├── AdaptiveDecisionPolicy      — Rule-based evaluation, scoring, safety
├── AdaptationSimulationEngine  — Simulate & score scenarios pre-approval
├── AdaptiveProgrammingRepository  — Append-only immutable store
├── AdaptiveMetricsCalculator   — Quality metrics from plan + decisions
├── AdaptiveReportGenerator     — Human-readable reports
├── AdaptationHistoryTracker    — Immutable adaptation event records
└── Serializers                 — Full dict/JSON round-trip for all models
```

### Domain Models

All models are frozen dataclasses for immutability:

| Model | Purpose |
|-------|---------|
| `AdaptiveContext` | Current monitored state from all platforms |
| `AdaptationReason` | Explainable trigger with source, thresholds, evidence |
| `AdaptiveDecision` | Decision with lifecycle (pending→approved→completed/rolled_back) |
| `AdaptiveRecommendation` | Strategy adapter output before approval |
| `AdaptationHistory` | Immutable record of completed adaptations |
| `AdaptationSnapshot` | Point-in-time full state capture |
| `AdaptiveStrategy` | Current training strategy with active adaptations |
| `AdaptivePlan` | Complete user plan — strategy + decisions + history |
| `AdaptationScenario` | Simulated outcome with score and risk factors |
| `AdaptiveMetrics` | Aggregate quality metrics |
| `AdaptiveConfig` | All configurable thresholds and toggles |

### Enums

- `AdaptationType`: 8 types (volume, frequency, exercise_substitution, mesocycle_adjustment, progression_adjustment, deload_timing, nutrition_target, goal_reprioritization)
- `DecisionStatus`: 5 statuses (pending, approved, rejected, rolled_back, completed)
- `StrategyPhase`: 6 phases (initiation, development, peak, deload, transition, maintenance)
- `RecommendationPriority`: 4 levels (critical, high, medium, low)
- `MonitorSource`: 7 sources (intent, recovery, prediction, optimization_knowledge, knowledge_evolution, progress, compliance)

### 8 Adaptation Strategies

| # | Strategy | Triggers | Priority |
|---|----------|----------|----------|
| 1 | Volume | Recovery, compliance, progress thresholds | MEDIUM/HIGH |
| 2 | Frequency | Recovery, progress, fatigue thresholds | MEDIUM |
| 3 | Exercise Substitution | Low recovery, plateau detection | MEDIUM |
| 4 | Mesocycle Adjustment | Knowledge confidence | MEDIUM |
| 5 | Progression Adjustment | Knowledge confidence, optimization insight | MEDIUM |
| 6 | Deload Timing | High fatigue, low recovery | HIGH |
| 7 | Nutrition Target | Phase-based (6 phases) | MEDIUM |
| 8 | Goal Reprioritization | Stagnant progress, stagnant prediction | HIGH |

### Decision Policy

6 sequential deterministic rules:
1. Reject if max concurrent adaptations exceeded (default: 3)
2. Reject if compliance below minimum (default: 0.7)
3. Reject if same adaptation type in cooldown
4. Approve unconditionally for CRITICAL priority
5. Approve if confidence >= 0.7 and expected improvement > 0
6. Fall through to score-based: score >= 0.5 approve, else reject

### Domain Events

8 event types published during the adaptation lifecycle, registered in `ADAPTIVE_PROGRAMMING_EVENT_REGISTRY`:

| Event | When Emitted |
|-------|-------------|
| `ContextUpdated` | Context merged with new platform data |
| `RecommendationGenerated` | Strategy adapter produces a recommendation |
| `DecisionApproved` | Recommendation passes evaluation + safety check |
| `DecisionRejected` | Recommendation fails evaluation or safety |
| `DecisionRolledBack` | Previously approved decision is reversed |
| `AdaptationApplied` | Approved decision is applied to strategy |
| `StrategyPhaseChanged` | Strategy phase transitions |
| `ScenarioSimulated` | A scenario is simulated (for each recommendation) |

### No AI/LLM

All computations are deterministic:
- Strategy triggers = threshold comparisons
- Confidence mapping = evidence count → fixed confidence values
- Scoring = weighted linear formula
- Safety = threshold comparisons
- Rollback = outcome drop comparison
- Simulation = risk factor penalty formula
- All deterministic, explainable, and reproducible

## Consequences

### Positive

1. **Continuous adaptation** — Training strategy adjusts in real-time as platform signals change
2. **Deterministic decisions** — Same inputs always produce same outputs; no randomness
3. **Fully explainable** — Every decision records trigger source, threshold, value, and evidence list
4. **Simulation before action** — All adaptations are simulated and safety-checked before approval
5. **Versioned history** — Every adaptation is immutably recorded with full audit trail
6. **Concurrency protection** — Cooldown and concurrent adaptation limits prevent rapid overlapping changes
7. **Cross-platform integration** — All 7 platform sources feed into a unified context
8. **518+ tests** — Comprehensive coverage across 9 test files (6900+ lines)
9. **Full serialization** — Every model has dict/JSON round-trip serializers
10. **Configurable** — All thresholds, limits, and toggles in `AdaptiveConfig`

### Negative

1. **In-memory repository** — Current implementation stores data in memory; no persistent database backend
2. **Simple conflict detection** — No cross-recommendation conflict resolution beyond per-type cooldown
3. **No time-based cooldown yet** — Cooldown is currently based on active decisions only (config field reserved)
4. **No external persistence** — Serialization to dict/JSON must be managed by the caller
5. **Linear scoring only** — Scoring formula is a fixed weighted sum; no non-linear or learned weights

### Neutral

1. **Opinionated thresholds** — Default thresholds chosen for general fitness; may need tuning per user
2. **Phase-based nutrition** — Nutrition targets are phase-derived; individual variation not modeled

## Technical Notes

- All domain models are frozen dataclasses with `from __future__ import annotations`
- `AdaptiveConfig` is a frozen dataclass with 10 configurable parameters and sensible defaults
- Event registry enables runtime deserialization of any domain event
- `MonitorSource` enum supports future platform additions without schema changes
- Recommendation confidence is evidence-count-based (0.1–0.95) not AI-generated
- Safety threshold (`0.3`) is independent of approval threshold (`0.5`)
- Rollback supports both outcome-drop (>0.2) and absolute-floor (<0.5) criteria
- 518+ tests across 9 test files:
  - `test_domain.py` — Model creation, immutability, property access (625 lines)
  - `test_engines.py` — Strategy adapters, simulation engine (756 lines)
  - `test_orchestrator.py` — Full orchestrator lifecycle (1064 lines)
  - `test_integration.py` — Cross-module integration (625 lines)
  - `test_infrastructure.py` — Repository, serializers, metrics, reports (1098 lines)
  - `test_events.py` — Event creation and registry (213 lines)
  - `test_full_pipeline.py` — End-to-end adaptation pipeline (1270 lines)
  - `test_edge_cases.py` — Boundary conditions (598 lines)
  - `test_scenarios.py` — Scenario simulation (656 lines)

### Related Documents

- [ADAPTIVE_PROGRAMMING.md](../ADAPTIVE_PROGRAMMING.md) — Comprehensive system overview
- [STRATEGY_ENGINE.md](../STRATEGY_ENGINE.md) — 8 strategy adapters with thresholds
- [ADAPTATION_POLICY.md](../ADAPTATION_POLICY.md) — Decision policy and scoring details
- [ADR-010: Predictive Intelligence](../ADR-010-predictive-intelligence.md) — Prediction platform integration
- [ADR-011: Intent Platform](../architecture/ADR-011-intent-platform.md) — Intent platform integration
- [ADR-014: Optimization Knowledge](../architecture/ADR-014-optimization-knowledge.md) — Optimization knowledge integration
- [ADR-015: Knowledge Evolution](../architecture/ADR-015-knowledge-evolution.md) — Knowledge evolution integration

### Module Location

```
shared/adaptive_programming/
├── __init__.py              # AdaptiveProgrammingOrchestrator + public API
├── domain.py                # Domain models + enums + config
├── monitor_engine.py        # AdaptiveMonitorEngine — context ingestion
├── strategy_engine.py       # AdaptationStrategyEngine — 8 strategy adapters
├── decision_policy.py       # AdaptiveDecisionPolicy — rule-based evaluation
├── simulation.py            # AdaptationSimulationEngine — scenario simulation
├── events.py                # 8 domain events + event registry
├── metrics.py               # AdaptiveMetricsCalculator
├── history.py               # AdaptationHistoryTracker
├── repository.py            # AdaptiveProgrammingRepository — append-only store
├── reports.py               # AdaptiveReportGenerator — human-readable reports
├── serializer.py            # Full round-trip serializers for all models
└── tests/                   # 9 test files (6900+ lines, 518+ tests)
```
