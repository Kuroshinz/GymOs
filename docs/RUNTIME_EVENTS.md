# Runtime Event System

## Overview

The runtime's event system connects domain events to pipelines through declarative bindings. The `Orchestrator` subscribes to the `EventBus`, and when a domain event fires, it executes all bound pipelines and records execution traces.

## Orchestrator

The central class that manages event-to-pipeline bindings, EventBus subscriptions, and execution traces.

### EventBinding

```python
EventBinding(
    event_name: str,
    pipeline_name: str,
    description: str = "",
    enabled: bool = True,
    priority: int = 0,
)
```

### PipelineTrace

```python
PipelineTrace(
    trace_id: str,
    event_name: str,
    pipeline_name: str,
    correlation_id: str,
    started_at: str,
    completed_at: str,
    duration_ms: float,
    success: bool,
    result: PipelineResult | None,
)
```

## Usage

```python
from shared.runtime.orchestrator import Orchestrator, EventBinding
from shared.events.event_bus import get_event_bus
from shared.runtime.pipeline import PipelineRegistry

bus = get_event_bus()
orchestrator = Orchestrator(event_bus=bus)
registry = PipelineRegistry()
orchestrator.set_pipeline_registry(registry)

# Register pipelines
registry.register_def(PipelineDef(name="workout_pipeline", ...))

# Bind events to pipelines
orchestrator.bind("workout.completed", "workout_pipeline")
orchestrator.bind("nutrition.meal_logged", "meal_pipeline", priority=10)

# Bind many at once
orchestrator.bind_many([
    EventBinding(event_name="recovery.score_updated", pipeline_name="recovery_pipeline"),
    EventBinding(event_name="goal.progress", pipeline_name="goal_pipeline"),
])

# Subscribe to EventBus (activates all bindings)
await orchestrator.subscribe_all()

# Unsubscribe (deactivates)
orchestrator.unsubscribe_all()
```

## How It Works

1. **`bind(event_name, pipeline_name)`** — registers a binding (no EventBus subscription yet)
2. **`subscribe_all()`** — for each unique event name, creates an async handler that iterates bindings, looks up the pipeline in the registry, executes it, and records a `PipelineTrace`
3. When an event fires via `bus.publish(event)` or `bus.publish_async(event)`, the handler executes all bound pipelines in priority order
4. **`unsubscribe_all()`** — removes all handlers from the EventBus

## Trace Recording

Each pipeline execution generates a `PipelineTrace` with timing, success status, and the full `PipelineResult`. Traces are stored in-memory (max 1000) and used by:

- `ReportGenerator` for daily/weekly reports
- `HealthMonitor` for pipeline success rate metrics
- Runtime status queries

## API

| Method | Description |
|---|---|
| `set_pipeline_registry(registry)` | Set the pipeline registry |
| `bind(event_name, pipeline_name, ...)` | Create a binding |
| `bind_many(bindings)` | Create multiple bindings |
| `unbind(event_name, pipeline_name)` | Remove a binding |
| `subscribe_all()` | Subscribe all bindings to EventBus |
| `unsubscribe_all()` | Unsubscribe all from EventBus |
| `clear_traces()` | Clear all execution traces |

### Properties

| Property | Returns |
|---|---|
| `traces` | All pipeline execution traces |
| `bindings` | All registered bindings (grouped by event name) |
| `is_subscribed` | Whether currently subscribed to EventBus |

## EventBus Integration

The runtime uses the existing `shared.events` infrastructure:

- **Event type**: `DomainEvent` (dataclass with `event_name`, `correlation_id`, `event_id`, `timestamp`, `to_dict()`, `stop_propagation()`)
- **Bus singleton**: `shared.events.event_bus.get_event_bus()`
- **Subscribe**: `bus.subscribe(event_name, handler)` — the handler receives a `DomainEvent` instance
- **Publish**: `bus.publish(event)` (sync) or `bus.publish_async(event)` (async)

The Orchestrator's handler is async and properly awaited by the EventBus's internal dispatcher.

## Domain Event Naming Convention

Events follow the pattern `<domain>.<action>`:

- `workout.completed`
- `workout.planned`
- `nutrition.meal_logged`
- `recovery.score_updated`
- `goal.progress`
- `notification.sent`
