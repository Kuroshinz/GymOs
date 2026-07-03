# GymBrain Module

## Responsibilities
- Analyze training, nutrition, and recovery data to produce recommendations
- Evaluate deterministic rules against current user state
- Detect plateaus, fatigue, recovery deficits, and nutrition gaps
- Generate weekly reviews and goal progress reports
- Provide a single facade (DecisionEngine) consumed by the application layer

## Dependencies
- `modules/workout/` — GymDatabase, PREngine, RecoveryEngine, ProgressionEngine
- `modules/nutrition/` — NutritionProvider (via DataProvider)
- `shared/events/` — EventBus (subscribes to ExerciseKnowledgeUpdated)
- `shared/interfaces/` — IDataProvider, INutritionProvider, IRecommendationEngine Protocols
- `shared/knowledge_loader.py` — Exercise/muscle definitions

## Exported Types
- `DecisionEngine` — central orchestrator, primary API
- `DataProvider` — facade for all domain data (training, nutrition, recovery)
- `BaseRule`, `RuleResult`, `RuleEngine` — rule framework
- `Recommendation`, `RecommendationCategory`, `RecommendationPriority` — recommendation model
- `PlateauDetector`, `FatigueAnalyzer`, `MuscleAnalyzer`, `GoalTracker` — analysis engines
- `WeeklyReviewGenerator` — weekly report builder
- `AnalysisCache` — in-memory result cache

## Extension Points
- **New rule**: Subclass `BaseRule`, implement `evaluate()`, register in `DecisionEngine._register_default_rules()`
- **New analysis engine**: Create analyzer class, inject into DecisionEngine constructor
- **New data source**: Implement `INutritionProvider`, `IRecoveryProvider`, etc. and inject into DataProvider
- **Custom recommendation ranking**: Override `RuleEngine.evaluate()` sort logic
- **Alternative DecisionEngine**: Implement `IRecommendationEngine` Protocol

## Known Limitations
- `DataProvider` is oversized (~30 methods, 6 domains) — needs splitting into focused providers
- `ProductionDataProvider` duplicates base `DataProvider` methods with try/except wrappers
- `DecisionEngine` instantiates analyzers internally (should inject them)
- `_import_rule()` uses getattr on dynamic imports (should use a registry dict)
- No persistence for recommendation history

## Architecture

```
gymbrain/
├── providers/        # DataProvider, ProductionDataProvider
├── rules/            # BaseRule, RuleEngine, 18 concrete rule classes
├── analysis/         # PlateauDetector, FatigueAnalyzer, MuscleAnalyzer, GoalTracker
├── services/         # DecisionEngine, WeeklyReviewGenerator
├── models/           # Recommendation, Analysis models
├── cache/            # AnalysisCache
└── tests/            # 163 unit tests
```

### Data Flow

```
User Data (DB)  ──►  DataProvider  ──►  Rule Engine
     │                                     │
     │                                     ▼
     └──►  Analysis Engines         Recommendations
                    │                     │
                    ▼                     ▼
           DecisionEngine API      Dashboard / UI
```

## Roadmap
- Sprint 3.3 : Split DataProvider into TrainingDataProvider + NutritionDataProvider
- Sprint 3.3 : Add recovery provider integration
- Sprint 3.4 : Decision Engine v2 with adaptive rule prioritization
- Sprint 3.5 : Prediction Engine (plateau timing, goal completion estimates)
- Sprint 4.x : AI Coach with natural language explanations
