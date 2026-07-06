# Adaptation Strategy Engine

## Overview

`AdaptationStrategyEngine` evaluates 8 independent adaptation strategies against the current `AdaptiveContext` and `AdaptiveStrategy` to produce `AdaptiveRecommendation` objects. Each strategy adapter fires when its trigger conditions are met and returns a recommendation with confidence score, expected improvement, priority, and supporting evidence.

All strategies use `_score_confidence(evidence_count)`:
| Evidence Count | Confidence |
|----------------|------------|
| 0 | 0.1 |
| 1 | 0.4 |
| 2 | 0.6 |
| 3 | 0.8 |
| 4+ | 0.95 |

---

## 1. Volume Adaptation

**Method:** `adapt_volume(strategy, context, config)`

### Increase Rules
| Condition | Threshold | Default |
|-----------|-----------|---------|
| `recovery_score > min_recovery_for_volume_increase` | `config.min_recovery_for_volume_increase` | 0.6 |
| `compliance_rate > min_compliance_for_adaptation` | `config.min_compliance_for_adaptation` | 0.7 |
| `progress_percentage > 0.5` | hardcoded | 0.5 |

**Increase factor** = min of normalized deltas across recovery (0.6→1.0), compliance (0.7→1.0), progress (0.5→1.0), clamped to [0.1, 1.0].

**Change** = `current_volume * max_volume_change_per_week * factor`

**Priority:** MEDIUM

### Decrease Rules
| Condition | Threshold | Factor |
|-----------|-----------|--------|
| `recovery_score < 0.4` | 0.4 | 0.5 (0.75 if < 0.4, 1.0 if < 0.3) |
| `compliance_rate < 0.5` | 0.5 | — |

**Change** = `current_volume * max_volume_change_per_week * factor`, subtracted.

**Priority:** HIGH

### Evidence
- Increase: "High recovery score", "Good compliance rate", "Positive progress"
- Decrease: "Low recovery score (N)", "Low compliance rate (N)"

---

## 2. Frequency Adaptation

**Method:** `adapt_frequency(strategy, context, config)`

### Increase Rules
| Condition | Threshold |
|-----------|-----------|
| `recovery_score > 0.7` | 0.7 |
| `progress_percentage > 0.6` | 0.6 |

**Suggestion:** `current_frequency + 1`

**Expected improvement:** 0.1

**Priority:** MEDIUM

### Decrease Rules
| Condition | Threshold |
|-----------|-----------|
| `fatigue_level > 0.7` | 0.7 |

**Suggestion:** `max(1, current_frequency - 1)`

**Expected improvement:** 0.05

**Priority:** MEDIUM

### Evidence
- Increase: "High recovery (N)", "Good progress (N)"
- Decrease: "High fatigue level (N)"

---

## 3. Exercise Substitution

**Method:** `adapt_exercise_substitution(strategy, context, config)`

### Triggers
| Condition | Details |
|-----------|---------|
| `recovery_score < 0.4` | Low recovery triggers substitution |
| `prediction_progress < 0.2 AND weeks_into_phase >= 3` | Plateau detection |

**Suggestion:** 1.0 (binary — substitute recommended)

**Expected improvement:** 0.15

**Priority:** MEDIUM

### Evidence
- "Low recovery (N)"
- "Progress plateau detected"

---

## 4. Mesocycle Adjustment

**Method:** `adapt_mesocycle(strategy, context, config)`

### Triggers
| Condition | Action | Expected Improvement |
|-----------|--------|---------------------|
| `knowledge_confidence < 0.5` | Restructure (suggested=1.0) | 0.1 |
| `knowledge_confidence > 0.8` | Maintain (suggested=0.0) | 0.0 |

**Priority:** MEDIUM

### Evidence
- "Low knowledge confidence (N)"
- "High knowledge confidence (N)"

---

## 5. Progression Adjustment

**Method:** `adapt_progression(strategy, context, config)`

### Triggers
| Condition | Action | Expected Improvement |
|-----------|--------|---------------------|
| `knowledge_confidence < 0.5` | Adjust scheme (suggested=1.0) | 0.1 |
| `knowledge_confidence > 0.8 AND optimization_insight_score > 0.7` | Maintain (suggested=0.0) | 0.0 |

**Priority:** MEDIUM

### Evidence
- "Low knowledge confidence (N)"
- "High knowledge confidence (N)"
- "Strong optimization insight (N)"

---

## 6. Deload Timing

**Method:** `adapt_deload_timing(strategy, context, config)`

### Triggers
| Condition | Threshold |
|-----------|-----------|
| `fatigue_level > 0.7` | 0.7 |
| `recovery_score < 0.3` | 0.3 |

**Suggestion:** 1.0 (deload recommended)

**Expected improvement:** 0.2

**Priority:** HIGH

### Evidence
- "Elevated fatigue (N)"
- "Low recovery (N)"

---

## 7. Nutrition Target Adjustment

**Method:** `adapt_nutrition_target(strategy, context, config)`

### Phase-Based Rules
| Phase | Suggested | Reason | Expected Improvement |
|-------|-----------|--------|---------------------|
| INITIATION | 0.3 | Baseline nutrition support | 0.08 |
| DEVELOPMENT | 0.5 | Steady nutritional requirements | 0.08 |
| PEAK | 1.0 | Increased nutritional demands | 0.08 |
| DELOAD | 0.8 | Recovery-focused nutrition | 0.08 |
| TRANSITION | 0.6 | Adjusting nutritional strategy | 0.08 |
| MAINTENANCE | 0.4 | Steady nutritional support | 0.08 |

**Priority:** MEDIUM

### Evidence
- Phase-specific evidence strings (e.g. "Peak phase — increased nutritional demands")

---

## 8. Goal Reprioritization

**Method:** `adapt_goal_reprioritization(strategy, context, config)`

### Triggers
| Condition | Details |
|-----------|---------|
| `progress_percentage < 0.1 AND weeks_into_phase >= 2` | Stagnant progress |
| `prediction_progress < 0.1` | Prediction stagnation |

**Suggestion:** 1.0 (reprioritize)

**Expected improvement:** 0.25

**Priority:** HIGH

### Evidence
- "Stagnant progress (N) for N weeks"
- "Low prediction progress (N)"

---

## Strategy Priority Summary

| Strategy | Default Priority |
|----------|------------------|
| Volume (decrease) | HIGH |
| Deload Timing | HIGH |
| Goal Reprioritization | HIGH |
| Volume (increase) | MEDIUM |
| Frequency | MEDIUM |
| Exercise Substitution | MEDIUM |
| Mesocycle Adjustment | MEDIUM |
| Progression Adjustment | MEDIUM |
| Nutrition Target | MEDIUM |

## Configuration Thresholds

All thresholds are configurable via `AdaptiveConfig`:

| Parameter | Default | Used By |
|-----------|---------|---------|
| `min_recovery_for_volume_increase` | 0.6 | Volume increase |
| `max_volume_change_per_week` | 0.2 (20%) | Volume change |
| `max_frequency_change_per_week` | 1 | Frequency change |
| `min_compliance_for_adaptation` | 0.7 | Volume increase |
