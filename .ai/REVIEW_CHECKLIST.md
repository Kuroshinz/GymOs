# NEXUS — Code Review Checklist

## Architecture (Must Pass)

- [ ] Clean Architecture layers respected? (Domain ← Application ← Infrastructure ← Presentation)
- [ ] No cross-module imports? (Communication via EventBus only)
- [ ] No UI → Database direct access?
- [ ] No business logic in core/ or infrastructure/?

## Code Quality

- [ ] Type hints on all public functions?
- [ ] No magic numbers? (All values named as constants)
- [ ] No duplicate code? (If similar logic exists, extract)
- [ ] No functions > 50 lines?
- [ ] No classes violating single responsibility?
- [ ] No global state or mutable module-level variables?
- [ ] Error handling: specific exceptions, not `except Exception`?

## Testing

- [ ] Business logic has tests?
- [ ] Repository layer has tests?
- [ ] Edge cases covered? (Empty state, invalid input, boundary values)
- [ ] No tests that depend on production database?

## Documentation

- [ ] Public functions have Google-style docstrings?
- [ ] Architecture change reflected in docs?
- [ ] New events documented in shared/constants/?
- [ ] New DB tables have Alembic migration?
- [ ] CHANGELOG.md updated?

## Performance

- [ ] No blocking calls on async path?
- [ ] Database queries use appropriate indexes?
- [ ] No N+1 queries?
- [ ] Lazy loading where appropriate?

## Security

- [ ] No credentials in code or config committed?
- [ ] Input validation on all user-facing APIs?
- [ ] SQL injection prevented? (Parameterised queries only)

## Domain Knowledge

- [ ] Exercise data matches knowledge/exercises/?
- [ ] Nutrition calculations accurate?
- [ ] Progression rules followed correctly?

## Dependency & Build

- [ ] No new dependencies without review?
- [ ] `pyproject.toml` consistent?
- [ ] CI pipeline passes? (ruff, mypy, pytest)
- [ ] Migration files reviewed?
