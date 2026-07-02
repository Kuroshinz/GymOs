---
name: nexus-architect
description: Use ONLY when making architectural changes to NEXUS — restructuring modules, adding new modules, modifying core infrastructure, changing module boundaries, or evaluating cross-cutting concerns. Not for routine feature work within a single module.
---

# NEXUS Architecture Guidelines

## Structure

```
modules/<name>/           # Business modules (workout, nutrition, analytics, recovery, ai, settings, brain)
core/                     # Infrastructure (event_bus, di, plugin, database, ...)
plugins/<Name>/           # External integrations (Cronometer, Discord, ...)
sdk/                      # Public API for plugins
shared/                   # Constants, types, exceptions, helpers
nexus/                    # Platform bootstrap + engines
tests/                    # Unit, integration, ui, performance
docs/                     # Architecture, ADR, API, design, db, roadmap
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

## Before adding new code

1. Does this belong in an existing module or a new one?
2. Does it need new events? Update `shared/constants/` and docs.
3. Does it need database tables? Add Alembic migration.
4. Does it need plugin integration? Define SDK contract first.
5. Does it need AI? Route through Brain layer, not UI.
