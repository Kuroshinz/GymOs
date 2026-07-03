# ADR-001: Event Architecture

**Status:** Accepted (supersedes `docs/adr/001-core-architecture-decisions.md` §1)

**Date:** 2026-07-03

---

## Context

GymOS needs a robust event communication layer that:
- Decouples modules so they never import each other directly
- Supports tracing and replay for debugging and testing
- Enables plugins to hook into any system event
- Provides schema evolution without breaking existing subscribers
- Works in both sync and async contexts

The initial prototype used a string-based event bus with dict payloads, which lacked type safety, discoverability, and schema evolution guarantees.

## Decision

### 1. Typed Domain Events

All events MUST be frozen dataclasses extending `shared.events.domain_events.DomainEvent`:

```python
@dataclass(frozen=True)
class MealLogged(DomainEvent):
    meal_name: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    date: str
```

**Rationale:** Type safety, IDE autocompletion, schema documentation, serialization round-trips.

### 2. Single Event Registry

All event classes MUST be registered in `DOMAIN_EVENT_REGISTRY` (a `dict[str, type[DomainEvent]]`) in `shared/events/domain_events.py`. This enables deserialization from storage or wire format.

**Rationale:** A single source of truth for event types. Prevents the duplicate-event bug that occurred in Sprint 3.2 (MealLogged existed in two files).

### 3. EventBus as Singleton Mediator

A single `EventBus` instance mediates all publish/subscribe. It supports:
- Typed event publishing via `publish(event: DomainEvent)`
- Wildcard subscription patterns (`workout.*`, `**`)
- Concurrent async handler dispatch
- Middleware pipeline for logging, metrics, validation

**Rationale:** Central coordination enables tracing, debugging, and consistent middleware application.

### 4. Append-Only Event Schema

Events are append-only. New fields MUST have default values. Removing or renaming fields requires a new event version.

**Rationale:** Backward compatibility with stored events and running subscribers.

### 5. Subscriber Isolation

Each subscriber runs in its own try/except. A failing subscriber MUST NOT crash other subscribers or the EventBus itself.

**Rationale:** Resilience. One broken integration must not take down the platform.

## Consequences

- **Positive:** Type-safe, discoverable, testable event system
- **Positive:** Event replay tests verify serialization round-trips
- **Positive:** Plugins subscribe to the same typed events
- **Negative:** Adding a new event requires updating the registry (one line)
- **Negative:** Append-only means old events accumulate deprecated fields

## Compliance

All modules MUST:
- Define events in `shared/events/domain_events.py` only
- Register in `DOMAIN_EVENT_REGISTRY`
- Publish typed `DomainEvent` instances (not strings + dicts)
- Never raise exceptions from subscribers

## Related

- ADR-005: Event-Driven Communication
- Architecture Constitution Article I.5, Article VI.2
