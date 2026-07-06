# Intent Engine — Processing Pipeline

**RFC-020.9** | Intent Platform | Engine Layer

## Overview

The Intent Engine orchestrates the full intent processing pipeline: build → merge
→ detect conflicts → resolve → validate → score → version. It is stateless —
all state lives in `IntentRepository` and `IntentVersioner`.

## Pipeline Stages

```
Config dict → IntentEngine.full_pipeline()
  │
  ├─ 1. IntentBuilder.build(config)       → UserIntent (immutable)
  ├─ 2. IntentMerger.merge(base, override) → UserIntent (merge rules)
  ├─ 3. ConflictResolver.detect(intent)    → list[IntentConflict]
  ├─ 4. ConflictResolver.resolve(intent)   → UserIntent (conflicts attached)
  ├─ 5. IntentValidator.validate(intent)   → ValidationResult
  ├─ 6. IntentScorer.score(intent)         → float (0–1)
  └─ 7. IntentVersioner.save_version()     → IntentSnapshot
```

## Components

### IntentBuilder
- Single deterministic construction from dict.
- Converts raw strings to enum values (`DayPreference`, `TimeOfDay`, `AdaptiveScope`, etc.).
- Defaults for every field — empty config produces a valid default intent.

### IntentMerger
- Merges two intents: override takes precedence for each sub-profile.
- Lists are replaced entirely when override is non-empty.
- Conflicts from both intents are concatenated.

### ConflictResolver
Detects 6 rule-based conflicts:

| Conflict | Condition | Severity |
|----------|-----------|----------|
| Sessions vs work hours | `sessions > 6 && occupation >= 50h` | HIGH |
| Sleep target vs avg | `sleep_target > avg + 2h` | MEDIUM |
| Protein vs approach | `lean_bulk && protein < 1.6g/kg` | MEDIUM |
| Duration vs frequency | `duration > 90min && sessions >= 5` | LOW |
| Volume vs deload | `max_volume > 25 && auto_deload` | LOW |
| Adaptive scopes vs approval | `require_approval && no scopes` | MEDIUM |

Auto-resolve generates NL resolution strings.

### IntentValidator
Validates 7 groups with ~25 rules:

| Group | Rules |
|-------|-------|
| Goals | At least 1 goal, target > 0, priority 1-10 |
| Timeline | Sessions 1-14, duration 20-180min, valid hours |
| Training | Volume range 4-30, RPE ≤ 10, deload ≥ 3 weeks |
| Nutrition | Protein 1.0-3.5 g/kg, fat ≥ 40g, hydration ≥ 1500ml |
| Recovery | Sleep 5-12h, min ≤ target, deload trigger ≥ 50 |
| Lifestyle | Work hours ≤ 80, capacity check |
| Adaptive | Max change ≥ 0, ≤ 50%, learning ≥ 7 days, data ≥ 3 |

### IntentScorer
Produces 5 weighted sub-scores → composite 0-1:

| Score | Weight | Description |
|-------|--------|-------------|
| Completeness | 25% | How many fields have values |
| Consistency | 25% | Inverse of conflict severity penalty |
| Confidence | 20% | Based on historical compliance rates |
| Stability | 15% | Ratio of resolved to total conflicts |
| Alignment | 15% | Goal-nutrition-training alignment |

### IntentVersioner
- Class-level in-memory version history (ephemeral).
- Semantic versioning (1.0, 2.0, ...) per intent ID.
- Supports rollback to any version (creates new version).

## Engine API

```python
engine = IntentEngine()
intent = engine.build(config)
merged = engine.merge(base, override)
resolved = engine.resolve(intent)
conflicts = engine.detect_conflicts(intent)
validation = engine.validate(intent)
score = engine.score(intent)
snapshot = engine.save_version(intent, "description")
history = engine.get_history(intent_id)
rolled_back = engine.rollback(intent_id, "2.0")
intent, score, validation = engine.build_and_score(config)
intent, score, validation, conflicts = engine.full_pipeline(config)
```
