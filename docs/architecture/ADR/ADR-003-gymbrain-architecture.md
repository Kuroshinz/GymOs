# ADR-003: GymBrain Architecture

**Status:** Accepted

**Date:** 2026-07-03

---

## Context

GymBrain is the AI/decision-making subsystem of GymOS. It must:

- Consume data from multiple domains (workout, nutrition, recovery, goals)
- Produce actionable recommendations for the user
- Be deterministic (same data → same output)
- Support replaceable rules (new science, user preferences)
- Be testable without external dependencies

The initial prototype mixed rule logic with data access and used `getattr()` to lazily resolve providers.

## Decision

### 1. DecisionEngine as Central Orchestrator

`DecisionEngine` is the single entry point for GymBrain. It:
- Holds a `DataProvider` facade for all domain data access
- Maintains a registry of `BaseRule` instances
- Evaluates all rules against current data on `evaluate()`
- Returns a typed `EvaluationResult` with triggered rules and recommendations

### 2. DataProvider as Typed Facade

`DataProvider` is a facade that aggregates all domain providers and engines. It is NOT a rule itself. It provides typed accessors:
- `nutrition_provider: NutritionProvider`
- `recovery_engine: ...`
- `volume_engine: ...`
- `pr_engine: ...`
- Domain-specific getters (exercises, muscles, sessions, body weight, etc.)

All providers are injected via constructor. `getattr()` is forbidden in production code.

### 3. Rules as Isolated Units

Each rule:
- Extends `BaseRule` (or a future typed Protocol)
- Has a `condition()` and `action()` method
- Is stateless (all state comes from `DataProvider`)
- Returns a `RuleResult` with `triggered: bool`, `priority: int`, and `recommendations: list[str]`
- Is registered in `_register_default_rules()` or added externally

### 4. Deterministic Evaluation

For the same `DataProvider` state, `evaluate()` MUST return the same results. Rules do not modify data provider state. No randomness in rule evaluation.

### 5. Replaceable Rules

Rules can be added, removed, or reordered at composition time. The default set is registered in `DecisionEngine._register_default_rules()`, which lazy-imports rule classes to avoid circular imports.

**Rationale:** Users can disable rules they don't want. Future AI Coach can reorder rules based on user preferences.

## Consequences

- **Positive:** Testable — mock `DataProvider`, test rules in isolation
- **Positive:** Deterministic — reproducible evaluations
- **Positive:** Extensible — add rules without modifying DecisionEngine
- **Negative:** DataProvider tends to grow (needs periodic splitting)
- **Negative:** Rule ordering matters for priority but is hard to optimize

## Compliance

All GymBrain modules MUST:
- Access domain data only through `DataProvider`
- Define rules as stateless `BaseRule` subclasses
- Register rules in `DecisionEngine._register_default_rules()` or externally
- Never import other modules' data access layers directly

## Related

- ADR-004: Provider Interfaces
- Architecture Constitution Article I.1, I.4
- `docs/DECISION_ENGINE.md`
- `docs/GYMBRAIN.md`
