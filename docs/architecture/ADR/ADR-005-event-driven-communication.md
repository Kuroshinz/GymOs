# ADR-005: Event-Driven Communication

**Status:** Accepted

**Date:** 2026-07-03

---

## Context

GymOS modules must communicate without direct imports. The initial prototype used both direct imports and string-based events, leading to:
- Hidden coupling between modules (workout importing nutrition directly)
- Duplicate event definitions (the Sprint 3.2 `MealLogged` bug)
- No traceability for event flows
- Runtime errors from misspelled event names

## Decision

### 1. EventBus as Exclusive Cross-Module Channel

All inter-module communication MUST go through the EventBus. Direct imports between modules are forbidden:
- `modules.workout` → `modules.nutrition` ❌
- `modules.workout` → `shared.events` → EventBus → `modules.nutrition` ✅

### 2. Typed DomainEvent Hierarchy

Every event MUST be a frozen dataclass extending `DomainEvent`:

```
DomainEvent (base)
├── WorkoutStarted
├── WorkoutCompleted
├── ExerciseCompleted
├── SetCompleted
├── ProgramImported
├── ProgramActivated
├── BodyWeightUpdated
├── PersonalRecordUnlocked
├── RecoveryScoreUpdated
├── MealLogged
├── NutritionUpdated
├── MacroTargetChanged
├── ExerciseKnowledgeUpdated
└── RecommendationsUpdated
```

### 3. Event Naming Convention

Event class names use `PascalCase` with domain context (`MealLogged`, not `MealLoggedEvent`). The string serialization uses dot notation: `"nutrition.meal_logged"`.

| Domain | Class Name | Serialized |
|--------|-----------|------------|
| Workout | `WorkoutCompleted` | `workout.completed` |
| Nutrition | `MealLogged` | `nutrition.meal_logged` |
| Nutrition | `NutritionUpdated` | `nutrition.updated` |
| Recovery | `RecoveryScoreUpdated` | `recovery.score_updated` |

### 4. Publisher → EventBus → Subscriber Flow

```
Publisher module → DomainEvent → EventBus.publish(event)
                                      ↓
                              Middleware pipeline (logging, metrics, validation)
                                      ↓
                              Concurrent dispatch to subscribers
                                      ↓
                              Subscriber modules react to events
```

Publishers do not know who subscribes. Subscribers do not know who publishes. The EventBus mediates all communication.

### 5. Subscriber Registration

Subscribers register via:
```python
event_bus.subscribe("nutrition.meal_logged", handler_function)
# or with wildcards:
event_bus.subscribe("nutrition.*", handler_function)
event_bus.subscribe("**", logging_handler)
```

### 6. Event Schema Registry

All event classes MUST be registered in `DOMAIN_EVENT_REGISTRY` in `shared/events/domain_events.py`. The registry maps class names to classes for deserialization:

```python
DOMAIN_EVENT_REGISTRY: dict[str, type[DomainEvent]] = {
    "WorkoutStarted": WorkoutStarted,
    "WorkoutCompleted": WorkoutCompleted,
    ...
}
```

### 7. Event Serialization

Events MUST support round-trip serialization:
```python
event_dict = event.to_dict()         # Event → dict
restored = event_from_dict(event_dict)  # dict → Event
```

This enables event persistence, replay testing, and cross-process communication.

### 8. Error Isolation

Each subscriber runs in an isolated try/except. A failing subscriber MUST NOT crash other subscribers or the EventBus. Errors MUST be logged at ERROR level.

### 9. No Sync Return Values

Event publishing is fire-and-forget. Publishers MUST NOT expect return values from subscribers. If a response is needed, use a request/response event pair.

## Consequences

- **Positive:** Zero direct coupling between modules
- **Positive:** Event flows are traceable and auditable
- **Positive:** New subscribers can be added without modifying publishers
- **Positive:** Event replay enables integration testing without real data sources
- **Negative:** Control flow is harder to follow (no direct call chain)
- **Negative:** Debugging requires event tracing middleware
- **Negative:** Event schema evolution must be backward-compatible

## Compliance

All modules MUST:
- Publish typed `DomainEvent` instances via `EventBus.publish()`
- Subscribe via `EventBus.subscribe()` with typed handlers
- Register event classes in `DOMAIN_EVENT_REGISTRY`
- Handle `to_dict()` / `event_from_dict()` round-trips
- Never catch exceptions from EventBus dispatch in subscriber code

## Related

- ADR-001: Event Architecture
- Architecture Constitution Article I.5, Article VI.2
- `shared/events/domain_events.py`
- `shared/events/event_bus.py`
- `docs/architecture/event-bus.md`
- `docs/EVENT_SYSTEM.md`
- `docs/DOMAIN_EVENTS.md`
