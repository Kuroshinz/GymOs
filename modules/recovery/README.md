# Recovery Module

**Current status:** Scaffolding only — no implementations.

## Responsibilities (Planned)
- Track sleep duration, quality, and timestamps
- Log HRV (heart rate variability) readings
- Calculate composite recovery scores from multiple metrics
- Provide readiness assessments for workout recommendations
- Publish RecoveryScoreUpdated events to GymBrain

## Dependencies (Planned)
- `shared/events/` — EventBus for RecoveryScoreUpdated
- `shared/interfaces/` — IRecoveryProvider Protocol
- `data/gymos.db` — SQLite database via future RecoveryRepository
- Wearable device SDKs (future: Apple Health, Garmin, Fitbit)

## Exported Types (Planned)
- `RecoverySession` — sleep hours, HRV, readiness, fatigue
- `RecoveryScore` — composite score from weighted metrics
- `SleepLog` — duration, quality, timestamps

## Extension Points (Planned)
- **Wearable integration**: Implement IRecoveryProvider with wearable API adapter
- **Custom recovery formula**: Override score calculation in application service
- **Manual logging**: Implement manual entry as an alternative provider

## Architecture (Planned)

```
recovery/
├── domain/           # RecoverySession, RecoveryScore, SleepLog
├── application/      # LogRecoverySession, CalculateRecoveryScore, GetRecoveryTrend
├── infrastructure/   # RecoveryRepository (SQLite), WearableAdapter
└── presentation/     # RecoveryScoreWidget, SleepTrendWidget, FatigueIndicatorWidget
```

## Known Limitations
- No recovery data is tracked yet — module is empty scaffolding
- RecoveryScoreUpdated event already exists in shared/events/ but has no producer
- DataProvider already accepts a recovery_engine parameter (not yet used)

## Roadmap
- Sprint 3.3 : Implement recovery domain entities and SQLite repository
- Sprint 3.3 : Wire recovery provider into GymBrain DataProvider
- Sprint 3.3+ : Add wearable API adapter
- Sprint 3.3+ : Create recovery dashboard widgets
