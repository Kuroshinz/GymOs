# NEXUS Architecture Overview

## System Design

```
┌─────────────────────────────────────────────────────────┐
│                     Applications                         │
│  (CLI, Desktop, Mobile, Web)                            │
├─────────────────────────────────────────────────────────┤
│                     SDK Layer                            │
│  Plugin  │  Event  │  Theme  │  Widget  │  Command      │
├─────────────────────────────────────────────────────────┤
│                  Core Platform                           │
│  EventBus  │  DI Container  │  Scheduler                │
│  Config    │  Cache         │  Logger                    │
│  Security  │  Notifications │  Settings                  │
│  PluginManager │ CommandBus │ ThemeManager               │
├─────────────────────────────────────────────────────────┤
│                  Nexus Engines                           │
│  Workout  │  Nutrition  │  Recovery  │  Analytics       │
│  Prediction │  AI                                       │
├─────────────────────────────────────────────────────────┤
│                  Infrastructure                          │
│  Database  │  Cache Store  │  Queue  │  External APIs   │
└─────────────────────────────────────────────────────────┘
```

## Core Principles

1. **Event-Driven**: All module communication goes through EventBus
2. **Dependency Injection**: Services resolved via Container
3. **Plugin-Based**: Extensions via SDK contract
4. **Clean Architecture**: Domain → Application → Presentation → Infrastructure
5. **Immutable Events**: Events are value objects with metadata

## Layer Boundaries

### Core (`core/`)
- Framework-agnostic infrastructure services
- No business logic
- Singleton services managed by Container

### SDK (`sdk/`)
- Public contracts for plugin developers
- Re-exports from core with stable API
- Backward-compatible versioning

### Nexus Engines (`nexus/engines/`)
- Business logic aggregates
- Subscribe to domain events
- Produce analytics/recommendations

### Source Modules (`src/<module>/`)
- **domain/**: Entities, value objects, enums
- **application/**: Use cases, ports
- **presentation/**: UI/view models
- **infrastructure/**: Adapters (DB, APIs)

### Plugins (`plugins/`)
- Third-party integrations
- Follow SDK contract
- Isolated lifecycle
