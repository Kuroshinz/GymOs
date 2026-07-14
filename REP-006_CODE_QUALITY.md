# REP-006 — Code Quality Hardening

## Before / After Statistics

| Tool      | Before | After  | Δ     | Target |
|-----------|--------|--------|-------|--------|
| Ruff      | 356    | 0      | -356  | 0 ✅   |
| mypy      | 965    | 870    | -95   | ↓      |
| pytest    | 3371p / 2f | 3371p / 2f | 0 | —  |
| main.py   | ✅     | ✅     | —     | ✅     |

- **193 files modified**
- **501 insertions, 658 deletions**

## Violations Eliminated (Ruff)

| Code | Rule                          | Fixed |
|------|-------------------------------|-------|
| N802 | Function name casing (Qt overrides) | 71 (noqa) |
| F841 | Unused variable               | ~50   |
| F401 | Unused import                 | ~60   |
| B007 | Unused loop control variable  | ~25   |
| F821 | Undefined name                | 5     |
| B905 | zip() without strict=         | 7     |
| SIM108 | If-else → ternary           | 7     |
| SIM105 | Try-except-pass → suppress  | 10    |
| SIM102 | Collapsible if              | 10    |
| E741 | Ambiguous variable name (`l`) | 4     |
| B904 | raise without from           | 3     |
| B008 | Function call in arg default | 15    |
| N801 | Class name casing            | 1     |
| N817 | CamelCase import acronym     | 2     |
| E712 | == True/False comparison     | 3     |
| E731 | Lambda assignment            | 2     |
| E402 | Module-level import          | 1     |
| UP042 | str+Enum → StrEnum          | 2     |
| SIM103 | Needless bool return        | 1     |
| SIM110 | Reimplemented builtin       | 1     |

## mypy Reductions (95 fewer errors)

Key fixes in:
- **shared/capabilities/__init__.py** — `frozenset` → `tuple` for Capability constructor args
- **shared/events/publisher.py** — Added `TypeVar` so publish() returns correct subtype
- **shared/events/event_bus.py** — Handler type accepts `Awaitable[None] | None`
- **shared/graph/builder.py** — Fixed tuple element counts
- **shared/crash/handler.py** — Proper traceback types, BaseException type
- **shared/crash/recovery.py** — Named function instead of lambda returning tuple

## Design Improvements

- **Crash recovery metadata**: `.recovered` marker → JSON `.meta` with `schema`, `handled`, `timestamp`, `version`
- **Atomic write**: `.meta.tmp` + `os.replace()` to prevent partial writes
- **Orphaned metadata cleanup**: Auto-remove `.meta` / `.recovered` without matching `.log`
- **Old report lifecycle**: Archive at 30 days, delete at 90 days
- **Backward compat**: Legacy `.recovered` files still recognized

## Files Modified

193 files across:
- `core/` (11) — Cleaned unused imports
- `modules/` (25) — Removed unused imports/vars, fixed B008
- `shared/` (35) — F401/F841/B007/F821, fixed frozenset→tuple, type annotations
- `ui/` (110) — Qt override noqa, unused vars/imports, loop vars, SIM fixes
- `tests/` (3) — Updated `type_scale` → `TypeScale`
- Other (9) — Scripts, config

## Remaining Technical Debt

| Item | Count | Notes |
|------|-------|-------|
| mypy errors | 870 | Mostly PySide6 Qt namespace (`Qt.PointingHandCursor`, `QFrame`, etc.) and `None` checks on `QLayout \| None` — hard to fix without runtime guarantees |
| `type: ignore` | 0 | Never used |
| `# noqa` | ~71 | All N802 (legitimate Qt override naming) |
| Pre-existing test failures | 2 | `test_get_latest_sleep` / `test_get_latest_stress` — unrelated to this REP |
