# Changelog

## [0.2.1] — 2026-07-02

### Added
- `.ai/PROJECT_CONTEXT.md` — single-user context for AI agents
- `.ai/DATABASE_RULES.md` — database conventions and principles
- `.ai/FITNESS_RULES.md` — comprehensive hypertrophy training guide
- `.ai/UI_GUIDELINES.md` — gym-ready UI design principles
- `docs/README.md` — project overview and quick start
- `docs/FEATURE_MATRIX.md` — feature tracking with scope decisions
- `knowledge/user/` — user profile, goals, training config, nutrition plan, preferences, history
- `knowledge/nutrition/protein.md`, `calories.md`, `carbs.md`, `fat.md`, `fiber.md`, `hydration.md` — detailed nutrition references
- `knowledge/progression/linear_progression.md`, `volume.md`, `rir.md`, `failure.md` — progression knowledge
- `knowledge/recovery/stress.md`, `fatigue.md`, `doms.md`, `recovery_score.md` — recovery knowledge
- `knowledge/research/hypertrophy.md`, `volume.md`, `frequency.md`, `range_of_motion.md`, `progressive_overload.md`, `exercise_selection.md`, `recovery.md`, `nutrition.md` — evidence summaries
- ADR-008: Single-User Focus (GymOS rebrand)
- ADR-009: Double Progression as Primary Hypertrophy Method
- ADR-010: Prioritised Muscle Focus in Programming

### Changed
- **Rebrand to GymOS:** All `.ai/` files updated for single-user hypertrophy focus
- `docs/PRODUCT_REQUIREMENTS.md` — rewritten for single-user lean bulk goal
- `docs/roadmap/index.md` — updated for GymOS scope (removed multi-user, marketplace, social)
- `.ai/PROJECT_VISION.md` — rewritten for hypertrophy mission
- `.ai/CURRENT_MILESTONE.md` — updated with user profile and focus muscles
- `.ai/AGENT.md` — rewritten for GymOS mission directives
- `knowledge/nutrition/meal_timing.md` — enhanced with user-specific schedule

## [0.2.0] — 2026-07-02

### Added
- AI Development Kit: `.ai/` directory with AGENT.md, PROJECT_VISION.md,
  CURRENT_MILESTONE.md, ARCHITECTURE_RULES.md, CODING_STANDARD.md,
  REVIEW_CHECKLIST.md, TASK_TEMPLATE.md, DECISION_LOG.md
- Domain Knowledge Layer: `knowledge/` with structured fitness data
  (exercises, nutrition, recovery, progression, research)
- `docs/PRODUCT_REQUIREMENTS.md` — comprehensive product specification
- `docs/AI_ENGINE.md` — AI Coach and engine architecture
- `docs/CHANGELOG.md` — this file

### Changed
- `docs/architecture/overview.md` — enhanced with complete layer documentation
- `docs/database/schema.md` — enhanced with MVP entities and relationships
- `.opencode/skills/nexus-architect/SKILL.md` — enhanced with full ruleset

## [0.1.0] — 2026-06-15

### Added
- Core architecture: EventBus v2, DI Container, lifecycle management
- Plugin SDK contracts and PluginManager
- Design System with token-based theming
- CI/CD pipeline with GitHub Actions
- Test infrastructure: unit, integration, performance tests (21+ tests)
- Database migration system (Alembic)
- NEXUS Engines: WorkoutEngine, NutritionEngine, RecoveryEngine,
  AnalyticsEngine, AIEngine, PredictionEngine
- Plugin integrations: Cronometer, Discord, Telegram, Spotify, Weather,
  GitHub, Hevy
- Technical documentation: architecture, module boundaries, event-bus,
  coding standards, ADR, internal API
- Design system documentation with color tokens, typography, spacing
- Database schema for workouts, exercises, sets, meals, plugin config
- Demo CLI application
