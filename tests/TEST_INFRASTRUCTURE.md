# Test Infrastructure Standard

**Part of:** Sprint 3.2.5 Platform Standardization

---

## 1. Test Directory Structure

```
tests/
├── unit/             # Pure unit tests (no external deps, no DB)
├── integration/      # Tests with DB, file I/O, or network
├── ui/               # Qt/PySide6 widget tests
├── performance/      # Benchmark and load tests
└── conftest.py       # Project-wide fixtures

modules/*/tests/
├── conftest.py       # Module-specific fixtures
├── test_domain.py    # Domain entity/value object tests
├── test_services.py  # Application service tests
├── test_*            # Other test modules
└── __init__.py       # Package marker
```

## 2. Test Types & Patterns

### 2.1 Unit Tests (Domain Layer)

Test domain entities, value objects, and invariants in isolation.

```python
def test_empty_meal_totals():
    meal = Meal()
    assert meal.total_calories == 0.0
    assert meal.total_protein == 0.0

def test_meal_totals_multiple_items():
    meal = Meal(items=[
        MealItem(calories=500, protein_g=40, carbs_g=60, fat_g=10),
        MealItem(calories=300, protein_g=20, carbs_g=40, fat_g=5),
    ])
    assert meal.total_calories == 800.0
    assert meal.total_protein == 60.0
```

**Pattern:** Arrange → Act → Assert. No mocks. Pure data transformations.

### 2.2 Service Tests (Application Layer)

Test application services with mocked repositories/providers.

```python
def test_log_meal_increases_meal_count():
    repo = MagicMock()
    day = DailyNutrition(date="2026-07-03")
    repo.get_day.return_value = day
    repo.save_day.return_value = day

    service = NutritionService(repo=repo, event_bus=MagicMock())
    meal = Meal(name="Lunch", items=[MealItem(calories=500, protein_g=40)])
    result = service.log_meal("2026-07-03", meal)

    assert len(result.meals) == 1
    repo.save_day.assert_called_once()
```

**Pattern:** Mock interface boundaries (repositories, providers, event bus). Verify interactions and state changes.

### 2.3 Provider Contract Tests

Verify that a provider implementation conforms to its Protocol/interface contract.

```python
class INutritionProviderContract:
    """Abstract test class — subclass for each implementation."""

    @pytest.fixture
    def provider(self) -> INutritionProvider: ...

    def test_get_today_returns_none_when_no_data(self, provider):
        result = provider.get_today()
        assert result is None or not result.has_data

    def test_get_day_returns_none_for_missing_date(self, provider):
        result = provider.get_day("2099-01-01")
        assert result is None

    def test_get_default_target_returns_valid_target(self, provider):
        target = provider.get_default_target()
        assert target.calories > 0
        assert target.protein_g > 0
```

### 2.4 Event Replay Tests

Verify that events survive serialization round-trips.

```python
def test_meal_logged_round_trip():
    event = MealLogged(
        meal_name="Lunch", calories=800, protein_g=50,
        carbs_g=90, fat_g=20, date="2026-07-03",
    )
    data = event.to_dict()
    restored = event_from_dict(data)
    assert restored == event
    assert restored.meal_name == "Lunch"
```

### 2.5 Repository Contract Tests

Verify repository behavior against a shared contract.

```python
class NutritionRepositoryContract:
    @pytest.fixture
    def repo(self) -> NutritionRepository: ...

    def test_get_day_returns_none_for_no_data(self, repo):
        assert repo.get_day("2099-01-01") is None

    def test_save_and_retrieve_day(self, repo):
        day = DailyNutrition(date="2026-07-03")
        day.log_meal(Meal(name="Breakfast"))
        repo.save_day(day)
        loaded = repo.get_day("2026-07-03")
        assert loaded is not None
        assert len(loaded.meals) == 1
```

### 2.6 Knowledge Validation Tests

Verify knowledge data integrity.

```python
def test_knowledge_validation_passes():
    validator = KnowledgeValidator()
    errors = validator.validate_all()
    assert len(errors) == 0, f"Knowledge validation failed: {errors}"
```

### 2.7 Rule Engine Tests (GymBrain)

Verify rules against a mock DataProvider.

```python
def test_protein_deficit_rule_triggers_when_below_target():
    provider = (
        MockDataBuilder()
        .with_nutrition_provider(target_protein=160.0, avg_protein=100.0)
        .build()
    )
    rule = ProteinDeficitRule()
    result = rule.evaluate(provider)
    assert result.triggered
    assert "protein" in result.reason.lower()
```

## 3. Mocking Guidelines

### 3.1 Mock Boundaries
Only mock at interface boundaries (Protocols, ABCs, or repository classes). Never mock domain entities or value objects.

```python
# ✅ Correct — mock at repository boundary
repo = MagicMock(spec=NutritionRepository)

# ❌ Wrong — mocking a domain entity
meal = MagicMock(spec=Meal)
```

### 3.2 Use `spec` Parameter
Always use `spec=` or `spec_set=` when creating mocks to catch interface mismatches:

```python
mock_provider = MagicMock(spec=INutritionProvider)
repo = MagicMock(spec=NutritionRepository)
```

### 3.3 MockDataBuilder Pattern
Use the builder pattern (from `modules/gymbrain/tests/conftest.py`) for complex mock setups:

```python
provider = (
    MockDataBuilder()
    .with_exercise("bench_press", "Bench Press", category="compound")
    .with_session(session_id=1, days_ago=1)
    .with_body_weight(75.0)
    .with_program()
    .build()
)
```

## 4. Running Tests

```bash
# All tests
pytest

# Specific module
pytest modules/nutrition/tests/

# Specific test
pytest modules/nutrition/tests/test_domain.py::TestMeal::test_empty_meal -v

# With coverage
pytest --cov=modules/nutrition --cov-report=term-missing

# Parallel
pytest -n auto
```

## 5. Assertion Best Practices

1. Use `assert` with descriptive messages for complex checks:
   ```python
   assert result.triggered, f"Expected rule to trigger but it didn't. Evidence: {result.evidence}"
   ```

2. Use `pytest.approx` for float comparisons:
   ```python
   assert meal.total_calories == pytest.approx(800.0, abs=0.01)
   ```

3. Use context managers for exception testing:
   ```python
   with pytest.raises(ValueError, match="Invalid macro target"):
       MacroTarget(calories=-100, ...)
   ```

4. Use `in` for string containment in evidence/reason checks:
   ```python
   assert "protein" in result.reason.lower()
   ```

## 6. Coverage Targets

| Layer | Target | Exclusions |
|-------|--------|-----------|
| Domain | 95%+ | `__init__.py`, dataclass boilerplate |
| Application | 90%+ | Error handlers, logging |
| Infrastructure | 85%+ | SQLAlchemy model definitions |
| Presentation | 80%+ | Qt widget boilerplate |
| Rules | 95%+ | Dead code paths |
| Events | 100% | Serialization round-trips |

## 7. CI Integration

All tests MUST pass before merging:
- `pytest` (all tests, any platform)
- Ruff checks pass
- MyPy strict mode passes (config: `pyproject.toml`)
