# Exception Handling Audit — REP-001H Phase 2

**Date:** 2026-07-06  
**Files scanned:** All `.py` in `ui/`, `modules/`, `shared/`, `core/`, `scripts/`, `tests/`  

---

## Severity Classification

| Level | Count | Definition |
|-------|-------|------------|
| **SUPPRESSED** | ~50 | Exception caught, silently discarded (`pass`) |
| **SUPPRESSED_MINIMAL** | 5 | Logged at `DEBUG` level only — invisible in production |
| **PARTIAL** | ~45 | Returns default/empty values but never logs |
| **LEGITIMATE** | 12 | Proper `logger.exception()` with recovery |
| **LEGACY** | 7 | Intentional test patterns |

---

## Fixed in this Sprint

All 7 CommandCenter service files now log at `WARNING` level on failure:

| File | Before | After |
|------|--------|-------|
| `ui/command_center/services/analytics_service.py` | `except Exception: pass` | `logger.warning(..., exc_info=True)` |
| `ui/command_center/services/mission_service.py` | `except Exception: pass` | `logger.warning(..., exc_info=True)` |
| `ui/command_center/services/planning_service.py` | `except Exception: pass` | `logger.warning(..., exc_info=True)` |
| `ui/command_center/services/prediction_service.py` | `except Exception: pass` | `logger.warning(..., exc_info=True)` |
| `ui/command_center/services/recovery_service.py` | `except Exception: pass` | `logger.warning(..., exc_info=True)` |
| `ui/command_center/services/adaptive_service.py` | `except Exception: pass` | `logger.warning(..., exc_info=True)` |
| `ui/command_center/services/system_service.py` | `except Exception: pass` | `logger.warning(..., exc_info=True)` |

---

## Remaining — Highest Priority

### 1. `ui/dashboard/dashboard_services/dashboard_data_service.py` (12 SUPPRESSED)
Every `_fetch_*()` method wraps individual DB/engine calls in `try/except: pass`. This feeds the main legacy dashboard, so failures produce empty sections with NO logging.

**Fix:** Replace all 12 with `logger.warning()` calls. The `DashboardDataService` already has a `logger` at module level.

### 2. `modules/gymbrain/providers/production_provider.py` (28 PARTIAL)
All methods return `None`/`[]`/`0.0` on failure, with zero logging. This is the central data bridge for DecisionEngine.

**Fix:** Add `logger.warning()` to all 28 `except Exception` handlers. The module already has a `logger` at line 7.

### 3. `modules/prediction/application/__init__.py` (10 SUPPRESSED)
Every `_generate_*_prediction()` method has `except Exception: pass` around DB queries. Predictions silently use default values.

**Fix:** Add `logger.warning()` to all 10 handlers.

### 4. `modules/recovery/application/__init__.py` (4 SUPPRESSED)
Same pattern — DB query failures silenced, recovery scores computed with defaults.

**Fix:** Add `logger.warning()` to all 4 handlers.

### 5. `ui/experience/integration.py` and `theme_transition_manager.py` (4 SUPPRESSED)
Data propagation and theme transition failures are silently swallowed.

**Fix:** Change to `logger.warning()`.

### 6. `logger.debug` → `logger.warning` (5 instances)
- `modules/nutrition/services/__init__.py:194` — event publish failures
- `modules/recovery/application/__init__.py:498` — event publish failures
- `modules/prediction/application/__init__.py:402` — event publish failures
- `ui/dashboard/dashboard_controller.py:93` — event subscription failure
- `ui/command_center/controller.py:72` — event subscription failure

---

## Well-Handled Patterns (Reference)

These files demonstrate correct exception handling:
- `core/event_bus/__init__.py` — `logger.exception()` (includes traceback)
- `core/plugin/__init__.py` — `logger.exception()` with continue
- `core/scheduler/__init__.py` — `logging.exception()` with continue
- `shared/events/subscribers/*.py` — all use `logger.exception()`
- `shared/observability/subscriber_monitor.py` — tracks metrics then re-raises

---

## Risk Register

| # | Location | Severity | Impact |
|---|----------|----------|--------|
| E1 | `dashboard_data_service.py` | **HIGH** | Silent data loss on main dashboard |
| E2 | `production_provider.py` | **HIGH** | Decision engine sees empty data without error |
| E3 | `prediction/__init__.py` | **MEDIUM** | Predictions silently degrade to defaults |
| E4 | `recovery/__init__.py` | **MEDIUM** | Recovery scores silently degrade |
| E5 | `command_center/services/*.py` | **FIXED** | Now logs on failure |
| E6 | `experience/integration.py` | **MEDIUM** | Data propagation fails silently |
| E7 | `logger.debug` handlers | **LOW** | Just not visible; events still fail silently |
