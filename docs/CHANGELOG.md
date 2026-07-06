# Changelog

## [0.5.0] — 2026-07-03 — Platform Standardization

### Added
- **Engineering Constitution** (`.ai/ENGINEERING_CONSTITUTION.md`) — 8 Articles governing architecture, DI, testing, code quality, knowledge, platform standards, AI agent conduct
- **Architecture Decision Records** (5 new):
  - ADR-001: Event Architecture — Typed DomainEvents, single registry, append-only schema
  - ADR-002: Knowledge System — Layered pipeline, versioned files
  - ADR-003: GymBrain Architecture — DecisionEngine, DataProvider, stateless rules
  - ADR-004: Provider Interfaces — Protocol-based interfaces (I prefix)
  - ADR-005: Event-Driven Communication — EventBus as exclusive cross-module channel
- **Interface Contracts** (`shared/interfaces/__init__.py`) — 7 Protocols: IDataProvider, ITrainingProvider, INutritionProvider, IRecoveryProvider, IGoalProvider, IKnowledgeRepository, IRecommendationEngine
- **DI Standard** (`docs/architecture/DI_STANDARD.md`) — Composition root pattern, dependency graph, wiring rules
- **Module Audit** (`docs/architecture/MODULE_AUDIT.md`) — Health assessment of all 8 modules with issue tracking
- **Knowledge Platform** (`docs/architecture/KNOWLEDGE_PLATFORM.md`) — Validated pipeline documentation
- **Engineering Standards** (4 new):
  - `.ai/CODE_QUALITY_STANDARD.md` — Python, linting, typing, testing standards
  - `.ai/AI_BEHAVIOR.md` — Agent conduct rules (read-before-write, change summaries)
  - `.ai/PROJECT_PHILOSOPHY.md` — Core beliefs, design values, golden rule
  - `.ai/FITNESS_ENGINE_STANDARD.md` — Engine classification, rule requirements, scientific thresholds
- **Product Documentation** (8 new/rewritten):
  - `README.md` — Root README reflecting platform maturity
  - `docs/PRODUCT_STRATEGY.md` — Long-term mission, positioning, competitive advantages
  - `docs/VERSION_STRATEGY.md` — 0.5 through 1.0 definition
  - `docs/ENGINE_ROADMAP.md` — Maturity of every intelligence engine
  - `docs/EXPERIENCE_ROADMAP.md` — Complete user journey
  - `docs/PRODUCT_PILLARS.md` — 7 pillars: Training, Nutrition, Recovery, Consistency, Intelligence, Automation, Knowledge
  - `docs/PRODUCT_REQUIREMENTS.md` — Rewritten for v0.5 platform maturity
  - `docs/roadmap/index.md` — Rewritten for current state
- **Module READMEs** (5 new): workout, nutrition, gymbrain, workout_program, recovery
- **Test infrastructure** (`tests/conftest.py`, `tests/TEST_INFRASTRUCTURE.md`)
- **Scaffolding documentation**: All `recovery/` and `settings/` `__init__.py` files now have docstrings

### Changed
- `shared/__init__.py` — Created with public API re-exports
- `.ai/CURRENT_MILESTONE.md` — Rewritten for v0.5 Platform Maturity
- `.ai/PROJECT_CONTEXT.md` — Updated to reflect current phase
- `.ai/PROJECT_VISION.md` — Updated phased vision to 7 pillars
- `docs/archive/` — Outdated MVP-era docs preserved for reference

### Fixed
- `modules/nutrition/application/` — Deleted (dead scaffolding)
- Empty `__init__.py` files in recovery/ and settings/ — Documented with planned scope

## [0.4.0] — 2026-07-03 — Nutrition Architecture Hardening

### Added
- **Nutrition Intelligence**: domain models (DailyNutrition, Meal, MacroTarget, NutritionSummary, etc.)
- **Nutrition Analysis**: MacroAnalyzer, LeanBulkAnalyzer — quality scoring, protein deficit detection
- **Nutrition Providers**: NutritionProvider (ABC), ProductionNutritionProvider (SQLite-backed)
- **Nutrition Services**: NutritionService — meal logging, water tracking, summary generation
- **Meal Logging**: Manual meal entry with macro breakdown, MealType enum
- **Hydration Tracking**: Daily water intake with target progress
- **Lean Bulk Analysis**: Quality score, protein status, weight gain rate evaluation
- **Nutrition Events**: MealLogged, NutritionUpdated, MacroTargetChanged (typed, registered)
- **Nutrition Subscriber**: Cache invalidation on meal/nutrition events
- **Nutrition Rules** (5 new): ProteinDeficitRule, CalorieAdjustmentRule, GainRateRule, HydrationRule, LeanBulkQualityRule
- **Dashboard Integration**: NutritionService wired through MainWindow → DashboardView → DashboardController → DashboardDataService
- **49 nutrition tests**: Domain models, analysis engines, providers, services, event round-trips
- **DataProvider nutrition_property**: Typed property + setter (no more getattr)

### Changed
- `modules/nutrition/events.py` — Deleted (reconciled into shared/events/domain_events.py)
- `shared/events/domain_events.py` — Added NutritionUpdated, MacroTargetChanged to registry
- `shared/events/publishers/nutrition_publisher.py` — Fixed fat_g=carbs_g copy-paste bug
- `modules/nutrition/services/__init__.py` — Changed from string events to typed DomainEvent objects
- `modules/gymbrain/services/decision_engine.py` — Removed broken NutritionRule/BodyweightStallRule imports; increased rule count 15→18
- `modules/gymbrain/rules/__init__.py` — Updated for 5 new nutrition rule classes

### Fixed
- `NutritionSummary.to_dict()` — Added missing `lean_bulk` field
- `nutrition_publisher.py:24` — `fat_g=carbs_g` → `fat_g=fat_g`

## [0.3.0] — 2026-07-02 — GymBrain Intelligence

### Added
- GymBrain module with DecisionEngine, DataProvider, RuleEngine
- 15 deterministic rules (training, recovery, volume, progression, plateau, fatigue)
- Analysis engines: PlateauDetector (6 types), FatigueAnalyzer (5-factor), MuscleAnalyzer, GoalTracker
- WeeklyReviewGenerator with structured weekly summary
- AnalysisCache with time-based invalidation
- 130 GymBrain tests
- Nutrition knowledge files (protein, calories, carbs, fat, fiber, hydration)
- Recovery knowledge files (sleep, stress, fatigue, DOMS, recovery score)
- Progression knowledge (linear progression, volume landmarks, RIR, RPE, deload, failure)

### Changed
- Rebrand: NEXUS → GymOS
- All .ai/ files rewritten for single-user hypertrophy focus
- docs/PRODUCT_REQUIREMENTS.md rewritten for lean bulk goal

## [0.2.0] — 2026-07-02 — AI Development Kit

### Added
- .ai/ directory with AGENT.md, PROJECT_VISION.md, CURRENT_MILESTONE.md
- Knowledge layer with exercises, nutrition, recovery, progression, research
- AI Development Kit structure

## [0.1.0] — 2026-06-15 — Foundation

### Added
- Core architecture: EventBus v2, DI Container, lifecycle management
- Plugin SDK contracts and PluginManager
- Design System with token-based theming
- Database migration system (Alembic)
- NEXUS Engines architecture
- Plugin integrations (Cronometer, Discord, Telegram, Spotify, Weather, GitHub, Hevy)
