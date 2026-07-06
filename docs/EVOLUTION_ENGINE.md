# Evolution Engine

**Part of:** RFC-018.6 — GymOS Evolution Engine

---

## 1. Overview

The Evolution Engine understands how GymOS evolves over time. It answers:

- How much has GymOS evolved?
- Which RFC contributed the most?
- Which capability improved the fastest?
- What is required to reach v1.0?
- What is the predicted maturity after the next RFCs?
- How are RFCs, capabilities, milestones, and versions linked?

It consumes the Kernel (shared/kernel/) and Capability Platform (shared/capabilities/) to produce evolution analysis. It does not duplicate their data.

### Architecture

```
Capability Platform ─┐
                     ├──> Kernel ──> Evolution Engine ──> Reports
Product Identity ────┘
```

The evolution chain flows as:

```
RFC → Capability → Milestone → Version
```

---

## 2. Module Structure

```
shared/evolution/
├── __init__.py           # EvolutionOrchestrator — unified entry point
├── evolution_engine.py   # Core dataclasses (ProductCompletion, EvolutionVelocity, etc.)
├── timeline.py           # Timeline builders (evolution, RFC, capability growth, chain)
├── forecast.py           # Forecast engine (release, capability, product completion)
├── version_graph.py      # Version readiness trend builder
├── milestone_graph.py    # Milestone progress tracker
├── capability_history.py # Capability velocity, evolution velocity, RFC contributions
├── rfc_history.py        # RFC impact scoring
├── product_forecast.py   # Product completion forecast
└── reports.py            # Markdown and JSON report generators
```

---

## 3. Core Concepts

### 3.1 Evolution Chain

The evolution chain links RFC → Capability → Milestone → Version:

- **RFC**: A product change proposal (e.g., RFC-018 Capability Platform)
- **Capability**: A subsystem affected by an RFC (e.g., capability-platform)
- **Milestone**: A product milestone grouping capabilities (e.g., Platform Maturity)
- **Version**: A release version delivering milestones (e.g., v0.5.0)

The chain is built by `build_evolution_chain()` in `timeline.py`.

### 3.2 Evolution Velocity

The product-wide evolution velocity tracks:

- `maturity_delta`: Average capability health across all capabilities
- `capabilities_completed`: Number of completed capabilities
- `rfc_impact_sum`: Sum of all RFC impact scores
- `velocity_score`: Weighted composite of the above

### 3.3 RFC Impact Score

Each RFC is scored on:

- **Completion Ratio** (40%): Completed / affected capabilities
- **Maturity Gain** (30%): Average health of affected capabilities
- **Product Health** (30%): Overall platform health delta

Scores are multiplied by status modifiers: COMPLETE (1.0x), IN_PROGRESS (0.5x), DRAFT (0.1x).

### 3.4 RFC Contribution

Each RFC's contribution to overall product evolution is calculated as its percentage share of the total impact score.

### 3.5 Capability Velocity

Each capability's velocity is computed as:

- `maturity_gain`: Current health score
- `time_periods`: Number of snapshots tracking this capability
- `velocity`: Maturity gain per time period
- `growth_rate`: Percentage growth across snapshots

### 3.6 Forecasting

The forecast engine uses simple extrapolation:

- **Release Forecast**: Predicts readiness for a target version based on current trajectory
- **Capability Forecast**: Predicts future maturity of a single capability
- **Product Completion Forecast**: Predicts when v1.0 will be reached

---

## 4. Data Flow

### 4.1 Computing Product Completion

```
compute_product_completion()
  → compute_platform_state()          [capabilities]
  → estimate_remaining_work()         [forecast]
  → ProductCompletion                 [dataclass]
```

### 4.2 Building Evolution Timeline

```
build_evolution_timeline(snapshots, rfcs, releases)
  → TimelineEntry per RFC, release, snapshot
  → Sort by timestamp
  → EvolutionTimeline
```

### 4.3 Computing RFC Impact

```
compute_rfc_impact_scores(snapshots)
  → create_default_state()            [kernel]
  → For each RFC: match capabilities
  → Calculate completion, maturity, health
  → Weighted composite score
  → Sorted list of RfcImpactScore
```

### 4.4 Building Evolution Chain

```
build_evolution_chain(snapshots)
  → _get_rfc_capability_mapping()     [RFC -> capabilities]
  → _get_capability_milestone_mapping() [capability -> milestone]
  → For each RFC/capability: build chain link
  → EvolutionChain
```

---

## 5. Report Types

| Report | Function | Format | Content |
|--------|----------|--------|---------|
| Evolution Report | `generate_evolution_report()` | Markdown | Full product evolution analysis |
| Version Report | `generate_version_report()` | Markdown | Version-by-version progress |
| Timeline Report | `generate_timeline_report()` | Markdown | Chronological event timeline |
| Forecast Report | `generate_forecast_report()` | Markdown | Product completion forecast |
| Product Journey | `generate_product_journey()` | Markdown | Full evolution story |
| JSON Report | `generate_json_evolution_report()` | dict | Machine-readable evolution data |
| Evolution Summary | `generate_evolution_summary_report()` | Markdown | Concise one-table summary |

---

## 6. Usage

```python
from shared.evolution import EvolutionOrchestrator

engine = EvolutionOrchestrator()

# Metrics
completion = engine.get_product_completion()
velocities = engine.get_capability_velocities()
impacts = engine.get_rfc_impacts()
velocity = engine.get_evolution_velocity()
chain = engine.get_evolution_chain()
summary = engine.get_evolution_summary()

# Forecasts
forecast = engine.get_forecast()
release_fc = engine.get_release_forecast("0.6.0")
remaining = engine.get_remaining_work()

# Reports
print(engine.generate_evolution_report())
print(engine.generate_evolution_summary_report())
```

---

## 7. Dependencies

- `shared.capabilities` — Capability registry, health scoring, platform state
- `shared.kernel` — Product identity, RFC records, releases, snapshots, history
- Python `dataclasses` — Immutable value objects (no external dependencies)

---

## 8. Extending

To add a new RFC:

1. Register it in `kernel_state.py:create_default_state()`
2. Add its capability mapping to `_get_rfc_capability_mapping()` in `timeline.py`
3. If it introduces new capabilities, register them in `capabilities/__init__.py`
4. If it targets a new version, add a milestone in `milestone_graph.py`

All other analysis flows automatically from these data structures.
