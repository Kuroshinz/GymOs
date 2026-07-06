# Evidence Graph

## Overview

The Evidence Graph collects structured evidence from all 8 GymOS engines. Evidence is typed, sourced, and confidence-scored, providing the foundation for reasoning chains and confidence aggregation.

## EvidenceItem

```python
@dataclass
class EvidenceItem:
    evidence_id: str
    source: EvidenceSource    # Which engine produced this
    evidence_type: EvidenceType
    label: str
    value: Any = None
    confidence: float = 0.0
    supporting_ids: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=utc_now)
    metadata: dict = field(default_factory=dict)
```

## EvidenceSource

| Source | Engines |
|---|---|
| `DECISION_ENGINE` | Rule evaluation, recommendations, analyses |
| `PREDICTION` | Forecasts, ETAs, plateau/deload predictions |
| `RECOVERY` | Scores, readiness, fatigue, deload recommendations |
| `PLANNING` | Macrocycles, mesocycles, session plans, allocations |
| `INTENT` | Goals, preferences, constraints, priorities |
| `KNOWLEDGE` | Knowledge records, evidence, confidence, conflicts |
| `ADAPTIVE` | Adaptation recommendations, decisions, scenarios |
| `OPTIMIZATION` | Optimization candidates, patterns, insights, rules |

## EvidenceType

- `RECOMMENDATION` — A recommendation from any engine
- `PREDICTION` — A forecast or prediction
- `SCORE` — A numeric score or rating
- `ANALYSIS` — An analytical result or report
- `CONSTRAINT` — A constraint or violation
- `RULE` — A deterministic rule evaluation
- `PATTERN` — A mined pattern from optimization knowledge
- `INSIGHT` — A derived insight
- `DECISION` — An approved/rejected/rolled-back decision
- `GOAL` — A goal or intent

## EvidenceGraph API

| Method | Description |
|---|---|
| `add_evidence(item)` | Add an evidence item |
| `add_from_event(event)` | Auto-detect source/type from DomainEvent, add item |
| `get_evidence(id)` | Lookup by ID |
| `query(source, type, min_confidence)` | Filtered query |
| `get_by_source(source)` | All items from a source |
| `get_by_type(type)` | All items of a type |
| `get_all()` | All items |
| `clear()` | Remove all items |
| `to_dict()` | Serialize to dict |

### Properties

| Property | Returns |
|---|---|
| `size` | Item count |
| `sources` | Set of unique sources |
| `types` | Set of unique types |

## Event Collection

The `add_from_event` method auto-detects evidence source by scanning the event name:

| Event Name Contains | Detected Source |
|---|---|
| `decision`, `recommendation`, `rule` | DECISION_ENGINE |
| `prediction`, `forecast`, `plateau`, `eta` | PREDICTION |
| `recovery`, `readiness`, `deload`, `fatigue` | RECOVERY |
| `plan`, `macrocycle`, `mesocycle`, `session`, `allocation` | PLANNING |
| `intent`, `goal`, `preference` | INTENT |
| `knowledge`, `evidence`, `confidence`, `conflict`, `version` | KNOWLEDGE |
| `adaptive`, `adaptation`, `scenario`, `strategy` | ADAPTIVE |
| `optimization`, `candidate`, `generation`, `experience`, `pattern`, `insight` | OPTIMIZATION |
