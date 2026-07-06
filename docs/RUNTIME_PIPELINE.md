# Runtime Pipeline System

## Overview

The pipeline system executes multi-step async workflows in response to domain events. Pipelines are defined declaratively, registered in a `PipelineRegistry`, and executed by the `Orchestrator` when bound events fire.

## Pipeline Lifecycle

1. **Define** — create a `PipelineDef` with a name and ordered list of `(step_name, handler)` tuples
2. **Register** — add to `PipelineRegistry`
3. **Bind** — connect an event name to the pipeline via `Orchestrator.bind(event_name, pipeline_name)`
4. **Execute** — when the event fires, the `Orchestrator` handler executes the pipeline asynchronously

## PipelineDef

```python
PipelineDef(
    name: str,
    steps: list[tuple[str, StepHandler]],
    description: str = "",
    timeout_ms: float = 30000.0,
)
```

## Step Handlers

Steps are async (or sync) callables with signature:

```python
async def handler(event: DomainEvent, context: dict) -> dict | None:
    # Process the event
    return {"key": "value"}  # merged into context for downstream steps
```

- Return `None` or `{}` — no context merge
- Return a dict — merged into shared context (accessible by subsequent steps)
- Raise an exception — step fails, pipeline continues to next step

## PipelineResult

```python
PipelineResult(
    pipeline_id: str,
    pipeline_name: str,
    trigger_event: str,
    correlation_id: str,
    status: PipelineStatus,     # PENDING → RUNNING → COMPLETED | PARTIAL | FAILED
    steps: list[PipelineStep],
    started_at: str,
    completed_at: str,
    total_duration_ms: float,
    error: str | None,
)
```

### Status Rules

| Condition | Status |
|---|---|
| All steps succeeded | COMPLETED |
| Some steps succeeded, some failed | PARTIAL |
| All steps failed | FAILED |
| No steps defined | COMPLETED |

### Properties

| Property | Returns |
|---|---|
| `success` | `True` if COMPLETED or PARTIAL |
| `step_count` | Number of steps |
| `failed_steps` | List of failed PipelineStep |
| `duration_s` | Total duration in seconds |

## PipelineStep

```python
PipelineStep(
    step_id: str,
    name: str,
    processor: str,
    duration_ms: float,
    status: PipelineStatus,
    error: str | None,
    output: dict | None,
    started_at: str | None,
    completed_at: str | None,
)
```

## PipelineRegistry

| Method | Description |
|---|---|
| `register(pipeline)` | Register a `Pipeline` instance |
| `register_def(pipeline_def)` | Register a `PipelineDef`, returns new `Pipeline` |
| `unregister(name)` | Remove a pipeline by name |
| `get(name)` | Lookup by name (returns `Pipeline` or `None`) |
| `clear()` | Remove all pipelines |

## Example

```python
from shared.runtime.pipeline import PipelineDef, PipelineRegistry
from shared.events.event import DomainEvent

async def validate_workout(event: DomainEvent, ctx: dict) -> dict:
    data = event.to_dict().get("payload", {})
    if not data.get("duration"):
        raise ValueError("Missing duration")
    return {"validated": data}

async def log_workout(event: DomainEvent, ctx: dict) -> dict:
    print(f"Workout logged: {ctx['validated']}")
    return {"logged": True}

pdef = PipelineDef(
    name="workout_logger",
    steps=[
        ("validate", validate_workout),
        ("log", log_workout),
    ],
)

reg = PipelineRegistry()
reg.register_def(pdef)
```
