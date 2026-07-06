# Statistical Learning (No ML)

## Overview

The StatisticsEngine computes descriptive statistics and trends from optimization experiences using classical statistical methods. There is **no machine learning, no neural networks, no clustering, and no AI** — every computation is deterministic, explainable, and reproducible.

## Statistics Computed

### Descriptive Statistics
- **Mean** — Average overall score
- **Median** — Middle score (50th percentile)
- **Standard Deviation** — Spread of scores around the mean
- **Variance** — Squared standard deviation
- **Min/Max** — Range of observed scores
- **Success Rate** — Proportion of successful experiences

### Confidence Interval (95%)
Uses the normal approximation via the Central Limit Theorem:
```
margin = z * std_dev / sqrt(n)
ci_lower = mean - margin
ci_upper = mean + margin
```
Where `z = 1.96` for 95% confidence.

### Trend Analysis
Linear regression over experience index:
```
slope = sum((x - x_mean) * (y - y_mean)) / sum((x - x_mean)^2)
```
Trend directions:
- `up` — slope > 0.01
- `down` — slope < -0.01
- `stable` — otherwise
- `insufficient` — fewer than 3 data points

### Moving Average
Simple trailing window average (default window: 5):
```
moving_avg = sum(last_n_scores) / n
```

## Profiles

The StatisticsEngine also builds optimization profiles by grouping successful experiences:
- **Best Sessions/Week** — Most common frequency among successes
- **Best Total Weeks** — Most common program duration among successes
- **Best Split Style** — Most common split among successes
- **Best Average Weekly Sets** — Mean weekly sets among successes
- **Best Mesocycle Count** — Most common mesocycle count among successes

## Grouping

Statistics are computed at multiple scopes:
- **Global** — All experiences
- **Per Goal** — Grouped by training goal
- **Per Split** — Grouped by split style

Groups with fewer than `min_pattern_sample` experiences are skipped.

## Why Not ML?

1. **Reproducibility** — Statistical methods always produce the same result for the same input. ML models can vary between runs.
2. **Explainability** — Every metric has a clear mathematical definition. No black boxes.
3. **Debuggability** — If a pattern looks wrong, you can trace through the exact computation.
4. **Minimal Data** — Classical statistics works with small sample sizes (n >= 3 for trends, n >= 2 for confidence intervals).
5. **Zero Dependencies** — No ML frameworks, no model serialization, no GPU requirements.
