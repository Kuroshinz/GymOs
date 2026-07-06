# Adaptive Programming Engine

## Purpose

Continuously adapt training strategy in real-time using canonical platform outputs from all NexusOS systems — Intent, Recovery, Prediction, Optimization Knowledge, Knowledge Evolution, Progress, and Compliance. The engine evaluates the current context against 8 adaptation strategies, simulates proposed changes, and applies deterministic, evidence-driven decisions without AI or LLM involvement.

## Architecture

```
┌───────────────────────────────────────────────────────────────────────┐
│                       Canonical Platform Outputs                       │
│  Intent │ Recovery │ Prediction │ Optimization │ Knowledge │ Progress │
└───────────────────────────────┬───────────────────────────────────────┘
                                │
                                ▼
┌─────────────────── AdaptiveMonitorEngine ──────────────────────────┐
│  update_context(updates)  │  check_*() thresholds  │  get_summary() │
└───────────────────────────────────┬──────────────────────────────────┘
                                    │ AdaptiveContext
                                    ▼
┌─────────────── AdaptationStrategyEngine ───────────────────────────┐
│  8 strategy adapters evaluate context → AdaptiveRecommendation[]   │
│  Volume  │  Frequency  │  Exercise  │  Mesocycle                  │
│  Progression  │  Deload  │  Nutrition  │  Goal                     │
└───────────────────────────────────┬──────────────────────────────────┘
                                    │ recommendations
                                    ▼
┌─────────────── AdaptationSimulationEngine ─────────────────────────┐
│  simulate_adaptation() → risk/score  │  simulate_all()  │  compare │
└───────────────────────────────────┬──────────────────────────────────┘
                                    │ scenarios
                                    ▼
┌───────────────── AdaptiveDecisionPolicy ───────────────────────────┐
│  evaluate_recommendation()  │  score_recommendation()             │
│  check_safety()             │  should_rollback()                  │
│  Deterministic │ Rule-based │ Evidence-driven                     │
└───────────────────────────────────┬──────────────────────────────────┘
                                    │ decision
                                    ▼
┌──────────────── AdaptiveProgrammingOrchestrator ───────────────────┐
│  approve/reject/rollback  │  apply  │  snapshot  │  metrics/reports│
└───────────────────────────────────┬──────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────┐
│  Repository (append-only)  │  History  │  Metrics  │  Serializers  │
└────────────────────────────────────────────────────────────────────┘
```

## Components

### AdaptiveMonitorEngine
- Continuously ingests updates from all platform sources
- Maintains `AdaptiveContext` — a frozen dataclass with all monitored inputs
- Provides `check_*()` threshold methods for recovery, prediction, knowledge, compliance, and progress
- Generates `get_monitor_summary()` for full status snapshot

### AdaptationStrategyEngine
- Evaluates 8 independent strategy adapters against current context
- Each adapter returns `Optional[AdaptiveRecommendation]` with confidence scoring
- `_score_confidence()` maps evidence count (1–4+) to confidence (0.1–0.95)
- Uses configurable thresholds from `AdaptiveConfig`

### AdaptiveDecisionPolicy
- Deterministic rule-based evaluation engine
- 6 sequential rules for approval/rejection
- Composite scoring formula: `confidence*0.4 + expected_improvement*0.3 + recovery*0.15 + compliance*0.15`
- Safety checks for volume/frequency change limits and scenario score thresholds
- Rollback detection via outcome drop > 0.2 or outcome < 0.5

### AdaptationSimulationEngine
- Simulates each recommendation before approval
- Identifies 6 risk factors (recovery, fatigue, compliance, confidence, change magnitude, knowledge)
- Computes scenario score = `expected_improvement * (1 - risk_penalty)`
- Sorts scenarios by score for comparison

## 8 Adaptation Strategies

| # | Strategy | Trigger | Priority |
|---|----------|---------|----------|
| 1 | **Volume** — Increase when recovery > 0.6, compliance > 0.7, progress > 0.5; decrease when recovery < 0.4 or compliance < 0.5 | Context thresholds | MEDIUM / HIGH |
| 2 | **Frequency** — Increase when recovery > 0.7 and progress > 0.6; decrease when fatigue > 0.7 | Recovery, progress, fatigue | MEDIUM |
| 3 | **Exercise Substitution** — When recovery < 0.4 or plateau detected (prediction < 0.2, weeks >= 3) | Recovery, prediction | MEDIUM |
| 4 | **Mesocycle Adjustment** — Restructure when knowledge confidence < 0.5; maintain when > 0.8 | Knowledge confidence | MEDIUM |
| 5 | **Progression Adjustment** — Adjust scheme when knowledge confidence < 0.5; maintain when > 0.8 with strong optimization insight | Knowledge, optimization | MEDIUM |
| 6 | **Deload Timing** — When fatigue > 0.7 or recovery < 0.3 | Fatigue, recovery | HIGH |
| 7 | **Nutrition Target** — Phase-based: peak (1.0), deload (0.8), transition (0.6), development (0.5), maintenance (0.4), initiation (0.3) | Current phase | MEDIUM |
| 8 | **Goal Reprioritization** — When progress stagnant (< 0.1 for >= 2 weeks) or prediction stagnant (< 0.1) | Progress, prediction | HIGH |

## Usage Examples

```python
from shared.adaptive_programming import (
    AdaptiveProgrammingOrchestrator,
    AdaptiveContext,
    AdaptiveStrategy,
    AdaptiveConfig,
    StrategyPhase,
)

# Initialize
orchestrator = AdaptiveProgrammingOrchestrator()
config = AdaptiveConfig()

# Start with a strategy and context
strategy = AdaptiveStrategy(
    strategy_id="strat_abc123",
    user_id="user_456",
    phase=StrategyPhase.DEVELOPMENT,
    base_volume=100.0,
    base_frequency=4,
    current_volume=100.0,
    current_frequency=4,
)
context = AdaptiveContext(
    context_id="ctx_001",
    recovery_score=0.75,
    compliance_rate=0.85,
    progress_percentage=0.6,
    fatigue_level=0.3,
)

# Update context with new platform data
context = orchestrator.update_context(context, {
    "recovery_score": 0.82,
    "progress_percentage": 0.68,
})

# Evaluate all strategies → get recommendations
recommendations = orchestrator.evaluate_strategies(strategy, context)
for rec in recommendations:
    print(f"[{rec.priority.label}] {rec.adaptation_type.label}: {rec.reason}")

# Simulate recommendations
scenarios = orchestrator.simulate_recommendations(recommendations, context)
for sc in sorted(scenarios, key=lambda s: s.score, reverse=True):
    print(f"  Scenario {sc.adaptation_type.label}: score={sc.score:.3f}, safe={sc.is_safe}")

# Approve a recommendation (with safety check)
decision = orchestrator.approve_decision(recommendations[0], context, strategy)
if decision.status.label == "Approved":
    history, updated_strategy = orchestrator.apply_adaptation(decision, strategy)
    print(f"Applied: {decision.adaptation_type.label} ({decision.previous_value} → {decision.new_value})")

# Rollback if needed
if config.enable_rollback:
    rolled_back, reverted = orchestrator.rollback_decision(
        decision, updated_strategy, "Outcome drop detected"
    )

# Create point-in-time snapshot
snapshot = orchestrator.create_snapshot(strategy, [decision], recommendations, context)

# Compute metrics
plan = AdaptivePlan(strategy=strategy, decisions=[decision])
metrics = orchestrator.compute_metrics(plan)
print(f"Success rate: {metrics.success_rate:.2f}, Stability: {metrics.strategy_stability:.2f}")

# Generate reports
print(orchestrator.generate_adaptive_report(plan))
```

## Integration with All Platforms

| Platform | Source | Context Field | Monitor Method |
|----------|--------|---------------|----------------|
| **Intent** | `intent` | `intent_goal` | `check_intent_changes()` |
| **Recovery** | `recovery` | `recovery_score` | `check_recovery_status()` |
| **Prediction** | `prediction` | `prediction_progress` | `check_prediction_progress()` |
| **Optimization Knowledge** | `optimization_knowledge` | `optimization_insight_score` | — |
| **Knowledge Evolution** | `knowledge_evolution` | `knowledge_confidence` | `check_knowledge_confidence()` |
| **Progress** | `progress` | `progress_percentage` | `check_progress()` |
| **Compliance** | `compliance` | `compliance_rate` | `check_compliance()` |

All platforms feed into `AdaptiveContext` via `AdaptiveMonitorEngine.update_context()`. The orchestrator publishes domain events for every lifecycle step, enabling reactive integration with any subscriber.

## Decision Policy

The `AdaptiveDecisionPolicy` is:

- **Deterministic** — Same inputs always produce the same decision
- **Rule-based** — 6 sequential rules evaluated in order
- **Evidence-driven** — Every decision records its trigger source, threshold, and supporting evidence

### Evaluation Rules

1. REJECT if max concurrent adaptations exceeded (default: 3)
2. REJECT if compliance rate below minimum (default: 0.7)
3. REJECT if same adaptation type already active (cooldown)
4. APPROVE unconditionally for CRITICAL priority
5. APPROVE if confidence >= 0.7 and expected improvement > 0
6. Fall through to score-based: score >= 0.5 → APPROVE, else REJECT

### Scoring Formula

```
score = confidence * 0.4 + expected_improvement * 0.3
        + (1 - |recovery - 0.5| * 2) * 0.15
        + compliance * 0.15
```

## File Structure

```
shared/adaptive_programming/
├── __init__.py              # AdaptiveProgrammingOrchestrator + public API
├── domain.py                # Frozen dataclass models + enums + AdaptiveConfig
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
└── tests/                   # 9 test files (6900+ lines)
    ├── test_domain.py
    ├── test_edge_cases.py
    ├── test_engines.py
    ├── test_events.py
    ├── test_full_pipeline.py
    ├── test_infrastructure.py
    ├── test_integration.py
    ├── test_orchestrator.py
    └── test_scenarios.py
```
