# GymOS Recovery Intelligence

Recovery is a first-class domain alongside Training and Nutrition.

## Overview

The Recovery Intelligence subsystem provides deterministic, evidence-based recovery metrics that inform training readiness, deload timing, fatigue management, and overall recovery optimization.

## Domain Entities

| Entity | Description |
|--------|-------------|
| `RecoveryProfile` | User baseline settings (HRV, sleep need, sensitivities) |
| `RecoveryScore` | Composite 0-100 score with component breakdown |
| `RecoverySession` | User-reported recovery data point |
| `SleepLog` | Sleep duration, quality, timing |
| `StressLog` | Stress level and source |
| `ReadinessAssessment` | Training readiness with volume/intensity modifiers |
| `DeloadPlan` | Scheduled deload with protocol instructions |
| `RecoveryTrend` | Trend analysis over lookback period |
| `FatigueFactors` | Fatigue factor breakdown |
| `RecoveryFactors` | Recovery factor breakdown |
| `RecoverySnapshot` | Point-in-time dashboard snapshot |
| `RecoveryHistory` | Historical data collection |

## Scoring

Recovery Score (0-100) weighted factors:

| Factor | Weight |
|--------|--------|
| Training fatigue | 25% |
| Sleep (quality + duration) | 35% |
| Stress | 15% |
| Bodyweight trend | 5% |
| Nutrition adherence | 10% |
| Workout consistency | 5% |
| Deload benefit | 5% |

Readiness levels: READY, GOOD, CAUTION, FATIGUED, DELOAD.

## Usage

```python
from modules.recovery import RecoveryService
from modules.recovery.infrastructure.repository import RecoveryRepository

repo = RecoveryRepository("data/gymos.db")
service = RecoveryService(repo, db=db, event_bus=event_bus)

# Get today's snapshot
snapshot = service.get_snapshot()

# Log sleep
service.log_sleep("2026-07-03", hours=8.0, quality=SleepQuality.GOOD)

# Assess readiness
assessment = service.assess_readiness()

# Check deload
should_deload, reason, plan = service.check_deload()

# Generate recommendations
recs = service.generate_recommendations()
```

## Events

| Event | Trigger |
|-------|---------|
| `RecoveryUpdated` | Any recovery data change |
| `RecoveryScoreChanged` | Score changes significantly |
| `ReadinessChanged` | Readiness level transitions |
| `DeloadRecommended` | Deload is recommended |
