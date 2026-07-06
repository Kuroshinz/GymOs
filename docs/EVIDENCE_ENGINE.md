# Evidence & Confidence Engine

## Overview

The ConfidenceEngine computes multi-dimensional confidence scores for knowledge records using evidence accumulation, Bayesian statistics, exponential freshness decay, and source reliability analysis. Every knowledge record's confidence score is a weighted combination of three sub-scores, all derived deterministically from its evidence trail.

## Confidence Formula

```
Overall = Bayesian × 0.4 + Freshness × 0.3 + Reliability × 0.3
```

All sub-scores are in [0.0, 1.0], producing an overall score also in [0.0, 1.0].

### Confidence Levels

| Level | Score Range | Numeric Value |
|-------|-------------|---------------|
| VERY_LOW | [0.0, 0.2) | 0.1 |
| LOW | [0.2, 0.4) | 0.3 |
| MEDIUM | [0.4, 0.6) | 0.5 |
| HIGH | [0.6, 0.8) | 0.7 |
| VERY_HIGH | [0.8, 1.0] | 0.9 |

## Evidence Collection

### Evidence Model

```python
@dataclass(frozen=True)
class KnowledgeEvidence:
    evidence_id: str
    knowledge_id: str
    source: str
    evidence_type: EvidenceType
    supports: bool          # True = supporting, False = contradicting
    weight: float           # Magnitude of the evidence (default: 1.0)
    timestamp: str          # ISO-8601 timestamp
    metadata: dict
```

### Evidence Types

| Type | Source Module |
|------|---------------|
| `OPTIMIZATION_RESULT` | Optimizer / Planning Optimizer |
| `PREDICTION_OUTCOME` | Prediction Engine |
| `RECOVERY_OBSERVATION` | Recovery Monitor |
| `NUTRITION_OBSERVATION` | Nutrition Analyzer |
| `DECISION_OUTCOME` | Decision Engine |
| `USER_FEEDBACK` | Direct user input |
| `EXTERNAL_RESEARCH` | External data sources |

### Evidence Weighting

Each piece of evidence carries a `weight` that reflects its significance:

| Scenario | Weight |
|----------|--------|
| Default | 1.0 |
| Optimization with positive reward | `abs(reward)`, clamped to >= 0.1 |
| Optimization with negative reward | `abs(reward)`, clamped to >= 0.1 |
| Prediction with small error | `1.0 / (1.0 + abs(error))` |
| Prediction with zero error | 1.0 |
| Successful recovery | 1.0 |
| Failed recovery | 0.8 |
| Decision outcome with confidence | `confidence` value, clamped to >= 0.1 |

### Evidence Aggregation

Evidence is collected via the orchestrator and appended to the record's evidence list:

```python
def add_evidence(self, evidence: KnowledgeEvidence) -> KnowledgeEvidence:
    collected = self.engine.collect_evidence(evidence)  # assigns ID + timestamp
    kid = collected.knowledge_id
    if kid:
        self._pending_evidence.setdefault(kid, []).append(collected)
        existing = self.repository.get_record(kid)
        if existing is not None:
            updated = replace(
                existing,
                evidence=list(existing.evidence) + [collected],
            )
            self.repository.store_record(updated)
    return collected
```

## Bayesian Score

The Bayesian score uses the posterior mean of a Beta distribution with a uniform prior Beta(1, 1). This is equivalent to Laplace smoothing with pseudocounts of 1.

### Formula

```python
def compute_bayesian_score(self, support_count: int, contradiction_count: int) -> float:
    alpha = support_count + 1      # +1 for uniform prior
    beta = contradiction_count + 1 # +1 for uniform prior
    return alpha / (alpha + beta)
```

Equivalent to:
```
Bayesian = (support + 1) / (support + contradiction + 2)
```

### Behavior

| Support | Contradiction | Bayesian Score | Interpretation |
|---------|---------------|----------------|----------------|
| 0 | 0 | 0.5000 | No evidence → 50% (uniform prior) |
| 10 | 0 | 0.9167 | Strong support |
| 0 | 10 | 0.0833 | Strong contradiction |
| 5 | 5 | 0.5455 | Balanced evidence (slight bias from prior) |
| 10 | 5 | 0.6471 | Moderate support |

### Properties

- **Uniform prior** — With zero evidence, score defaults to 0.5 (maximum uncertainty)
- **Asymptotic** — As evidence accumulates, the prior's influence diminishes
- **Symmetric** — Swapping support↔contradiction produces 1 - score
- **Weighted** — Uses weighted counts (sum of `weight` values), not just raw counts

## Freshness Score

The freshness score measures how recently evidence was collected using exponential decay with a configurable half-life.

### Formula

```python
def compute_freshness_score(self, timestamp: str) -> float:
    age_days = (now - timestamp).total_seconds() / 86400.0
    half_life = self.config.freshness_half_life_days  # default: 30 days
    return exp(-age_days * ln(2) / half_life)
```

Equivalent to:
```
Freshness = exp(-age_days × ln(2) / half_life)
```

### Behavior

| Age | Freshness (30-day half-life) | Freshness (60-day half-life) |
|-----|------|------|
| 0 days | 1.0000 | 1.0000 |
| 7 days | 0.8467 | 0.9231 |
| 15 days | 0.7071 | 0.8409 |
| 30 days | 0.5000 | 0.7071 |
| 60 days | 0.2500 | 0.5000 |
| 90 days | 0.1250 | 0.3536 |
| 365 days | 0.0002 | 0.0148 |

### Edge Cases

| Condition | Score | Reason |
|-----------|-------|--------|
| Future timestamp | 1.0 | Maximum freshness |
| Empty/missing timestamp | 0.0 | No evidence to judge |
| Invalid/parseable timestamp | 0.0 | Corrupt data |
| `enable_freshness_decay = False` | 1.0 | Freshness disabled |
| Self-consistent timestamp on empty evidence | 0.5 (reliability only) | Reliability defaults to 0.5 below min_evidence |

### Half-Life Configuration

```python
config = EvolutionConfig(freshness_half_life_days=60.0)  # slower decay
config = EvolutionConfig(freshness_half_life_days=7.0)   # faster decay
config = EvolutionConfig(enable_freshness_decay=False)    # disable entirely
```

The freshness score uses the **newest** evidence timestamp across all evidence for a record:

```python
def _latest_timestamp(evidence_list):
    valid = [e.timestamp for e in evidence_list if e.timestamp]
    return max(valid) if valid else ""
```

## Reliability Score

The reliability score measures source consistency — how much of the evidence supports versus contradicts the knowledge.

### Formula

```python
def compute_reliability_score(self, evidence_list):
    if len(evidence_list) < self.config.min_evidence_for_confidence:  # default: 3
        return 0.5  # uncertain with insufficient evidence

    support = sum(e.weight for e in evidence_list if e.supports)
    contradiction = sum(e.weight for e in evidence_list if not e.supports)
    total = support + contradiction

    if total <= 0:
        return 0.5
    return support / total
```

### Behavior

| Supporting Weight | Contradicting Weight | Reliability | Interpretation |
|-------------------|---------------------|-------------|----------------|
| 0 | 0 | 0.5 | No evidence → uncertain |
| 5 | 0 | 1.0 | All sources agree |
| 0 | 5 | 0.0 | All sources disagree |
| 3 | 2 | 0.6 | Mostly supportive |
| 2 | 3 | 0.4 | Mostly contradictory |
| < min_evidence | any | 0.5 | Too few items to trust |

### Minimum Evidence Threshold

The configurable `min_evidence_for_confidence` (default: 3) ensures that scores are not overly influenced by sparse data. Below this threshold, reliability defaults to 0.5 (uncertain).

## Overall Confidence Computation

### Full Pipeline

```python
def compute_confidence(self, knowledge_id, evidence_list):
    if total_evidence == 0:
        return KnowledgeConfidence(level=VERY_LOW, score=0.0, ...)

    support_count = sum(e.weight for e in evidence_list if e.supports)
    contradiction_count = sum(e.weight for e in evidence_list if not e.supports)

    freshness_score = self._compute_freshness(latest_timestamp)
    reliability_score = self.compute_reliability_score(evidence_list)
    bayesian_score = self.compute_bayesian_score(support_count, contradiction_count)

    overall = bayesian_score * 0.4 + freshness_score * 0.3 + reliability_score * 0.3
    level = self._score_to_level(overall)

    return KnowledgeConfidence(
        score=overall,
        level=level,
        support_count=support_count,
        contradiction_count=contradiction_count,
        total_evidence=len(evidence_list),
        freshness_score=freshness_score,
        reliability_score=reliability_score,
        ...
    )
```

### Score to Level Mapping

```python
@staticmethod
def _score_to_level(score):
    if score >= 0.8: return ConfidenceLevel.VERY_HIGH
    if score >= 0.6: return ConfidenceLevel.HIGH
    if score >= 0.4: return ConfidenceLevel.MEDIUM
    if score >= 0.2: return ConfidenceLevel.LOW
    return ConfidenceLevel.VERY_LOW
```

### Example Calculations

**Scenario A: Strong recent support**
- 10 supporting, 0 contradicting, all from today
- Bayesian = 11/12 = 0.9167
- Freshness = 1.0 (recent)
- Reliability = 1.0 (all supporting)
- Overall = 0.9167 × 0.4 + 1.0 × 0.3 + 1.0 × 0.3 = 0.9667 → VERY_HIGH

**Scenario B: Mixed evidence, somewhat recent**
- 5 supporting, 3 contradicting, 15 days old
- Bayesian = 6/10 = 0.6000
- Freshness = 0.7071 (15 days with 30-day half-life)
- Reliability = 5/8 = 0.6250
- Overall = 0.6000 × 0.4 + 0.7071 × 0.3 + 0.6250 × 0.3 = 0.6396 → HIGH

**Scenario C: Old contradictory evidence**
- 2 supporting, 8 contradicting, 180 days old
- Bayesian = 3/12 = 0.2500
- Freshness = 0.0156 (180 days with 30-day half-life)
- Reliability = 2/10 = 0.2000
- Overall = 0.2500 × 0.4 + 0.0156 × 0.3 + 0.2000 × 0.3 = 0.1647 → VERY_LOW

**Scenario D: No evidence**
- 0 supporting, 0 contradicting
- Bayesian = 0.5 (uniform prior)
- Freshness = 0.0 (no timestamp)
- Reliability = 0.5 (below min_evidence)
- Overall = 0.5 × 0.4 + 0.0 × 0.3 + 0.5 × 0.3 = 0.3500 → LOW (but marked as VERY_LOW with 0.0 score for empty evidence)

## Confidence Updates

When new evidence arrives after an initial confidence computation, `update_confidence()` accumulates counts and recomputes:

```python
def update_confidence(self, existing_confidence, new_evidence):
    support_count = existing_confidence.support_count + sum(
        e.weight for e in new_evidence if e.supports
    )
    contradiction_count = existing_confidence.contradiction_count + sum(
        e.weight for e in new_evidence if not e.supports
    )
    total_evidence = existing_confidence.total_evidence + len(new_evidence)

    # Recompute all sub-scores from accumulated counts
    freshness_score = self._compute_freshness(latest_timestamp(new_evidence))
    reliability_score = self.compute_reliability_score(
        self._all_evidence_from_counts(support_count, contradiction_count)
    )
    bayesian_score = self.compute_bayesian_score(support_count, contradiction_count)

    overall = bayesian_score * 0.4 + freshness_score * 0.3 + reliability_score * 0.3
    # ...
```

## Confidence Model

```python
@dataclass(frozen=True)
class KnowledgeConfidence:
    confidence_id: str
    knowledge_id: str
    level: ConfidenceLevel
    score: float                # Overall confidence [0.0, 1.0]
    support_count: int          # Weighted sum of supporting evidence
    contradiction_count: int    # Weighted sum of contradicting evidence
    total_evidence: int         # Raw count of evidence items
    freshness_score: float      # Freshness sub-score [0.0, 1.0]
    reliability_score: float    # Reliability sub-score [0.0, 1.0]
    last_updated: str           # ISO-8601 timestamp of last update
```

## Determinism Guarantee

All confidence computations are fully deterministic:

- Same evidence list → Same Bayesian score (same Beta posterior)
- Same timestamp → Same freshness score (same exponential decay)
- Same support/contradiction proportions → Same reliability score
- Same three sub-scores → Same overall score and confidence level

No randomness, no machine learning, no LLM calls are involved in any confidence computation.
