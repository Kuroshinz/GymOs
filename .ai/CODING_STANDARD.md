# NEXUS — Coding Standards

## Language & Runtime

- Python 3.11+
- Type hints on every function signature
- Async for all I/O-bound code

## Style

| Rule | Standard |
|------|----------|
| Line length | 100 characters |
| Indentation | 4 spaces |
| Quotes | Double quotes (`"`) |
| Imports order | stdlib → third-party → core → sdk → local |
| Line ending | LF |

## Naming

| Element | Convention | Example |
|---------|-----------|---------|
| Modules/Packages | `snake_case` | `event_bus.py` |
| Classes | `PascalCase` | `WorkoutService` |
| Functions/Methods | `snake_case` | `create_workout()` |
| Variables | `snake_case` | `workout_id` |
| Constants | `UPPER_CASE` | `MAX_SETS_PER_EXERCISE` |
| Private members | Prefix `_` | `_validate_reps()` |
| Protocols | Suffix `Protocol` | `WorkoutRepositoryProtocol` |
| Type variables | `_T` | `_TWorkout` |

## Code Quality Rules

### Always
- Type hints on all public APIs
- Docstrings on public functions (Google style)
- Meaningful names (no `x`, `data`, `temp`)
- Small functions (max 30 lines, preferably <15)
- Small classes (single responsibility)
- Dependency Injection (no `import` of concrete implementations)
- Logging via Logger (no `print`)
- Error handling with specific exceptions from `shared.exceptions`

### Never
- Magic numbers (use named constants)
- Duplicate code (extract to shared utility)
- Global state
- Circular dependencies
- Functions longer than 50 lines
- `except Exception` (catch specific types)
- `from module import *`
- Mutable default arguments

## File Structure

```
module/
├── __init__.py       # Re-exports public API only
├── domain/
│   ├── __init__.py
│   ├── entities.py   # Domain entities
│   └── value_objects.py
├── application/
│   ├── __init__.py
│   ├── use_cases.py  # Orchestration logic
│   └── ports.py      # Repository interfaces
├── infrastructure/
│   ├── __init__.py
│   └── repositories.py  # SQLAlchemy implementations
└── presentation/
    ├── __init__.py
    └── views.py      # PySide6 widgets
```

## Testing

- Write tests for: repositories, services, utilities
- Don't test UI unless necessary
- Unit tests: no external dependencies
- Integration tests: use test fixtures, not production DB
- Async tests: `pytest-asyncio` with `asyncio_mode = "auto"`
- Coverage target: 80%+ on business logic

## Documentation

Every public function needs a docstring:
```python
def calculate_volume(sets: list[CompletedSet]) -> float:
    """Calculate total training volume.

    Args:
        sets: Completed sets with weight and reps.

    Returns:
        Total volume in kg (weight × reps summed).
    """
```

## Git

- Branch naming: `feat/description`, `fix/description`, `refactor/description`
- Commits: Conventional Commits
  - `feat(workout): add exercise reordering`
  - `fix(database): correct migration ordering`
  - `refactor(core): extract theme token resolver`
  - `docs: update architecture diagram`
  - `test: add repository unit tests`
  - `chore: bump pyproject.toml version`
- No direct commits to `main`
