# Adaptive Decision Policy

## Overview

`AdaptiveDecisionPolicy` is a **deterministic, rule-based, evidence-driven** policy engine that evaluates, scores, and safety-checks adaptive programming recommendations. No AI, no LLM, no randomness — every decision is fully explainable and reproducible.

---

## Deterministic Evaluation Rules

Rules are evaluated **in order**. The first matching rule produces an immediate APPROVE or REJECT decision.

### Rule 1 — Concurrent Adaptation Limit
```
IF active_decisions >= config.max_concurrent_adaptations (default: 3)
→ REJECT
Reason: "Max concurrent adaptations (N) already active"
```

### Rule 2 — Minimum Compliance
```
IF context.compliance_rate < config.min_compliance_for_adaptation (default: 0.7)
→ REJECT
Reason: "Compliance rate X below minimum Y"
```

### Rule 3 — Adaptation Cooldown (per type)
```
IF any active decision has same adaptation_type as current recommendation
→ REJECT
Reason: "Adaptation type 'X' is in cooldown; active decision Y already in progress"
```

### Rule 4 — Critical Priority Bypass
```
IF rec.priority == RecommendationPriority.CRITICAL
→ APPROVE unconditionally
Reason: "CRITICAL priority — approved unconditionally"
```

### Rule 5 — High Confidence + Positive Improvement
```
IF rec.confidence >= 0.7 AND rec.expected_improvement > 0
→ APPROVE
Reason: "Confidence X >= 0.7 and expected improvement Y > 0"
```

### Rule 6 — Score-Based Fallthrough
```
Compute score via composite formula (see below)
IF score >= 0.5
→ APPROVE, Reason: "Score X >= 0.5"
ELSE
→ REJECT, Reason: "Score X < 0.5"
```

---

## Scoring Formula

```
score = (confidence * 0.4)
      + (expected_improvement * 0.3)
      + ((1 - abs(recovery_score - 0.5) * 2) * 0.15)
      + (compliance_rate * 0.15)
```

Result is clamped to [0.0, 1.0].

### Weight Justification

| Component | Weight | Rationale |
|-----------|--------|-----------|
| Confidence | 0.40 | Highest weight — reflects evidence quality supporting the recommendation |
| Expected Improvement | 0.30 | Measures potential upside of the adaptation |
| Recovery Alignment | 0.15 | `1 - |recovery - 0.5| * 2` peaks at 1.0 when recovery is balanced (0.5) |
| Compliance Rate | 0.15 | Higher compliance increases likelihood of successful adaptation |

### Example Scores

| Scenario | Confidence | Exp. Improvement | Recovery | Compliance | Score | Decision |
|----------|-----------|-----------------|----------|------------|-------|----------|
| Strong ALL | 0.90 | 0.50 | 0.80 | 0.95 | 0.82 | APPROVE |
| Low confidence | 0.30 | 0.10 | 0.60 | 0.80 | 0.35 | REJECT |
| Edge case | 0.50 | 0.30 | 0.50 | 0.70 | 0.52 | APPROVE |

---

## Safety Checks

After a recommendation passes evaluation, `check_safety()` validates the simulated scenario before final approval.

### Volume Change Check
```
IF abs(proposed - current) > config.max_volume_change_per_week (default: 0.2)
→ Risk factor: "Volume change X exceeds max Y per week"
```

### Frequency Change Check
```
IF abs(int(proposed - current)) > config.max_frequency_change_per_week (default: 1)
→ Risk factor: "Frequency change X exceeds max Y per week"
```

### Scenario Score Check
```
IF scenario.score < config.safety_threshold (default: 0.3)
→ Risk factor: "Scenario score X below safety threshold Y"
```

A scenario is **safe** only when **zero risk factors** are identified. Any risk factor causes rejection.

---

## Rollback Criteria

`should_rollback(decision, current_outcome)` determines whether a previously approved decision should be reversed.

### Outcome Drop Rule
```
IF (decision.score - current_outcome) > 0.2
→ Rollback: "Outcome dropped X (> 0.2) from Y to Z"
```

### Outcome Floor Rule
```
IF current_outcome < 0.5
→ Rollback: "Compliance/outcome X dropped below 0.5 after adaptation"
```

Rollback is gated by `config.enable_rollback` (default: `True`).

---

## Cooldown Mechanism

| Mechanism | Implementation |
|-----------|---------------|
| **Per-type cooldown** | Same adaptation type cannot have multiple concurrent active decisions |
| **Configurable** | `config.adaptation_cooldown_days` (default: 14) available for future time-based cooldown |
| **Active decision tracking** | `strategy.active_decisions` list is checked for matching types |

---

## Concurrent Adaptation Limits

| Parameter | Default | Behavior |
|-----------|---------|----------|
| `max_concurrent_adaptations` | 3 | Reject new recommendations when N active decisions exist |

Active decisions are those with status `APPROVED` or `COMPLETED` mixed into the strategy's active list.

---

## Explainable Adaptation Reasons

Every decision carries an `AdaptationReason` with full explainability:

```
AdaptationReason
├── reason_id          — Unique identifier
├── adaptation_type    — Which strategy triggered (volume, frequency, etc.)
├── trigger_source     — Which platform source (MonitorSource enum)
├── trigger_value      — The value that triggered the decision
├── threshold_value    — The threshold that was compared against
├── description        — Human-readable explanation string
└── evidence[]         — List of supporting evidence strings
```

### Example Reasons

```
"Confidence 0.85 >= 0.7 and expected improvement 0.1200 > 0"
"Increase volume by 15% due to favorable recovery (0.78), compliance (0.82), and progress (0.65)"
"Deload recommended: Elevated fatigue (0.75)"
"Goal reprioritization recommended: Stagnant progress (0.05) for 3 weeks"
"Score 0.3240 < 0.5"
"Max concurrent adaptations (3) already active"
"Outcome dropped 0.4500 (> 0.2) from 0.8500 to 0.4000 after adaptation"
```
