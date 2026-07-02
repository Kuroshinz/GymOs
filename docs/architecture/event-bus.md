# Event Bus Architecture

## Overview

EventBus is the central communication backbone. All inter-module communication passes through it.

## Event Object

```python
Event:
  id: str              # Unique 12-char hex
  name: str            # Dot-notation: "workout.created"
  data: dict           # Payload
  timestamp: datetime  # UTC
  source: str          # Origin module
  correlation_id: str  # Trace across events
```

## Event Naming Convention

```
<domain>.<action>[.<sub_action>]

Examples:
  workout.created
  workout.completed
  nutrition.meal_logged
  analytics.updated
  plugin.loaded
  platform.started
```

## Wildcard Subscriptions

| Pattern | Matches |
|---------|---------|
| `workout.*` | `workout.created`, `workout.completed` |
| `*.error` | `workout.error`, `db.error` |
| `**` | All events |

## Middleware Pipeline

Middleware run before handlers:

```python
bus.use(lambda event, bus: log_event(event))
```

Use cases: logging, validation, metrics, tracing.

## Handler Contract

```python
async def handler(event: Event) -> None: ...
```

- Handlers run concurrently via `asyncio`
- Exceptions in one handler don't affect others
- `event.stop_propagation()` halts further handlers
