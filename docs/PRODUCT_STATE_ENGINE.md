# Product State Engine

The Product State Engine is the runtime "self-awareness" layer of GymOS. It continuously evaluates the product and determines its current operational state by consuming four canonical sources: the Capability Platform, Kernel, Evolution Engine, and Product Knowledge Graph.

## Purpose

The engine answers:
- **What state is GymOS in right now?** → Bootstrapping, Growing, Stable, etc.
- **How confident are we in this assessment?** → 0–100 confidence score
- **Is the product drifting from its ideal state?** → Multi-dimensional drift analysis
- **Is the product ready for release?** → Release readiness assessment
- **What would a transition cost?** → Legal transition determination

## Architecture

```
shared/state/
├── __init__.py       # Public API
├── state.py          # 9 ProductState types with metadata
├── evaluator.py      # StateEvaluator — consumes canonical sources
├── transitions.py    # TransitionEngine — legal transitions + history
├── indicators.py     # IndicatorSet — computes product indicators
├── drift.py          # DriftAnalyzer — 5 drift dimensions
├── confidence.py     # ConfidenceScorer — state/release confidence
├── runtime.py        # StateOrchestrator — unified entry point
├── reports.py        # 5 report generators
└── serializer.py     # JSON/dict serialization
```

## 9 Product States

| State | Meaning | Entry Criteria |
|-------|---------|----------------|
| Bootstrapping | Initial development | Few capabilities complete |
| Growing | Active development | In progress ≥1, completion ≥30% |
| Stable | Core complete | Health ≥60, completion ≥70%, in progress ≤3 |
| Optimizing | Quality focus | Health ≥50, no active dev, few not started |
| Refactoring | Debt reduction | Debt ≥10, health ≥30 |
| Blocked | External blockers | Blocking debt ≥3 or blockers ≥2 |
| Release Candidate | Validation | Health ≥70, readiness ≥70, completion ≥80% |
| Ready for Release | Production | Health ≥85, readiness ≥90 |
| Maintenance | Bug fixes | Complete ≥80%, nothing not started |

## Data Sources

The engine consumes ONLY canonical sources without duplication:
- **Capability Platform** (`shared/capabilities/`) — capability registry, health, dependencies
- **Kernel** (`shared/kernel/`) — product identity, RFCs, releases
- **Evolution Engine** (`shared/evolution/`) — milestones, velocity, forecasts
- **Product Knowledge Graph** (`shared/graph/`) — graph health, impact analysis

## Usage

```python
from shared.state import StateOrchestrator

engine = StateOrchestrator()
state = engine.get_current_state()
print(f"Current state: {state.label}")  # e.g. "Growing"
print(f"Health: {state.overall_health}/100")
print(f"Release readiness: {state.release_readiness}/100")

# Drift analysis
drift = engine.get_drift()
print(f"Overall drift: {drift.overall_drift}/100")

# Confidence assessment
confidence = engine.get_confidence()
print(f"Confidence: {confidence.overall}/100")

# Reports
print(engine.generate_report("state"))
print(engine.generate_report("drift"))
print(engine.generate_report("confidence"))
```
