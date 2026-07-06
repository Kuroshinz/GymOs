# Confidence Model

## Overview

The Confidence Engine aggregates confidence from multiple platform sources into a single decomposable score. Every confidence score is fully transparent — you can see which components contributed, which are strongest, and which are weakest.

## ConfidenceBreakdown

```python
@dataclass
class ConfidenceBreakdown:
    prediction: float = 0.0
    knowledge_quality: float = 0.0
    recovery_quality: float = 0.0
    planning_certainty: float = 0.0
    evidence_strength: float = 0.0
```

### Properties

| Property | Returns |
|---|---|
| `overall` | Weighted average (see weights below) |
| `weakest` | `(component_name, value)` tuple |
| `strongest` | `(component_name, value)` tuple |

## Weighting

| Component | Weight | Source |
|---|---|---|
| Prediction | 25% | Prediction engine confidence scores |
| Knowledge Quality | 20% | Knowledge evolution confidence metrics |
| Recovery Quality | 15% | Recovery score quality |
| Planning Certainty | 15% | Planning validation certainty |
| Evidence Strength | 25% | Average item confidence × source diversity |

## ConfidenceResult

```python
@dataclass
class ConfidenceResult:
    overall: float
    breakdown: ConfidenceBreakdown | None
    evidence_count: int
    source_count: int
    timestamp: str
```

## ConfidenceEngine API

| Method | Description |
|---|---|
| `aggregate(evidence_items)` | Compute aggregate confidence from evidence |
| `compute_from_chain(chain)` | Compute confidence from a reasoning chain |
| `clear_results()` | Clear historical results |

### Aggregation Logic

1. **Per-source average** — for each source, compute mean confidence of its evidence items
2. **Evidence strength** — `avg_confidence × 0.6 + diversity × 0.4` where diversity = `min(1, source_count / 4)`
3. **Weighted overall** — sum of each component × its weight

### Chain Confidence

When computing from a reasoning chain:
1. Average node confidences boost the prediction component
2. Evidence items count boosts evidence strength (capped at 10 items = 1.0)
3. Chain confidence is blended into the existing breakdown

## Interpretation

| Overall Score | Interpretation |
|---|---|
| 0.8 – 1.0 | High confidence — strong evidence across multiple sources |
| 0.5 – 0.8 | Moderate confidence — some evidence, potential gaps |
| 0.2 – 0.5 | Low confidence — limited or conflicting evidence |
| 0.0 – 0.2 | Very low confidence — insufficient evidence |
