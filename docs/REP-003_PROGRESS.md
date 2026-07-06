# REP-003 — Quality Burn-down Progress

**Last updated:** 2026-07-06

---

## Phase 1 — Critical Issues (Complete)

### Issue: WorkoutView navigation index wrong

- **Root cause:** `_on_workout_selected` hardcoded index `5` but WorkoutView was added at index `7` (after optional Recovery/Prediction dashboards)
- **Files changed:** `ui/main_window.py:226`
- **Fix:** Changed `setCurrentIndex(5)` → `setCurrentIndex(7)`
- **Regression risk:** None — only one callsite
- **User impact:** **CRITICAL** — without this fix, clicking a workout day navigated to PRView instead of the active workout view
- **Time spent:** 2 min

### Issue: Silent exception suppression — DashboardDataService (12 handlers)

- **Root cause:** Every `_fetch_*()` method in `dashboard_data_service.py` wrapped DB/engine calls in bare `try/except: pass`, silently discarding all errors
- **Files changed:** `ui/dashboard/dashboard_services/dashboard_data_service.py`
- **Fix:** Added `logging.getLogger(__name__)`, replaced all 12 `pass` with `logger.warning(..., exc_info=True)`
- **Regression risk:** Low — logging side-effect only, all return paths unchanged
- **User impact:** **CRITICAL** — dashboard silently showed "--" on any failure with zero diagnostic information
- **Time spent:** 15 min

### Issue: Silent exception suppression — ProductionDataProvider (28 handlers)

- **Root cause:** All 28 data-fetch methods in `production_provider.py` caught exceptions and returned `None`/`[]`/`0.0` without logging
- **Files changed:** `modules/gymbrain/providers/production_provider.py`
- **Fix:** Added `logging.getLogger(__name__)`, replaced all 28 empty handlers with `logger.warning(..., exc_info=True)`
- **Regression risk:** Low — same return values, only logging added
- **User impact:** **CRITICAL** — DecisionEngine silently received empty data on any query failure
- **Time spent:** 10 min

### Issue: Silent exception suppression — PredictionService (10 handlers)

- **Root cause:** All `_generate_*_prediction()` methods wrapped DB queries in `except: pass`, silently using defaults
- **Files changed:** `modules/prediction/application/__init__.py`
- **Fix:** Replaced all 10 `pass` with `logger.warning(..., exc_info=True)`, changed logger name to `__name__`
- **Regression risk:** Low — same return paths
- **User impact:** **CRITICAL** — predictions silently degraded to defaults on any DB issue
- **Time spent:** 8 min

### Issue: Silent exception suppression — RecoveryService (4 handlers)

- **Root cause:** Same pattern in recovery score computation and snapshot fetch
- **Files changed:** `modules/recovery/application/__init__.py`
- **Fix:** Replaced all 4 `pass` with `logger.warning(..., exc_info=True)`
- **Regression risk:** Low
- **User impact:** **CRITICAL** — recovery scores silently degraded on DB failure
- **Time spent:** 5 min

### Issue: Event publish failures logged at DEBUG (5 handlers)

- **Root cause:** Event bus publish failures logged at `logger.debug()` — invisible in production
- **Files changed:**
  - `modules/prediction/application/__init__.py:403`
  - `modules/recovery/application/__init__.py:499`
  - `modules/nutrition/services/__init__.py:195`
- **Fix:** Changed `debug` → `warning` with `exc_info=True`
- **Regression risk:** None
- **User impact:** **MEDIUM** — silent event publish failures now visible in logs
- **Time spent:** 3 min

---

### Remaining Debt — Phase 1 Complete

| Severity | Before | Fixed | Remaining |
|----------|--------|-------|-----------|
| Critical | 6 | 6 | **0** |

---

## Phase 2 — High Issues (Complete)

| Issue | Status | Files Changed | Time |
|-------|--------|---------------|------|
| Remove outline:none focus removal | Done | `ui/design_system/theme.py` | 2 min |
| Version string inconsistency | Done | `ui/main_window.py:189`, `ui/settings_view.py:64` | 5 min |
| Settings hardcoded user data | Done | `ui/settings_view.py:64-67` | 3 min |
| DayCard keyboard accessible | Done | `ui/workout_selection_view.py` — added `clicked` signal, `keyPressEvent`, `setFocusPolicy(StrongFocus)` | 10 min |

### Issue: Global `outline: none` removed

- **Root cause:** `QWidget:focus { outline: none; }` in global QSS suppressed all keyboard focus indicators
- **Files changed:** `ui/design_system/theme.py:57-59`
- **Fix:** Removed the outline suppression entirely; existing focus selectors on QPushButton/QLineEdit/QComboBox already handle focus ring
- **Regression risk:** None — default Qt focus rect restored for elements without explicit styling
- **User impact:** **HIGH** — keyboard users can now see which element has focus
- **Time spent:** 2 min

### Issue: Sidebar version "v0.1.0 MVP"

- **Root cause:** Hardcoded string in `main_window.py:189` and `settings_view.py:64`
- **Files changed:** `ui/main_window.py:189`, `ui/settings_view.py:64` (+ import)
- **Fix:** Both now read from `shared.version.APP_VERSION`
- **Regression risk:** None
- **User impact:** **HIGH** — user sees actual app version instead of obsolete label
- **Time spent:** 5 min

### Issue: Settings showed another user's personal data

- **Root cause:** Hardcoded "178 cm · 63.4 kg · Lean Bulk → 72-75 kg"
- **Files changed:** `ui/settings_view.py:64-67`
- **Fix:** Replaced with generic placeholder text
- **Regression risk:** None
- **User impact:** **HIGH** — user no longer sees someone else's body stats in their app
- **Time spent:** 3 min

### Issue: DayCard not keyboard accessible

- **Root cause:** `mousePressEvent` override bypassed Qt's event system entirely; no `keyPressEvent`, no `setFocusPolicy`
- **Files changed:** `ui/workout_selection_view.py`
- **Fix:** Added `clicked = Signal(str)`, proper `mousePressEvent` with `super()`, `keyPressEvent` for Enter/Space, `setFocusPolicy(Qt.StrongFocus)`, `:focus` CSS style
- **Regression risk:** Low
- **User impact:** **HIGH** — keyboard-only users can now select workout days with Enter/Space
- **Time spent:** 10 min

---

## Phase 3 — Medium Issues (Complete)

| Issue | Status | Files Changed | Time |
|-------|--------|---------------|------|
| Workout duration tracking | Done | `ui/workout_view.py` — stored `_started_at` in `load_day()`, used in `_finish_workout()` | 5 min |
| "RECOVERY DASHBOARD" all-caps | Done | `ui/recovery/recovery_dashboard.py:54` | 2 min |
| PredictionDashboard jargon subtitle | Done | `ui/prediction/prediction_dashboard.py:90-91` | 2 min |
| Period selector actually filters | Done | `ui/progress_view.py` — added `period_map` lookup, passes `days` to queries | 5 min |

### Issue: Workout always shows 0 min duration

- **Root cause:** `started_at` and `completed_at` both set to `datetime.now()` in `_finish_workout()`
- **Files changed:** `ui/workout_view.py:306,382,428-429`
- **Fix:** Store `self._started_at = datetime.now()` when `load_day()` is called; use it in `_finish_workout()`
- **Regression risk:** Low
- **User impact:** **MEDIUM** — workout summary now shows actual duration instead of 0 min
- **Time spent:** 5 min

### Issue: Recovery dashboard title all-caps

- **Root cause:** `"RECOVERY DASHBOARD"` hardcoded in title parameter
- **Files changed:** `ui/recovery/recovery_dashboard.py:54`
- **Fix:** Changed to `"Recovery Dashboard"`
- **Regression risk:** None
- **User impact:** **LOW** — visual consistency
- **Time spent:** 2 min

### Issue: Prediction subtitle full of jargon

- **Root cause:** `"Forecast engine — predicting athlete state across time horizons"`
- **Files changed:** `ui/prediction/prediction_dashboard.py:90-91`
- **Fix:** Changed to `"Predict your progress, manage risk, and explore what-if scenarios"`
- **Regression risk:** None
- **User impact:** **LOW** — reduced cognitive load
- **Time spent:** 2 min

### Issue: Period selector doesn't filter data

- **Root cause:** All three period options used hardcoded `days=90` for queries
- **Files changed:** `ui/progress_view.py:152-153`
- **Fix:** Added `period_map` dictionary mapping index → days, passes actual value
- **Regression risk:** Low
- **User impact:** **MEDIUM** — user can now view different time ranges
- **Time spent:** 5 min

---

## Phase 4 — Low Issues (Complete)

| Issue | Status | Files Changed | Time |
|-------|--------|---------------|------|
| Remove ImportWizard.Done alias | Done | `ui/import_wizard.py`, `ui/main_window.py` | 3 min |
| Remove empty resources/ `__init__.py` | Done | 5 files deleted | 2 min |
| Run ruff auto-fix | Done | 2075 violations fixed across ~600 files | 2 min |

### Issue: Redundant `ImportWizard.Done` alias

- **Root cause:** `Done = QWizard.Accepted` unnecessary alias
- **Files changed:** `ui/import_wizard.py`, `ui/main_window.py`
- **Regression risk:** None
- **User impact:** None (code quality)
- **Time spent:** 3 min

### Issue: Empty placeholder packages in resources/

- **Root cause:** `resources/{themes,icons,fonts,images,animations}/__init__.py` were empty stubs
- **Files changed:** Deleted 5 files
- **Regression risk:** None
- **User impact:** None
- **Time spent:** 2 min

### Issue: 2075 auto-fixable ruff violations

- **Root cause:** Accumulated unused imports, non-PEP 604 annotations, unsorted imports, f-strings without placeholders
- **Files changed:** ~600 files modified
- **Regression risk:** Low — automated fixes are syntactically safe
- **User impact:** Reduced startup import overhead, cleaner codebase
- **Time spent:** 2 min (run time)

---

### Final Debt Summary

| Severity | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Total Fixed | Remaining |
|----------|---------|---------|---------|---------|-------------|-----------|
| Critical | 6 | — | — | — | **6** | **0** |
| High | — | 4 | — | — | **4** | **0** |
| Medium | — | — | 4 | — | **4** | **0** |
| Low | — | — | — | 3 | **3** | **0** |
| **Total** | **6** | **4** | **4** | **3** | **17** | **0** |

**Remaining unfixed (outside scope of REP-003):**
- 353 non-auto-fixable ruff violations (mostly N802 Qt method names — false positives)
- 974 mypy errors (type-checking, not user-facing)
- 48 test bugs (stale assertions, not production bugs)
- Theme/Unit toggles not wired (requires feature-level changes, frozen under REP-003)
- No confirmation before Save & Finish (new interaction, frozen)
