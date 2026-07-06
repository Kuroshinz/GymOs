# ADR-017: GymOS Command Center

## Status

Accepted

## Context

GymOS platform engines (Planning, Optimizer, Knowledge, Evolution, Adaptive) are mature. There is no unified interface for users to monitor, explore, and interact with platform intelligence. The existing UI is fragmented across separate views.

## Decision

Create `ui/command_center/` as a premium desktop experience layer that:
1. Exposes existing platform intelligence through a modern dashboard
2. Consumes canonical services via composition (no duplicated logic)
3. Uses event-driven updates via `CommandCenterController`
4. Uses the existing dark theme design system
5. Tests at 350+ coverage threshold

## Architecture

```
CommandCenter (QWidget)
├── Sidebar (left, 220px)
├── Top Bar (breadcrumb + QuickSearch)
├── StackedWidget (9 pages)
│   ├── HomePage
│   ├── MissionPage
│   ├── PlanningPage
│   ├── PredictionCenterPage
│   ├── RecoveryCenterPage
│   ├── KnowledgeCenterPage
│   ├── AdaptiveCenterPage
│   ├── AnalyticsCenterPage
│   └── SystemCenterPage
└── CommandPalette (Ctrl+K modal)
```

## Key Decisions

- **No AI/LLM** — all visualization is pure deterministic rendering
- **No cross-module imports** — services use attribute access (`getattr`) for canonical engine interfaces
- **Frozen dataclasses** — all models follow the shared pattern
- **Section-level refresh** — event handlers refresh only affected sections
- **Auto-refresh** — 60-second polling timer as backup for event bus

## Consequences

Positive:
- Unified experience across all platform capabilities
- No architectural violations (no duplicated business logic)
- 366+ tests verify all components independently
- Event-driven reactivity without tight coupling

Negative:
- Widgets depend on `update_data(Any)` pattern (duck typing)
- Some fallback data hardcoded in services for demo purposes

## File Impact

- 50 new source files in `ui/command_center/`
- 20 new test files (366+ tests)
- No modifications to existing business logic or shared modules
