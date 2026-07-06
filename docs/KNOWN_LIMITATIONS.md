# GymOS v1.0.0-rc1 — Known Limitations

**Date:** 2026-07-06  
**Status:** Acknowledged — non-blocking for RC  

---

## Critical (0)

None. No data loss, crash, or security vulnerabilities are known.

---

## High (2)

### H1 — DashboardDataService Silently Swallows Exceptions

**File:** `ui/dashboard/dashboard_services/dashboard_data_service.py`  
**Impact:** 12 exception handlers use bare `except Exception: pass`. When a dashboard data fetch fails, the error is invisible to the user — widgets show `"--"` values with no indication that something went wrong.

**Symptom:** Dashboard widgets may silently show no data.

**Workaround:** Restart the application. Check `data/crashes/` for any logged errors.

**Fix:** Replace `pass` with `logger.warning(..., exc_info=True)` across all handlers.

---

### H2 — ProductionProvider Silently Swallows Exceptions

**File:** `modules/gymbrain/providers/production_provider.py`  
**Impact:** 28 exception handlers use bare `except Exception: pass`. When GymBrain data fetching fails, the error is invisible — the DecisionEngine may receive incomplete data.

**Symptom:** AI coaching features may silently return default/incomplete recommendations.

**Fix:** Replace `pass` with `logger.warning(..., exc_info=True)` and add fallback return values.

---

## Medium (6)

### M1 — 48 Test Bugs

**Impact:** Test suite is not green. All failures are test bugs (stale assertions), not production bugs.

**Breakdown:**
- 9 kernel tests: capability count `13` → `19`
- 3 navigation tests: stale `PAGE_INDEX` values
- 1 theme test: default theme changed to `"dark"`
- 1 event test: `RecoverySubscriber` keyword renamed
- 17 command center tests: stale mocks/widget APIs
- 5 dashboard tests: stale data structures
- 12 UI widget tests: stale update_data signatures

**Target:** Fix all before v1.0.0-stable.

---

### M2 — TrendIndicator Non-Interactive

**File:** `ui/design_system/visualization/trend_indicator.py`  
**Impact:** Out of 124 interactive surfaces, TrendIndicator is the only one that does not emit any click/hover signal.

**Usage:** Single instance used as a type hint — no user-facing impact in current UI.

**Fix:** Add `clicked` signal and `mousePressEvent`.

---

### M3 — Goal Persistence Path Missing

**File:** `ui/command_center/command_center.py` (`_on_adjust_goal`)  
**Impact:** The GoalAdjustmentDialog can be opened, but there is no write API for goals. The DecisionEngine is read-only.

**Symptom:** Goal adjustments display the dialog but the value is never persisted.

**Fix:** Add a `set_goal_progress()` method to the goal repository or DecisionEngine.

---

### M4 — 47 Actionable `Any` Annotations

**Impact:** ~250 `Any` annotations exist. 47 are avoidable and should be replaced with concrete types.

**Top fix:** Type `shared/interfaces/__init__.py` protocol methods (eliminates ~50 `Any` usages).

---

### M5 — AdaptiveService Hardcoded Demo Data

**File:** `ui/command_center/services/adaptive_service.py`  
**Impact:** The service returns hardcoded `AdaptiveTimelineItem` and `DecisionTimelineItem` objects instead of fetching from a real service.

**Fix:** Wire to a real adaptive provider.

---

### M6 — No Database Encryption

**Impact:** The SQLite database file is unencrypted on disk.

**Mitigation:** This is a local-only, single-user application. No data is transmitted over a network. The database is stored in the user's `%APPDATA%` or `~/.local/share` directory.

**Target:** Evaluate encryption needs for v1.1.0.

---

## Low (8)

### L1 — No Code Signing (Windows/macOS)
Build pipeline includes code signing steps, but signing certificates have not been obtained. Users will see SmartScreen warnings on Windows and Gatekeeper warnings on macOS.

### L2 — Build Pipeline Not Verified on Clean Machine
All build scripts compile and are syntactically valid, but none have been run on a clean machine without developer tools. The PyInstaller bundle may have missing dependencies.

### L3 — No Screen Reader Support
Interactive widgets lack `setAccessibleName()` and `setAccessibleDescription()` calls.

### L4 — No Tab Order on Pages
Pages in the command center and dashboard do not explicitly set `setTabOrder()` between widgets.

### L5 — GridPanel Tests Fail
6 GridPanel layout tests fail due to mock compatibility issues. The production GridPanel widget works correctly.

### L6 — No Flatpak/Snap Packages
Only DEB and AppImage are available for Linux. Flatpak and Snap packaging are not implemented.

### L7 — No ARM64 Builds
All Linux/macOS builds target x86_64. ARM64 (Apple Silicon, Raspberry Pi) builds require additional CI infrastructure.

### L8 — No Internationalization
All UI text is in English. No i18n framework is implemented.

---

## Deprecated / Legacy

### D1 — Legacy Dashboard Views
`ui/dashboard/`, `ui/recovery/`, `ui/prediction/` contain pre-command-center views that are still functional but receive fewer updates. The Command Center (`ui/command_center/`) is the primary UI.

### D2 — Legacy Visualization Copy
`ui/design_system/visualization/` contains copies of visualization widgets that are shadows of `ui/visualization/core/base.py`. The `__init__.py` re-exports from the canonical source.

---

## Summary

| Severity | Count | Examples |
|----------|-------|---------|
| Critical | 0 | — |
| High | 2 | Silenced exceptions in dashboard/production services |
| Medium | 6 | Test bugs, TrendIndicator, goals, Any types, adaptive data, encryption |
| Low | 8 | Code signing, build verification, screen reader, tab order, GridPanel tests, Flatpak, ARM64, i18n |
| Legacy | 2 | Dashboard views, visualization copy |

**30 total known limitations — none blocking for RC.**
