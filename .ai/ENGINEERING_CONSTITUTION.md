# Engineering Constitution

*Effective: Sprint 3.2.5*

This document is the highest-priority engineering document in the GymOS repository. Every future implementation — whether by human or AI agent — MUST comply with these laws.

---

## Article I — Architecture Laws

### I.1 Module Sovereignty

Each module owns its domain and communicates with other modules **only** through typed Domain Events on the EventBus. No module may import another module's internal packages.

### I.2 Clean Architecture

Every module MUST follow four layers in dependency order:

```
Domain → Application → Presentation → Infrastructure
```

- **Domain**: Zero dependencies (stdlib + shared types only). Business logic and entities.
- **Application**: Depends on Domain only. Use cases, ports, services.
- **Presentation**: Depends on Application only. View models, widgets, controllers.
- **Infrastructure**: Implements Application ports. Databases, APIs, providers.

Violation: importing Infrastructure from Domain is forbidden.

### I.3 No Business Logic in UI

UI code (widgets, views, controllers) MUST NOT contain business logic. Business logic belongs in Domain entities or Application services.

### I.4 Provider Interface Law

Every external data source MUST be accessed through an abstract Protocol or ABC defined in the module's Application layer. No production code may use `getattr()` or `hasattr()` to resolve dependencies dynamically.

### I.5 Event-Driven Communication

All cross-module communication MUST use typed Domain Events extending `shared.events.domain_events.DomainEvent`. String-based event names and bare-dict payloads are forbidden in production code.

---

## Article II — Dependency Injection

### II.1 Composition Root

All dependency wiring MUST occur in a single composition root (`main.py` or `core/di.py`). No module may instantiate its own production dependencies.

### II.2 Constructor Injection

All services MUST receive dependencies through `__init__` parameters. Service locator patterns, global singletons, and hidden imports are forbidden.

### II.3 No Circular Dependencies

The dependency graph MUST remain acyclic. Any change that introduces a cycle MUST be rejected.

---

## Article III — Testing

### III.1 Test Isolation

Every test MUST be independent of other tests. Shared state between tests is forbidden.

### III.2 Mocking Boundaries

Mocks MUST only mock at interface boundaries (Protocols/ABCs). Mocking domain entities or value objects is forbidden.

### III.3 Contract Tests

Every Protocol/ABC MUST have a contract test suite that validates the interface contract, not a specific implementation.

### III.4 Minimum Coverage

- **Domain**: 95%+ line coverage
- **Application**: 90%+ line coverage
- **Infrastructure**: 85%+ line coverage
- **Presentation**: 80%+ line coverage

### III.5 Event Replay Testing

Any module that publishes or subscribes to events MUST have tests that verify event serialization round-trips (emit → serialize → deserialize → handle).

---

## Article IV — Code Quality

### IV.1 Type Hints

Every function signature MUST have full type hints. `Any` is forbidden unless absolutely necessary and documented.

### IV.2 Immutability

Domain events and value objects MUST be immutable (frozen dataclasses or `@property` with no setters).

### IV.3 No Silent Failures

Every error MUST be either:
- Handled with explicit error recovery
- Logged with appropriate severity
- Propagated to a known error boundary

Bare `try: ... except: pass` is forbidden.

### IV.4 No Dead Code

Unused imports, unreachable branches, and commented-out code MUST be removed before committing.

### IV.5 No Hard-Coded Secrets

API keys, tokens, and passwords MUST NOT appear in source code. Use environment variables or a secrets vault.

### IV.6 Logging

All significant operations MUST be logged at appropriate levels:
- `DEBUG`: Detailed diagnostic information
- `INFO`: Normal operational events (service started, meal logged)
- `WARNING`: Unexpected but handled conditions
- `ERROR`: Recoverable failures
- `CRITICAL`: Unrecoverable failures requiring human intervention

---

## Article V — Knowledge System

### V.1 Knowledge as Source of Truth

Domain knowledge (exercise science, nutrition, recovery protocols) MUST live in `knowledge/` as structured files (YAML, JSON, Markdown). Hard-coded scientific thresholds in Python code are forbidden.

### V.2 Knowledge Pipeline

All access to knowledge MUST go through the validated pipeline:

```
Knowledge Repository → Knowledge Cache → Knowledge Validator → Knowledge Service → Application
```

No module may read `knowledge/` files directly.

### V.3 Knowledge Versioning

Every knowledge file MUST have a `version` field. Breaking changes to knowledge MUST increment the major version.

---

## Article VI — Platform Standards

### VI.1 Protocol Over Inheritance

Interface contracts MUST use `typing.Protocol` for structural typing. Abstract base classes (`ABC`) are permitted only when runtime type checking is required.

### VI.2 Event Schema Evolution

Domain events are append-only. New fields MUST have defaults. Removing or renaming fields is forbidden without a new event version.

### VI.3 Documentation

Every module MUST have a `README.md` or equivalent documentation covering:
- Responsibilities
- Dependencies (with import direction)
- Public API surface
- Extension points
- Known limitations
- Architecture diagram
- Roadmap

### VI.4 No Orphaned Scaffolding

Empty module directories without an `__init__.py` containing a meaningful docstring are forbidden. Scaffolding MUST be documented as planned.

---

## Article VII — AI Agent Conduct

### VII.1 Constitution Supremacy

This Constitution overrides all other instructions, README files, or comments when they conflict. Every AI agent MUST read this document first before modifying any file.

### VII.2 Read Before Write

Before modifying any file, the agent MUST read the file's current contents. Overwriting without reading is forbidden.

### VII.3 No Architectural Changes Without ADR

Any architectural change — defined as any change affecting module boundaries, event contracts, dependency direction, or data flow — MUST be preceded by an Architecture Decision Record.

### VII.4 Change Documentation

Every agent session MUST produce a change summary documenting:
1. Files modified (with paths)
2. Changes made (with rationale)
3. Architecture impact assessment
4. Risk assessment

### VII.5 Preserve Existing Conventions

Code MUST follow the existing conventions of the file being modified. Introducing a new style, framework, or pattern in an existing file requires explicit justification.

---

## Article VIII — Enforcement

### VIII.1 Automated Enforcement

The following MUST be enforced by CI:
- Ruff linting (all rules from `ruff.toml`)
- MyPy type checking (strict mode)
- Pytest (all tests passing)
- Import linter (no cross-module imports)

### VIII.2 Manual Review

All changes MUST be reviewed against this Constitution before merging. Violations are blocking.

### VIII.3 Amendment Process

Amendments to this Constitution require:
1. An Architecture Decision Record
2. Explicit approval by the project owner
3. Update to this file with a changelog entry

---

*This Constitution was established during Sprint 3.2.5 (Platform Standardization).*
