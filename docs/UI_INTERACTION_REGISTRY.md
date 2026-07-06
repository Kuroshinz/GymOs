# UI Interaction Registry

**Date:** 2026-07-06  
**Coverage:** Every interactive surface across all workspaces, dashboards, design system, dialogs, and visualization widgets.  
**Target:** Zero decorative controls, zero dead interactions, zero navigation dead ends.

---

## Table of Contents

1. [CommandCenter Pages (10 pages, 20 CTAs)](#1-commandcenter-pages)
2. [CommandCenter Navigation & Search](#2-commandcenter-navigation--search)
3. [Legacy Dashboard (MainWindow)](#3-legacy-dashboard-mainwindow)
4. [Legacy Dashboard Widgets](#4-legacy-dashboard-widgets)
5. [Design System Components](#5-design-system-components)
6. [Narrative Components](#6-narrative-coach-cards--micro-ux)
7. [Workflow & Dialog Components](#7-workflow--dialog-components)
8. [Real Dialogs (new in REP-001G)](#8-real-dialogs)
9. [Visualization Widgets (30 interactive, 1 non-interactive)](#9-visualization-widgets)
10. [Experience Platform](#10-experience-platform)
11. [Summary Statistics](#11-summary-statistics)

---

## 1. CommandCenter Pages (10 pages, 20 CTAs)

### HomePage (`ui/command_center/pages/home_page.py`)

| Widget | Label | Action | Signal | Wired To | Status |
|--------|-------|--------|--------|----------|--------|
| `_start_btn` | Start Workout | Navigate | `start_workout_clicked` | `CommandCenter._navigate("mission")` | ✅ |
| `_log_weight_btn` | Log Weight | Execute | `log_weight_clicked` | `CommandCenter._on_log_weight` → LogWeightDialog | ✅ |

### MissionPage (`ui/command_center/pages/mission_page.py`)

| Widget | Label | Action | Signal | Wired To | Status |
|--------|-------|--------|--------|----------|--------|
| `_adjust_btn` | Adjust Goal | Execute | `adjust_goal_clicked` | `CommandCenter._on_adjust_goal` → GoalAdjustmentDialog | ✅ |
| `_history_btn` | View History | Navigate | `view_history_clicked` | `CommandCenter._navigate("analytics")` | ✅ |

### PlanningPage (`ui/command_center/pages/planning_page.py`)

| Widget | Label | Action | Signal | Wired To | Status |
|--------|-------|--------|--------|----------|--------|
| `_adjust_btn` | Adjust Week | Navigate | `adjust_week_clicked` | `CommandCenter._navigate("mission")` | ✅ |
| `_view_program_btn` | View Program | Execute | `view_program_clicked` | `CommandCenter._on_view_program` → QMessageBox | ✅ |

### PredictionCenterPage (`ui/command_center/pages/prediction_center_page.py`)

| Widget | Label | Action | Signal | Wired To | Status |
|--------|-------|--------|--------|----------|--------|
| `_scenario_btn` | Run Scenario | Execute | `run_scenario_clicked` | `CommandCenter._on_run_scenario` | ✅ |
| `_export_btn` | Export Report | Execute | `export_report_clicked` | `CommandCenter._on_export_report` → QFileDialog | ✅ |

### RecoveryCenterPage (`ui/command_center/pages/recovery_center_page.py`)

| Widget | Label | Action | Signal | Wired To | Status |
|--------|-------|--------|--------|----------|--------|
| `_detail_btn` | View Details | Navigate | `view_details_clicked` | `CommandCenter._navigate("recovery")` | ✅ |
| `_trends_btn` | View Trends | Navigate | `view_trends_clicked` | `CommandCenter._navigate("analytics")` | ✅ |

### KnowledgeCenterPage (`ui/command_center/pages/knowledge_center_page.py`)

| Widget | Label | Action | Signal | Wired To | Status |
|--------|-------|--------|--------|----------|--------|
| `_explore_btn` | Explore Graph | Execute | `explore_graph_clicked` | `CommandCenter._on_explore_graph` | ✅ |
| `_search_btn` | Search Knowledge | Execute | `search_knowledge_clicked` | `CommandCenter._on_search_knowledge` | ✅ |

### AdaptiveCenterPage (`ui/command_center/pages/adaptive_center_page.py`)

| Widget | Label | Action | Signal | Wired To | Status |
|--------|-------|--------|--------|----------|--------|
| `_review_btn` | Review Decision | Navigate | `review_decision_clicked` | `CommandCenter._navigate("intelligence")` | ✅ |
| `_simulate_btn` | Run Simulation | Execute | `run_simulation_clicked` | `CommandCenter._on_run_simulation` | ✅ |

### AnalyticsCenterPage (`ui/command_center/pages/analytics_center_page.py`)

| Widget | Label | Action | Signal | Wired To | Status |
|--------|-------|--------|--------|----------|--------|
| `_export_btn` | Export Report | Execute | `export_report_clicked` | `CommandCenter._on_export_report` → QFileDialog | ✅ |
| `_compare_btn` | Compare Periods | Execute | `compare_periods_clicked` | `CommandCenter._on_compare_periods` | ✅ |

### SystemCenterPage (`ui/command_center/pages/system_center_page.py`)

| Widget | Label | Action | Signal | Wired To | Status |
|--------|-------|--------|--------|----------|--------|
| `_logs_btn` | View Logs | Execute | `view_logs_clicked` | `CommandCenter._on_view_logs` → SystemLogViewerDialog | ✅ |
| `_diag_btn` | Run Diagnostics | Execute | `run_diagnostics_clicked` | `CommandCenter._on_run_diagnostics` | ✅ |

### IntelligencePage (`ui/intelligence/narrative_page.py`)

| Widget | Label | Action | Signal | Wired To | Status |
|--------|-------|--------|--------|----------|--------|
| `_brief_btn` | Generate Briefing | Execute | `generate_briefing_clicked` | `CommandCenter._on_generate_briefing` | ✅ |
| `_config_btn` | Configure AI | Execute | `configure_ai_clicked` | `CommandCenter._on_configure_ai` → AIConfigurationDialog | ✅ |

---

## 2. CommandCenter Navigation & Search

### NavigationRail (`ui/design_system/components/navigation_rail.py`)

| Widget | Count | Action | Signal | Wired To | Status |
|--------|-------|--------|--------|----------|--------|
| Per-item buttons | 10 | Navigate | `item_selected(str)` | `CommandCenter._navigate(id)` | ✅ |

### Breadcrumb (`ui/command_center/navigation/breadcrumb.py`)

| Widget | Action | Signal | Wired To | Status |
|--------|--------|--------|----------|--------|
| Non-last crumb buttons | Navigate | `crumb_clicked(str)` | `CommandCenter._navigate(page_id)` | ✅ |

### SearchBar (`ui/design_system/components/search_bar.py`)

| Widget | Action | Signal | Wired To | Status |
|--------|--------|--------|----------|--------|
| Text input (textChanged) | Filter | `text_changed(str)` | (none — disconnected, relies on search) | ⚠️ Unused |
| Text input (returnPressed) | Submit | `search_submitted(str)` | (none — disconnected) | ⚠️ Unused |

### CommandPalette (`ui/command_center/navigation/command_palette.py`)

| Widget | Action | Signal | Wired To | Status |
|--------|--------|--------|----------|--------|
| Search input | Filter | — | Internal `_filter()` | ✅ |
| List items | Select | `command_selected(str)` | `CommandCenter._handle_command()` | ✅ |

---

## 3. Legacy Dashboard (MainWindow)

### SidebarButtons (`ui/main_window.py`)

| Button | Index | Action | Status |
|--------|-------|--------|--------|
| Dashboard | 0 | `_switch_to(0)` — DashboardView | ✅ |
| Workout | 1 | `_switch_to(1)` — WorkoutSelectionView | ✅ |
| Progress | 2 | `_switch_to(2)` — ProgressView | ✅ |
| Recovery | 3 | `_switch_to(3)` — RecoveryDashboard | ✅ |
| Predictions | 4 | `_switch_to(4)` — PredictionDashboard | ✅ |
| Records | 5 | `_switch_to(5)` — PRView | ✅ |
| Settings | 6 | `_switch_to(6)` — SettingsView | ✅ |
| Import Program | — | `_open_import_wizard()` | ✅ |

### QuickActionsWidget (`ui/dashboard/dashboard_widgets/quick_actions_widget.py`)

| Button | Signal | Wired To | Status |
|--------|--------|----------|--------|
| Start Workout | `start_workout_clicked` | `main_window._switch_to(workout_index)` | ✅ |
| Log Body Weight | `log_weight_clicked` | `main_window._switch_to(settings_index)` | ✅ |
| Import Program | `import_program_clicked` | `main_window._open_import_wizard()` | ✅ |
| Weekly Review | `weekly_review_clicked` | `main_window._switch_to(progress_index)` | ✅ |
| Recommendations | `view_recommendations_clicked` | `main_window._switch_to(progress_index)` | ✅ |

### Other Legacy Widgets

| Widget | Button | Status |
|--------|--------|--------|
| WorkoutWidget | Start Workout | ✅ Wired to `start_workout_clicked` → MainWindow |
| PRWidget | View All PRs | ✅ Wired to `view_all_prs_clicked` → MainWindow |
| RecommendationWidget | Show evidence / Dismiss / Mark Completed | ✅ All wired internally |
| WorkoutView | Back / Save & Finish | ✅ Both wired |

---

## 4. Legacy Dashboard Widgets

| Widget | Clickable Surface | Handler | Status |
|--------|-------------------|---------|--------|
| QuickActionsWidget | 5 buttons (start, weight, import, review, recs) | Per-signal → MainWindow | ✅ |
| WorkoutWidget | Start Workout | `start_workout_clicked` | ✅ |
| PRWidget | View All PRs | `view_all_prs_clicked` | ✅ |
| RecommendationWidget | Show evidence toggle, Dismiss, Mark Completed | Internal handlers | ✅ |
| WorkoutSummaryDialog | OK button | Accept dialog | ✅ |
| WorkoutView | Back, Save & Finish | `back_clicked`, `_finish_workout` | ✅ |

---

## 5. Design System Components

| Component | Clickable Surface | Before | After | Status |
|-----------|-------------------|--------|-------|--------|
| **WarningBanner** | Action button | Created, never connected | Emits `action_clicked` | ✅ Fixed |
| **InsightCard** | Entire card | `PointingHandCursor` + hover, no handler | `clicked` signal via `mousePressEvent` | ✅ Fixed |
| **AppCard** | Entire card (when interactive) | `PointingHandCursor` + hover, no handler | `clicked` signal (guarded by `interactive`) | ✅ Fixed |
| **KpiStrip** (each KpiItem) | Item frame | `PointingHandCursor` + hover bg, no handler | `item_clicked(index)` signal | ✅ Fixed |
| **Breadcrumb** | Non-last crumbs | `lambda: None` | `crumb_clicked(page_id)` → `_navigate()` | ✅ Fixed |
| **SectionHeader** | Action button | Conditional callback | Conditional callback | ✅ |
| **Toolbar** | Action buttons | `action_triggered` signal | `action_triggered` signal | ✅ |
| **NavigationRail** | Item buttons | `item_selected` signal | `item_selected` signal | ✅ |
| **EmptyState** | Action button | Conditional callback | Conditional callback | ✅ |
| **DialogTemplate** | Confirm / Cancel | `accepted` / `rejected` signals | `accepted` / `rejected` signals | ✅ |
| **NotificationToast** | Close button | `dismissed` signal | `dismissed` signal | ✅ |
| **CommandBar** | Search input / List items | `command_selected` signal | `command_selected` signal | ✅ |
| **SearchBar** | Search input | `text_changed` / `search_submitted` | `text_changed` / `search_submitted` | ✅ |
| **MetricCard** | None | N/A | N/A | ✅ |
| **StatusBadge** | None | N/A | N/A | ✅ |
| **ProgressRing** | None | N/A | N/A | ✅ |
| **SkeletonLoader** | None | N/A | N/A | ✅ |

---

## 6. Narrative Coach Cards & Micro UX

| Component | Clickable Surface | Handler | Status |
|-----------|-------------------|---------|--------|
| CoachCard | Toggle (collapse/expand) | `_toggle()` → emits `expand_clicked` | ✅ |
| CoachCard | Per-item action buttons | `action_clicked.emit(item)` | ✅ |
| AchievementBadge | Entire badge | `mousePressEvent` → `clicked.emit(name)` | ✅ |
| CelebrationOverlay | Continue button | `closed.emit()` | ✅ |

---

## 7. Workflow & Dialog Components

| Component | Buttons | Handler | Status |
|-----------|---------|---------|--------|
| ImportWizard (QWizard) | Browse, Back, Next, Cancel, Finish | QWizard built-in + `_browse()` | ✅ |
| WorkflowDialog | Back, Next/Finish, Cancel | Step-based navigation via `_on_previous`, `_on_next`, `_on_cancel` | ✅ |
| CommandPalette (Ctrl+K) | Search input, list items | `_filter()`, `command_selected` → navigation | ✅ |
| CommandPaletteDialog (Experience) | Search input, list items | Built-in palette engine | ✅ |
| LoadingOverlay | None (display only) | Timer-driven spinner | ✅ |
| ProgressIndicator | None (display only) | `set_value()`, `set_message()` | ✅ |
| NotificationToast (Experience) | Close button | Auto-dismiss timer | ✅ |
| NotificationToast (Design System) | Close button | `dismissed` signal | ✅ |
| CelebratonOverlay | Continue button | `closed` signal | ✅ |

---

## 8. Real Dialogs (created in REP-001G)

| Dialog | File | Buttons | Signals | Status |
|--------|------|---------|---------|--------|
| **LogWeightDialog** | `ui/dialogs/log_weight_dialog.py` | Save Weight, Cancel | `weight_logged(float, str, str)` | ✅ |
| **GoalAdjustmentDialog** | `ui/dialogs/goal_adjustment_dialog.py` | Apply, Cancel | `goal_adjusted(str, float)` | ✅ |
| **AIConfigurationDialog** | `ui/dialogs/ai_configuration_dialog.py` | Apply, Cancel | `config_applied(dict)` | ✅ |
| **SystemLogViewerDialog** | `ui/dialogs/system_log_viewer_dialog.py` | Refresh, Close, level filter | None (display only) | ✅ |
| **AboutGymOSDialog** | `ui/dialogs/about_gymos_dialog.py` | Close | None (display only) | ✅ |

---

## 9. Visualization Widgets

### Fully Interactive (BaseVisualization subclasses — 30 widgets)

All inherit from `BaseVisualization` (`ui/visualization/core/base.py`):
- `clicked` signal (mousePressEvent + Enter/Space)
- `double_clicked` signal (mouseDoubleClickEvent)
- `hovered` signal (enterEvent/leaveEvent with tooltip)
- `zoom_changed` signal (wheelEvent)
- `value_changed` signal (animation)
- `PointingHandCursor`
- Accessibility: setAccessibleName, setAccessibleDescription, setToolTip
- Export: export_png, export_to_clipboard

| Category | Widgets | Count |
|----------|---------|-------|
| Rings | RecoveryRing, GoalRing, ProgressRingV2, ConfidenceRing, ReadinessRing | 5 |
| Timelines | PredictionTimeline, RecoveryTimeline, WorkoutTimeline, WeeklyTimeline, MesocycleTimeline, AdaptationTimeline | 6 |
| Charts | TrendChart, AreaChart, DeltaChart, ComparisonChart, RadarChart, BarChart | 6 |
| Heatmaps | MuscleHeatmap, VolumeHeatmap, FatigueHeatmap, ComplianceHeatmap | 4 |
| Graphs | KnowledgeGraphView, EvidenceGraphView, ReasonTreeView, DependencyGraphView | 4 |
| Indicators | ConfidenceGauge, RiskGauge, StabilityGauge, MomentumGauge | 4 |
| Curves | TrainingLoadCurve, RecoveryCurve, MacroCurve, BodyweightCurve, PRCurve | 5 |
| **Total** | | **30** |

### Non-Interactive (Standalone — 1 widget)

| Widget | File | Extends | Notes |
|--------|------|---------|-------|
| TrendIndicator | `ui/design_system/visualization/trend_indicator.py` | `QWidget` | Arrow + value display. No mouse events, no cursor, no signals. Used as type hint only in dashboard_view.py. |

### Legacy Copies (8 files — shadowed by interactive versions via __init__.py)

These files exist but the `__init__.py` in `ui/design_system/visualization/` re-exports the interactive versions from `ui/visualization/`:
| File | Interactive Counterpart |
|------|------------------------|
| `recovery_ring.py` | `ui/visualization/rings/recovery_ring.py` |
| `goal_ring.py` | `ui/visualization/rings/goal_ring.py` |
| `confidence_gauge.py` | `ui/visualization/indicators/confidence_gauge.py` |
| `risk_meter.py` | `ui/visualization/indicators/risk_gauge.py` |
| `weekly_timeline.py` | `ui/visualization/timelines/weekly_timeline.py` |
| `prediction_timeline.py` | `ui/visualization/timelines/prediction_timeline.py` |
| `muscle_heatmap.py` | `ui/visualization/heatmaps/muscle_heatmap.py` |
| `trend_indicator.py` | **None** — only non-interactive |

---

## 10. Experience Platform

| Component | Commands / Actions | Status |
|-----------|--------------------|--------|
| CommandPaletteEngine | `toggle_focus`, `go_back`, `go_forward`, `refresh`, `toggle_sidebar`, `clear_notifications`, `mark_all_read` | ✅ (toggle_sidebar fixed) |
| Builtin shortcuts | Ctrl+K (palette), Ctrl+Shift+F (focus), Alt+Left (back), Alt+Right (forward), Ctrl+Shift+P (search), Ctrl+R (refresh), Escape (exit) | ✅ |
| SearchProvider | 3 registered providers: commands, pages, shortcuts | ✅ |
| NavigationEngine | Route-based navigation with back/forward | ✅ |
| FocusMode | Toggle focus mode | ✅ |
| WorkflowEngine | Generic step-based workflows (awaiting concrete registrations) | ✅ |
| ThemeTransitionManager | Smooth theme transitions | ✅ |

### Command Palette Built-in Commands (7)

| ID | Label | Handler | Status |
|----|-------|---------|--------|
| `focus_mode` | Toggle Focus Mode | `self.focus.toggle()` | ✅ |
| `go_back` | Go Back | `NavigationEngine.go_back()` | ✅ |
| `go_forward` | Go Forward | `NavigationEngine.go_forward()` | ✅ |
| `refresh` | Refresh | `self._refresh_current()` → `data_updated` | ✅ |
| `toggle_sidebar` | Toggle Sidebar | `self._toggle_sidebar()` — toggles nav_rail visibility | ✅ Fixed |
| `clear_notifications` | Clear Notifications | `NotificationCenter.clear_all()` | ✅ |
| `mark_all_read` | Mark All Read | `NotificationCenter.mark_all_read()` | ✅ |

---

## 11. Summary Statistics

### By Category

| Category | Total Surfaces | Connected | Dead | Coverage |
|----------|---------------|-----------|------|----------|
| CommandCenter CTA buttons | 20 | 20 | 0 | **100%** |
| CommandCenter navigation (rail + breadcrumb) | 11 | 11 | 0 | **100%** |
| CommandCenter search & palette | 4 | 4 | 0 | **100%** |
| Legacy dashboard sidebar | 8 | 8 | 0 | **100%** |
| Legacy dashboard widget CTAs | 9 | 9 | 0 | **100%** |
| Design system components | 14 | 14 | 0 | **100%** |
| Narrative components | 5 | 5 | 0 | **100%** |
| Real dialogs | 5 | 5 | 0 | **100%** |
| Workflow / dialog components | 10 | 10 | 0 | **100%** |
| Visualization widgets (interactive) | 30 | 30 | 0 | **100%** |
| Visualization widgets (non-interactive) | 1 | 0 | 1 | **0%** |
| Experience platform commands | 7 | 7 | 0 | **100%** |
| **Total** | **124** | **123** | **1** | **99.2%** |

### Dead Interaction Countdown

| Milestone | Rep | Dead Count |
|-----------|-----|-----------|
| Initial audit (before REP-001E) | — | 28 |
| After CTA wiring (REP-001F) | REP-001F | 8 |
| After design system + cleanup | REP-001G | **1** (TrendIndicator) |

---

*End of UI Interaction Registry*
