# Nutrition Module

## Responsibilities
- Track daily meals, macronutrients, fiber, and hydration
- Calculate macro targets based on user goals (lean bulk, cut, maintain)
- Analyze nutrition quality (protein deficit, gain rate, lean bulk quality)
- Provide production-ready NutritionProvider for GymBrain consumption
- Publish MealLogged, NutritionUpdated, MacroTargetChanged events

## Dependencies
- `shared/events/` — EventBus for publishing domain events
- `shared/interfaces/` — INutritionProvider Protocol
- `modules/workout/infrastructure/repository.py` — GymDatabase (for body weight queries)
- `data/gymos.db` — SQLite database via NutritionRepository

## Exported Types
- `DailyNutrition`, `Meal`, `MealItem`, `MealType` — meal tracking domain
- `MacroTarget`, `NutritionGoal`, `NutritionGoalType` — goal configuration
- `NutritionSummary`, `Hydration`, `MacroStatus`, `MacroStatusResult` — analysis results
- `MacroAnalysis`, `LeanBulkAnalysis` — analysis engine outputs
- `NutritionProvider` (ABC), `ProductionNutritionProvider` — provider interface + impl
- `NutritionService` — application service facade
- `NutritionRepository` — SQLite data access
- `MacroAnalyzer`, `LeanBulkAnalyzer` — analysis engines

## Extension Points
- **New provider (Cronometer API)**: Implement `INutritionProvider` Protocol from `shared/interfaces/`
- **New analysis metric**: Add analyzer class in `analysis/`, register in `NutritionService`
- **New goal type**: Add enum to `NutritionGoalType`, define target logic in domain
- **New knowledge-backed threshold**: Replace hard-coded thresholds with `knowledge/nutrition/` lookups

## Known Limitations
- `NutritionService` accesses both `NutritionRepository` and `GymDatabase` (body weight coupling)
- Default macro targets duplicated in domain model and SQLAlchemy model
- No meal plan generation or recipe management yet
- `presentation/` layer is empty (no nutrition UI widgets)

## Architecture

```
nutrition/
├── domain/           # DailyNutrition, Meal, MacroTarget, NutritionSummary, etc.
├── analysis/         # MacroAnalyzer, LeanBulkAnalyzer
├── services/         # NutritionService (application facade)
├── providers/        # NutritionProvider (ABC), ProductionNutritionProvider
├── infrastructure/   # NutritionRepository (SQLite), importers
├── presentation/     # (empty — planned for future widgets)
└── tests/            # 49 unit tests
```

## Roadmap
- Sprint 3.3+ : Add knowledge-backed thresholds from `knowledge/nutrition/`
- Sprint 3.3+ : Create nutrition dashboard widgets
- Sprint 3.4+ : Cronometer API integration via INutritionProvider
- Sprint 4.x : Meal planning and recipe management
