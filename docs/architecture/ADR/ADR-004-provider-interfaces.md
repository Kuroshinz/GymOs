# ADR-004: Provider Interfaces

**Status:** Accepted

**Date:** 2026-07-03

---

## Context

GymOS modules need to access data from multiple sources: SQLite databases, third-party APIs (Cronometer, Hevy), knowledge files, and user input. Each data source has different access patterns and lifecycle requirements.

The initial prototype used:
- Concrete class injection (tight coupling)
- `getattr()`-based lazy resolution (no type safety, runtime errors)
- No explicit interface contracts between modules

## Decision

### 1. Protocol-Based Interfaces

All provider interfaces MUST use `typing.Protocol` for structural typing:

```python
class INutritionProvider(Protocol):
    def get_today(self) -> Optional[DailyNutrition]: ...
    def get_day(self, date: str) -> Optional[DailyNutrition]: ...
    def get_recent_days(self, days: int = 7) -> list[DailyNutrition]: ...
    def get_default_target(self) -> MacroTarget: ...
    def has_data(self) -> bool: ...
```

**Rationale:** Protocol allows duck typing (any object with the right methods is a valid provider) and avoids the inheritance coupling of ABCs. ABCs are reserved for cases requiring `isinstance()` checks.

### 2. Interface Naming Convention

All provider interfaces use the prefix `I`:

| Interface | Domain |
|-----------|--------|
| `IDataProvider` | GymBrain data aggregation facade |
| `ITrainingProvider` | Workout, session, exercise data |
| `INutritionProvider` | Nutrition data and targets |
| `IRecoveryProvider` | Recovery scores and metrics |
| `IGoalProvider` | User goals and preferences |
| `IKnowledgeRepository` | Knowledge file access |
| `IRecommendationEngine` | GymBrain recommendation output |

### 3. Constructor Injection

All providers MUST receive their dependencies through `__init__`:
- No `getattr()` for production dependencies
- No service locator pattern
- No global singletons

### 4. Replaceable Implementations

Each interface MUST have:
- A **production** implementation (SQLite, API client, etc.)
- A **mock/fake** implementation for testing

Mock implementations MUST be in the module's test package, not in production code.

### 5. Null Safety

Provider methods that may not have data MUST return `None` or an empty collection, never raise `KeyError` or `AttributeError`. All providers MUST handle missing data gracefully.

## Consequences

- **Positive:** Type safety — mypy catches provider mismatches at compile time
- **Positive:** Testability — mock implementations are trivial (just implement the Protocol)
- **Positive:** Replaceability — swap SQLite for PostgreSQL by writing a new Protocol implementor
- **Negative:** Protocol interface drift — must keep interface and implementations in sync
- **Negative:** More files per module (interface + production impl + test impl)

## Compliance

All provider interfaces MUST:
- Use `typing.Protocol` (not ABC) by default
- Be defined in the module's `application/` or `providers/` layer
- Return `Optional[T]` or empty collections for missing data
- Be injected via constructor (not `getattr()`)

## Related

- ADR-003: GymBrain Architecture
- Architecture Constitution Article I.4, Article VI.1
- `modules/gymbrain/providers/data_provider.py` (current implementation)
- `modules/nutrition/providers/__init__.py` (current ABC implementation)
