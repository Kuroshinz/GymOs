# RFC-034: Design System 3.0 — Production-Grade Component Library

**Status:** IMPLEMENTATION  
**Priority:** CRITICAL  
**Author:** Design System Team  
**Date:** 2026-07-14  
**Supersedes:** REP-006A5, RFC-030, RFC-031  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Component Hierarchy](#2-component-hierarchy)
3. [Dependency Graph](#3-dependency-graph)
4. [Canonical Components](#4-canonical-components)
5. [Deprecated Components](#5-deprecated-components)
6. [Migration Table](#6-migration-table)
7. [Token Usage Audit](#7-token-usage-audit)
8. [Accessibility Audit](#8-accessibility-audit)
9. [Responsive Audit](#9-responsive-audit)
10. [Duplication Analysis](#10-duplication-analysis)
11. [Implementation Checklist](#11-implementation-checklist)

---

## 1. Executive Summary

GymOS has grown a rich but fragmented design system across four directories:

| Directory | Files | Components |
|-----------|-------|------------|
| `ui/design_system/components/` | 18 | AppCard, InsightCard, MetricCard, StatusBadge, SectionHeader, EmptyState, ChartContainer, DialogTemplate, SkeletonLoader, NotificationToast, WarningBanner, ActivityFeed, CommandBar, NavigationRail, SearchBar, SidebarItem, Toolbar, ProgressRing |
| `ui/design_system/layout/` | 3 | EditorialGrid, KpiStrip, ScrollContainer |
| `ui/design_system/visualization/` | 8 | GoalRing, RecoveryRing, WeeklyTimeline, PredictionTimeline, ConfidenceGauge, MuscleHeatmap, RiskMeter, TrendIndicator |
| `ui/visualization/` | ~30+ | Rings (5), Timelines (6), Charts (6), Heatmaps (4), Indicators (4), Graphs (4), Curves (5), Core (2) |
| `ui/narrative/` | 3+ | CoachCard, CoachCardStack, MicroUX, CelebrationOverlay, AchievementBadge, MilestoneIndicator |
| `ui/shell/` | 3 | AppShell, ShellHeader, ShellSidebar |

**Key Findings:**

1. **~40% duplication** across card, ring, gauge, and timeline families
2. **33 components use raw CSS literals** instead of design tokens
3. **24 components lack accessibility metadata** (accessible name/description)
4. **3 lazy-import re-export chains** create implicit circular dependencies
5. **2 identical implementations** of GoalRing, RecoveryRing exist in different directories
6. **ShellSidebar duplicates** NavigationRail/SidebarItem patterns
7. **Multiple panel/card types** overlap in API and purpose

---

## 2. Component Hierarchy

### Foundation Layer (Tokens)
```
TypographyTokens → font_style()
SpacingTokens   → spacing_step() + semantic spacing properties
RadiusTokens    → radius_to_px(), px_from_token()
ColorTokens     → color_from_scheme(), resolve_alpha()
DarkColorTokens → (dark variant)
HighContrastColorTokens → (a11y variant)
ElevationTokens → apply_elevation(), elevation_style()
GlowTokens      → glow_effect()
MotionTokens    → easing_style()
MotionCurves    → (curve definitions)
IconTokens      → (icon size definitions)
LayoutTokens    → breakpoint()
```

### Layout Layer
```
ScrollContainer
    - Scrollable page container with styled scrollbars
    
ContentGrid
    - Grid system (12-column based)
    ├── EditorialGrid
    │   ├── add_panel(widget, span)
    │   ├── add_section(section)
    │   └── add_row(sections)
    ├── KpiStrip
    │   └── KpiItem[]
    └── PanelSpan (FULL, HALF, THIRD, TWO_THIRDS, QUARTER, HERO)
```

### Surface Layer (Containers)
```
Card (WIP - merging AppCard + InsightCard + SectionPanel)
    ├── AppCard (retain as generic)
    │   - title, subtitle, badge, elevated, interactive
    │   - add_content(), add_layout()
    ├── MetricCard
    │   - label, value, unit, icon, trend
    │   - set_value(), set_trend()
    └── SectionPanel (retain for EditorialGrid)
        - title, subtitle, span
        - add_content(), add_layout(), clear()

ChartContainer
    - title, subtitle
    - set_chart(), clear_chart()

Dialog
    └── DialogTemplate
        - title, message, confirm/cancel
        - confirm(), add_content()

Toast
    └── NotificationToast
        - message, title, type, duration
        - auto-dismiss, dismissable
```

### Information Layer
```
StatusBadge
    - text, level (SUCCESS/WARNING/ERROR/INFO/NEUTRAL)
    - outlined variant
    - set_level(), set_text()

Badge (ALIAS → StatusBadge)

EmptyState
    - icon, title, message, action
    - set_message()

WarningBanner
    - icon, message, action, level
    - action_clicked signal

ActivityFeed / ActivityItem
    - title, items[]
    - set_items()

CoachCard / CoachCardStack (narrative)
    - narrative expansion, action items
    - expand_clicked, action_clicked signals

HeroPanel (layout - editorial use)
    - title, subtitle, accent_color
    - add_content()
```

### Action Layer
```
PrimaryButton (STUB - use QPushButton with theme.css)
SecondaryButton (STUB - use QPushButton with theme.css)
GhostButton (STUB - use QPushButton with theme.css)
IconButton (STUB - use QPushButton with theme.css)

Toolbar
    - title, actions[]
    - action_triggered signal

CommandBar
    - placeholder, commands[]
    - command_selected, dismissed signals
    - show_command_bar(), hide_command_bar()

SearchBar
    - placeholder, shortcut_hint
    - text_changed, search_submitted signals
```

### Feedback Layer
```
StatusBadge → [already listed above]
NotificationToast → [already listed above]
WarningBanner → [already listed above]

SkeletonLoader / SkeletonBlock
    - lines, line_height, last_line_width
    - animated progress property

ProgressRing (deprecated → use ui/visualization rings)
```

### Chart Layer (ui/visualization/charts/ + timelines)
```
CAR Chart Layer:
    BaseVisualization
        ├── TrendChart (line)
        ├── AreaChart (filled area)
        ├── BarChart (horizontal/vertical)
        ├── RadarChart (spider)
        ├── ComparisonChart (grouped bars)
        └── DeltaChart (up/down bars)

Timeline Layer (ui/visualization/timelines/):
    ├── WeeklyTimeline (day bars)
    ├── WorkoutTimeline (exercise sequence)
    ├── RecoveryTimeline (recovery over time)
    ├── PredictionTimeline (forecast line)
    ├── MesocycleTimeline (block planning)
    └── AdaptationTimeline (long-term trends)

Ring Layer (ui/visualization/rings/):
    ├── GoalRing (goal progress)
    ├── RecoveryRing (recovery status)
    ├── ConfidenceRing (prediction confidence)
    ├── ProgressRingV2 (generic ring)
    └── ReadinessRing (readiness gauge)

Gauge Layer (ui/visualization/indicators/):
    ├── ConfidenceGauge (horizontal bar)
    ├── RiskGauge (segmented risk)
    ├── MomentumGauge (trend momentum)
    └── StabilityGauge (variance display)

Heatmap Layer (ui/visualization/heatmaps/):
    ├── MuscleHeatmap
    ├── VolumeHeatmap
    ├── FatigueHeatmap
    └── ComplianceHeatmap
```

### Shell Layer
```
AppShell
    ├── ShellHeader
    │   - page_title, breadcrumb
    │   - palette_triggered, notifications_triggered
    └── ShellSidebar
        - nav sections, expanded/collapsed
        - page_selected signal
        - ShellSidebarButton (per item)

NavigationRail (standalone alternative)
SidebarItem (individual button component)
```

---

## 3. Dependency Graph

```
ui/design_system/tokens/
    ├── color.py  ← no dependencies (standalone)
    ├── spacing.py ← no dependencies
    ├── typography.py ← no dependencies
    ├── radius.py ← no dependencies
    ├── shadow.py ← PySide6 only
    ├── elevation.py ← re-exports from shadow.py
    ├── motion.py ← no dependencies
    ├── icon.py ← no dependencies
    ├── layout.py ← no dependencies
    └── __init__.py ← aggregates all tokens

ui/design_system/components/
    ├── app_card.py ← tokens/color, tokens/elevation, tokens/radius, tokens/spacing
    ├── insight_card.py ← components/status_badge, tokens/color, tokens/radius
    ├── metric_card.py ← tokens/color, tokens/radius, tokens/spacing
    ├── status_badge.py ← tokens/color, tokens/radius
    ├── section_header.py ← tokens/color, tokens/spacing
    ├── empty_state.py ← tokens/color, tokens/spacing
    ├── chart_container.py ← tokens/color, tokens/radius, tokens/spacing
    ├── dialog_template.py ← tokens/color, tokens/elevation, tokens/radius, tokens/spacing
    ├── skeleton_loader.py ← tokens/color, tokens/radius
    ├── notification_toast.py ← tokens/color, tokens/elevation, tokens/radius
    ├── warning_banner.py ← tokens/color, tokens/radius
    ├── activity_feed.py ← tokens/color, tokens/radius
    ├── command_bar.py ← tokens/color, tokens/elevation, tokens/radius, tokens/spacing
    ├── navigation_rail.py ← tokens/color, tokens/layout, tokens/radius, tokens/spacing
    ├── search_bar.py ← tokens/color, tokens/radius, tokens/spacing
    ├── sidebar_item.py ← tokens/color, tokens/radius
    ├── toolbar.py ← tokens/color, tokens/radius, tokens/spacing
    ├── progress_ring.py ← tokens/color
    └── __init__.py ← aggregates all components

ui/design_system/layout/
    ├── editorial_grid.py ← tokens/color, tokens/radius, tokens/spacing
    ├── kpi_strip.py ← tokens/color, tokens/radius, tokens/spacing
    ├── scroll_container.py ← tokens/color
    └── __init__.py ← aggregates layouts

ui/design_system/visualization/
    ├── goal_ring.py ← tokens/color
    ├── recovery_ring.py ← tokens/color, tokens/radius
    ├── weekly_timeline.py ← tokens/color, tokens/radius
    ├── prediction_timeline.py ← tokens/color, tokens/radius
    ├── confidence_gauge.py ← tokens/color, tokens/radius
    ├── muscle_heatmap.py ← tokens/color, tokens/radius
    ├── risk_meter.py ← tokens/color, tokens/radius
    ├── trend_indicator.py ← tokens/color
    └── __init__.py ← lazy-loads from ui/visualization/* + TrendIndicator

ui/visualization/core/
    ├── base.py ← tokens/color, tokens/motion, tokens/radius
    └── utils.py ← standalonel

ui/visualization/charts/
    ├── trend_chart.py ← core/base
    ├── area_chart.py ← core/base
    ├── bar_chart.py ← core/base, tokens/radius
    ├── radar_chart.py ← core/base
    ├── comparison_chart.py ← core/base, tokens/radius
    └── delta_chart.py ← core/base

ui/narrative/
    ├── cards.py ← tokens/color, engine.py
    ├── engine.py ← standalonel
    ├── micro.py ← tokens/color
    └── templates/ ← engine.py (11 template modules)

ui/shell/
    ├── app_shell.py ← components/command_bar, components/dialog_template, components/notification_toast, tokens/color, tokens/spacing, shell/header, shell/sidebar
    ├── header.py ← tokens/color, tokens/radius, tokens/spacing
    └── sidebar.py ← tokens/color, tokens/layout, tokens/radius, tokens/spacing
```

---

## 4. Canonical Components

### 4.1 Foundation Tokens (KEEP - already canonical)

| Token File | Status | Notes |
|------------|--------|-------|
| `tokens/color.py` | ✅ CANONICAL | Frozen dataclasses, scheme mapping, resolve_alpha |
| `tokens/spacing.py` | ✅ CANONICAL | Full step scale + semantic aliases |
| `tokens/typography.py` | ✅ CANONICAL | Style template, font_style(), weight map |
| `tokens/radius.py` | ✅ CANONICAL | Full scale + px conversion |
| `tokens/shadow.py` | ✅ CANONICAL | Level mapping, compute_shadow, apply_elevation |
| `tokens/motion.py` | ✅ CANONICAL | Duration, curve, easing_style |
| `tokens/icon.py` | ✅ CANONICAL | Size scale |
| `tokens/layout.py` | ✅ CANONICAL | Breakpoints, container widths |

### 4.2 Layout Components

| Component | File | Status | Notes |
|-----------|------|--------|-------|
| `ScrollContainer` | `layout/scroll_container.py` | ✅ CANONICAL | Complete with scrollbar styling |
| `EditorialGrid` | `layout/editorial_grid.py` | ✅ CANONICAL | 12-column grid system |
| `KpiStrip` | `layout/kpi_strip.py` | ✅ CANONICAL | KPI row with items |
| `SectionPanel` | `layout/editorial_grid.py` | ✅ CANONICAL | Grid section panel |
| `HeroPanel` | `layout/editorial_grid.py` | ✅ CANONICAL | Hero section panel |
| `MetricPanel` | `layout/editorial_grid.py` | ✅ CANONICAL | Metric display panel |

### 4.3 Surface Components

| Component | File | Status | Notes |
|-----------|------|--------|-------|
| `AppCard` | `components/app_card.py` | ✅ CANONICAL | Generic card with header, body, interactive mode |
| `MetricCard` | `components/metric_card.py` | ⚠️ NEEDS FIX | Uses literals, set_value/set_trend need fixing |
| `ChartContainer` | `components/chart_container.py` | ⚠️ NEEDS FIX | Uses literals |
| `DialogTemplate` | `components/dialog_template.py` | ⚠️ NEEDS FIX | Uses literals |
| `CoachCard` | `narrative/cards.py` | ✅ CANONICAL | Narrative card with expand |
| `CoachCardStack` | `narrative/cards.py` | ✅ CANONICAL | Vertical card stack |

### 4.4 Information Components

| Component | File | Status | Notes |
|-----------|------|--------|-------|
| `StatusBadge` | `components/status_badge.py` | ⚠️ NEEDS FIX | Missing accessible name |
| `EmptyState` | `components/empty_state.py` | ⚠️ NEEDS FIX | set_message is stub |
| `SectionHeader` | `components/section_header.py` | ⚠️ NEEDS FIX | set_title/set_subtitle are stubs |
| `WarningBanner` | `components/warning_banner.py` | ⚠️ NEEDS FIX | Missing accessible name |
| `ActivityFeed` | `components/activity_feed.py` | ⚠️ NEEDS FIX | Missing accessible name |
| `InsightCard` | `components/insight_card.py` | ⚠️ REDUNDANT | Overlaps with AppCard + StatusBadge |
| `TrendIndicator` | `visualization/trend_indicator.py` | ✅ CANONICAL | Trend display widget |

### 4.5 Action Components

| Component | File | Status | Notes |
|-----------|------|--------|-------|
| `Toolbar` | `components/toolbar.py` | ⚠️ NEEDS FIX | add/remove_action are stubs |
| `CommandBar` | `components/command_bar.py` | ✅ CANONICAL | Command palette |
| `SearchBar` | `components/search_bar.py` | ⚠️ NEEDS FIX | Missing accessible desc |
| `NavigationRail` | `components/navigation_rail.py` | ✅ CANONICAL | Rail navigation |
| `SidebarItem` | `components/sidebar_item.py` | ✅ CANONICAL | Sidebar button item |

### 4.6 Feedback Components

| Component | File | Status | Notes |
|-----------|------|--------|-------|
| `NotificationToast` | `components/notification_toast.py` | ⚠️ NEEDS FIX | Missing accessible name |
| `SkeletonLoader` | `components/skeleton_loader.py` | ✅ CANONICAL | Skeleton lines |
| `SkeletonBlock` | `components/skeleton_loader.py` | ✅ CANONICAL | Skeleton block |
| `ProgressRing` | `components/progress_ring.py` | ⚠️ REDUNDANT | Superseded by ui/visualization/rings |

### 4.7 Shell Components

| Component | File | Status | Notes |
|-----------|------|--------|-------|
| `AppShell` | `shell/app_shell.py` | ✅ CANONICAL | Main shell layout |
| `ShellHeader` | `shell/header.py` | ⚠️ NEEDS FIX | Missing accessible names |
| `ShellSidebar` | `shell/sidebar.py` | ⚠️ REDUNDANT | Duplicates NavigationRail pattern |
| `ShellSidebarButton` | `shell/sidebar.py` | ⚠️ REDUNDANT | Duplicates SidebarItem pattern |

### 4.8 Chart Components (ui/visualization/charts/)

| Component | File | Status | Notes |
|-----------|------|--------|-------|
| `BaseVisualization` | `core/base.py` | ✅ CANONICAL | Foundation for all charts |
| `TrendChart` | `charts/trend_chart.py` | ✅ CANONICAL | Line chart |
| `AreaChart` | `charts/area_chart.py` | ✅ CANONICAL | Filled area chart |
| `BarChart` | `charts/bar_chart.py` | ⚠️ NEEDS FIX | Minor token issues |
| `RadarChart` | `charts/radar_chart.py` | ✅ CANONICAL | Spider chart |
| `ComparisonChart` | `charts/comparison_chart.py` | ✅ CANONICAL | Grouped bars |
| `DeltaChart` | `charts/delta_chart.py` | ✅ CANONICAL | Up/down bars |

### 4.9 Ring Components (ui/visualization/rings/)

| Component | File | Status | Notes |
|-----------|------|--------|-------|
| `GoalRing` | `rings/goal_ring.py` | ✅ CANONICAL | Goal progress ring |
| `RecoveryRing` | `rings/recovery_ring.py` | ✅ CANONICAL | Recovery status ring |
| `ProgressRingV2` | `rings/progress_ring_v2.py` | ✅ CANONICAL | Generic progress ring |
| `ConfidenceRing` | `rings/confidence_ring.py` | ✅ CANONICAL | Confidence display ring |
| `ReadinessRing` | `rings/readiness_ring.py` | ✅ CANONICAL | Readiness gauge ring |

### 4.10 Timeline Components (ui/visualization/timelines/)

| Component | File | Status | Notes |
|-----------|------|--------|-------|
| `WeeklyTimeline` | `timelines/weekly_timeline.py` | ✅ CANONICAL | Day bars |
| `WorkoutTimeline` | `timelines/workout_timeline.py` | ✅ CANONICAL | Exercise timeline |
| `RecoveryTimeline` | `timelines/recovery_timeline.py` | ✅ CANONICAL | Recovery over time |
| `PredictionTimeline` | `timelines/prediction_timeline.py` | ✅ CANONICAL | Forecast line |
| `MesocycleTimeline` | `timelines/mesocycle_timeline.py` | ✅ CANONICAL | Block planning |
| `AdaptationTimeline` | `timelines/adaptation_timeline.py` | ✅ CANONICAL | Long-term trends |

### 4.11 Gauge Components (ui/visualization/indicators/)

| Component | File | Status | Notes |
|-----------|------|--------|-------|
| `ConfidenceGauge` | `indicators/confidence_gauge.py` | ✅ CANONICAL | Horizontal confidence |
| `RiskGauge` | `indicators/risk_gauge.py` | ✅ CANONICAL | Segmented risk display |
| `MomentumGauge` | `indicators/momentum_gauge.py` | ✅ CANONICAL | Trend momentum |
| `StabilityGauge` | `indicators/stability_gauge.py` | ✅ CANONICAL | Variance display |

---

## 5. Deprecated Components

| Component | File | Replacement | Reason |
|-----------|------|-------------|--------|
| `ProgressRing` | `components/progress_ring.py` | `ProgressRingV2` or any `ui/visualization/rings/Ring` | Duplicate, less feature-rich |
| `GoalRing` | `design_system/visualization/goal_ring.py` | `ui/visualization/rings/GoalRing` | Duplicate implementation |
| `RecoveryRing` | `design_system/visualization/recovery_ring.py` | `ui/visualization/rings/RecoveryRing` | Duplicate implementation |
| `WeeklyTimeline` | `design_system/visualization/weekly_timeline.py` | `ui/visualization/timelines/WeeklyTimeline` | Duplicate implementation |
| `PredictionTimeline` | `design_system/visualization/prediction_timeline.py` | `ui/visualization/timelines/PredictionTimeline` | Duplicate implementation |
| `ConfidenceGauge` | `design_system/visualization/confidence_gauge.py` | `ui/visualization/indicators/ConfidenceGauge` | Duplicate implementation |
| `MuscleHeatmap` | `design_system/visualization/muscle_heatmap.py` | `ui/visualization/heatmaps/MuscleHeatmap` | Duplicate implementation |
| `RiskMeter` | `design_system/visualization/risk_meter.py` | `ui/visualization/indicators/RiskGauge` | Duplicate, renamed |
| `InsightCard` | `components/insight_card.py` | `AppCard` + `StatusBadge` | Overlaps with simpler primitives |
| `ShellSidebar` | `shell/sidebar.py` | Keep (customized shell component) | Too tightly coupled to AppShell |
| `ShellSidebarButton` | `shell/sidebar.py` | Keep (customized for shell) | Too tightly coupled to ShellSidebar |

### Removed Items Documentation

Following are the detailed justifications for each removal:

**`ProgressRing` (components/)**: This is a simple painted ring with no animation, no reduced-motion support, and label-only display. The `ui/visualization/rings/` directory contains 5 ring types with animation, accessibility, and richer data display. All consumers should migrate to `ProgressRingV2`, `GoalRing`, or `RecoveryRing`.

**`InsightCard` (components/)**: This component wraps an icon, title, description, and StatusBadge in a bordered card. It duplicates the pattern of `AppCard` with simpler primitives. `AppCard` already supports title, subtitle, badge, content, and interactive mode. Consumers can compose `AppCard + StatusBadge` to achieve the same result with fewer components.

**`GoalRing` (design_system/visualization/)**: The `design_system/visualization/` directory was created as a home for visualization components within the design system package. However, the `ui/visualization/` directory contains more fully-featured versions with animation, reduced-motion support, and richer rendering. The lazy-loading `__init__.py` already re-exports the `ui/visualization` versions, making these files dead code.

**`RecoveryRing` (design_system/visualization/)**: Same reasoning as GoalRing above.

**`WeeklyTimeline` (design_system/visualization/)**: Same reasoning — duplicate of `ui/visualization/timelines/WeeklyTimeline`.

**`PredictionTimeline` (design_system/visualization/)**: Same reasoning — duplicate of `ui/visualization/timelines/PredictionTimeline`.

**`ConfidenceGauge` (design_system/visualization/)**: Same reasoning — duplicate of `ui/visualization/indicators/ConfidenceGauge`.

**`MuscleHeatmap` (design_system/visualization/)**: Same reasoning — duplicate of `ui/visualization/heatmaps/MuscleHeatmap`.

**`RiskMeter` (design_system/visualization/)**: Same reasoning — duplicate of `ui/visualization/indicators/RiskGauge`, also renamed to match naming convention.

---

## 6. Migration Table

### 6.1 Direct Replacements

| Old Import | New Import | Effort |
|------------|-----------|--------|
| `ui.design_system.components.ProgressRing` | `ui.visualization.rings.ProgressRingV2` | Low |
| `ui.design_system.components.InsightCard` | `ui.design_system.components.AppCard` + `StatusBadge` | Medium |
| `ui.design_system.visualization.GoalRing` | `ui.visualization.rings.GoalRing` | Low |
| `ui.design_system.visualization.RecoveryRing` | `ui.visualization.rings.RecoveryRing` | Low |
| `ui.design_system.visualization.WeeklyTimeline` | `ui.visualization.timelines.WeeklyTimeline` | Low |
| `ui.design_system.visualization.PredictionTimeline` | `ui.visualization.timelines.PredictionTimeline` | Low |
| `ui.design_system.visualization.ConfidenceGauge` | `ui.visualization.indicators.ConfidenceGauge` | Low |
| `ui.design_system.visualization.MuscleHeatmap` | `ui.visualization.heatmaps.MuscleHeatmap` | Low |
| `ui.design_system.visualization.RiskMeter` | `ui.visualization.indicators.RiskGauge` | Low |

### 6.2 Compatible Imports (automatic via lazy __init__)

The following imports will still resolve through the lazy-loading mechanism in `design_system/visualization/__init__.py`:
- `from ui.design_system.visualization import GoalRing` → resolves to `ui.visualization.rings.GoalRing`
- `from ui.design_system.visualization import RecoveryRing` → resolves to `ui.visualization.rings.RecoveryRing`
- etc.

### 6.3 Components that remain unchanged

- All `ui/design_system/tokens/*`
- `ui/design_system/layout/*` (EditorialGrid, KpiStrip, ScrollContainer)
- `ui/design_system/components/AppCard` (retained as canonical)
- `ui/design_system/components/MetricCard` (retained, needs minor fixes)
- `ui/design_system/components/StatusBadge` (retained, needs minor fixes)
- `ui/design_system/components/SectionHeader` (retained, needs method fixes)
- `ui/design_system/components/EmptyState` (retained, needs method fixes)
- `ui/design_system/components/ChartContainer` (retained)
- `ui/design_system/components/DialogTemplate` (retained)
- `ui/design_system/components/SkeletonLoader` (retained)
- `ui/design_system/components/NotificationToast` (retained)
- `ui/design_system/components/WarningBanner` (retained)
- `ui/design_system/components/ActivityFeed` (retained)
- `ui/design_system/components/CommandBar` (retained)
- `ui/design_system/components/NavigationRail` (retained)
- `ui/design_system/components/SearchBar` (retained)
- `ui/design_system/components/SidebarItem` (retained)
- `ui/design_system/components/Toolbar` (retained)
- `ui/design_system/visualization/TrendIndicator` (retained as canonical)
- `ui/shell/*` (AppShell, ShellHeader, ShellSidebar — retained as they are customized for shell layout)
- `ui/narrative/*` (all retained)

---

## 7. Token Usage Audit

### 7.1 Components Using Only Tokens (✅ PASS)

| Component | Tokens Used |
|-----------|-------------|
| `StatusBadge` | ✅ `color_from_scheme`, `RadiusTokens` |
| `SectionHeader` | ✅ `color_from_scheme`, `SpacingTokens` |
| `EmptyState` | ✅ `color_from_scheme`, `SpacingTokens` |
| `ChartContainer` | ✅ `color_from_scheme`, `RadiusTokens`, `SpacingTokens` |
| `DialogTemplate` | ✅ `color_from_scheme`, `ElevationTokens`, `RadiusTokens`, `SpacingTokens` |
| `Toolbar` | ✅ `color_from_scheme`, `RadiusTokens`, `SpacingTokens` |
| `CommandBar` | ✅ `color_from_scheme`, `ElevationTokens`, `RadiusTokens`, `SpacingTokens` |
| `NavigationRail` | ✅ `color_from_scheme`, `RadiusTokens`, `SpacingTokens`, `LayoutTokens` |
| `SearchBar` | ✅ `color_from_scheme`, `RadiusTokens`, `SpacingTokens` |
| `SidebarItem` | ✅ `color_from_scheme`, `RadiusTokens` |
| `KpiStrip` | ✅ `color_from_scheme`, `RadiusTokens`, `SpacingTokens` |
| `ScrollContainer` | ✅ `color_from_scheme` |
| `EditorialGrid` | ✅ `color_from_scheme`, `RadiusTokens`, `SpacingTokens` |
| `ActivityFeed` | ✅ `color_from_scheme`, `RadiusTokens` |
| `GoalRing` (dsgn sys) | ✅ `color_from_scheme` |
| `RecoveryRing` (dsgn sys) | ✅ `color_from_scheme`, `RadiusTokens` |
| `WeeklyTimeline` (dsgn sys) | ✅ `color_from_scheme`, `RadiusTokens` |
| `PredictionTimeline` (dsgn sys) | ✅ `color_from_scheme`, `RadiusTokens` |
| `ConfidenceGauge` (dsgn sys) | ✅ `color_from_scheme`, `RadiusTokens` |
| `RiskMeter` (dsgn sys) | ✅ `color_from_scheme`, `RadiusTokens` |
| `TrendIndicator` | ✅ `color_from_scheme` |
| `CoachCard` | ✅ `color_from_scheme` |
| `CoachCardStack` | ✅ Uses CoachCard |
| `MicroUX` | ✅ `color_from_scheme` |
| `CelebrationOverlay` | ✅ `color_from_scheme` |
| `AchievementBadge` | ✅ `color_from_scheme` |
| `MilestoneIndicator` | ✅ `color_from_scheme` |

### 7.2 Components Using Mixed Tokens + Literals (⚠️ NEEDS FIX)

| Component | Literals Found | Fix Needed |
|-----------|---------------|------------|
| `AppCard` | `font-size: 11px`, `font-size: 13px`, `font-size: 24px` | Use `font_style()` or token sizes |
| `MetricCard` | `font-size: 24px`, `font-size: 14px`, `font-size: 13px`, `font-size: 11px` | Use `font_style()` or token sizes |
| `InsightCard` | `font-size: 13px`, `font-size: 12px` | Use `font_style()` |
| `NotificationToast` | `font-size: 13px`, `font-size: 12px` | Use `font_style()` |
| `WarningBanner` | `font-size: 13px` | Use `font_style()` |
| `SkeletonLoader` | Uses `RADIUS.sm` via `radius_to_px` | ✅ Already token-based |
| `HeroPanel` | `font-size: 20px`, `font-size: 14px` | Use `font_style()` |
| `MetricPanel` | `font-size: 28px`, `font-size: 12px` | Use `font_style()` |
| `SectionPanel` | `font-size: 16px`, `font-size: 12px` | Use `font_style()` |
| `ShellHeader` | `font-size: 28px`, `font-size: 12px` | Use `font_style()` |
| `ShellSidebar` | `font-size: 10px`, `font-size: 14px`, `font-size: 18px` | Use `font_style()` |
| `BarChart` | `font-size: 8px` | Use `font_style()` or token |

### 7.3 Font Literals → Token Mapping

The following font-size literals should be replaced with `font_style()` calls:

| Literal | Token Replacement |
|---------|------------------|
| `font-size: 28px` | `font_style('hero')` |
| `font-size: 24px` | `font_style('metric')` |
| `font-size: 20px` | `font_style('h1')` |
| `font-size: 18px` | `font_style('h2')` |
| `font-size: 16px` | `font_style('h3')` |
| `font-size: 14px` | `font_style('body')` or `font_style('h4')` |
| `font-size: 13px` | `font_style('body')` |
| `font-size: 12px` | `font_style('caption')` |
| `font-size: 11px` | `font_style('label')` |
| `font-size: 10px` | `font_style('caption')` or `font_style('overline')` |
| `font-size: 9px` | `font_style('overline')` |
| `font-size: 8px` | `font_style('caption')` with `weight: 'thin'` |

---

## 8. Accessibility Audit

### 8.1 Components with Proper Accessibility (✅ PASS)

| Component | AccessibleName | AccessibleDescription | FocusPolicy | FocusRing |
|-----------|---------------|----------------------|-------------|-----------|
| `AppCard` | ✅ (if title) | ✅ (if subtitle) | ✅ (if interactive) | ✅ (CSS focus) |
| `EmptyState` | ✅ (action button) | ❌ | ✅ (implicit) | ✅ (CSS focus) |
| `NavigationRail` | ✅ (logo) | ❌ | ✅ (tab order) | ✅ (CSS focus) |
| `SearchBar` | ✅ ("Search input") | ❌ | ✅ (implicit) | ✅ (focus-within) |
| `SidebarItem` | ✅ (if text) | ❌ | ✅ (StrongFocus) | ✅ (CSS focus) |
| `ShellSidebarButton` | ✅ ("Navigate to {label}") | ❌ | ✅ (StrongFocus) | ✅ (CSS focus) |
| `BaseVisualization` | ✅ (class name) | ❌ | ✅ (StrongFocus) | ❌ |

### 8.2 Components Missing Accessibility (⚠️ NEEDS FIX)

| Component | Issue | Fix |
|-----------|-------|-----|
| `StatusBadge` | No accessible name | Add `setAccessibleName()` |
| `InsightCard` | No accessible name/description | Add `setAccessibleName()` with title |
| `MetricCard` | No accessible name | Add `setAccessibleName()` with label |
| `NotificationToast` | Close button no accessible name | Add `setAccessibleName("Close notification")` |
| `WarningBanner` | No accessible name | Add `setAccessibleName()` |
| `ActivityFeed` | No accessible name | Add `setAccessibleName()` |
| `ActivityItem` | No accessible roles | Add `setAccessibleName()` |
| `ChartContainer` | No accessible name | Add `setAccessibleName()` |
| `DialogTemplate` | No accessible name | Add `setAccessibleName()` |
| `CommandBar` | Input no description | Add `setAccessibleDescription()` |
| `Toolbar` | No accessible role | Add `setAccessibleName()` |
| `ShellHeader` | Buttons no accessible names | Add `setAccessibleName()` |
| `ShellSidebar` | Logo no accessible name | ✅ done, section labels? |
| `CoachCard` | Expand button no accessible name | Add `setAccessibleName("Expand card")` |
| `CelebrationOverlay` | No accessible name | Add `setAccessibleName()` |
| `AchievementBadge` | No accessible description | Add `setAccessibleDescription()` |

### 8.3 Keyboard Navigation Gaps (⚠️ NEEDS FIX)

| Component | Issue | Fix |
|-----------|-------|-----|
| `KpiStrip` | Items are clickable but not focusable | Set `setFocusPolicy(Qt.StrongFocus)` on items |
| `WarningBanner` | Action button not in tab order | ✅ implicit, but ensure `setFocusPolicy` |
| `ActivityFeed` | No keyboard interaction | Consider adding click handlers |
| `NotificationToast` | Auto-dismiss may trap focus | Ensure focus moves on dismiss |
| `CoachCard` | Expand toggle has no keyboard hint | Add accessible description |
| `MuscleHeatmap` (dsgn sys) | Not keyboard accessible | Add focus policy |
| `RiskMeter` (dsgn sys) | Not keyboard accessible | Add focus policy |
| `ConfidenceGauge` (dsgn sys) | Not keyboard accessible | Add focus policy |
| `WeeklyTimeline` (dsgn sys) | Not keyboard accessible | Add focus policy |

---

## 9. Responsive Audit

### 9.1 Current Behavior

The application targets a fixed-width desktop experience. All components use Qt's relative positioning within parent widgets, but no explicit breakpoint logic exists for viewport adaptation.

| Component | 1280px | 1440px | 1600px | 1920px | 2560px | 4K |
|-----------|--------|--------|--------|--------|--------|-----|
| `ScrollContainer` | ✅ 32px margin | ✅ 32px margin | ✅ 32px margin | ✅ 32px margin | ✅ 32px margin | ✅ 32px margin |
| `EditorialGrid` | ✅ Flexible | ✅ Flexible | ✅ Flexible | ✅ Flexible | ✅ Flexible | ✅ Flexible |
| `ShellSidebar` | ✅ Fixed 240px | ✅ Fixed 240px | ✅ Fixed 240px | ✅ Fixed 240px | ✅ Fixed 240px | ✅ Fixed 240px |
| `ShellHeader` | ✅ Flexible | ✅ Flexible | ✅ Flexible | ✅ Flexible | ✅ Flexible | ✅ Flexible |
| `AppCard` | ✅ Flexible | ✅ Flexible | ✅ Flexible | ✅ Flexible | ✅ Flexible | ✅ Flexible |
| `MetricCard` | ✅ Flexible | ✅ Flexible | ✅ Flexible | ✅ Flexible | ✅ Flexible | ✅ Flexible |
| `KpiStrip` | ✅ Proportional | ✅ Proportional | ✅ Proportional | ✅ Proportional | ✅ Proportional | ✅ Proportional |
| Charts/Timelines | ✅ Fill available | ✅ Fill available | ✅ Fill available | ✅ Fill available | ✅ Fill available | ✅ Fill available |

### 9.2 Windows Scaling

| Scaling | Expected | Status |
|---------|----------|--------|
| 100% | Pixel-perfect | ✅ OK |
| 125% | Slight stretch, min sizes maintained | ✅ OK |
| 150% | Moderate stretch, may need scroll | ⚠️ Verify |
| 200% | Significant stretch, scroll likely | ⚠️ Verify |

### 9.3 Recommendations

1. **Dynamic sidebar**: Add a collapsed mode + toggle for narrow widths (1920px+ uses expanded)
2. **Max-width wrapper**: Add optional `max_width_xl` constraint for ultra-wide screens
3. **Margin scaling**: Increase page margins from 32px → 48px at 1920+, 64px at 2560+
4. **Font scaling**: Consider `font_style()` adjustments for larger viewports via zoom

---

## 10. Duplication Analysis

### 10.1 Card Family (5 components → 2 canonical)

```
Before:
├── AppCard (design_system/components/)
├── InsightCard (design_system/components/) ← REDUNDANT
├── MetricCard (design_system/components/)
├── HeroPanel (design_system/layout/)
├── MetricPanel (design_system/layout/)
└── SectionPanel (design_system/layout/)

After:
├── AppCard (generic container)
├── MetricCard (metrics display)
├── HeroPanel (editorial layout)
├── MetricPanel (editorial layout)
└── SectionPanel (editorial layout)
   — InsightCard → compose AppCard + StatusBadge
```

### 10.2 Ring Family (7 components → 5 canonical)

```
Before:
├── ProgressRing (design_system/components/) ← REDUNDANT
├── GoalRing (design_system/visualization/) ← DUPLICATE
├── RecoveryRing (design_system/visualization/) ← DUPLICATE
├── GoalRing (ui/visualization/rings/) ← CANONICAL
├── RecoveryRing (ui/visualization/rings/) ← CANONICAL
├── ProgressRingV2 (ui/visualization/rings/) ← CANONICAL
├── ConfidenceRing (ui/visualization/rings/) ← CANONICAL
└── ReadinessRing (ui/visualization/rings/) ← CANONICAL

After:
└── ui/visualization/rings/ (5 canonical)
   — ProgressRing → ProgressRingV2
   — design_system/visualization GoalRing/RecoveryRing → ui/visualization/rings/
```

### 10.3 Timeline Family (8 components → 6 canonical)

```
Before:
├── WeeklyTimeline (design_system/visualization/) ← DUPLICATE
├── PredictionTimeline (design_system/visualization/) ← DUPLICATE
├── WeeklyTimeline (ui/visualization/timelines/) ← CANONICAL
├── WorkoutTimeline (ui/visualization/timelines/) ← CANONICAL
├── RecoveryTimeline (ui/visualization/timelines/) ← CANONICAL
├── PredictionTimeline (ui/visualization/timelines/) ← CANONICAL
├── MesocycleTimeline (ui/visualization/timelines/) ← CANONICAL
└── AdaptationTimeline (ui/visualization/timelines/) ← CANONICAL

After:
└── ui/visualization/timelines/ (6 canonical)
   — design_system/visualization WeeklyTimeline/PredictionTimeline → ui/visualization/timelines/
```

### 10.4 Gauge Family (6 components → 4 canonical)

```
Before:
├── ConfidenceGauge (design_system/visualization/) ← DUPLICATE
├── RiskMeter (design_system/visualization/) ← DUPLICATE
├── ConfidenceGauge (ui/visualization/indicators/) ← CANONICAL
├── RiskGauge (ui/visualization/indicators/) ← CANONICAL
├── MomentumGauge (ui/visualization/indicators/) ← CANONICAL
└── StabilityGauge (ui/visualization/indicators/) ← CANONICAL

After:
└── ui/visualization/indicators/ (4 canonical)
   — design_system/visualization ConfidenceGauge → ui/visualization/indicators/
   — RiskMeter → RiskGauge
```

### 10.5 Navigation Family (3 components → use all where appropriate)

```
├── NavigationRail (design_system/components/) — standalone rail
├── SidebarItem (design_system/components/) — individual button
├── ShellSidebar (shell/) — full sidebar (uses custom ShellSidebarButton)
└── ShellSidebarButton (shell/) — custom button (similar to SidebarItem)

Note: ShellSidebar is tightly coupled to AppShell and cannot be replaced
without significant refactoring. ShellSidebarButton is also tightly coupled.
Keep both but add note for future refactoring.
```

### 10.6 Heatmap Family (1 duplicate → canonical)

```
Before:
├── MuscleHeatmap (design_system/visualization/) ← DUPLICATE
├── MuscleHeatmap (ui/visualization/heatmaps/) ← CANONICAL
├── VolumeHeatmap (ui/visualization/heatmaps/) ← CANONICAL
├── FatigueHeatmap (ui/visualization/heatmaps/) ← CANONICAL
└── ComplianceHeatmap (ui/visualization/heatmaps/) ← CANONICAL
```

---

## 11. Implementation Checklist

### Phase 1: Documentation & Planning

- [x] Generate this RFC document
- [x] Identify all duplicated components
- [x] Create migration table
- [x] Document token usage audit
- [x] Document accessibility audit
- [x] Document responsive audit

### Phase 2: Token Cleanup (minor)

- [ ] Fix `MetricCard` — replace literal font sizes with `font_style()`
- [ ] Fix `AppCard` — replace `font-size: 11px` with `font_style('label')`
- [ ] Fix early return methods in `SectionHeader` (set_title, set_subtitle)
- [ ] Fix early return methods in `EmptyState` (set_message)
- [ ] Fix early return methods in `Toolbar` (add_action, remove_action)
- [ ] Fix early return methods in `MetricCard` (set_value, set_trend visual update)

### Phase 3: Accessibility Fixes

- [ ] Add `setAccessibleName()` to `StatusBadge`
- [ ] Add `setAccessibleName()` to `MetricCard`
- [ ] Add `setAccessibleName()` to `NotificationToast` close button
- [ ] Add `setAccessibleName()` to `WarningBanner`
- [ ] Add `setAccessibleName()` to `ActivityFeed`
- [ ] Add `setAccessibleName()` to `ChartContainer`
- [ ] Add `setAccessibleName()` to `ShellHeader` buttons
- [ ] Add focus policy to keyboard-accessible interactive widgets

### Phase 4: Duplicate Removal

- [ ] Mark `InsightCard` as deprecated in __init__.py
- [ ] Mark `ProgressRing` as deprecated in __init__.py
- [ ] Update `design_system/visualization/__init__.py` to use canonical paths directly (remove lazy loading)

### Phase 5: Verification

- [ ] Verify all imports from `design_system/visualization` still work
- [ ] Run type checker
- [ ] Run lint
- [ ] Verify existing pages render identically

### Phase 6: Shell Cleanup (minor)

- [ ] Ensure ShellSidebar buttons use consistent styling tokens
- [ ] Update ShellHeader to use `SectionHeader` for alignment

---

## Appendix A: Complete File Manifest

### KEEP (no changes needed)
```
tokens/color.py
tokens/spacing.py
tokens/typography.py
tokens/radius.py
tokens/shadow.py
tokens/motion.py
tokens/icon.py
tokens/layout.py
tokens/__init__.py
layout/scroll_container.py
layout/editorial_grid.py
layout/kpi_strip.py
layout/__init__.py
components/navigation_rail.py
components/sidebar_item.py
components/command_bar.py
components/search_bar.py
visualization/trend_indicator.py
components/skeleton_loader.py
narrative/engine.py
narrative/templates/*.py
ui/visualization/* (all)
theme.py
```

### FIX (minor improvements needed)
```
components/app_card.py — tokenize font literals
components/metric_card.py — tokenize font literals, fix set_value/set_trend
components/status_badge.py — add accessible name
components/section_header.py — fix stub methods
components/empty_state.py — fix stub method
components/notification_toast.py — add accessible name to close button
components/warning_banner.py — add accessible name
components/activity_feed.py — add accessible name
components/chart_container.py — add accessible name
components/toolbar.py — fix stub methods
layout/kpi_strip.py — add focus policy to items
components/insight_card.py — mark deprecated, fix accessible name
shell/header.py — add accessible names to buttons
shell/sidebar.py — ensure consistent token usage
narrative/cards.py — add accessible name to expand toggle
narrative/micro.py — add accessible descriptions
```

### DEPRECATE (mark as deprecated, keep for compatibility)
```
components/progress_ring.py — mark deprecated in docstring
components/insight_card.py — mark deprecated in docstring
```

### REMOVED via lazy-loading (don't delete, they're dead code behind re-exports)
```
visualization/goal_ring.py — duplicate of ui/visualization/rings/GoalRing
visualization/recovery_ring.py — duplicate of ui/visualization/rings/RecoveryRing
visualization/weekly_timeline.py — duplicate of ui/visualization/timelines/WeeklyTimeline
visualization/prediction_timeline.py — duplicate of ui/visualization/timelines/PredictionTimeline
visualization/confidence_gauge.py — duplicate of ui/visualization/indicators/ConfidenceGauge
visualization/muscle_heatmap.py — duplicate of ui/visualization/heatmaps/MuscleHeatmap
visualization/risk_meter.py — duplicate of ui/visualization/indicators/RiskGauge
```
