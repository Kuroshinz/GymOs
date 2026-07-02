---
name: nexus-architect
description: Use ONLY when making architectural changes to NEXUS — restructuring modules, adding new modules, modifying core infrastructure, changing module boundaries, or evaluating cross-cutting concerns. Not for routine feature work within a single module.
---

# NEXUS Architecture Guidelines

## Structure

```
├── .ai/                   # Agent identity + process files
├── core/                  # Infrastructure services
├── modules/<name>/        # Business modules (Clean Architecture)
│   ├── domain/            #   Entities, value objects, repository interfaces
│   ├── application/       #   Use cases, services, ports
│   ├── infrastructure/    #   Repository implementations, adapters
│   └── presentation/      #   View models, PySide6 widgets
├── nexus/
│   ├── platform.py        #   Platform bootstrap
│   └── engines/           #   Event-driven engines
├── sdk/                   # Public API for plugins
├── plugins/<Name>/        # External integrations
├── shared/                # Constants, types, exceptions, helpers
├── knowledge/             # Domain knowledge (exercises, nutrition, recovery, ...)
├── tests/                 # Unit, integration, ui, performance
├── docs/                  # Architecture, ADR, API, design, db, roadmap
└── resources/             # Themes, icons, fonts, images
```

## Inviolable Rules

1. **No cross-module imports.** Modules communicate via EventBus only.
2. **Clean Architecture** per module: domain → application → infrastructure → presentation (dependency inward).
3. **Core has NO business logic.** Only infrastructure services.
4. **Plugins use SDK only.** Never import core directly.
5. **Every module has 4 layers**: domain/, application/, infrastructure/, presentation/.
6. **Database via repositories.** No raw SQL in application/presentation.
7. **Events follow `<domain>.<action>`** naming (e.g., `workout.created`).
8. **Async throughout.** All I/O is async def.
9. **DI Container** for service resolution. No new singletons.
10. **Design tokens** from core.theme for all visual properties.

## AI Knowledge Integration

- All AI features must read from `knowledge/` for domain data
- Exercise data comes from `knowledge/exercises/*.json`
- Progression rules from `knowledge/progression/`
- Nutrition guidelines from `knowledge/nutrition/`
- The AI Engine context builder assembles knowledge for LLM prompts

## Before adding new code

1. Does this belong in an existing module or a new one?
2. Does it need new events? Update shared/ and docs.
3. Does it need database tables? Add Alembic migration.
4. Does it need plugin integration? Define SDK contract first.
5. Does it need AI? Route through Brain layer, not UI.
6. Is there domain knowledge in `knowledge/` to reference?
7. Have you read the relevant `.ai/` files?

## Key File Paths

| What | Where |
|------|-------|
| Agent constitution | `.ai/AGENT.md` |
| Project vision | `.ai/PROJECT_VISION.md` |
| Current milestone | `.ai/CURRENT_MILESTONE.md` |
| Architecture rules | `.ai/ARCHITECTURE_RULES.md` |
| Coding standards | `.ai/CODING_STANDARD.md` |
| Review checklist | `.ai/REVIEW_CHECKLIST.md` |
| Task template | `.ai/TASK_TEMPLATE.md` |
| Decision log | `.ai/DECISION_LOG.md` |
| Product requirements | `docs/PRODUCT_REQUIREMENTS.md` |
| Architecture | `docs/architecture/overview.md` |
| Database schema | `docs/database/schema.md` |
| AI Engine | `docs/AI_ENGINE.md` |
| Exercise library | `knowledge/exercises/` |
| Progression rules | `knowledge/progression/` |
| Nutrition data | `knowledge/nutrition/` |
