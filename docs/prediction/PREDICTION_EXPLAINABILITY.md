# Prediction Explainability

## Architecture

Explainability is a **post-hoc analysis layer** that runs after the 9 core prediction engines produce their outputs. It is implemented as a single stateless engine class:

```
PredictionService.generate_all_predictions()
  └─ for each Prediction:
       └─ ExplainabilityEngine.explain(prediction) → ExplainabilityDetail
            ├─ factor_contributions:  list[FactorContribution]
            ├─ reason_chain:          ReasonChain
            ├─ nl_explanation:        NLExplanation
            ├─ mr_explanation:        MRExplanation
            └─ evidence_ranking:      list[PredictionEvidence]
```

The engine never modifies predictions — it only consumes them and produces explanation artifacts.

---

## Evidence Pipeline

Each `Prediction` carries a `PredictionExplanation` with:
- `summary` — one-line summary
- `reasoning` — list of strings, each a reasoning step
- `assumptions` — list of strings, each a stated assumption
- `risk_factors` — list of strings flagging risks
- `evidence` — `list[PredictionEvidence]`, each with source, data_point, value, timestamp, relevance

The evidence ranking step sorts all `PredictionEvidence` items by relevance descending, producing the most significant evidence first.

---

## Confidence Reasoning

`PredictionConfidence` is computed by the engines and consumed by explainability:

| Field | Source | Meaning |
|-------|--------|---------|
| `score` | Engine | 0.0–1.0 composite confidence |
| `level` | Post-init | Mapped from score via `ConfidenceLevel.from_score()` |
| `factors` | Engine | Named reasons affecting confidence |
| `data_quality` | Engine | 0.0–1.0 quality of input data |
| `sample_size` | Engine | Number of data points available |
| `variance` | Engine | Variance in the underlying data |

The explainability engine surfaces the confidence level prominently in both NL and MR explanations.

---

## Factor Ranking

`_compute_factor_contributions()` builds a list of `FactorContribution` objects from:

1. **Evidence items** — each evidence source becomes a factor; contribution weighted by relevance
2. **Reasoning steps** — each reasoning line becomes a factor; contribution derived from position (earlier = more influential)
3. **Assumptions** — each assumption becomes a factor with moderate negative contribution
4. **Risk factors** — each risk becomes a factor with strong negative contribution
5. **Predicted probability** — final factor representing the value itself

All contributions are sorted by `abs(contribution)` descending and capped at **top 15**. Each factor has:

| Field | Description |
|-------|-------------|
| `factor_name` | Human-readable name |
| `contribution` | Signed float (-1 to 1); positive = supports prediction, negative = opposes |
| `direction` | `"positive"` or `"negative"` (auto-derived from contribution sign) |
| `description` | Explanation of how this factor affects the outcome |
| `weight` | 0.0–1.0 importance weight (clamped) |

---

## Rule Contribution

The explainability engine does not inspect internal engine rules directly. Instead, it consumes the **output artifacts** of the engines:

- **Evidence list** → factor names + relevance scores
- **Reasoning steps** → chain of logic
- **Assumptions** → transparency about model limits
- **Risk factors** → downside flags

This design preserves engine encapsulation while providing full traceability.

---

## Natural Language Explanation Generation

`_generate_nl_explanation()` produces three levels:

### Short
One sentence summarizing the prediction and its top factor:
> "You have a 72% probability of hitting a new PR in the next 7 days, primarily driven by your recent volume progression."

### Detailed
2–3 paragraphs explaining the evidence, confidence, assumptions, and risks:
> "This prediction is based on 4 weeks of training data showing consistent volume increases. Your recovery score of 68/100 and RIR trend of 1.5 suggest adequate readiness. Assumptions include continued adherence and no major life disruptions. Key risk: fatigue accumulation may reduce performance."

### Actionable
Concrete recommendation derived from the explanation:
> "To maintain this trajectory: keep weekly volume increases under 10%, prioritize sleep on leg days, and monitor RIR for signs of accumulating fatigue."

### Per-Type Variations
The engine tailors explanations to `PredictionType`:
- `NEXT_PR_PROBABILITY` — volume progression, recovery, deload status
- `PLATEAU_PROBABILITY` — stalled metrics, insufficient variation
- `RECOVERY_DECLINE` — sleep/stress trends, fatigue ratios
- `DELOAD_PROBABILITY` — weeks since deload, fatigue/recovery ratio

---

## Machine-Readable Explanation Schema

`MRExplanation` provides structured data for UIs, analytics, and downstream consumers:

```python
@dataclass
class MRExplanation:
    top_factors: list[dict]           # [{"name": "...", "contribution": 0.0, "direction": "positive"}]
    confidence_breakdown: dict        # {"data_quality": 0.9, "sample_size": 0.7, "variance": 0.3}
    evidence_summary: list[dict]      # [{"source": "...", "relevance": 0.9}]
    assumptions_used: list[str]       # ["Assumes continued adherence"]
    risk_flags: list[str]             # ["Fatigue accumulation possible"]
    model_version: str                # "1.0"
```

### Confidence Breakdown Schema
```json
{
  "training_volume_trend": 0.85,
  "recovery_score": 0.72,
  "rir_trend": 0.68,
  "consistency_streak": 0.91
}
```

Each key is a factor name, each value is that factor's confidence score (0.0–1.0), how much the system trusts that data point.
