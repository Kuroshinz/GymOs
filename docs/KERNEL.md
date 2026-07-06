# GymOS Kernel

## Purpose

The Kernel is the **Product Operating System** — the single runtime authority for product identity, capability lifecycle, RFC lifecycle, release readiness, architecture health, technical debt, and platform evolution.

It does NOT duplicate the Capability Platform. It **consumes** it, adding product-level orchestration on top.

## Architecture

```
KernelRuntimeOrchestrator (entry point)
    │
    ├── kernel_state.py ───── Product state (RFCs, releases, identity)
    ├── kernel_context.py ─── Bridge to Capability Platform
    ├── kernel_runtime.py ─── Unified runtime layer
    ├── kernel_metrics.py ─── Aggregated metrics computation
    ├── kernel_health.py ──── Multi-dimensional health assessment
    ├── kernel_history.py ─── Snapshot tracking, trends, timelines
    ├── kernel_reports.py ─── Markdown/JSON/console report generation
    └── kernel_validator.py ─ State/debt/release validation
```

### Layer Overview

| Module | Responsibility | Stateless? |
|--------|---------------|------------|
| `kernel.py` | Domain types (dataclasses, enums) | Yes |
| `kernel_state.py` | Mutable product state (RFCs, releases) | No — holds state |
| `kernel_context.py` | Consumes Capability Platform | Yes |
| `kernel_runtime.py` | Orchestrator — unified entry point | Holds state |
| `kernel_metrics.py` | Aggregated metrics | Yes |
| `kernel_health.py` | Product health scores | Yes |
| `kernel_history.py` | In-memory snapshots, trends | Holds state |
| `kernel_reports.py` | All report formats | Yes |
| `kernel_validator.py` | Validation rules | Yes |

## Relationship to Capability Platform

```
Kernel ───consumes─── Capability Platform (shared/capabilities/)
                          │
                    CapabilityRegistry (12 capabilities)
                          │
                    compute_platform_state()
                          │
                    calculate_health()
```

The Kernel does NOT:
- Define capabilities
- Maintain a second registry
- Duplicate capability health scoring
- Store capability data

The Kernel DOES:
- Add product-level state (RFCs, releases, identity)
- Compute runtime maturity from capability sub-scores
- Track history via snapshots
- Assess release readiness
- Generate product-level reports

## Key Concepts

### Product Identity
Name, version, phase (ALPHA/BETA/STABLE/MATURE), roadmap stage (FOUNDATION/GROWTH/OPTIMIZATION/EXPANSION).

### RFC Lifecycle
DRAFT → IN_REVIEW → APPROVED → IN_PROGRESS → COMPLETE | SUPERSEDED.

### Release Readiness
Computed score (0-100) with three tiers: NOT_READY, ALMOST_READY, READY. Factors: blockers, capability completion, documentation, tests, health, debt.

### Runtime Maturity
Per-capability weighted score computed from architecture, documentation, test, completion, debt, and dependency health — NOT the stored maturity level.

### Product Health
Six-dimension health: overall, architecture, engineering, knowledge, capability, documentation. Each 0-100.

### Capability History
In-memory snapshots with timeline, trend lines, and growth rates.

## Usage

```python
from shared.kernel import KernelRuntimeOrchestrator

kernel = KernelRuntimeOrchestrator()

# Get current runtime
runtime = kernel.get_runtime()
print(f"{runtime.version}: {runtime.capabilities_complete}/{runtime.total_capabilities}")

# Get metrics
metrics = kernel.get_metrics()
for m in metrics:
    print(f"{m.name}: maturity {m.runtime_maturity}")

# Assess release readiness
release = kernel.assess_release("0.5.0")
print(f"Readiness: {release.readiness.name} ({release.score}/100)")

# Take a snapshot
snapshot = kernel.take_snapshot()

# Get product health
health = kernel.get_product_health()
```

## Files

- `shared/kernel/__init__.py` — Public API
- `shared/kernel/kernel.py` — Domain types
- `shared/kernel/kernel_state.py` — Product state + `create_default_state()`
- `shared/kernel/kernel_context.py` — Capability Platform bridge
- `shared/kernel/kernel_runtime.py` — `KernelRuntimeOrchestrator`
- `shared/kernel/kernel_metrics.py` — Metrics + distribution
- `shared/kernel/kernel_health.py` — Health computation
- `shared/kernel/kernel_history.py` — HistoryStore + trends
- `shared/kernel/kernel_reports.py` — Report generators
- `shared/kernel/kernel_validator.py` — Validators
