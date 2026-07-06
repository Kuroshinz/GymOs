# Runtime Scheduler

## Overview

The Scheduler manages 7 predefined runtime cycles. Each cycle represents a phase of the GymOS daily/weekly/monthly operational loop. Cycles are triggered **on demand** (by events or manual calls), not by wall-clock timer — keeping the system purely event-driven.

## Runtime Cycles

| Cycle | Enum Value | Typical Purpose |
|---|---|---|
| Morning | `MORNING` | Daily initialization, morning readiness check |
| Workout | `WORKOUT` | Post-workout processing, logging, analysis |
| Meal | `MEAL` | Meal logging, nutrition analysis |
| Recovery | `RECOVERY` | Recovery score update, readiness check |
| Night | `NIGHT` | End-of-day aggregation, daily summary |
| Weekly | `WEEKLY` | Weekly trend analysis, report generation |
| Monthly | `MONTHLY` | Monthly aggregation, long-term insights |

## Usage

```python
from shared.runtime.scheduler import Scheduler, RuntimeCycle, CycleResult

scheduler = Scheduler()

# Register a handler
async def morning_routine() -> CycleResult:
    # ... processing ...
    return CycleResult(cycle=RuntimeCycle.MORNING, pipelines_run=["p1", "p2"])

scheduler.register_cycle_handler(RuntimeCycle.MORNING, morning_routine)

# Run a cycle
result = await scheduler.run_cycle(RuntimeCycle.MORNING)
# Or using convenience method:
result = await scheduler.run_morning()

# Multiple handlers for same cycle
async def another_handler():
    return CycleResult(cycle=RuntimeCycle.MORNING, pipelines_run=["p3"])
scheduler.register_cycle_handler(RuntimeCycle.MORNING, another_handler)
```

## CycleResult

```python
CycleResult(
    cycle: RuntimeCycle,
    started_at: str,
    completed_at: str,
    duration_ms: float,
    success: bool,
    error: str | None,
    pipelines_run: list[str],
)
```

## API

| Method | Description |
|---|---|
| `register_cycle_handler(cycle, handler)` | Register a handler for a cycle |
| `unregister_cycle_handler(cycle, handler)` | Remove a handler |
| `run_cycle(cycle, trigger_event=None)` | Execute all handlers for a cycle |
| `run_morning()` | Convenience for `run_cycle(MORNING)` |
| `run_workout()` | Convenience for `run_cycle(WORKOUT)` |
| `run_meal()` | Convenience for `run_cycle(MEAL)` |
| `run_recovery()` | Convenience for `run_cycle(RECOVERY)` |
| `run_night()` | Convenience for `run_cycle(NIGHT)` |
| `run_weekly()` | Convenience for `run_cycle(WEEKLY)` |
| `run_monthly()` | Convenience for `run_cycle(MONTHLY)` |

### Properties

| Property | Returns |
|---|---|
| `recent_results` | All `CycleResult` entries |
| `last_result` | Most recent `CycleResult` or `None` |
| `clear_results()` | Clear all stored results |
