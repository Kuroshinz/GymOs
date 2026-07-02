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
│  Database  │  Queue         │  External                  │
│  PluginManager │ CommandBus │ ThemeManager               │
├─────────────────────────────────────────────────────────┤
│                  Modules                                │
│  Workout  │  Nutrition  │  Recovery  │  Analytics       │
│  AI       │  Settings   │  Brain                        │
│    ┌──────┴──────┐                                     │
│    │ Coach       │  Planner  │  Reasoner               │
│    │ Memory      │  Research │  Prediction              │
│    └─────────────┘                                      │
├─────────────────────────────────────────────────────────┤
│                  Plugins                                │
│  Cronometer │ Discord │ Telegram │ Spotify              │
│  Weather    │ GitHub  │ Hevy                             │
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
- Includes database, queue, and external service abstractions

### Modules (`modules/`)
- Business logic organized by domain
- Each module follows Clean Architecture
- Communication only via EventBus (no cross-module imports)
- Modules: workout, nutrition, analytics, recovery, ai, settings, brain

### SDK (`sdk/`)
- Public contracts for plugin developers
- Re-exports from core with stable API
- Backward-compatible versioning

### Plugins (`plugins/`)
- Third-party integrations
- Follow SDK contract
- Isolated lifecycle
- Communication via EventBus

### Nexux Engines (`nexus/engines/`)
- Event-driven processors
- Cross-module analytics and predictions

## Module Clean Architecture

```
modules/<name>/
├── __init__.py          # Public exports
├── domain/              # Entities, value objects, business rules
├── application/         # Use cases, services, ports
├── infrastructure/      # Adapters, repositories (implements ports)
└── presentation/        # Controllers, view models
```

Dependency flow:
```
Presentation → Application → Domain
                    ↓
           Infrastructure
```

No layer may skip another layer.
