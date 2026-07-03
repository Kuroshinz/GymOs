# Code Quality Standard

*Effective: Sprint 3.2.5*

## 1. Python Standards

### 1.1 Version & Tooling
- Python 3.11+ with `from __future__ import annotations` in all files
- Ruff for linting (config: `ruff.toml`, all rules enabled)
- MyPy for type checking (strict mode)
- Pytest 9.x for testing

### 1.2 Formatting
- Line length: 100 characters
- Indentation: 4 spaces (no tabs)
- Quotes: Double quotes (`"`) for strings consistently
- Trailing newline at end of every file

### 1.3 Type Hints
- Every function signature MUST have full type hints
- Use `Optional[T]` (not `T | None`) for backward compatibility when needed, but prefer `T | None`
- `Any` is forbidden unless absolutely necessary AND documented with a comment
- Use `Protocol` for interface contracts, not ABCs (unless `isinstance()` is required)

### 1.4 Documentation
- Every module `__init__.py` MUST have a docstring describing module purpose
- Every public class MUST have a docstring
- Every public method/function SHOULD have a docstring
- Docstrings use triple double-quotes (`"""..."""`) with concise first line
- Comments explain WHY, not WHAT (the code is the WHAT)

### 1.5 Imports
Order (groups separated by blank line):
1. `from __future__ import annotations` (first, always)
2. Standard library
3. Third-party
4. Core (`core.*`)
5. Shared (`shared.*`)
6. Modules (`modules.*`)

### 1.6 Error Handling
- Use `shared.exceptions` hierarchy (`NexusError` base)
- Catch specific exceptions, never bare `except:`
- No `except: pass` — log the error at minimum
- Event handlers must never crash the bus (wrap in try/except)

## 2. Architecture Standards

### 2.1 Clean Architecture
- Domain: zero external dependencies (stdlib + shared types only)
- Application: depends on Domain only
- Presentation: depends on Application only
- Infrastructure: implements Application ports

### 2.2 Testing
- Unit tests: no external dependencies (DB, network)
- Integration tests: use test fixtures, not production services
- Async tests: use `pytest-asyncio` with `asyncio_mode = "auto"`
- Coverage targets: Domain 95%+, Application 90%+, Infrastructure 85%+, Presentation 80%+

### 2.3 Naming
| Element | Convention | Example |
|---------|-----------|---------|
| Modules | `snake_case` | `event_bus.py` |
| Classes | `PascalCase` | `EventBus` |
| Functions | `snake_case` | `register_handler` |
| Variables | `snake_case` | `workout_id` |
| Constants | `UPPER_CASE` | `MAX_RETRIES` |
| Private | Prefix `_` | `_internal_method` |
| Protocols | Prefix `I` | `INutritionProvider` |

## 3. Git Standards

- Branch naming: `feature/description`, `fix/description`, `chore/description`
- Commits: Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`)
- No direct commits to `main` (use pull requests)
- Commit messages: present tense, imperative mood ("Add feature" not "Added feature")

## 4. Review Checklist

Before merging any PR:
- [ ] All tests pass (`pytest`)
- [ ] Ruff passes (`ruff check .`)
- [ ] MyPy passes (`mypy .`)
- [ ] No dead code (unused imports, commented code)
- [ ] No `print()` statements (use Logger)
- [ ] No `getattr()` for production dependencies
- [ ] No cross-module imports (violation of Article I.1)
- [ ] Event classes registered in `DOMAIN_EVENT_REGISTRY`
- [ ] New Protocol interfaces added to `shared/interfaces/`
