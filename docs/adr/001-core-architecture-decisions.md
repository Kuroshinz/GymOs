# ADR-001: Core Architecture Decisions

## Status: Accepted

## Context

NEXUS needs a modular, extensible architecture that supports:
- Plugin-based integrations
- Clean separation of concerns
- Async-first I/O
- Testability

## Decisions

### 1. EventBus as Central Communication
- **Option**: Direct calls vs EventBus
- **Choice**: EventBus with middleware
- **Rationale**: Decouples modules, enables tracing, allows plugins to hook events

### 2. DI Container (not full framework)
- **Option**: Injector/DependencyInjector vs custom
- **Choice**: Custom lightweight Container
- **Rationale**: Minimal dependencies, explicit registration, easy debugging

### 3. Clean Architecture Layers
- **Option**: Flat modules vs layered
- **Choice**: Domain/Application/Presentation/Infrastructure
- **Rationale**: Proven testability, enforces boundaries

### 4. Plugin SDK as Stable API
- **Option**: Direct core imports vs SDK wrapper
- **Choice**: SDK re-exports from core
- **Rationale**: Backward compatibility, core can refactor without breaking plugins

### 5. Async Throughout
- **Option**: Sync vs async
- **Choice**: `asyncio`-based
- **Rationale**: I/O-bound operations (DB, APIs), concurrent event handling

## Consequences

- Positive: Loose coupling, testable, extensible
- Negative: More boilerplate for simple flows
- Mitigation: SDK reduces boilerplate for plugin authors
