# Dependency Injection Standard

**Part of:** Sprint 3.2.5 Platform Standardization

---

## 1. Composition Root

All dependency wiring MUST occur in a single **composition root**. The production composition root is `main.py`.

### Current State

`main.py` performs manual wiring (no DI Container used):

```
main()
├── init_db(DB_PATH)
├── GymDatabase(DB_PATH)                                    # db
├── ProgramManager(DB_PATH)                                 # prog_mgr
├── NutritionRepository(DB_PATH)                            # nutrition_repo
├── get_event_bus()                                         # event_bus (singleton)
├── NutritionService(nutrition_repo, db, event_bus)         # nutrition_service
│   └── ProductionNutritionProvider (created internally)
├── DecisionEngine.from_production(db, nutrition_provider)  # engine
├── NutritionSubscriber(event_bus, engine)
├── MainWindow(db, prog_mgr, nutrition_service)
└── app.exec()
```

The DI Container (`core/di.py`) exists but is NOT used in production. All wiring is explicit constructor injection — this is correct but manual.

### Future State

The composition root MAY use `core.di.Container` for explicit registration, but the key principle is:

- **One place** where all production objects are created
- **No module** instantiates its own dependencies
- **Transitive dependencies** are wired at the composition root, not discovered by modules

---

## 2. Wiring Rules

### 2.1 Constructor Injection

Every service MUST receive dependencies through `__init__` parameters:

```python
# ✅ Correct
class NutritionService:
    def __init__(self, repository: NutritionRepository, db: Any, event_bus: EventBus) -> None: ...

# ❌ Wrong — service locator
class NutritionService:
    def __init__(self) -> None:
        self._repo = NutritionRepository()  # Hidden dependency

# ❌ Wrong — global singleton
class NutritionService:
    def __init__(self) -> None:
        self._bus = get_event_bus()  # Hidden dependency
```

### 2.2 No `getattr()` for Production Dependencies

Production dependencies MUST be resolved through typed properties or constructor parameters:

```python
# ✅ Correct
@property
def nutrition_provider(self) -> INutritionProvider | None:
    return self._nutrition_provider

# ❌ Wrong
provider = getattr(self, 'nutrition_provider', None)
```

### 2.3 No Circular Imports

The dependency graph MUST remain acyclic. Violations are detected by:
- ImportError at module load time
- Optional: automated import linter in CI

### 2.4 Interface Dependencies

Dependencies between modules SHOULD be on Protocol interfaces (`shared/interfaces/`), not concrete classes:

```python
# ✅ Correct — depends on interface
class NutritionRule(BaseRule):
    def evaluate(self, provider: IDataProvider, context: ...) -> RuleResult: ...

# ✅ Also correct — depends on concrete facade (DataProvider is the sole implementation)
class NutritionRule(BaseRule):
    def evaluate(self, provider: DataProvider, context: ...) -> RuleResult: ...
```

---

## 3. Dependency Graph

```
                        main.py (Composition Root)
                              │
            ┌─────────────────┼──────────────────┐
            │                 │                   │
       GymDatabase      ProgramManager      NutritionRepository
            │                 │                   │
            └────────┬────────┘                   │
                     │                            │
              DecisionEngine ◄──── NutritionService
                     │                            │
                     │                     EventBus (singleton)
                     │                            │
              NutritionSubscriber ─────────────────┘
                     │
                     ▼
              MainWindow
                     │
            ┌────────┴────────┐
            │                 │
      DashboardView      TrainingView
            │
    DashboardController
            │
    DashboardDataService
```

### Module Dependency Flow

```
workout/ ──► GymDatabase (shared repository)
     │
     ├──► workout_program/ ──► ProgramManager
     │
     ├──► nutrition/ ──► NutritionService ──► NutritionRepository
     │                        │
     │                        └──► EventBus (shared/events/)
     │
     └──► gymbrain/ ──► DecisionEngine ──► DataProvider
                              │
                              ├──► NutritionProvider (from nutrition/)
                              ├──► KnowledgeLoader (from shared/)
                              └──► GymDatabase (from workout/)
```

### Layer Dependency Rules

```
Presentation (ui/)  ──► Application (modules/*/application/)
                                  │
                                  ▼
Application         ──► Domain (modules/*/domain/)
                                  │
                                  ▼
Infrastructure      ──► Implements Application ports
                                  │
                                  ▼
Shared (shared/)    ──► Used by all layers (no reverse dependency)
```

---

## 4. Service Lifetime Rules

| Lifetime | When to Use | Examples |
|----------|-------------|---------|
| **Singleton** | Stateless services, configuration, event bus | EventBus, KnowledgeService, NutritionService |
| **Transient** | Stateful per-operation objects | Rule instances, Analysis requests |
| **Scoped** | Per-request/session state | (Reserved for future server mode) |

---

## 5. Disposal

Services that hold resources (DB connections, file handles, threads) MUST implement `Disposable` from `core/di.py`:

```python
from core.di import Disposable

class NutritionService(Disposable):
    async def dispose(self) -> None:
        await self._repo.close()
```

The composition root is responsible for calling `dispose()` on all registered disposable services during shutdown.

---

## 6. Testing

### Test Wiring

Test code MUST NOT use the production composition root. Each test constructs its own dependencies (typically using mocks):

```python
def test_nutrition_rule():
    mock_provider = MagicMock(spec=IDataProvider)
    mock_provider.nutrition_provider = MagicMock(spec=INutritionProvider)
    mock_provider.get_latest_body_weight.return_value = {"weight_kg": 80.0}

    rule = ProteinDeficitRule()
    result = rule.evaluate(mock_provider)
    assert result.triggered
```

### Test Fixtures

Shared test infrastructure (mock providers, builder patterns) MUST live in module test conftest files, not in production code.

---

## 7. Compliance Checklist

- [ ] All dependencies injected via `__init__`
- [ ] No `getattr()` for production dependency resolution
- [ ] No circular imports between modules
- [ ] Cross-module interfaces typed with Protocols from `shared/interfaces/`
- [ ] Composition root is the single place for production wiring
- [ ] All disposable services have `dispose()` called during shutdown
- [ ] Tests construct their own dependency graphs (don't use `main.py`)
