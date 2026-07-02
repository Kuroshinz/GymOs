# NEXUS — Architecture Rules (Inviolable)

## Layer Architecture

```
┌─────────────────────────────────────────┐
│            Presentation                  │
│  (PySide6 UI, ViewModels, Controllers)  │
├─────────────────────────────────────────┤
│            Application                   │
│  (Use Cases, Services, DTOs, Ports)     │
├─────────────────────────────────────────┤
│            Domain                        │
│  (Entities, Value Objects, Business     │
│   Rules, Repository Interfaces)         │
├─────────────────────────────────────────┤
│         Infrastructure                   │
│  (SQLAlchemy Repositories, Adapters)    │
└─────────────────────────────────────────┘
```

## Rules

### Rule 1: Dependency flows inward
- Presentation → Application → Domain
- Infrastructure implements Application ports
- Domain imports NOTHING except stdlib + shared types
- Application imports only Domain + shared
- Infrastructure imports Application interfaces

### Rule 2: No cross-module imports
Modules communicate exclusively via EventBus.
`workout/` must never import `nutrition/` directly.

### Rule 3: UI never accesses database
All data access goes through:
UI → Application Service → Repository Interface → Infrastructure → DB

### Rule 4: Core has zero business logic
`core/` contains only infrastructure services:
EventBus, DI Container, Theme Manager, Scheduler, Logger, Database
No domain concepts in core.

### Rule 5: Events are the contract
- Naming: `<domain>.<action>` (e.g., `workout.created`)
- All inter-module data flows through typed events
- Events are immutable value objects

### Rule 6: Every module has 4 layers
```
module/
├── domain/         # Entities, value objects, repository interfaces
├── application/    # Use cases, services, ports
├── infrastructure/ # Repository implementations, adapters
└── presentation/    # View models, PySide6 widgets
```

### Rule 7: Repositories only
All database operations go through repositories defined in domain/, implemented in infrastructure/.
No raw SQL, no direct ORM usage outside infrastructure.

### Rule 8: Dependency injection
All services are registered in the DI Container.
No `new Service()`, no global singletons, no service locator anti-pattern.

### Rule 9: Async I/O
All I/O-bound operations are `async def`.
Blocking operations use `asyncio.to_thread()`.
UI thread is never blocked.

### Rule 10: Design tokens
All visual properties use tokens from `core.theme`.
No hardcoded colors, spacing, or typography.

## Enforcement

- CI runs `ruff check .` — flags layer violations
- CI runs `mypy .` — enforces type safety
- Code review checks all 10 rules
- Architecture Review for any new module
