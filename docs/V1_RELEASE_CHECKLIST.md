# GymOS v1.0 Release Checklist

> Required items before GymOS can be tagged as `v1.0.0 Release Candidate`.
> Based on REP-001C audit findings.

---

## Product

- [ ] **Fix dashboard_data_service.py empty stubs** — 21 `except Exception: pass` handlers replaced with proper error propagation/logging
- [ ] **Fix command_center/services/__init__.py stubs** — 22 empty pass registrations for workspace services wired or removed
- [ ] **Remove dead file** `shared/events/prediction_events.py` — duplicate of `domain_events.py`
- [ ] **Resolve 5 empty stub dirs** in `shared/`: `exceptions/`, `constants/`, `validators/`, `helpers/`, `types/` — implement or remove
- [ ] **Fix prediction module bugs**:
  - [ ] `MockEventBus.__init__` typo in `modules/prediction/tests/test_prediction_service.py:52`
  - [ ] Duplicate import in `modules/prediction/infrastructure/repository.py:19-21`
- [ ] **Fix migration 002** — `002_add_is_active.py` references `workout_programs` table that version 001 never creates
- [ ] **Add recovery module tests** — zero coverage currently
- [ ] **Audit unused infrastructure** for intentional exclusion or removal:
  - `shared/runtime/`, `shared/cognitive/`, `shared/evolution/`, `shared/intent/`,
  - `shared/planning/`, `shared/planning_optimizer/`, `shared/adaptive_programming/`,
  - `shared/knowledge_evolution/`, `shared/optimization_knowledge/`, `shared/kernel/`,
  - `shared/explainability/`, `shared/state/`, `shared/graph/`
- [ ] **Remove `print()` debug statements** from `shared/runtime/runtime.py` — replace with proper logging
- [ ] **Remove all other `print()` statements** from non-script production files
- [ ] **Clean up monoliths** — split files >500 lines: `prediction/engines/__init__.py` (751), `planning/engine.py` (597), `recovery/infrastructure/repository.py` (594), `capabilities/__init__.py` (559), `recovery/engines/__init__.py` (547), `planning/domain.py` (537)
- [ ] **Update `shared/observability/logger/__init__.py:48`** — resolve `# type: ignore` properly
- [ ] **`ui/experience/` audit** — verify `focus_mode.py`, `integration.py`, `layout_engine.py`, `search_provider.py`, `workflow_engine.py`, `theme_transition_manager.py` are fully wired or intentionally gated

---

## UX

- [ ] **About dialog** — show app name, version, credits, Python/Qt versions
- [ ] **Application icon** — set window icon via `app.setWindowIcon()`; provide `.ico`/`.png` in `resources/`
- [ ] **Crash handler** — override `sys.excepthook` to show user-friendly error dialog before exit
- [ ] **Settings persistence** — wire `QSettings` for theme, unit system, and window geometry
- [ ] **First-run experience** — welcome dialog or quick-start guide on initial launch
- [ ] **Empty states** — replace static "No X available" labels with meaningful empty states across all 10 workspace pages
- [ ] **Loading states** — add skeleton loaders or progress indicators for data-fetching workspaces
- [ ] **Error states** — add retry-capable error UI for service failures in workspace pages
- [ ] **Notifications** — wire `NotificationCenter` into main event loop; verify toast rendering
- [ ] **Undo support** — document as known gap or implement for key destructive actions
- [ ] **Confirmation dialogs** — add for data-destructive actions
- [ ] **Keyboard shortcuts** — wire `ShortcutManager` globally; add discoverable shortcut help screen
- [ ] **Command palette** — verify all workspaces accessible via command palette
- [ ] **Search** — extend `QuickSearch` beyond page navigation to workspace content search
- [ ] **Navigation consistency** — single authority for nav; unify `main_window.py` sidebar and `command_center.py` nav rail
- [ ] **Window resizing** — test minimum sizes, content reflow, no overlapping widgets
- [ ] **HiDPI support** — set `Qt.AA_EnableHighDpiScaling`; test on high-DPI displays

---

## Engineering

- [ ] **Resolve 48 failing tests** — fix or add `@pytest.mark.xfail` with documented reason:
  - [ ] 18 capability registry count failures (hardcoded `== 13`)
  - [ ] 11 Command Center layout failures (`MagicMock` vs `QWidget`)
  - [ ] 5 Command Center sidebar failures (`_sidebar` → `_nav_rail`)
  - [ ] 4 page labels/index failures
  - [ ] 4 dashboard widget failures (removed fields, wrong signatures)
  - [ ] 3 `AdaptiveTimelineWidget` failures (missing `update_data`)
  - [ ] 1 performance timing failure (224ms vs 100ms)
  - [ ] 2 theme color failures (`#FACC15` vs `#FBBF24`)
- [ ] **Remove all 26 placeholder tests** (bare `pass` bodies) — implement or remove
- [ ] **Add class docstrings** to ~45+ undocumented public classes
- [ ] **Replace `Any` type annotations** (~224 instances) with concrete types:
  - Priority: `data_provider.py`, `production_provider.py`, `decision_engine.py`, `controller.py`
  - Secondary: `command_center_service.py`, `integration.py`, `dashboard_controller.py`
- [ ] **Fix silent error swallowing** (~25 `except Exception: pass` blocks) — at minimum log every exception
- [ ] **Update pytest config** — add `shared/` and `modules/` to `testpaths` for full auto-discovery
- [ ] **Add coverage threshold** — enforce minimum coverage (e.g., `--cov-fail-under=70`)
- [ ] **Remove `# type: ignore`** escapes without proper typing fix
- [ ] **Add module-level docstrings** to all `__init__.py` files
- [ ] **Add `__main__` guards** to test files that are accidentally importable

---

## Performance

- [ ] **Profile startup time** — identify bottlenecks in `main.py` initialization
- [ ] **Profile widget creation cost** — measure rendering time for all workspace pages
- [ ] **Fix performance test** — `test_fetch_all_under_100ms` currently averages 224ms
- [ ] **Lazy-load unused infrastructure** — avoid importing `shared/` subsystems until needed
- [ ] **Audit `__init__.py` imports** — ensure top-level module imports are lazy or scoped
- [ ] **Memory profile** — detect widget leaks, unclosed database connections, unbounded event stores
- [ ] **Optimize `dashboard_data_service.py`** — magic-number formulas, redundant queries, synchronous event handling

---

## Accessibility

- [ ] **Add `QAccessible` interfaces** to interactive widgets
- [ ] **Audit tab order** — `setTabOrder()` across all workspace pages
- [ ] **Keyboard navigation** — verify all interactive elements reachable via keyboard
- [ ] **Color contrast** — verify text meets WCAG AA minimum contrast ratios in both themes
- [ ] **Screen reader labels** — add `setAccessibleName()` and `setAccessibleDescription()` to all controls

---

## Packaging

- [ ] **Generate lockfile** — run `pip freeze > requirements.txt` or adopt Poetry/Pipenv
- [ ] **Audit dependencies** — remove 50+ undeclared packages from environment (torch, transformers, celery, flask, opencv, etc.)
- [ ] **Update outdated packages** — 41 packages behind latest; at minimum update security-sensitive deps
- [ ] **Version consistency** — unify version string across `main.py`, `pyproject.toml`, kernel, and PRD
- [ ] **Set license field** in `pyproject.toml`
- [ ] **Add installer** — PyInstaller spec or NSIS/InnoSetup script in `scripts/installer/`
- [ ] **Application icon** — `.ico` for Windows, `.icns` for macOS, `.png` for Linux
- [ ] **Splash screen** — brief loading dialog for slow initialization
- [ ] **Build automation** — script that produces distributable artifact (single binary or installer)
- [ ] **Portable mode** — flag to use local data directory instead of user home
- [ ] **QRC compilation** — move inline stylesheets to `.qrc`/`.qss` resource files
- [ ] **Verify no .gitignore'd files** are required at runtime

---

## Documentation

- [ ] **User-facing README** — what GymOS is, how to install, how to start
- [ ] **Quick start guide** — 3-step "import a program → log a workout → see your dashboard"
- [ ] **Consistent ADR format** — verify all ADRs follow the same template
- [ ] **API documentation** — at minimum module-level docstrings for public API surface
- [ ] **Known issues doc** — document gaps from this audit as known limitations
- [ ] **Changelog** — up-to-date from `docs/CHANGELOG.md`

---

## QA

- [ ] **CI/CD pipeline operational** — GitHub Actions (or equivalent) running on push/PR:
  - [ ] `pytest` with 100% of discovered tests
  - [ ] `ruff` linting
  - [ ] `mypy --strict` or Pyright type checking
  - [ ] Coverage threshold enforcement
  - [ ] Build artifact generation
- [ ] **Integration test** — verify `main.py` initializes without error (headless or via `QOffscreenSurface`)
- [ ] **Smoke test** — manual walkthrough: launch → navigate all 10 workspaces → verify no crashes
- [ ] **Migration test** — apply all alembic migrations to fresh database; verify compatibility
- [ ] **Edge case pass** — test with empty database, corrupted database, missing `program.json`
- [ ] **Regression pass** — verify no new failures after fixing the 48 known failures
- [ ] **Recovery module tests added** — minimum 10 test cases covering domain, engine, service
- [ ] **All workspace pages render** — automated screenshot comparison or smoke test

---

## Sign-off Gates

Once all above items are complete, verify:

- [ ] `pytest -q` shows **0 failed, 0 errors**
- [ ] `ruff check .` shows **0 violations**
- [ ] `mypy --strict .` shows **0 type errors**
- [ ] Build produces working binary
- [ ] Fresh database → import program → full workflow completes without error

---

*Generated from REP-001C Release Readiness Audit — 2026-07-06*
