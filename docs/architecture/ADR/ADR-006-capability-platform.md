# ADR-006: Capability Platform

**Status:** Accepted

**Date:** 2026-07-03

---

## Context

GymOS has grown to 7+ subsystems (GymBrain, Nutrition, Event Platform, Knowledge Platform, Dashboard, etc.) but has no way to answer fundamental questions about itself:

- What capabilities exist?
- Which is the weakest?
- What blocks v1.0?
- What technical debt remains?
- What milestone comes next?

Without this introspection layer, the platform's evolution is managed manually through documents that drift from reality.

## Decision

### 1. Create `shared/capabilities/`

A new platform package that describes every subsystem as a **Capability** with typed metadata:

- Maturity level (CONCEPT → SELF_EVOLVING)
- Dependencies (which capabilities it needs)
- Health scores (architecture, test, documentation, platform)
- Technical debt items
- Roadmap with milestones

### 2. Static Registry Pattern

Capabilities are defined as constants at import time, not discovered at runtime. The `CapabilityRegistry` is populated when the module loads.

**Rationale:** Capabilities are a static description of the platform's current state. Dynamic discovery would add complexity without benefit — every capability is known at coding time.

### 3. Flat Package Structure

Following the convention of `shared/events/`:
- Domain types: `capability.py`, `enums.py`, `metrics.py`, `technical_debt.py`, `milestone.py`
- Application services: `registry.py`, `health.py`, `dependency_graph.py`, `roadmap.py`, `platform_state.py`, `report_generator.py`
- Infrastructure: `validators.py`, `serializers.py`

### 4. Read-Only

The Capability Platform is introspection-only. It does not:
- Emit events (capabilities don't change at runtime)
- Query databases
- Modify GymOS state
- Import from modules

### 5. Self-Describing

The Capability Platform registers itself as a capability ("Capability Platform") with a note about self-reference. This ensures the platform can answer "Does GymOS have a self-description system?"

## Consequences

- **Positive:** GymOS can now answer 10+ questions it couldn't before (weakest capability, blockers for v1.0, technical debt, etc.)
- **Positive:** Report generation provides actionable engineering intelligence
- **Positive:** Dependency graph reveals cross-capability coupling
- **Negative:** Capability definitions must be kept in sync with actual implementation (manual maintenance)

## Related

- RFC-018: Capability Platform
- ADR-001: Event Architecture (convention reference)
- Engineering Constitution Article II (Dependency Injection)
