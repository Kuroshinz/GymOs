# Pattern Mining

## Overview

The PatternMiningEngine extracts actionable training patterns from optimization experiences across 7 dimensions. Each pattern represents a range of values for a training parameter and its associated success rate, sample size, and confidence level.

## Pattern Types

### Volume Patterns
- **Parameter:** Average weekly sets
- **Method:** Range binning (bins of 20, from 10 to 200)
- **Output:** Pattern for each bin with sufficient samples
- **Label Format:** `Average Weekly Sets [lo-hi]`

### Frequency Patterns
- **Parameter:** Sessions per week
- **Method:** Discrete value grouping
- **Output:** Pattern for each unique frequency value
- **Label Format:** `Sessions Per Week: N`

### Split Patterns
- **Parameter:** Training split style (e.g., "PPL", "upper/lower", "full body")
- **Method:** Categorical grouping
- **Output:** Pattern for each split style
- **Label Format:** `Split Style: Name`

### Recovery Patterns
- **Parameter:** Total program weeks
- **Method:** Range binning (bins of 4, from 4 to 52)
- **Output:** Pattern for each bin
- **Label Format:** `Total Weeks [lo-hi]`

### Adherence Patterns
- **Parameter:** Mesocycle count
- **Method:** Range binning (bins of 1, from 1 to 10)
- **Output:** Pattern for each bin
- **Label Format:** `Mesocycle Count [lo-hi]`

### Deload Patterns
- **Parameter:** Presence of deload weeks
- **Method:** Binary splitting
- **Output:** Two patterns: "With Deload Weeks" and "Without Deload Weeks"
- **Special:** Unique tags (`included` / `excluded`)

### Fatigue Patterns
- **Parameter:** Total program sets
- **Method:** Range binning (bins of 200, from 0 to 3000)
- **Output:** Pattern for each bin
- **Label Format:** `Total Sets [lo-hi]`

## Statistical Methods

### Success Rate
```
success_rate = successful_experiences / total_experiences
```

### Confidence Score
```
base = min(1.0, sample_size / 100)
variance = success_rate * (1 - success_rate) / max(sample_size, 1)
std_err = sqrt(variance)
confidence = base * (1.0 - std_err)
```

### Reliability Criteria
A pattern is considered **reliable** when:
- `sample_size >= 10`
- `confidence >= 0.8`

## Configuration

| Parameter | Default | Description |
|---|---|---|
| `min_pattern_sample` | 3 | Minimum experiences needed to create a pattern |
| `success_threshold` | 0.7 | Score threshold for SUCCESS classification |
| `confidence_z_score` | 1.96 | Z-score for confidence interval computation |

## Determinism

Pattern mining is fully deterministic:
- Same experiences → Same bins
- Same bins → Same success rates
- Same success rates → Same confidence scores
