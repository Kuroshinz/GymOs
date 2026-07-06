# ADR-019: GymOS Intelligence Runtime

## Status

Accepted

## Context

GymOS platform engines (Planning, Optimizer, Knowledge, Evolution, Adaptive, Prediction, Recovery) are mature but operate as disconnected silos. There is no central orchestration layer that:

1. Coordinates execution of cross-engine workflows (pipelines)
2. Provides lifecycle management (startup, shutdown, health monitoring)
3. Collects and exposes runtime context (system state, engine status, pipeline metrics)
4. Generates operational reports (daily, weekly, cycle summaries)
5. Schedules recurring cycles (morning, workout, meal, recovery, night, weekly, monthly)

Each engine implements its own internal logic, but the runtime must not duplicate or import internal engine code — it operates only through public event APIs.

## Decision

Create `shared/runtime/` as a stateless, event-driven orchestration layer with eight sub-modules:

### Modules

| Module | Responsibility |
|---|---|
| `runtime.py` | Top-level `Runtime` facade owning all sub-modules |
| `pipeline.py` | `Pipeline`, `PipelineDef`, `PipelineStep`, `PipelineRegistry`, `PipelineResult` — async step execution |
| `scheduler.py` | `Scheduler`, `RuntimeCycle` (7 cycle types), `CycleResult` — cycle lifecycle |
| `orchestrator.py` | `Orchestrator`, `EventBinding`, `PipelineTrace` — EventBus subscriptions → pipeline execution |
| `context.py` | `RuntimeContext` (11 sections), `ContextCollector` with pluggable providers |
| `health.py` | `HealthMonitor`, `Heartbeat`, `EngineStatus`, `PipelineMetrics`, `HealthReport` |
| `reports.py` | `ReportGenerator`, `DailyReport`, `WeeklyReport` — 5 report formats |
| `__init__.py` | `create_runtime()` factory, `Runtime` re-export |

### Key Design Rules

- **No AI, no LLM** — all logic is deterministic and event-driven
- **No engine internals** — runtime depends only on `shared.events` public API (`DomainEvent`, `EventBus`)
- **No cross-module imports** — runtime never imports from `modules/`, `nexus/`, or `core/` (except `shared.events`)
- **Async throughout** — all I/O and execution uses `asyncio`
- **EventBus subscriptions** are the only mechanism for event-driven processing (zero polling)
- **Pipeline steps** are async callables receiving `(DomainEvent, context_dict)` and returning optional dicts
- **Scheduler cycles** are triggered on demand (by events or manual calls), not by wall-clock timer

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

## Consequences

Positive:
- Central coordination of cross-engine workflows without duplicating engine logic
- Unified health monitoring, reporting, and context collection
- Event-driven reactivity through existing EventBus infrastructure
- Deterministic, testable architecture (152 unit tests)

Negative:
- Additional abstraction layer introduces indirection
- All engine integration must happen through event subscriptions, not direct calls

## Test Coverage

- 152 unit tests across all 8 modules
- 100% coverage of pipeline execution paths (success, partial, failure)
- All scheduler cycles tested (morning, workout, meal, recovery, night, weekly, monthly)
- Orchestrator integration tests with real EventBus subscriptions

## File Impact

- 8 new source files in `shared/runtime/`
- 7 new test files in `tests/unit/runtime/`
- 1 fix in `shared/events/event_bus.py` (async handler support + deserialization fallback)
- 0 modifications to existing engines or business logic
