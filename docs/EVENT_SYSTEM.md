# Event System Architecture

GymOS uses an event-driven architecture to decouple modules. Modules communicate exclusively through domain events — no module imports or calls another module directly.

## Why Event-Driven?

- **Decoupling**: Adding a new module never requires changing existing modules
- **Extensibility**: New subscribers can react to existing events without modifying publishers
- **Audit trail**: Every significant domain action is recorded as an event
- **Replay**: Events can be replayed for debugging, recovery, or populating new subscribers
- **Testability**: Modules can be tested in isolation by publishing/subscribing to events

## Core Layers

### 1. Transport Layer (`core/event_bus/`)

Low-level async event bus with:
- Pattern-matched subscriptions (wildcard support via `fnmatch`)
- Middleware pipeline
- Handler exception isolation (one failing handler never breaks others)
- `stop_propagation()` support
- `once()` auto-unsubscribe
- Correlation ID propagation

### 2. Typed Domain Layer (`shared/events/`)

Typed wrapper around the transport layer:

| Component | File | Purpose |
|-----------|------|---------|
| `DomainEvent` | `event.py` | Base dataclass for all events — `event_id`, `timestamp`, `source`, `event_version`, `correlation_id`, `to_dict()`, `from_dict()` |
| Domain events | `domain_events.py` | Typed event subclasses with strongly-typed payloads |
| `EventBus` | `event_bus.py` | Typed publish/subscribe wrapping the core bus |
| `Publisher` | `publisher.py` | Base class for module publishers |
| `Subscriber` | `subscriber.py` | ABC for subscribers — automatic registration via `handled_events()` |
| `EventStore` | `store.py` | Event persistence to JSONL files with replay support |
| `Dispatcher` | `dispatcher.py` | Auto-discovery and registration of subscriber classes |

### 3. Module Publishers (`shared/events/publishers/`)

Typed publishers for each module:

- `WorkoutPublisher` — workout lifecycle events
- `ProgramPublisher` — program import/activation events
- `KnowledgePublisher` — knowledge update events
- `NutritionPublisher` — meal logging events

### 4. Subscribers (`shared/events/subscribers/`)

| Subscriber | Handles | Purpose |
|------------|---------|---------|
| `PRSubscriber` | WorkoutCompleted | Detects personal records |
| `RecoverySubscriber` | WorkoutCompleted | Analyses recovery impact |
| `VolumeSubscriber` | WorkoutCompleted | Records volume analytics |
| `DashboardSubscriber` | WorkoutCompleted, PR, Weight, Program | Updates dashboard state |
| `AnalyticsSubscriber` | All events | Event logging and aggregation |
| `GymBrainSubscriber` | All events | Future AI/ML integration (placeholder) |

## Event Schema

Every event carries:
- `event_id` — unique 16-char hex identifier
- `event_name` — class name (e.g. `WorkoutCompleted`)
- `event_version` — semantic version (e.g. `1.0`)
- `source` — originating module (e.g. `workout`, `workout_program`)
- `timestamp` — ISO 8601 UTC timestamp
- `correlation_id` — trace ID linking related events
- `payload` — typed event-specific fields

## Usage

### Publishing an Event

```python
from shared.events import get_event_bus
from shared.events.domain_events import WorkoutCompleted

bus = get_event_bus()
bus.publish(WorkoutCompleted(
    workout_id="w123",
    total_volume_kg=15000.0,
    total_sets=24,
))
```

### Using a Module Publisher

```python
from shared.events.publishers.workout_publisher import WorkoutPublisher

pub = WorkoutPublisher(bus)
pub.publish_workout_completed(
    workout_id="w123",
    total_volume_kg=15000.0,
    total_sets=24,
)
```

### Subscribing to Events

```python
from shared.events import get_event_bus
from shared.events.domain_events import WorkoutCompleted

bus = get_event_bus()

def on_workout_done(event: WorkoutCompleted):
    print(f"Workout {event.workout_id} done: {event.total_sets} sets")

bus.subscribe_class(WorkoutCompleted, on_workout_done)
```

### Creating a Custom Subscriber

```python
from shared.events.subscriber import Subscriber
from shared.events.domain_events import WorkoutCompleted, DomainEvent

class MySubscriber(Subscriber):
    def handled_events(self):
        return [WorkoutCompleted]

    def handle(self, event: DomainEvent):
        if isinstance(event, WorkoutCompleted):
            print(f"Workout: {event.workout_id}")
```

## Auto-Discovery

Subscribers in `shared/events/subscribers/` are auto-discovered:

```python
from shared.events.dispatcher import register_subscribers
instances = register_subscribers()
```
