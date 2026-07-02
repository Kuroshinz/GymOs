# Coding Standards

## Python Style

- **Python 3.11+** with type hints everywhere
- **Line length**: 100 characters
- **Indentation**: 4 spaces
- **Quotes**: Double quotes (`"`) for strings
- Linting via **ruff** (config: `ruff.toml`)
- Type checking via **mypy**

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Modules | `snake_case` | `event_bus.py` |
| Classes | `PascalCase` | `EventBus` |
| Functions | `snake_case` | `register_handler` |
| Variables | `snake_case` | `workout_id` |
| Constants | `UPPER_CASE` | `MAX_RETRIES` |
| Private | Prefix `_` | `_internal_method` |
| Protocols | Suffix `Protocol` | `RepositoryProtocol` |

## File Structure (per module)

```
module/
├── __init__.py        # Public exports
├── domain/
│   ├── __init__.py
│   ├── entities.py
│   └── value_objects.py
├── application/
│   ├── __init__.py
│   ├── use_cases.py
│   └── ports.py
├── infrastructure/
│   ├── __init__.py
│   └── adapters.py
└── presentation/
    ├── __init__.py
    └── view_models.py
```

## Imports Order

1. Standard library
2. Third-party
3. Core (`core.*`)
4. SDK (`sdk.*`)
5. Local (`nexus.*`, `src.*`)

## Async

- All I/O-bound functions must be `async def`
- Use `asyncio` primitives, not `threading`
- Event handlers are `async def handler(event: Event) -> None`

## Testing

- Tests in `tests/unit/`, `tests/integration/`, `tests/ui/`, `tests/performance/`
- Unit tests: no external dependencies (DB, network)
- Integration tests: use test fixtures, not production services
- Async tests: use `pytest-asyncio` with `asyncio_mode = "auto"`
- Coverage target: 80%+

## Error Handling

- Use `shared.exceptions` hierarchy (`NexusError` base)
- Catch specific exceptions, not `Exception`
- Log errors via `Logger`, not `print`
- Event handlers must never crash the bus

## Git

- Branch: `feature/description`, `fix/description`, `chore/description`
- Commits: conventional commits (`feat:`, `fix:`, `docs:`, `refactor:`)
- No commits to `main` directly (use PRs)
