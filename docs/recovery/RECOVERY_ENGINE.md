# Recovery Engines

All engines are deterministic, stateless, and composable.

## Engine Architecture

```
SleepAnalyzer ─┐
               ├──▶ RecoveryScoreEngine ──▶ ReadinessEngine
StressAnalyzer ┘         │
                         ├──▶ DeloadEngine
FatigueAggregator ───────┘
                         │
RecoveryTrendAnalyzer ───┘
```

## SleepAnalyzer

Scores sleep from 0-100 based on:
- Duration vs sleep need (0-60 points)
- Quality rating (0-40 points)
- Sensitivity multiplier

## StressAnalyzer

Scores stress impact (0-100, higher = worse):
- VERY_LOW → 5, LOW → 15, MODERATE → 35, HIGH → 60, VERY_HIGH → 85
- Multiplied by stress sensitivity

## FatigueAggregator

Composite fatigue from:
- Training fatigue (30%)
- Sleep fatigue (25%) — inverted from sleep score
- Stress (20%)
- Soreness (15%)
- Subjective fatigue (10%)

Also computes detailed `FatigueFactors` with volume ratios, frequency, deload timing.

## RecoveryScoreEngine

Primary scoring engine. Uses weighted formula:
- 25% training fatigue (inverted)
- 35% sleep score
- 15% stress (inverted)
- 5% bodyweight trend
- 10% nutrition adherence
- 5% consistency
- 5% deload benefit

Muscle recovery adjustment applies a multiplier based on soreness.

## ReadinessEngine

Produces `ReadinessAssessment` with:
- Readiness level from score
- Volume/intensity modifiers per level
- Trend adjustments (declining → reduce 10%)
- Contextual flags (sleep, stress, fatigue, soreness, HRV)
- Recommended action text

## DeloadEngine

Determines if deload is needed based on:
- Weeks since last deload vs frequency setting
- Average recovery score (threshold: 50)
- Consecutive low scores (3 × <40)
- Fatigue factors (overall >70, volume ratio >2, sleep <6h)

Creates deload plans with 50% volume reduction, 20% intensity reduction.

## RecoveryTrendAnalyzer

Statistical trend analysis:
- Linear regression slope for direction
- Coefficient of variation for volatility
- Weekly averages
- Classification: IMPROVING, STABLE, DECLINING, VOLATILE
