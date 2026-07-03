# Workout Module

## Responsibilities
- Track training sessions (exercises, sets, reps, weight)
- Log body weight measurements
- Calculate training volume and detect personal records
- Analyze recovery and progression
- Store all training data in SQLite via GymDatabase

## Dependencies
- `shared/` — EventBus for publishing WorkoutStarted, WorkoutCompleted, SetCompleted, etc.
- `shared/knowledge_loader.py` — Exercise/muscle definitions from knowledge base
- `shared/domain/` — ExerciseData, MuscleData models, VolumeEngine, KnowledgeService
- `data/gymos.db` — SQLite database for persistent storage

## Exported Types
- `WorkoutSession`, `SessionExercise`, `SessionSet` — session domain models
- `BodyWeight` — body weight log entry
- `GymDatabase` — SQLite repository (also used by gymbrain, nutrition)
- `PREngine`, `RecoveryEngine`, `ProgressionEngine` — analysis engines consumed by GymBrain

## Extension Points
- **New exercise source**: Add adapter in `infrastructure/` that implements the same interface as GymDatabase
- **New PR formula**: Override `PREngine.detect_prs()` or inject a custom calculator
- **New recovery metric**: Extend `RecoveryEngine` with additional fatigue signals

## Known Limitations
- `GymDatabase` is both connection manager and repository (should be split)
- Analysis engines live in workout/ but serve GymBrain (should migrate to gymbrain/)
- No offline sync for multi-device use

## Architecture

```
workout/
├── domain/           # WorkoutSession, SessionExercise, SessionSet, BodyWeight
├── application/      # PREngine, RecoveryEngine, ProgressionEngine
├── infrastructure/   # GymDatabase (SQLite), DB models (init_db)
└── presentation/     # (planned: workout log widgets)
```

## Roadmap
- Sprint 3.3+ : Extract PREngine/RecoveryEngine/ProgressionEngine into gymbrain/
- Sprint 3.3+ : Split GymDatabase into DatabaseConnection + WorkoutRepository
- Sprint 4.x : Add offline-first sync with workout API
