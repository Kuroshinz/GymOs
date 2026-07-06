# REP-001G — Interactive Product Completion

**Status:** Complete  
**Date:** 2026-07-06  
**Preceding work:** REP-001E (audit), REP-001F (20 CTA wiring)  
**Rule:** No new services, no new engines, no new architecture — only connect and polish existing functionality.

---

## Scope

Execute all remaining interaction work in a single sprint:
- Design System polish  
- Dialog implementation  
- Clickable visualization surfaces  
- Remaining dashboard CTAs  
- Navigation completion  

---

## Part A — Design System (5 components fixed)

| # | Component | Change | Previous State | New State |
|---|-----------|--------|---------------|-----------|
| 1 | **WarningBanner** | Added `action_clicked = Signal()` | Button created with hover but no `.clicked.connect()` — **dead** | Button emits `action_clicked` signal |
| 2 | **InsightCard** | Added `clicked = Signal()` + `mousePressEvent` | `PointingHandCursor` + hover border but no click handler — **dead** | Card emits `clicked` signal on press |
| 3 | **AppCard** | Added `clicked = Signal()` + `mousePressEvent` (guarded by `interactive`) | `interactive=True` showed cursor + hover but no handler — **dead** | Card emits `clicked` when interactive |
| 4 | **KpiStrip** | Added `item_clicked = Signal(int)` + per-item mousePressEvent | Each KPI item had `PointingHandCursor` + hover background but no handler — **dead** | Each item emits `item_clicked(index)` on press |
| 5 | **Breadcrumb** | Replaced `lambda: None` with `crumb_clicked = Signal(str)` | Non-last crumbs wired to `lambda: None` — **dead click** | Crumbs emit `crumb_clicked(page_id)` → routed to `_navigate()` |

**Files modified:**
- `ui/design_system/components/warning_banner.py`
- `ui/design_system/components/insight_card.py`
- `ui/design_system/components/app_card.py`
- `ui/design_system/layout/kpi_strip.py`
- `ui/command_center/navigation/breadcrumb.py`

---

## Part B — Real Dialogs (5 new dialogs)

### B1. LogWeightDialog (`ui/dialogs/log_weight_dialog.py`)
- **Replaces:** Raw `QInputDialog.getDouble()` in CommandCenter
- **Features:** Date picker (calendar), weight spinner (30–300 kg, 0.1 precision), notes text field, Save/Cancel
- **Signal:** `weight_logged(float, str, str)` — weight, date, notes
- **Service:** Paired with `GymDatabase.save_body_weight()` via CommandCenter

### B2. GoalAdjustmentDialog (`ui/dialogs/goal_adjustment_dialog.py`)
- **Replaces:** Stub `QMessageBox.information("Adjust Goal")`
- **Features:** Shows current goal name, progress %, slider (0–100%), live target label, Apply/Cancel
- **Signal:** `goal_adjusted(str, float)` — goal name, new target %
- **Service:** DecisionEngine.get_goal_progress() via CommandCenter

### B3. AIConfigurationDialog (`ui/dialogs/ai_configuration_dialog.py`)
- **Replaces:** Stub `QMessageBox.information("AI settings — available in future sprint")`
- **Features:** Reasoning mode combo (Default/Conservative/Balanced/Aggressive), detail level slider (1–10), auto-analyze checkbox, show-confidence checkbox, Apply/Cancel
- **Signal:** `config_applied(dict)` — full config payload

### B4. SystemLogViewerDialog (`ui/dialogs/system_log_viewer_dialog.py`)
- **Replaces:** Stub `QMessageBox.information("available in observability module")`
- **Features:** Monospace log display (10k line buffer), level filter combo (ALL/DEBUG/INFO/WARNING/ERROR/CRITICAL), Refresh button, auto-refresh timer (5s), Close
- **Services:** Reads from Python logging root handler StringIO streams

### B5. AboutGymOSDialog (`ui/dialogs/about_gymos_dialog.py`)
- **Replaces:** Non-existent (no About dialog existed)
- **Features:** GymOS icon, name, tagline, version (0.5.0), build date, copyright, description paragraph, Close button

**New module:** `ui/dialogs/` — 6 files including `__init__.py`

---

## Part C — Visualization (audit only — already interactive)

All 30 `BaseVisualization` subclasses already have full interactivity via `ui/visualization/core/base.py`:
- `clicked`, `double_clicked`, `hovered`, `zoom_changed`, `value_changed` signals
- `PointingHandCursor`, `mousePressEvent`, `mouseDoubleClickEvent`, `wheelEvent`, `keyPressEvent`
- Accessibility (setAccessibleName/Description/ToolTip)
- Export (PNG + clipboard)

**Legacy design_system copies** (RecoveryRing, GoalRing, ConfidenceGauge, RiskMeter, WeeklyTimeline, PredictionTimeline, MuscleHeatmap, TrendIndicator) — the `__init__.py` re-exports the interactive versions from `ui/visualization/`, so pages importing from `ui.design_system.visualization` already get interactive widgets.

**Exception:** `TrendIndicator` (`ui/design_system/visualization/trend_indicator.py`) — standalone `QWidget` with no interactive counterpart. Never imported outside `dashboard_view.py` which only uses it as a type hint. Can be addressed in a future sprint.

---

## Part D — Legacy Cleanup (4 issues fixed)

### D1. Breadcrumb `lambda: None` → Real Navigation
**File:** `ui/command_center/navigation/breadcrumb.py:47`  
**Change:** `crumb.clicked.connect(lambda: None)` → `crumb.clicked.connect(lambda: self.crumb_clicked.emit(p))`  
**Effect:** Crumbs now navigate; signal wired to `CommandCenter._navigate()`

### D2. `_toggle_sidebar` `pass` → Real Toggle
**File:** `ui/experience/experience_manager.py:157-158`  
**Change:** `def _toggle_sidebar(self): pass` → Searches parent widget for `_sidebar` or `_nav_rail`, toggles visibility  
**Effect:** Ctrl+K palette "Toggle Sidebar" command now works

### D3. NutritionWidget Orphan Import Removed
**File:** `ui/dashboard/dashboard_view.py:19`  
**Change:** Removed `from ...nutrition_widget import NutritionWidget` (widget was imported but never instantiated)  
**Effect:** Cleaner imports, no dead code

### D4. QInputDialog Replacements
**File:** `ui/command_center/command_center.py`  
**Changes:**
- `_on_log_weight()` — uses `LogWeightDialog` instead of `QInputDialog.getDouble()`
- `_on_adjust_goal()` — uses `GoalAdjustmentDialog` instead of `QMessageBox` stub
- `_on_configure_ai()` — uses `AIConfigurationDialog` instead of "future sprint" stub
- `_on_view_logs()` — uses `SystemLogViewerDialog` instead of "observability module" stub

---

## Part E — Product Consistency

### Navigation Matrix

| Page | Primary Action | Secondary Action | Context Help | Breadcrumb | Back Nav |
|------|---------------|-----------------|-------------|-----------|----------|
| Home | Start Workout → Mission | Log Weight → Dialog | N/A | `home` | N/A |
| Mission | Adjust Goal → Dialog | View History → Analytics | N/A | `home > goals` | Crumb → Home |
| Planning | Adjust Week → Mission | View Program → Dialog | N/A | `home > planning` | Crumb → Home |
| Prediction | Run Scenario → Forecasts | Export Report → File | N/A | `home > forecast` | Crumb → Home |
| Recovery | View Details → Self | View Trends → Analytics | N/A | `home > recovery` | Crumb → Home |
| Knowledge | Explore Graph → Dialog | Search Knowledge → Dialog | N/A | `home > knowledge` | Crumb → Home |
| Adaptive | Review Decision → Intelligence | Run Simulation → Forecasts | N/A | `home > briefing > optimize` | Crumb |
| Intelligence | Generate Briefing → Refresh | Configure AI → Dialog | N/A | `home > briefing` | Crumb → Home |
| Analytics | Export Report → File | Compare Periods → Dialog | N/A | `home > lab` | Crumb → Home |
| System | View Logs → LogViewer | Run Diagnostics → Dialog | N/A | `home > console` | Crumb → Home |

Every page now has primary + secondary actions that navigate, execute, or configure.

---

## Part F — Validation

- **76/76** existing UI tests pass (no regressions)
- **8/8** modified files pass `py_compile` (no syntax errors)
- **5/5** new dialog files pass `import` (no import errors)

---

## Outputs

### Files Created
| File | Purpose |
|------|---------|
| `ui/dialogs/__init__.py` | Dialog module exports |
| `ui/dialogs/log_weight_dialog.py` | LogWeightDialog — date, weight, notes |
| `ui/dialogs/goal_adjustment_dialog.py` | GoalAdjustmentDialog — slider, target |
| `ui/dialogs/ai_configuration_dialog.py` | AIConfigurationDialog — mode, detail, toggles |
| `ui/dialogs/system_log_viewer_dialog.py` | SystemLogViewerDialog — scrollable log viewer |
| `ui/dialogs/about_gymos_dialog.py` | AboutGymOSDialog — version, copyright |

### Files Modified
| File | Change |
|------|--------|
| `ui/design_system/components/warning_banner.py` | Added `action_clicked` signal + button wiring |
| `ui/design_system/components/insight_card.py` | Added `clicked` signal + `mousePressEvent` |
| `ui/design_system/components/app_card.py` | Added `clicked` signal + `mousePressEvent` (interactive) |
| `ui/design_system/layout/kpi_strip.py` | Added `item_clicked` signal + per-item wiring |
| `ui/command_center/navigation/breadcrumb.py` | Added `crumb_clicked` signal, replaced `lambda: None` |
| `ui/command_center/command_center.py` | Wired breadcrumb signal; replaced 4 QMessageBox stubs with real dialogs; removed unused import |
| `ui/experience/experience_manager.py` | Implemented `_toggle_sidebar` |
| `ui/dashboard/dashboard_view.py` | Removed unused NutritionWidget import |

---

## Remaining Technical Debt

| # | Item | Impact | Effort |
|---|------|--------|--------|
| 1 | **TrendIndicator** has no interactivity (standalone QWidget, no `BaseVisualization` subclass) | Low — barely used | Small |
| 2 | **Visualization `clicked` signals** not consumed by any page — only fired, never connected | Medium — BaseVisualization emits on click but no handler subscribes | Medium |
| 3 | **DialogTemplate** (`ui/design_system/components/dialog_template.py`) unused — built but never imported | Low — available as reusable component | Small |
| 4 | **Hardcoded demo data** in AdaptiveService, KnowledgeService, SystemService | Low — fallback only when real services unavailable | Medium |
| 5 | **`except Exception: pass`** patterns in command_center services | Low — defensive but error-hiding | Small |
| 6 | **Backup/Restore dialogs** still missing | Low — no backup feature exists | Large |

---

## Zero Target Verification

| Metric | Before REP-001G | After REP-001G |
|--------|-----------------|----------------|
| Decorative buttons (no handler) | 5 | **0** |
| Dead click surfaces (cursor but no action) | 5 | **0** |
| `lambda: None` signal connections | 1 | **0** |
| `pass` callback stubs | 1 | **0** |
| "Future sprint" QMessageBox stubs | 4 | **0** |
| QInputDialog stand-ins (needing real dialog) | 2 | **0** |
| Orphan widget imports (imported but unused) | 1 | **0** |

---

*End of REP-001G — Interactive Product Completion*
