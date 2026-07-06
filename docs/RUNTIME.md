# GymOS Intelligence Runtime

## Overview

The Intelligence Runtime (`shared/runtime/`) is the central orchestration layer that transforms GymOS from disconnected engines into a continuously operating intelligent system. It coordinates cross-engine workflows, monitors system health, collects runtime context, generates operational reports, and schedules recurring cycles.

## Architecture

```
Runtime
├── PipelineRegistry     — registered pipeline definitions
├── Orchestrator         — EventBus bindings → pipeline execution → traces
├── Scheduler            — 7 cycle types with pluggable handlers
├── ContextCollector     — pluggable providers for 11 context sections
├── HealthMonitor        — heartbeats, engine checks, pipeline metrics, health score
└── ReportGenerator      — daily/weekly/event/health/cycle reports
```

## Quick Start

```python
from shared.runtime import create_runtime

runtime = create_runtime()
await runtime.initialize()

# Register a pipeline
from shared.runtime.pipeline import PipelineDef
async def my_step(event, ctx):
    return {"result": "processed"}
runtime.pipelines.register_def(PipelineDef(name="my_pipeline", steps=[("step1", my_step)]))

# Bind to an event
runtime.orchestrator.bind("workout.completed", "my_pipeline")

# Start
await runtime.start()
# System is now live — events trigger pipelines automatically

# Run a cycle
result = await runtime.run_cycle("morning")

# Check health
report = await runtime.check_health()

# Generate reports
daily = await runtime.daily_report()

# Stop
await runtime.stop()
```

## Key Concepts

### Pipelines
Sequences of async steps executed in order. Each step receives the triggering event and a shared context dict. Steps can produce output that flows into subsequent steps. See `docs/RUNTIME_PIPELINE.md`.

### Scheduler Cycles
7 predefined cycles (morning, workout, meal, recovery, night, weekly, monthly) with pluggable handlers. Cycles are triggered on demand, not by wall-clock timer. See `docs/RUNTIME_SCHEDULER.md`.

### Event-Driven Orchestration
The Orchestrator subscribes to the EventBus and executes pipelines in response to domain events. All bindings are registered declaratively. See `docs/RUNTIME_EVENTS.md`.

### Context Collection
11 context sections (user, workout, nutrition, recovery, health, goals, environment, system, notification, schedule, pipeline) populated by pluggable providers.

### Health Monitoring
Tracks heartbeats per engine, pipeline success/failure rates, cycle results, and computes a weighted health score.

### Reports
Daily and weekly report generation with pipeline traces, event traces, health summaries, cycle summaries, and context snapshots.

## Design Constraints

- **No AI/LLM** — all logic is deterministic and event-driven
- **No engine internals** — depends only on `shared.events` public API
- **No cross-module imports** — never imports from `modules/`, `nexus/`, or `core/`
- **Async throughout** — all execution uses `asyncio`
- **EventBus only** — zero polling for event-driven processing
