# Capability History

## Overview

Capability History tracks how capabilities **evolve over time**. It maintains in-memory snapshots of the full kernel state and computes trends, growth rates, and timelines.

## Snapshots

A `KernelSnapshot` captures the entire kernel runtime at a point in time:

```
KernelSnapshot
    ├── timestamp
    ├── snapshot_type (MANUAL, DAILY, MILESTONE, RELEASE)
    ├── runtime (KernelRuntime)
    ├── metrics (tuple[RuntimeMetrics, ...])
    └── overall_health (float)
```

### Snapshot Types

| Type | Purpose |
|------|---------|
| MANUAL | Taken on demand by user/agent |
| DAILY | (Planned) Daily automated snapshot |
| MILESTONE | Taken at milestone completion |
| RELEASE | Taken at release time |

## Trends

Trends are computed from a series of snapshots.

### Platform Trend
Overall health over time with growth rate:

```python
trend = compute_platform_trend(snapshots)
trend.growth_rate  # +5.5 = 5.5% improvement
```

### Per-Capability Trend
Individual capability maturity over time:

```python
trend = compute_trend_for_capability(snapshots, "capability-id")
trend.points  # list of TrendPoint
trend.growth_rate  # change over time
```

### All Capabilities
```python
trends = compute_all_trends(snapshots)
```

## Timeline

A flat chronological view of all snapshots:

```python
timeline = compute_timeline(snapshots)
# [{"timestamp": "...", "type": "MANUAL", "overall_health": 59.7, ...}, ...]
```

## Growth Rate

Simple formula: `(last_value - first_value) / first_value * 100`

- **Positive** = improving
- **Negative** = declining
- **Zero** = stable or no data

## HistoryStore

In-memory store with basic CRUD:

```python
store = HistoryStore()
store.record(snapshot)
store.get_all()
store.get_by_type(KernelSnapshotType.MANUAL)
store.get_latest()
store.clear()
```

## Reports

### Capability Timeline Report
```python
report = generate_capability_timeline_report(snapshots)
```
Outputs: snapshot count, platform growth rate, per-capability growth rates.

### Technical Debt Summary
```python
report = generate_debt_summary(debt_items)
```
Outputs: grouped by capability, with blocking counts.

## Key Files

- `shared/kernel/kernel.py` — `KernelSnapshot`, `CapabilityTrend`, `TrendPoint`
- `shared/kernel/kernel_history.py` — `HistoryStore`, `compute_timeline()`, `compute_trend_for_capability()`, `compute_all_trends()`, `compute_platform_trend()`
- `shared/kernel/kernel_reports.py` — `generate_capability_timeline_report()`, `generate_debt_summary()`
