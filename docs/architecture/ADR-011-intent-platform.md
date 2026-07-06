# ADR-011: Intent Platform Architecture

**Date**: 2026-07-03
**Status**: Accepted
**RFC**: RFC-020.9

## Context

GymOS lacks a canonical representation of user intent. Currently, each module
(training, nutrition, recovery) independently infers what the user wants from
raw data, leading to inconsistent assumptions and conflicting recommendations.
A unified intent model is needed so that all downstream decisions derive from
a single source of truth.

## Decision

Build an Intent Platform as a cross-cutting platform capability in `shared/intent/`
with the following architecture:

### Clean Architecture Layers

1. **Domain Layer** (`domain.py`) — Frozen dataclasses and enums. Zero dependencies.
2. **Engine Layer** (`builder.py`, `merger.py`, `versioner.py`, `scorer.py`, `validator.py`) — Deterministic, stateless processors.
3. **Infrastructure Layer** (`repository.py`, `serializer.py`) — Persistence and serialization.
4. **Analysis Layer** (`metrics.py`, `report.py`, `state.py`) — Health scoring and reporting.

### Key Design Choices

- **Frozen dataclasses** for all entities — immutability by default.
- **Enumeration types** for all categorical fields — type safety.
- **Default factories** for every field — partial construction is safe.
- **Stateless engines** — no hidden state; all state in Repository/Versioner.
- **Rule-based conflict detection** — 6 deterministic conflict rules with NL resolution.
- **In-memory versioning** — ephemeral unless serialized via Repository.
- **Builder pattern** — single construction path from dict config.

### What We Rejected

- **Mutable entities**: Would allow inconsistent intermediate states.
- **Database-backed versioning**: Premature; in-memory suffices for current scale.
- **Plugin-based conflict rules**: Over-engineering for 6 rules; rules are hard-coded.
- **Event-based intent changes**: Adds complexity without clear benefit at this stage.

## Consequences

### Positive
- All downstream modules derive user intent from a single canonical model.
- Deterministic behavior enables reproducible test scenarios.
- Immutability prevents accidental mutation bugs.
- 183 tests provide high confidence in correctness.
- Clean separation of concerns simplifies maintenance.

### Negative
- Existing modules must be migrated to consume Intent (future work).
- In-memory versioning is not persisted across restarts.
- Frozen dataclasses require reconstruction for any change (accepted trade-off).

## Future Work

- RFC-021: Module integration — training, nutrition, recovery engines consume Intent
- Persistent intent storage (DB-backed repository)
- Intent-based goal tracking and progress projection
- Multi-intent orchestration (simultaneous goals)
