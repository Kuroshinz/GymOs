# GymOS Implementation Rules

These are concrete, enforceable rules that every AI agent must follow when writing code.

---

## 1. SEARCH BEFORE YOU BUILD

Before writing **any** new code:

- Search the repository for existing implementations using `code_searcher`
- Check for existing components, services, models, and utilities
- If a similar implementation exists, **reuse or extend it** — do not create from scratch

**Violation:** Creating a second `WorkoutRepository` when one already exists.

---

## 2. REUSE COMPONENTS

- Reuse UI components, helpers, constants, and patterns
- If a helper function exists in `shared/helpers/`, use it
- If a constant exists in `shared/constants/`, reference it
- If a type exists in `shared/types/`, import it

**Violation:** Reimplementing `calculate_volume()` in a new module when it already exists.

---

## 3. NO DUPLICATE SERVICES

- Each service should exist once
- If two modules need similar logic, extract to `shared/` or a common parent
- Never have `WorkoutService` in two places

**Violation:** Creating `workout/application/services/workout_service.py` when `workout/application/workout_service.py` already exists.

---

## 4. PRESERVE NAMING CONSISTENCY

Follow the conventions in `.ai/CODING_STANDARD.md`:

| Element | Convention | Example |
|---------|-----------|---------|
| Modules | `snake_case` | `event_bus.py` |
| Classes | `PascalCase` | `WorkoutService` |
| Functions | `snake_case` | `create_workout()` |
| Variables | `snake_case` | `workout_id` |
| Constants | `UPPER_CASE` | `MAX_SETS` |
| Private | Prefix `_` | `_validate()` |

**Violation:** Naming a function `CreateWorkout` instead of `create_workout`.

---

## 5. PREFER COMPOSITION OVER INHERITANCE

- Use dependency injection and composition
- Avoid deep inheritance hierarchies (max 2 levels)
- Favour protocols/interfaces over abstract base classes
- Use `Protocol` for repository interfaces

**Violation:** Creating `BaseWorkoutView → WorkoutDetailView → PushWorkoutView` inheritance chain.

---

## 6. WRITE TESTS FOR BUSINESS LOGIC

Every significant business logic change must include tests:

- Use `pytest` with `pytest-asyncio` for async tests
- Test the public API, not implementation details
- Test edge cases: empty data, invalid input, boundary values
- Repository tests use in-memory or test fixtures

**Violation:** Adding a new `calculate_progressive_overload()` function without tests.

---

## 7. KEEP COMMITS FOCUSED

- One feature = one set of changes
- Do not mix refactoring with feature work
- Do not change unrelated files in the same implementation

**Violation:** Renaming `WorkoutService` methods while adding a Nutrition CSV parser.

---

## 8. NEVER CHANGE UNRELATED FILES

- If the task is about the **Workout** module, do not touch **Nutrition** files
- If the task is about **UI**, do not modify **Infrastructure** code
- Exceptions: global refactoring, dependency updates, shared utilities

**Violation:** Editing `modules/nutrition/domain/entities.py` while implementing a workout feature.

---

## 9. NO HARDCODED VALUES

- No magic numbers — use named constants
- No inline strings that may change — use constants or config
- No hardcoded paths — use `shared/constants/` or environment config
- Design tokens for all UI values

**Violation:** `if reps > 12:` instead of `if reps > MAX_HYPERTROPHY_REPS:`.

---

## 10. NO LAYER VIOLATIONS

- UI never accesses database directly
- UI never contains business logic
- Domain never imports from Infrastructure
- Application never imports from Presentation

**Violation:** Importing `SQLAlchemy` in a UI view file.

---

## 11. FUNCTIONS MUST BE SMALL

- Maximum 30 lines per function
- Preferably under 15 lines
- If a function does more than one thing, split it
- If a function has more than 3 parameters, use a dataclass or config object

**Violation:** A 80-line `save_workout()` function that validates, persists, updates stats, sends events, and refreshes UI.

---

## 12. TYPE HINTS ON EVERYTHING

- Every function signature must have type hints
- Every class attribute must be typed
- Use `| None` instead of `Optional[]` (Python 3.10+)
- Use `Self` return type for fluent interfaces
- Avoid `Any` unless truly necessary

**Violation:** `def process(data):` instead of `def process(data: WorkoutData) -> WorkoutResult:`.

---

## 13. ERROR HANDLING

- Use specific exception types from `shared/exceptions/`
- Catch specific exceptions, never `except Exception`
- Log errors with context, not just the message
- Present user-friendly error messages in the UI
- Fail fast for programming errors, handle gracefully for runtime errors

**Violation:** `except: pass` or `except Exception as e: print(e)`.

---

## 14. IMPORTS ORDER

```python
# 1. Standard library
import os
from datetime import datetime

# 2. Third-party
from PySide6.QtWidgets import QWidget
from sqlalchemy import select

# 3. Core / shared
from core.di import inject
from shared.constants import APP_NAME

# 4. Local module
from .domain.entities import Workout
```

**Violation:** Mixing stdlib and third-party imports.

---

## 15. DOCSTRINGS ON PUBLIC APIS

Every public function, class, and method needs a Google-style docstring:

```python
def calculate_volume(sets: list[CompletedSet]) -> float:
    """Calculate total training volume.

    Args:
        sets: Completed sets with weight and reps.

    Returns:
        Total volume in kg (weight × reps summed).
    """
```

**Violation:** A public function with no docstring.
