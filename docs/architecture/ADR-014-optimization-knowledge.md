# ADR-014: Optimization Knowledge Engine

## Status
Accepted

## Context
The Planning Optimizer (RFC-021.5) generates many candidate plans through evolutionary optimization. To learn from these optimizations over time, we need a system that:
1. Collects optimization results as "experiences"
2. Mines patterns from successful and failed plans
3. Computes statistics to quantify what works
4. Derives rules and insights for future planning
5. Generates actionable recommendations
6. Maintains a versioned, append-only knowledge history

## Decision
Create a new `optimization_knowledge` module with:

### Domain Models
- **OptimizationExperience** — Record of a single optimization result with plan parameters and outcome
- **OptimizationPattern** — A mined pattern with value range, success rate, sample size, and confidence
- **OptimizationOutcome** — Classification of a result (SUCCESS/FAILURE) with score
- **OptimizationEvidence** — Evidence linking an experience to a pattern
- **OptimizationStatistics** — Descriptive statistics with confidence intervals and trends
- **OptimizationProfile** — Best-performing parameter values from successful experiences
- **OptimizationKnowledge** — A versioned snapshot of all accumulated knowledge
- **OptimizationRule** — Derived rule (INCREASE/DECREASE/MAINTAIN) from a pattern
- **OptimizationInsight** — Natural-language insight from reliable patterns
- **OptimizationRecommendation** — Actionable recommendation from high-confidence rules

### Pattern Mining
Patterns are extracted across 7 dimensions:
- Volume (weekly sets), Frequency (sessions/week), Split (style)
- Recovery (program weeks), Adherence (mesocycles), Deload (boolean), Fatigue (total sets)

### Statistics
Descriptive statistics with:
- Mean, median, std dev, variance, min/max
- 95% confidence interval (normal approximation via CLT)
- Trend analysis (linear regression slope)
- Moving average

### Rules
Rule effects derived from success rate:
- INCREASE when success_rate >= 0.7
- DECREASE when success_rate <= 0.3
- MAINTAIN otherwise

### No AI/LLM
All computations are pure statistical — no machine learning, no clustering, no LLM calls. Every output is deterministic, explainable, and reproducible from the same inputs.

## Consequences

### Positive
1. **Learn from optimization** — The system improves over time as more experiences are accumulated
2. **Explainable insights** — Every recommendation traces back to specific patterns and data
3. **Versioned knowledge** — Full audit trail of knowledge evolution
4. **No AI dependencies** — Zero external model dependencies, fully deterministic
5. **Small data friendly** — Classical statistics works with small sample sizes
6. **400+ tests** — Comprehensive test coverage across all components

### Negative
1. **No clustering** — Cannot discover emergent patterns beyond the 7 predefined dimensions
2. **No confidence intervals for small samples** — Requires n >= 5 for meaningful confidence scores
3. **Simple trend analysis** — Linear regression only; no seasonality or non-linear trends
4. **No cross-pattern interactions** — Each pattern dimension is analyzed independently

## Technical Notes

- All domain models are frozen dataclasses with `from __future__ import annotations`
- Knowledge versions use semantic versioning (vX.Y.Z) with parent_version chain
- Events registered in `DOMAIN_EVENT_REGISTRY` and capability registered before `registry.freeze()`
- 400+ tests across 14 test files
- Documentation: OPTIMIZATION_KNOWLEDGE.md, PATTERN_MINING.md, STATISTICAL_LEARNING.md
