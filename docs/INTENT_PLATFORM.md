# Intent Platform — RFC-020.9

**Status**: Complete | **Maturity**: Implemented | **Version**: 0.5.0
**Test Count**: 183 | **Health**: 80/100

## Purpose

The Intent Platform provides the canonical user intent model for GymOS —
a declarative, deterministic specification of what a user wants to achieve and
how. All downstream decisions (training program, nutrition plan, recovery
schedule, predictions) should derive from Intent, not from raw data.

## Architecture

```
shared/intent/
├── __init__.py      # Public API — re-exports all intent symbols
├── domain.py        # 15 domain entities + 15 enums
├── builder.py       # IntentBuilder — deterministic dict→Intent
├── merger.py        # IntentMerger + ConflictResolver (6 rules)
├── versioner.py     # IntentVersioner — snapshot history
├── scorer.py        # IntentScorer — 5 weighted sub-scores
├── validator.py     # IntentValidator — 7 groups, ~25 rules
├── engine.py        # IntentEngine — orchestrator
├── repository.py    # IntentRepository — in-memory CRUD
├── serializer.py    # IntentSerializer — dict/JSON roundtrip
├── metrics.py       # IntentMetrics + IntentHealthScore
├── report.py        # IntentReport — markdown/JSON reporting
├── state.py         # IntentState — platform snapshot
└── tests/           # 183 tests across 12 test files
```

## Key Properties

- **Deterministic**: Same inputs always produce the same output.
- **Stateless**: Engines are stateless; all state in Repository/Versioner.
- **Immutable**: `UserIntent` is a frozen dataclass — never mutated.
- **Composable**: Pipeline stages can be used independently or chained.
- **Type-safe**: Enums for all categorical values prevent invalid states.

## Integration

Intent Platform is a cross-cutting **platform capability**, not a module.
It lives in `shared/intent/` and is consumed by:

- `prediction-engine` — future predictions conditioned on intent
- `decision-intelligence` — program recommendations aligned with intent
- `ai-coach` — coaching advice respecting user constraints and preferences

## Dependencies

- `capability-platform` — for capability registration

## Documentation

- [Intent Model Reference](INTENT_MODEL.md) — domain entities and enums
- [Intent Engine Reference](INTENT_ENGINE.md) — pipeline components and API
- [ADR-011: Intent Platform Architecture](architecture/ADR-011-intent-platform.md)
