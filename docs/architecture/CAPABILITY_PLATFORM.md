# Capability Platform

## Purpose

The Capability Platform provides **self-describing introspection** into GymOS — answering "where are we, what's weak, what's next for v1.0?" It is the nervous system for product intelligence.

## Design Principles

1. **Introspection-only** — reads capability registry, produces reports. No events, no database, no state mutation.
2. **Stateless engines** — HealthEngine, DependencyGraph, RoadmapEngine, PlatformState are pure functions. They take registry data, produce derived views.
3. **Static registry** — all 12 capabilities defined at coding time in `shared/capabilities/__init__.py`. No runtime discovery. Singleton is frozen after build.
4. **Self-describing** — Capability Platform registers itself as a capability. It eats its own dogfood.

## Architecture

```
Capability ───── CapabilityRegistry (singleton)
    │                    │
    ├── identity        HealthEngine ─── HealthScore per capability
    ├── maturity        DependencyGraph ── topological sort, cycles
    ├── health          RoadmapEngine ──── gap analysis, blockers
    ├── completion      PlatformState ──── aggregate view
    ├── technical_debt  ReportGenerator ── Markdown / JSON / terminal
    └── dependencies
```

### Layers

| Layer | Files | Responsibility |
|-------|-------|----------------|
| Domain | `capability.py`, `enums.py`, `metrics.py`, `technical_debt.py`, `milestone.py` | Pure data — dataclasses, enums, no logic |
| Application | `registry.py`, `health.py`, `dependency_graph.py`, `roadmap.py`, `platform_state.py`, `report_generator.py` | Business logic — compute health, sort deps, generate reports |
| Infrastructure | `validators.py`, `serializers.py` | Registry integrity, dict/JSON serialization |
| Composition | `__init__.py` | Build 12 capabilities, wire engines, freeze registry |

## The 12 Capabilities

| ID | Category | Maturity | Status | Health |
|----|----------|----------|--------|--------|
| training-intelligence | core | IMPLEMENTED | COMPLETE | 78 |
| nutrition-intelligence | core | IMPLEMENTED | COMPLETE | 74 |
| recovery-intelligence | core | DESIGN | IN_PROGRESS | 15 |
| decision-intelligence | intelligence | FOUNDATION | IN_PROGRESS | 40 |
| knowledge-platform | platform | IMPLEMENTED | COMPLETE | 65 |
| event-platform | platform | IMPLEMENTED | COMPLETE | 82 |
| experience-platform | platform | CONCEPT | NOT_STARTED | 2 |
| ai-coach | intelligence | CONCEPT | NOT_STARTED | 1 |
| prediction-engine | intelligence | CONCEPT | NOT_STARTED | 1 |
| digital-twin | future | CONCEPT | NOT_STARTED | 0 |
| product-intelligence | meta | IMPLEMENTED | COMPLETE | 82 |
| capability-platform | meta | IMPLEMENTED | COMPLETE | 85 |

## Health Scoring

Weighted formula: `Architecture * 0.30 + Test Coverage * 0.25 + Documentation * 0.20 + Platform Integration * 0.25`

Health rating thresholds:
- **Excellent**: >= 90
- **Good**: >= 75
- **Fair**: >= 50
- **Poor**: >= 25
- **Critical**: < 25

## Maturity Levels

```
CONCEPT (0) → DESIGN (1) → FOUNDATION (2) → IMPLEMENTED (3) → STABLE (4) → ADVANCED (5) → OPTIMIZED (6) → SELF_EVOLVING (7)
```

## Dependency Rules

- Capabilities may depend on any other capability (including those not yet built).
- `DependencyGraph.topological_sort()` raises `ValueError` on cycles.
- `DependencyGraph.find_orphans()` flags capabilities no other capability depends on.
- `blocked_by` is a separate set from `dependencies` — a capability can be built independently but blocked by missing infrastructure.

## Key Files

- `shared/capabilities/__init__.py` — Public API, 12 registered capabilities
- `shared/capabilities/capability.py` — Core `Capability` dataclass
- `shared/capabilities/enums.py` — Maturity, status, risk, priority enums
- `shared/capabilities/registry.py` — `CapabilityRegistry` singleton
- `shared/capabilities/health.py` — `HealthEngine`
- `shared/capabilities/dependency_graph.py` — `DependencyGraph` (Kahn's algorithm)
- `shared/capabilities/platform_state.py` — `PlatformState` aggregate
- `docs/architecture/ADR-006.md` — Decision record for this platform
