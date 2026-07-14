# REP-006A.5: Design System Consolidation Audit

**Status:** Draft · **Auditor:** opencode · **Date:** 2026-07-14  
**Prerequisite:** REP-006A (Visual Foundation Audit) — completed, score 3.5/10  
**Next:** REP-006B (Migration Execution)

---

## Executive Summary

The codebase has **three parallel visualization trees** and a **command center with its own theme** — all implementing the same UI concepts (rings, timelines, gauges, heatmaps, cards, trends) with zero code sharing. This produces 50+ widget source files for ~10 distinct UI concepts.

| Tree | Location | Count | Base Class | Token System |
|------|----------|-------|------------|--------------|
| Classic visualizations | `ui/visualization/` | 25+ files | `BaseVisualization` (QFrame) | Color, Motion, Radius tokens |
| Design system | `ui/design_system/visualization/` | 9 files | `QFrame` (raw) | Color, Radius tokens |
| Design system components | `ui/design_system/components/` | 16 files | `QFrame`/`QWidget` | Color tokens |
| Command center | `ui/command_center/visualization/` | 8 files | `QFrame` (raw) | `C.*` custom constants |
| Dashboard inline | Various pages | scattered | `QFrame` | Inline colors |

**Target:** 1 canonical component per UI concept → 10 canonical files, 40+ files deprecated.

---

## Component-by-Component Analysis

### 1. Ring / Progress Ring

| File | Class(es) | Base | Animation | Tokens | Notes |
|------|-----------|------|-----------|--------|-------|
| `ds/visualization/goal_ring.py` | `GoalRing` | QFrame | No | Color | paintEvent, fixed size 140 |
| `ds/visualization/recovery_ring.py` | `RecoveryRing` | QFrame | No | Color, Radius | paintEvent, fixed size 120 |
| `ds/components/progress_ring.py` | `ProgressRing` | QFrame | No | Color | paintEvent, fixed size 100 |
| `viz/rings/goal_ring.py` | `GoalRing` | BaseVisualization | Yes | Color, Motion, Radius | animate(), hover/click/zoom |
| `viz/rings/recovery_ring.py` | `RecoveryRing` | BaseVisualization | Yes | Color, Motion, Radius | animate(), hover/click/zoom |
| `viz/rings/confidence_ring.py` | `ConfidenceRing` | BaseVisualization | Yes | Color, Motion, Radius | animate(), hover/click/zoom |
| `viz/rings/readiness_ring.py` | `ReadinessRing` | BaseVisualization | Yes | Color, Motion, Radius | animate(), hover/click/zoom |
| `viz/rings/progress_ring_v2.py` | `ProgressRingV2` | BaseVisualization | Yes | Color, Motion, Radius | animate(), hover/click/zoom |
| `cc/visualization/progress_ring.py` | `ProgressRing` | QFrame | No | C.* (own) | no tokens |

**CANONICAL KEEP:** `ui/visualization/rings/` (BaseVisualization variants)  
**DEPRECATE:** All `ds/visualization/goal_ring.py`, `ds/visualization/recovery_ring.py`, `ds/components/progress_ring.py`, `cc/visualization/progress_ring.py`  
**Rationale:** The `BaseVisualization` variants provide animation, hover/click/zoom interaction, accessibility, and export out of the box. The design system ring files are impoverished copies that lack all of this. An `AbstractRing` base class should be extracted into `ds/visualization/` to standardize the API.

---

### 2. Timeline

| File | Class(es) | Base | Approach | Tokens |
|------|-----------|------|----------|--------|
| `ds/visualization/timeline_widget.py` | `TimelineWidget` | QFrame | Horizontal bar timeline (paintEvent) | Color, Radius |
| `ds/visualization/prediction_timeline.py` | `PredictionTimeline` | QFrame | Line chart timeline (paintEvent) | Color, Radius |
| `ds/visualization/weekly_timeline.py` | `WeeklyTimeline` | QFrame | Bar chart timeline (paintEvent) | Color, Radius |
| `viz/timelines/workout_timeline.py` | `WorkoutTimeline` | BaseVisualization | paintEvent with animation | Color, Motion, Radius |
| `viz/timelines/weekly_timeline.py` | `WeeklyTimeline` | BaseVisualization | Bar chart (paintEvent) | Color, Motion, Radius |
| `viz/timelines/recovery_timeline.py` | `RecoveryTimeline` | BaseVisualization | Line chart (paintEvent) | Color, Motion, Radius |
| `viz/timelines/prediction_timeline.py` | `PredictionTimeline` | BaseVisualization | Line chart (paintEvent) | Color, Motion, Radius |
| `viz/timelines/mesocycle_timeline.py` | `MesocycleTimeline` | BaseVisualization | Gantt-style (paintEvent) | Color, Motion, Radius |
| `viz/timelines/adaptation_timeline.py` | `AdaptationTimeline` | BaseVisualization | paintEvent | Color, Motion, Radius |
| `cc/visualization/timeline.py` | `TimelineWidget` | QFrame | Scroll-based QWidget list | C.* (own) |

**CANONICAL KEEP:** `ui/visualization/timelines/` (BaseVisualization variants)  
**DEPRECATE:** All `ds/visualization/timeline_widget.py`, `ds/visualization/prediction_timeline.py`, `ds/visualization/weekly_timeline.py`, `cc/visualization/timeline.py`  
**Rationale:** Same as rings — `BaseVisualization` variants are strictly more capable. The `ds/` painter-based timelines offer nothing that the `viz/` ones don't already provide better.

---

### 3. Gauge / Confidence

| File | Class(es) | Base | Approach | Tokens |
|------|-----------|------|----------|--------|
| `ds/visualization/confidence_gauge.py` | `ConfidenceGauge` | QFrame | Horizontal bar (paintEvent) | Color, Radius |
| `ds/visualization/gauge_widget.py` | `GaugeWidget` | QFrame | paintEvent | Color |
| `viz/indicators/confidence_gauge.py` | `ConfidenceGauge` | BaseVisualization | paintEvent with animation | Color, Motion, Radius |
| `viz/indicators/stability_gauge.py` | `StabilityGauge` | BaseVisualization | paintEvent with animation | Color, Motion, Radius |
| `viz/indicators/risk_gauge.py` | `RiskGauge` | BaseVisualization | paintEvent with animation | Color, Motion, Radius |
| `viz/indicators/momentum_gauge.py` | `MomentumGauge` | BaseVisualization | paintEvent with animation | Color, Motion, Radius |
| `cc/visualization/confidence_indicator.py` | `ConfidenceIndicator` + `ConfidenceBar` | QFrame | Widget composition | C.* (own) |

**CANONICAL KEEP:** `ui/visualization/indicators/` (BaseVisualization variants)  
**DEPRECATE:** `ds/visualization/confidence_gauge.py`, `ds/visualization/gauge_widget.py`, `cc/visualization/confidence_indicator.py`  
**Rationale:** The `ds/` gauge files are simple horizontal bars; the `viz/` indicators include animated circular gauges, risk gauges, stability gauges, and momentum gauges with full interaction. `ConfidenceIndicator` and `ConfidenceBar` can be replaced by `ConfidenceGauge` from `viz/` with a thin adapter.

---

### 4. Heatmap

| File | Class(es) | Base | Approach | Tokens |
|------|-----------|------|----------|--------|
| `ds/visualization/heatmap_widget.py` | `HeatmapWidget` | QFrame | Grid heatmap (paintEvent) | Color |
| `ds/visualization/muscle_heatmap.py` | `MuscleHeatmap` | QFrame | Horizontal bar heatmap (paintEvent) | Color, Radius |
| `viz/heatmaps/volume_heatmap.py` | `VolumeHeatmap` | BaseVisualization | paintEvent | Color, Motion, Radius |
| `viz/heatmaps/muscle_heatmap.py` | `MuscleHeatmap` | BaseVisualization | paintEvent | Color, Motion, Radius |
| `viz/heatmaps/fatigue_heatmap.py` | `FatigueHeatmap` | BaseVisualization | paintEvent | Color, Motion, Radius |
| `viz/heatmaps/compliance_heatmap.py` | `ComplianceHeatmap` | BaseVisualization | paintEvent | Color, Motion, Radius |
| `cc/visualization/heatmap.py` | `HeatmapWidget` | QFrame | Grid heatmap (paintEvent) | C.* (own) |

**CANONICAL KEEP:** `ui/visualization/heatmaps/` (BaseVisualization variants)  
**DEPRECATE:** `ds/visualization/heatmap_widget.py`, `ds/visualization/muscle_heatmap.py`, `cc/visualization/heatmap.py`  
**Rationale:** The `ds/` heatmap widgets are limited subsets of the `viz/` variants. `cc/visualization/heatmap.py` paints a color grid with hardcoded RGB; the `viz/` variants use token colors with animation.

---

### 5. Trend Indicator

| File | Class(es) | Base | Approach | Tokens |
|------|-----------|------|----------|--------|
| `ds/visualization/trend_indicator.py` | `TrendIndicator` | QWidget | QLabel icon + value | Color |
| `viz/indicators/trend_indicator.py` | `TrendIndicator` | QFrame | paintEvent with arrow | Color, Motion, Radius |
| `cc/visualization/trend_chart.py` | `TrendChart` + `_ChartCanvas` | QFrame | Mini sparkline with filled area | C.* (own) |
| `cc/timeline.py` (inline) | Inline trend labels | QLabel | Text-based arrow | C.* (own) |

**DUAL KEEP:** Both `ds/visualization/trend_indicator.py` (lightweight) and `viz/indicators/trend_indicator.py` are valid for different use cases.  
**DEPRECATE:** `cc/visualization/trend_chart.py` (replace with `viz/indicators/trend_indicator.py` or `viz/charts/trend_chart.py`)  
**Rationale:** The lightweight `TrendIndicator` (QLabel-based) is appropriate for inline use in cards. The `BaseVisualization` variant is better for standalone panels. These are complementary, not duplicative. However, `TrendChart` in command center duplicates `viz/charts/trend_chart.py`.

---

### 6. Card Components

| File | Class(es) | Base | Approach | Tokens |
|------|-----------|------|----------|--------|
| `ds/components/app_card.py` | `AppCard` | QFrame | styleSheet, composable content | Color, Radius, Spacing |
| `ds/components/metric_card.py` | `MetricCard` | QFrame | styleSheet, metric-specific slots | Color, Radius, Spacing |
| `ds/components/insight_card.py` | `InsightCard` | QFrame | styleSheet, insight-specific slots | Color, Radius, Spacing |
| `ds/layout/editorial_grid.py` | `SectionPanel`, `HeroPanel`, `MetricPanel` | QFrame | styleSheet, grid-aware containers | Color, Radius, Spacing |
| `dashboard/base_card.py` | `DashboardCard` | QFrame | styleSheet, header+body slots | Inline colors |
| `cc/visualization/prediction_card.py` | `PredictionCard` | QFrame | styleSheet, fixed size 240x130 | C.* (own) |

**CANONICAL KEEP:** `ui/design_system/components/app_card.py` (general) + `metric_card.py` + `insight_card.py` (specific) + `ui/design_system/layout/editorial_grid.py` (containers)  
**DEPRECATE:** `ui/dashboard/dashboard_widgets/base_card.py` (migrate to `AppCard`), `cc/visualization/prediction_card.py` (migrate to `AppCard` + `MetricCard`)  
**Rationale:** The design system cards are the most mature, using proper tokens. `DashboardCard` is a poor copy. `PredictionCard` is a fixed-size widget that should become a composition of `AppCard` + `TrendIndicator` + `MetricCard`.

---

### 7. Risk / Stability Meters

| File | Class(es) | Base | Approach | Tokens |
|------|-----------|------|----------|--------|
| `ds/visualization/risk_meter.py` | `RiskMeter` | QFrame | Segmented bar (paintEvent) | Color, Radius |
| `viz/indicators/risk_gauge.py` | `RiskGauge` | BaseVisualization | paintEvent with animation | Color, Motion, Radius |
| `viz/indicators/stability_gauge.py` | `StabilityGauge` | BaseVisualization | paintEvent with animation | Color, Motion, Radius |
| `viz/indicators/momentum_gauge.py` | `MomentumGauge` | BaseVisualization | paintEvent with animation | Color, Motion, Radius |

**CANONICAL KEEP:** `viz/indicators/` variants  
**DEPRECATE:** `ds/visualization/risk_meter.py`  
**Rationale:** `RiskMeter` is a simpler segmented bar; the `viz/` risk/stability gauges provide the same functionality with animation and interaction.

---

### 8. Base Visualization Class

| File | Class | Features |
|------|-------|----------|
| `viz/core/base.py` | `BaseVisualization` | QFrame, animation, hover/click/zoom/keyboard, export PNG/clipboard, accessibility, reduced-motion, value/color helpers |
| `ds/visualization/*.py` | (none) | No shared base — each reinvents paintEvent and styling |
| `cc/visualization/*.py` | (none) | No shared base — each uses C.* constants directly |

**CANONICAL KEEP:** `ui/visualization/core/base.py`  
**MIGRATE TARGET:** All `ds/visualization/` widgets should either (a) extend `BaseVisualization` or (b) be replaced by the `viz/` equivalent.  
**Rationale:** `BaseVisualization` provides animation, interaction, accessibility, and export in ~200 lines. The design system widgets each reimplement their own paintEvent with zero shared infrastructure.

---

## Migration Plan

### Phase 1: Adapter Layer (Week 1–2)
- Create adapter wrappers in `ui/design_system/visualization/` that re-export `viz/` widgets with the design system import paths.
- Example: `ds/visualization/goal_ring.py` → `from ui.visualization.rings.goal_ring import GoalRing; GoalRing = GoalRing`
- Add deprecation warning `warnings.warn("Import from ui.visualization.rings instead", DeprecationWarning)`.
- No functional changes — all existing imports continue to work.

### Phase 2: Migrate Consumers (Week 3–4)
- Update all page-level imports from `ds/visualization/` to `viz/` equivalents.
- Update `DashboardCard` → `AppCard` usage in dashboard code.
- Update `cc/visualization/` references to either `ds/components/` or `viz/` variants.
- Audit each consumer for API compatibility (e.g., `GoalRing.set_goal()` vs `GoalRing.set_data()`).

### Phase 3: Remove Deprecated Files (Week 5)
- Delete adapter shims.
- Delete `cc/visualization/` redundant files.
- Delete `ui/dashboard/dashboard_widgets/base_card.py`.
- Rename `ui/visualization/` → `ui/design_system/visualization/` (absorb into design system tree).

### API Standardization Targets

| Concept | Canonical File | Required Methods | Status |
|---------|---------------|-------------------|--------|
| Ring | `viz/rings/goal_ring.py` | `set_goal(current, target, label, unit)` | Exists |
| Ring | `viz/rings/recovery_ring.py` | `set_value(value, max_value, label, sub_label)` | Exists |
| Timeline | `viz/timelines/prediction_timeline.py` | `set_data(points, goal_line)` | Exists |
| Gauge | `viz/indicators/confidence_gauge.py` | `set_confidence(value, label)` | Exists |
| Heatmap | `viz/heatmaps/muscle_heatmap.py` | `set_data(muscles, max_volume)` | Exists |
| Trend | `ds/visualization/trend_indicator.py` | `set_trend(trend, value)` | Exists |
| Card | `ds/components/app_card.py` | `set_header(title, subtitle)`, `set_body(widget)`, `set_footer(widget)` | Needs method audit |
| Section | `ds/layout/section_panel.py` | `add_content(widget)`, `clear()` | Exists |

---

## Appendix: Full File Inventory

### `ui/visualization/` (KEEP — 25 files)
- `core/base.py` — BaseVisualization (keep)
- `core/utils.py` — utility functions (keep)
- `rings/` — GoalRing, ConfidenceRing, RecoveryRing, ReadinessRing, ProgressRingV2 (keep)
- `timelines/` — WorkoutTimeline, WeeklyTimeline, RecoveryTimeline, PredictionTimeline, MesocycleTimeline, AdaptationTimeline (keep)
- `curves/` — TrainingLoadCurve, RecoveryCurve, PRCurve, MacroCurve, BodyweightCurve (keep)
- `charts/` — DeltaChart, ComparisonChart, BarChart, AreaChart, TrendChart, RadarChart (keep)
- `indicators/` — StabilityGauge, RiskGauge, MomentumGauge, ConfidenceGauge, TrendIndicator (keep)
- `heatmaps/` — VolumeHeatmap, MuscleHeatmap, FatigueHeatmap, ComplianceHeatmap (keep)
- `graphs/` — ReasonTreeView, KnowledgeGraphView, EvidenceGraphView, DependencyGraphView (keep)
- `gallery/` — GalleryPage (keep)

### `ui/design_system/visualization/` (DEPRECATE — 9 files, migrate to adapter phase)
- `timeline_widget.py` → superseded by `viz/timelines/`
- `weekly_timeline.py` → superseded by `viz/timelines/`
- `prediction_timeline.py` → superseded by `viz/timelines/`
- `trend_indicator.py` → KEEP as lightweight variant
- `confidence_gauge.py` → superseded by `viz/indicators/`
- `gauge_widget.py` → superseded by `viz/indicators/`
- `risk_meter.py` → superseded by `viz/indicators/`
- `goal_ring.py` → superseded by `viz/rings/`
- `recovery_ring.py` → superseded by `viz/rings/`
- `muscle_heatmap.py` → superseded by `viz/heatmaps/`
- `heatmap_widget.py` → superseded by `viz/heatmaps/`

### `ui/design_system/components/` (KEEP — 16 files)
- `app_card.py`, `metric_card.py`, `insight_card.py` — canonical card components
- `section_header.py` — canonical header (fix set_title/set_subtitle no-op bug)
- `status_badge.py`, `empty_state.py`, `skeleton_loader.py` — utility components
- `progress_ring.py` → DEPRECATE (superseded by `viz/rings/`)
- `dialog_template.py`, `command_bar.py`, `search_bar.py`, `sidebar_item.py`, `navigation_rail.py`, `toolbar.py`, `warning_banner.py`, `notification_toast.py`, `activity_feed.py`, `chart_container.py` — keep

### `ui/command_center/visualization/` (DEPRECATE — 8 files)
- All files migrate to design system equivalents
- `prediction_card.py` → `AppCard` + `MetricCard` + `TrendIndicator`
- `confidence_indicator.py` → `viz/indicators/ConfidenceGauge`
- `heatmap.py` → `viz/heatmaps/`
- `progress_ring.py` → `viz/rings/`
- `timeline.py` → `viz/timelines/`
- `trend_chart.py` → `viz/charts/TrendChart` or `viz/indicators/TrendIndicator`
- `relationship_graph.py` → keep as unique (graph visualization not in design system)

### `ui/dashboard/dashboard_widgets/` (DEPRECATE — 1 file)
- `base_card.py` → migrate to `AppCard`

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Command center depends on `C.*` theme constants | All CC widgets break if swapped | Create a `C` → token adapter in Phase 1 |
| Page-level imports use scattered import paths | Migration touches 30+ page files | Use grep to catalog all imports before Phase 2 |
| API mismatch between `set_goal()` and `set_data()` naming | Silent regressions | Write adapter wrappers that normalize to a standard `set_data()` signature |
| `BaseVisualization` requires a11y manager | Missing dependency in some consumers | Make a11y registration optional (try/except) — already handled in `base.py:166-178` |

---

## Verification

After Phase 3:
```bash
# No files remaining in deprecated locations
Test-Path "ui/dashboard/dashboard_widgets/base_card.py"  # → False
# Canonical files intact
Test-Path "ui/visualization/core/base.py"  # → True
# All design system visualizations re-export from viz/
python -c "from ui.design_system.visualization import *"  # → no ImportError
```

Score target after consolidation: **8.5/10** (gains: +2 for consolidation, +1 for eliminated dead code, +1 for adapter layer, +1 for import clarity).
