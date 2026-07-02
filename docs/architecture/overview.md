# GymOS Architecture Overview

## System Design

```
┌──────────────────────────────────────────────────────────┐
│                     Applications                          │
│  (CLI, Desktop PySide6, Mobile, Web)                     │
├──────────────────────────────────────────────────────────┤
│                     SDK Layer                             │
│  Plugin  │  Event  │  Theme  │  Widget  │  Command       │
├──────────────────────────────────────────────────────────┤
│                   Core Platform                           │
│  EventBus  │  DI Container  │  Scheduler                 │
│  Config    │  Cache         │  Logger                     │
│  Security  │  Notifications │  Settings                   │
│  Database  │  Queue         │  External Services          │
│  PluginManager │ CommandBus │ ThemeManager                │
├──────────────────────────────────────────────────────────┤
│                   Modules                                │
│  Workout  │  Nutrition  │  Dashboard  │  Analytics       │
│  Recovery │  Settings   │  Progress   │                   │
│                   AI / Brain                              │
│    ┌──────────────┴──────────────┐                       │
│    │ Coach  │  Reasoner  │       │                       │
│    │ Memory │  Research  │       │                       │
│    └─────────────────────────────┘                       │
├──────────────────────────────────────────────────────────┤
│                   Engines                                 │
│  WorkoutEngine │ NutritionEngine │ RecoveryEngine         │
│  AnalyticsEngine │ AIEngine │ PredictionEngine            │
├──────────────────────────────────────────────────────────┤
│                   Plugins                                 │
│  Cronometer │ Discord │ Telegram │ Spotify                │
│  Weather    │ GitHub  │ Hevy                              │
└──────────────────────────────────────────────────────────┘
```

## Core Principles

1. **Event-Driven**: All module communication goes through EventBus
2. **Dependency Injection**: Services resolved via Container
3. **Plugin-Based**: Extensions via SDK contract
4. **Clean Architecture**: Domain → Application → Presentation → Infrastructure
5. **Immutable Events**: Events are value objects with metadata
6. **Offline-First**: All features work without internet

## Layer Boundaries

### Core (`core/`)
- Framework-agnostic infrastructure services
- No business logic
- Singleton services managed by Container
- Database, queue, external service abstractions
- EventBus, DI Container, Theme Manager, Scheduler, Logger

### Modules (`modules/`)
- Business logic organised by domain
- Each module follows Clean Architecture (4 layers)
- Communication only via EventBus (no cross-module imports)
- Modules: workout, nutrition, dashboard, analytics, recovery, settings, brain

### Engines (`nexus/engines/`)
- Event-driven processors
- Cross-module analytics, predictions, and AI
- Subscribe to domain events and produce derived insights

### SDK (`sdk/`)
- Public contracts for plugin developers
- Re-exports from core with stable API
- Backward-compatible versioning

### Plugins (`plugins/`)
- Third-party integrations
- Follow SDK contract
- Isolated lifecycle
- Communication via EventBus

## Data Flow

```
User Input → Controller → Use Case → Domain Entity
                ↓
           Repository ← Infrastructure
                ↓
         Database (SQLite)
```

Events flow:
```
Module A → emit(event) → EventBus → Module B (handler)
                                   → Engine (analytics)
                                   → Plugin (integration)
```

## AI Knowledge Integration

All AI features read domain knowledge from `knowledge/`:

```
AI Engine → Context Builder → knowledge/exercises/*.json
                              knowledge/progression/*.md
                              knowledge/nutrition/*.md
                              knowledge/recovery/*.md
           → LLM → Structured Response
```

## Project Structure

```
nexus/
├── .ai/                    # Agent identity and process files
├── .opencode/              # OpenCode skills configuration
├── core/                   # Infrastructure services
├── modules/                # Business modules (Clean Architecture)
├── nexus/
│   ├── platform.py         # Platform bootstrap
│   └── engines/            # Event-driven engines
├── sdk/                    # Plugin SDK
├── plugins/                # Third-party integrations
├── shared/                 # Constants, types, exceptions, helpers
├── tests/                  # Unit, integration, UI, performance
├── docs/                   # Product and technical documentation
├── knowledge/              # Domain knowledge (exercises, nutrition, etc.)
├── resources/              # Themes, icons, fonts, images
└── scripts/                # Build, release, migration, backup
```
