# REP-001C — GymOS Release Readiness Audit

**Status:** Draft  
**Date:** 2026-07-06  
**Auditor:** OpenCode  
**Version audited:** v0.1.0 (MVP) / v0.5 (Product Maturity)

---

## Overall Readiness Score

| Domain | Score | Interpretation |
|--------|-------|----------------|
| Product Completeness | 6/10 | Core capabilities built, but service stubs and invisible infrastructure gaps |
| UX Readiness | 4/10 | Functional navigation, zero polish — no loading, empty, or error states |
| Engineering Quality | 5/10 | 3377 tests (98.6% pass), but 48 real failures and no CI/CD |
| Platform Readiness | 7/10 | Rich infrastructure, mostly unplugged from main.py |
| Release Assets | 1/10 | No installer, icon, splash, about dialog, or crash handling |

**Overall:** 4.6 / 10 — **NOT READY for v1.0 Release Candidate**

---

## Critical Blockers (Block Ship)

| # | Issue | Domain | Severity | Effort |
|---|-------|--------|----------|--------|
| C1 | No crash handler — `sys.excepthook` not overridden; all errors silently swallowed | UX | Critical | 2h |
| C2 | `print()` debug statements in `shared/runtime/runtime.py:33-34` (production code) | Engineering | Critical | 15m |
| C3 | 48 failing tests across 7 categories — all real failures, none marked `xfail` | Engineering | Critical | 3-5d |
| C4 | No lockfile (`poetry.lock`/`Pipfile.lock`/`requirements.txt`) — non-reproducible builds | Release | Critical | 1h |
| C5 | `modules/prediction/tests/test_prediction_service.py:52` — `MockEventBus.__init` typo (missing `__`) means `self.core` is never set, causing `AttributeError` on code path hit | Engineering | Critical | 15m |
| C6 | `modules/prediction/infrastructure/repository.py:19-21` — duplicate import of 5 models | Engineering | Critical | 5m |
| C7 | Migration 002 (`002_add_is_active.py`) references table `workout_programs` which version 001 never creates (001 creates `workouts`) | Platform | Critical | 1h |

---

## High Priority Issues (Should Fix Before Ship)

| # | Issue | Domain | Effort |
|---|-------|--------|--------|
| H1 | ~25 `except Exception: pass` blocks silently swallowing errors across ui/ and shared/ | Engineering | 1-2d |
| H2 | ~224 `Any` type annotations across 70+ function signatures — systemic typing deficiency | Engineering | 5-7d |
| H3 | No CI/CD pipeline (no .github/workflows, no tox, no Dockerfile) | Release | 1-2d |
| H4 | `shared/events/prediction_events.py` — dead/duplicate file; all 5 events exist in `domain_events.py` | Engineering | 15m |
| H5 | `ui/dashboard/dashboard_services/dashboard_data_service.py` — 12 empty pass-stub handlers that silently swallow dashboard events | Product | 1d |
| H6 | No application icon (.ico, no window icon set) | Release | 2h |
| H7 | No About dialog — version only displayed as `QLabel("v0.1.0 MVP")` in sidebar | UX | 2h |
| H8 | No settings persistence — `QSettings` unused; theme/unit preferences lost on restart | UX | 4h |
| H9 | `ui/command_center/services/__init__.py` — 22 empty pass-stub registrations for workspace services | Product | 1d |
| H10 | `modules/recovery/` has zero tests — only module entirely untested | Engineering | 2-3d |
| H11 | `shared/runtime/` (8 files) completely unused — Runtime, Pipeline, Scheduler, HealthMonitor never instantiated | Platform | 1d (document or remove) |
| H12 | 5 empty stub directories in shared/: `exceptions/`, `constants/`, `validators/`, `helpers/`, `types/` | Engineering | 2h |
| H13 | Version inconsistency: `main.py` says `v0.1.0`, capability registry says `v0.5`, PRD says `v0.5` | Release | 1h |
| H14 | ~45+ public classes lacking docstrings across ui/domain layer | Engineering | 2d |
| H15 | No empty state, loading state, or error state components wired into workspace pages — only static "No X available" labels | UX | 2-3d |
| H16 | No onboarding / first-run experience — app opens to empty home page with no guide | UX | 2d |
| H17 | ~31 `print()` debug statements across 7 files (acceptable in scripts, bad in production modules) | Engineering | 1h |
| H18 | 6 files >500 lines — monoliths violating single-responsibility (especially `__init__.py` files with 751 and 547 lines of logic) | Engineering | 3-5d |
| H19 | `env.py` migration uses async engine (`async_engine_from_config`) but app uses sync SQLAlchemy | Platform | 2h |

---

## Medium Issues (Fix Before RC or Document as Known)

| # | Issue | Effort |
|---|-------|--------|
| M1 | No hotkey/command palette for any view other than CommandCenter — `ShortcutManager` exists but not wired | 2d |
| M2 | No undo support for any user action | Unknown |
| M3 | No confirmation dialogs for destructive actions | 1d |
| M4 | `shared/observability/logger/__init__.py:48` — `# type: ignore` escape suppressing typing issue | 15m |
| M5 | No keyboard shortcut discovery page or `QWhatsThis` usage | 2d |
| M6 | No search across workspaces — `QuickSearch` exists but scoped to page navigation only | 2d |
| M7 | No test isolation — `pytest-asyncio 1.4.0` outdated; fixture scoping issues possible | 1h |
| M8 | `pytest.ini_options` in `pyproject.toml` only sets `testpaths = ["tests"]` — tests in `shared/` and `modules/` not auto-discovered | 5m |
| M9 | No coverage thresholds configured — coverage runs but no minimum enforced | 1h |
| M10 | No accessibility considerations — no `QAccessible`, no `setTabOrder` audit, no screen reader support | Unknown |
| M11 | ~50+ packages installed but not declared in `pyproject.toml` (torch, transformers, celery, flask, opencv, etc.) — bloat and security surface | 1d |
| M12 | 41 outdated pip packages — includes `numpy`, `matplotlib`, `huggingface-hub` (69 versions behind) | 2h |
| M13 | `coverage` source omits `tests/` — no visibility into test code quality | 5m |
| M14 | HiDPI support untested — no `Qt.AA_EnableHighDpiScaling` attribute set | 1d |
| M15 | `main_window.py` hardcodes window min size `1024x768` — no responsive sizing | 1h |
| M16 | No resource compilation (no `.qrc` file) — all styling done via inline `setStyleSheet()` | 2d |
| M17 | `ui/experience/focus_mode.py`, `integration.py`, `layout_engine.py`, `search_provider.py`, `workflow_engine.py` exist but may not be fully wired | 2d (audit) |
| M18 | Navigation inconsistency — sidebar items handled by `main_window.py`, command center pages by `command_center.py`, no single navigation authority | 1d |
| M19 | No backup/restore strategy — SQLite database has no export/import for user data | 2d |
| M20 | No migration strategy for users upgrading between versions | 2d |

---

## Low Issues (Nice-to-Have Before Ship)

| # | Issue | Effort |
|---|-------|--------|
| L1 | One `# NOTE` comment in `production_provider.py:236` — should be docstring | 5m |
| L2 | `ui/experience/theme_transition_manager.py` — 3 `pass` stubs; transitions not animated | 1d |
| L3 | `GymBrainSubscriber` doesn't extend `Subscriber` base class (uses manual subscription) | 30m |
| L4 | No tests for subscriber/publisher implementations in `shared/events/subscribers/` and `publishers/` | 2d |
| L5 | `shared/cognitive/` marked as `v0.7` in registry but fully implemented — version claim inconsistency | 5m |
| L6 | No `portable_mode` flag — always uses path-relative `data/gymos.db` | 1h |
| L7 | No license file — `pyproject.toml` has no `license` field | 15m |
| L8 | No `__main__` guard in test files that are accidentally importable | 1h |
| L9 | `ui/` directory has no `__init__.py` with meaningful content (should at minimum document the UI layer) | 10m |
| L10 | No dark mode toggle — `main_window.py` hardcodes dark theme, no built-in light theme support | 2d |

---

## Estimated Work Summary

| Priority | Items | Estimated Effort |
|----------|-------|-----------------|
| Critical | 7 | 4-7 days |
| High | 19 | 18-30 days |
| Medium | 20 | 14-21 days |
| Low | 10 | 4-6 days |
| **Total** | **56** | **40-64 person-days** |

---

## Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Silent data loss from swallowed exceptions | High | High | Fix all `except Exception: pass` blocks |
| Untested recovery logic causes wrong training decisions | Medium | High | Add recovery module tests |
| Migration fails for new users (002 references missing table) | High | Medium | Fix migration 002 |
| `MockEventBus` typo hides prediction test coverage gaps | High | Medium | Fix typo, verify tests catch real bugs |
| Non-reproducible builds due to missing lockfile | Medium | High | Generate lockfile |
| No crash handler — user sees Python traceback | High | Medium | Install `sys.excepthook` |
| Type errors in production from `Any`-typed interfaces | Medium | High | Incrementally add concrete types |
| 50+ undeclared dependencies cause version conflicts | Medium | Medium | Audit and prune dependencies |
| CI/CD gap means regressions reach users undetected | High | High | Add GitHub Actions pipeline |
| No backup strategy — single SQLite file is single point of failure | Medium | High | Add export/backup flow |

---

## Ship / No Ship Recommendation

**RECOMMENDATION: NO SHIP**

GymOS requires **4-7 days of critical-blocker work** followed by **18-30 days of high-priority work** before a v1.0.0 Release Candidate can be confidently tagged.

### Minimum Viable Ship Criteria (Gate Checklist)

Before any v1.0.0 RC tag, the following must be resolved:

1. [ ] C1 — Crash handler installed (`sys.excepthook`)
2. [ ] C2 — `print()` removed from `runtime.py`
3. [ ] C3 — 48 failing tests resolved (either fix or legitimately mark xfail)
4. [ ] C4 — Lockfile committed
5. [ ] C5 — `MockEventBus.__init__` typo fixed
6. [ ] C6 — Duplicate import removed
7. [ ] C7 — Migration 002 fixed
8. [ ] H1 — All silent `except Exception: pass` blocks removed
9. [ ] H3 — CI/CD pipeline operational (at minimum: `pytest` on push)
10. [ ] H6 — Application icon set
11. [ ] H7 — About dialog added
12. [ ] H16 — First-run experience or at minimum a welcome dialog
13. [ ] H13 — Version string made consistent across all manifests

After these 13 gates, reassess. Estimated 1-2 weeks of focused work.

---

## Appendices

### A. Module Completeness Grid

| Module | Files | Tests | Test Count | Passes | Known Bugs |
|--------|-------|-------|-----------|--------|------------|
| workout + workout_program | 12 | ~5 | TBD | TBD | None found |
| nutrition | 15 | 5 | TBD | TBD | None found |
| prediction | 16 | 8 | 28 | varies | 2 (init typo, duplicate import) |
| recovery | 9 | 0 | 0 | N/A | No tests |
| gymbrain | 24 | 13 | TBD | TBD | None found |
| settings | 4 | 0 | 0 | N/A | UI-only, no tests |
| devtools | 5 | 0 | 0 | N/A | Dev-only |

### B. Unused Infrastructure

| Component | Location | Files | Lines | Status |
|-----------|----------|-------|-------|--------|
| Runtime | `shared/runtime/` | 8 | ~600 | Built, never instantiated |
| Scheduler | `shared/runtime/scheduler.py` | 1 | ~200 | Built, never instantiated |
| Pipeline | `shared/runtime/pipeline.py` | 1 | ~200 | Built, never instantiated |
| HealthMonitor | `shared/runtime/health.py` | 1 | ~100 | Built, never instantiated |
| Cognitive Orchestrator | `shared/cognitive/` | 9 | ~800 | Built, not wired into main.py |
| Evolution Engine | `shared/evolution/` | 10 | ~700 | Built, not wired into main.py |
| Intent Platform | `shared/intent/` | 14 | ~900 | Built, not wired into main.py |
| Planning Engine | `shared/planning/` | 12 | ~1200 | Built, not wired into main.py |
| Planning Optimizer | `shared/planning_optimizer/` | 14 | ~800 | Built, not wired into main.py |
| Adaptive Programming | `shared/adaptive_programming/` | 13 | ~700 | Built, not wired into main.py |
| Knowledge Evolution | `shared/knowledge_evolution/` | 14 | ~700 | Built, not wired into main.py |
| Optimization Knowledge | `shared/optimization_knowledge/` | 13 | ~600 | Built, not wired into main.py |
| Kernel | `shared/kernel/` | 10 | ~800 | Built, not wired into main.py |
| Explainability | `shared/explainability/` | 9 | ~500 | Built, not wired into main.py |
| Product State Engine | `shared/state/` | 10 | ~600 | Built, not wired into main.py |
| Knowledge Graph | `shared/graph/` | 10 | ~600 | Built, not wired into main.py |

**Total unused infrastructure: ~10,000+ lines of code across 15 subsystems**

### C. Test Failure Breakdown

| Category | Count | Root Cause | Effort |
|----------|-------|-----------|--------|
| Capability registry count | 18 | Hardcoded `== 13`, registry now has 19 | 1h |
| Command Center layout | 11 | `MagicMock` not accepted by PySide6 layout methods | 2-3d |
| Command Center sidebar | 5 | `_sidebar` attribute renamed to `_nav_rail` | 2h |
| Page labels/index | 4 | `PAGE_INDEX` and `PAGE_LABELS` values shifted | 1h |
| Dashboard widgets | 4 | Removed fields (`goal_progress`, `goal_weight`), wrong `update()` sig | 1d |
| AdaptiveTimelineWidget | 3 | Missing `update_data` method | 1h |
| Performance timing | 1 | `test_fetch_all_under_100ms` avg 224ms vs 100ms threshold | 1d |
| Theme colors | 2 | `#FACC15` vs `#FBBF24` mismatch | 15m |
| **Total** | **48** | | **4-8d** |

### D. Worst Offenders for Silent Error Swallowing

| File | `except Exception: pass` Count |
|------|-------------------------------|
| `ui/dashboard/dashboard_services/dashboard_data_service.py` | 21 |
| `ui/dashboard/dashboard_controller.py` | 8 |
| `ui/experience/theme_transition_manager.py` | 5 |
| `ui/command_center/controller.py` | 1 |
| `ui/command_center/services/*.py` | 7 (1 each in 7 services) |
| `ui/experience/integration.py` | 1 |
| `ui/experience/window_layout_manager.py` | 1 |

---

*End of REP-001C*
