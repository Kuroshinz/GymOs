# Changelog

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
