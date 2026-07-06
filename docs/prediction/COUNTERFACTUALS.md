# Counterfactual Engine

## "What-If" Philosophy

Counterfactual analysis answers: **"What would happen to my predictions if I changed one behavior?"**

Unlike scenario analysis (which compares many interventions across all metrics), counterfactuals are:
- **Narrow** — each query targets a single behavior change
- **Specific** — concrete deltas (e.g., "sleep 8h instead of 6.5h")
- **Impact-focused** — returns the delta and its significance level

The counterfactual engine implements a **minimal simulation** approach: modify one parameter, re-run the affected engine(s), compute the difference.

---

## Counterfactual Types

Five predefined what-if queries, each targeting a different behavioral lever:

| Type | Behavior Change | Affected Engine | Impact On |
|---|---|---|---|
| `SLEEP` | 6.5h → 8h | RecoveryPredictionEngine | Recovery score |
| `CALORIES` | +250 kcal surplus | BodyweightPredictionEngine | Bodyweight trend |
| `WORKOUT_MISS` | +1 missed session | ConsistencyPredictionEngine | Consistency / completion rate |
| `VOLUME_CHANGE` | +15% chest volume | FatiguePredictionEngine | Fatigue score |
| `DELOAD_NOW` | Immediate deload | RecoveryPredictionEngine | Recovery, PR probability |

Each type has a convenience method on `CounterfactualEngine`:

```python
engine = CounterfactualEngine()
result = engine.evaluate_sleep_8h()
result = engine.evaluate_calories_plus_250()
result = engine.evaluate_miss_workout()
result = engine.evaluate_increase_chest_volume()
result = engine.evaluate_deload_now()
```

---

## Counterfactual Generation

### `evaluate(query, baseline_kwargs) → CounterfactualResult`

The main evaluation method:

1. **Parse query** — extract `CounterfactualType` and parameter deltas
2. **Build baseline** — run the relevant engine with original parameters
3. **Apply change** — modify the parameter(s) according to the query
4. **Run counterfactual** — re-run the same engine with modified parameters
5. **Compute delta** — compare baseline vs counterfactual outputs
6. **Generate explanation** — describe what changed and why

```python
query = CounterfactualQuery(
    cf_type=CounterfactualType.SLEEP,
    parameter="sleep_avg",
    current_value=6.5,
    proposed_value=8.0,
    unit="hours",
)
result = engine.evaluate(query, baseline_kwargs)
```

---

## Simulation Pipeline

```
CounterfactualQuery
  │
  ├─► Baseline engine run (original params)
  │     └─► baseline_prediction
  │
  ├─► Parameter modification
  │     └─► Modified kwargs
  │
  ├─► Counterfactual engine run (modified params)
  │     └─► counterfactual_prediction
  │
  └─► CounterfactualResult
        ├─ absolute_delta
        ├─ percent_delta
        ├─ direction (“increase” / “decrease” / “no_change”)
        ├─ impact_level (“low” / “moderate” / “high”)
        └─ explanation (NL string)
```

### Impact Level Thresholds

| Percent Delta | Impact Level |
|---|---|
| < 10% | Low |
| 10–20% | Moderate |
| ≥ 20% | High |

---

## Baseline vs Counterfactual

The baseline is the **current prediction** using the athlete's actual data. The counterfactual is the **same prediction** with one parameter changed. All other parameters remain identical.

This isolates the effect of the single behavioral change:

```
Baseline:     sleep=6.5h, volume=40sets, calories=300surplus
Counterfactual: sleep=8.0h, volume=40sets, calories=300surplus
                                              ↑ only this changes
```

---

## Prediction Comparison

`CounterfactualResult` captures the full comparison:

```python
@dataclass
class CounterfactualResult:
    query: CounterfactualQuery           # The what-if that was asked
    baseline_prediction: float           # Original prediction value
    counterfactual_prediction: float     # Prediction under change
    absolute_delta: float                # Signed difference
    percent_delta: float                 # Relative difference (%)
    direction: str                       # "increase" | "decrease" | "no_change"
    impact_level: str                    # "high" | "moderate" | "low"
    explanation: str                     # Natural language description
    affected_predictions: list[str]      # Which prediction types were affected
```

All computed fields (`absolute_delta`, `percent_delta`, `direction`, `impact_level`) are auto-calculated in `__post_init__`.

---

## Examples

### Sleep improvement

```python
engine = CounterfactualEngine()
result = engine.evaluate_sleep_8h()
print(f"{result.absolute_delta:+.1f}")       # +3.2 (recovery score increase)
print(f"{result.percent_delta:+.1f}%")        # +4.6%
print(result.impact_level)                    # "low"
print(result.affected_predictions)            # ["Recovery Decline"]
```

### Missed workout

```python
result = engine.evaluate_miss_workout()
print(result.direction)                       # "decrease"
print(result.impact_level)                    # "moderate"
# Explanation: "Missing a workout reduces your consistency streak
#  and completion rate, potentially affecting long-term adherence."
```

### Deload now

```python
result = engine.evaluate_deload_now()
print(result.absolute_delta)                  # Positive (recovery improves)
print(result.impact_level)                    # "high"
# Affects: Recovery, PR probability, fatigue
```

### Evaluate all

```python
results = engine.evaluate_all()  # Returns list[CounterfactualResult]
for r in results:
    print(f"{r.query.cf_type.name}: {r.direction} ({r.impact_level})")
```
