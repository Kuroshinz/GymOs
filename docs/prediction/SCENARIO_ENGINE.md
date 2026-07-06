# Scenario Engine

## Scenario Lifecycle

The scenario engine evaluates "what if I change X?" by:

1. **Define baseline** — run all 8 core engines with default parameters
2. **Apply intervention** — modify one or more parameters (volume ±, deload early/late, calories ±, sleep ±, adherence ±)
3. **Run scenario** — re-run the 8 core engines with modified parameters
4. **Compare** — compute deltas between baseline and scenario for every metric
5. **Assess** — determine if the scenario is beneficial, risky, or neutral
6. **Rank** — score all interventions to find the best course of action

```
Baseline ──► 8 engine outputs ──┐
                                 ├── ScenarioBuilder ──► Modified params ──► 8 engine outputs ──► Comparison
Intervention ────────────────────┘
```

---

## Scenario Builder

`ScenarioBuilder.build_modifiers(intervention, base_kwargs) → dict`

Takes a `ScenarioIntervention` enum value and a baseline kwargs dict, returns a modified dict with one or more parameters changed:

| Intervention | Parameters Modified | Delta |
|---|---|---|
| `INCREASE_VOLUME` | `recent_volume_7d`, `recent_volume_14d`, `volume_change_percent` | +15% |
| `DECREASE_VOLUME` | `recent_volume_7d`, `recent_volume_14d`, `volume_change_percent` | -15% |
| `EARLY_DELOAD` | `days_since_deload`, `deload_frequency_weeks` | Reset to 0 |
| `LATE_DELOAD` | `days_since_deload` | +14 days |
| `INCREASE_CALORIES` | `calorie_surplus_avg` | +250 kcal |
| `DECREASE_CALORIES` | `calorie_surplus_avg` | -250 kcal |
| `HIGHER_SLEEP` | `sleep_avg`, `sleep_trend` | +1h avg |
| `LOWER_SLEEP` | `sleep_avg`, `sleep_trend` | -1h avg |
| `HIGHER_ADHERENCE` | `calorie_adherence`, `recent_completion_rate`, `weekly_consistency` | +15% |
| `LOWER_ADHERENCE` | `calorie_adherence`, `recent_completion_rate`, `weekly_consistency` | -15% |

Values are clamped to realistic ranges (e.g., sleep 4–10h, adherence 0–100%).

---

## Scenario Engine

`PredictionScenarioEngine` orchestrates scenario evaluation:

- **Internal state**: Instantiates the 8 core engines (Plateau, PR, Recovery, Fatigue, Bodyweight, Volume, Consistency, Deload)
- **Baseline**: `_get_baseline_kwargs()` returns hardcoded default athlete parameters
- **Engine dispatch**: `_run_baseline(kwargs)` runs all 8 engines with parameter-sliced kwargs and returns 8 metric values

### Running Multiple Interventions

```python
engine = PredictionScenarioEngine()
results = engine.evaluate_all(base_kwargs)           # All 10 interventions
ranking = engine.rank_scenarios(results, base_kwargs) # Ranked by net score
selected = engine.compare_interventions([             # Compare specific subset
    ScenarioIntervention.INCREASE_CALORIES,
    ScenarioIntervention.HIGHER_SLEEP,
])
```

---

## Scenario Comparison

`ScenarioComparison` captures the delta between baseline and scenario for a single metric:

| Field | Description |
|---|---|
| `intervention` | Which intervention was applied |
| `baseline_value` | Original metric value |
| `scenario_value` | Metric value under intervention |
| `delta` | `scenario_value - baseline_value` |
| `delta_percent` | `(delta / baseline) * 100` |
| `confidence` | `PredictionConfidence` of the scenario result |
| `description` | Human-readable description of the comparison |
| `is_positive` | `True` if delta >= 0 (improvement) |

Each `ScenarioResult` contains 8 `ScenarioComparison` objects — one per engine metric — providing a multi-dimensional view of the intervention's impact.

---

## Ranking

`ScenarioRanking` identifies the most beneficial interventions:

1. For each `ScenarioResult`, compute a **net score** by summing weighted deltas across all 8 metrics
2. Positive deltas (improvements) add to score; negative deltas (regressions) subtract
3. Metrics are normalized to 0–1 range before weighting
4. Results sorted descending by net score

```python
@dataclass
class ScenarioRanking:
    rankings: list[tuple[ScenarioIntervention, float]]   # Sorted desc by score
    top_intervention: Optional[ScenarioIntervention]     # Best intervention
    top_score: float                                     # Score of best intervention
```

---

## Recommendation Generation

The `recommended` flag on `ScenarioResult` is set to `True` when the net score is positive — meaning the intervention improves more metrics than it harms. Each result also carries:

- `overall_assessment` — narrative summary of the scenario's effect
- `risk_level` — `"low"`, `"moderate"`, or `"high"` based on the magnitude of negative deltas

---

## Risk Comparison

Risk is assessed per scenario by examining:

1. **Magnitude of negative deltas** — large regressions in any metric increase risk
2. **Number of metrics worsened** — more negative metrics = higher risk
3. **Confidence level** — lower confidence in scenario results increases risk

The `risk_level` is set to the worst observed across all metrics, providing a conservative assessment.

---

## Delta Calculation

For each metric:

```
absolute_delta = scenario_value - baseline_value
percent_delta  = (absolute_delta / baseline_value) * 100   (0 if baseline is 0)
is_positive    = delta >= 0
```

Deltas are computed in `__post_init__` of `ScenarioComparison`, making them immutable after construction.

---

## Examples

### Evaluate a single intervention

```python
engine = PredictionScenarioEngine()
base = {
    "recent_volume_7d": 40, "recent_volume_14d": 75,
    "sleep_avg": 6.5, "calorie_surplus_avg": 300,
    "recovery_scores": [70, 68, 72], "weeks_since_last_deload": 6,
}
result = engine.evaluate_intervention(
    ScenarioIntervention.EARLY_DELOAD, base
)
print(result.recommended)          # True (deload reduces fatigue)
print(result.comparisons[0].delta) # Fatigue score decreases
```

### Rank all interventions

```python
results = engine.evaluate_all(base)
ranking = engine.rank_scenarios(results, base)
print(ranking.top_intervention.label) # "Higher Sleep"
print(len(ranking.rankings))          # 10
```

### Compare two interventions

```python
comparison = engine.compare_interventions([
    ScenarioIntervention.INCREASE_SLEEP,
    ScenarioIntervention.DECREASE_VOLUME,
])
# Returns dict keyed by intervention label with list[ScenarioComparison]
```
