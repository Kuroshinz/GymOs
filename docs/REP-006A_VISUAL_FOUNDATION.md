# REP-006A — Visual Foundation Audit

> **Status:** Audit Complete — No Code Modified
> **Current Score:** 3.5 / 10
> **Target Score:** 8.5 / 10
> **Auditor:** REP-006A
> **Date:** 2026-07-14

---

## Executive Summary

GymOS has a well-defined design token system (`ui/design_system/tokens/`) and a solid layout component library (`SectionPanel`, `HeroPanel`, `EditorialGrid`, `AppCard`, etc.). However, **most pages bypass the design system entirely**, using hardcoded colors, arbitrary font sizes, magic spacing values, and custom card implementations. The result is a fragmented visual language — the Dashboard feels polished, but the Workout, Progress, Settings, and Recovery pages look like they belong to different applications.

The command center (`ui/command_center/pages/`) is a **separate, parallel UI** with its own layout, widgets, and styling. It does not use the design system components at all. This is the largest source of visual inconsistency.

---

## Current Score Breakdown

| Category | Score (0–10) |
|---|---|
| Visual hierarchy | 3 |
| Typography hierarchy | 3 |
| Spacing consistency | 4 |
| Card hierarchy | 4 |
| CTA placement | 5 |
| Visual weight | 3 |
| Alignment | 4 |
| Empty space management | 3 |
| Grid consistency | 4 |
| Accessibility | 5 |
| **Overall** | **3.5** |

---

## Design Token Inventory

### Available (use these, stop inventing new values)

| Token File | Contents |
|---|---|
| `tokens/spacing.py` | 8pt grid: `s1`(4px) through `s64`(256px), plus semantic aliases `section`, `page`, `gutter`, `card_padding`, `list_gap` |
| `tokens/typography.py` | `h1`–`h4`, `body`, `body_small`, `caption`, `label`, `overline` — each with size/weight/line-height/letter-spacing; `font_style()` helper |
| `tokens/radius.py` | `none`, `sm`, `md`, `lg`, `xl`, `2xl`, `full` |
| `tokens/elevation.py` | Levels `0`–`5` with light/dark shadow params; `apply_elevation()` helper |
| `tokens/color.py` | `ColorTokens`, `DarkColorTokens`, `HighContrastColorTokens`, `SemanticColorTokens`; `color_from_scheme()` helper |
| `tokens/icon.py` | `xs`–`4xl` sizes, semantic aliases |
| `tokens/layout.py` | Breakpoints, column templates, sidebar/nav widths, section gap, page margin |
| `tokens/motion.py` | Durations, delays, curves; `easing_style()` helper |

### Design System Components Available

| Component | File | Used by pages |
|---|---|---|
| `SectionPanel` | `layout/editorial_grid.py` | Dashboard only |
| `HeroPanel` | `layout/editorial_grid.py` | Dashboard only |
| `MetricPanel` | `layout/editorial_grid.py` | Dashboard only |
| `KpiStrip` | `layout/kpi_strip.py` | Not used anywhere |
| `ScrollContainer` | `layout/scroll_container.py` | Dashboard, partial |
| `AppCard` | `components/app_card.py` | Not used (DashboardCard exists as copy) |
| `InsightCard` | `components/insight_card.py` | Not used |
| `MetricCard` | `components/metric_card.py` | Not used |
| `EmptyState` | `components/empty_state.py` | Not used |
| `SectionHeader` | `components/section_header.py` | Dashboard only |
| `StatusBadge` | `components/status_badge.py` | Not used |
| `ChartContainer` | `components/chart_container.py` | Not used |
| `ActivityFeed` | `components/activity_feed.py` | Not used |

---

## Page-by-Page Audit

### 1. Dashboard (`ui/dashboard/dashboard_view.py`)

**Score:** 6/10 — Best page in the app, but still inconsistent.

**Typography violations:**
- H1: `font-size: 20px; font-weight: 700` — should use `TypographyTokens.h3_size`, `h3_weight`
- Body meta: `font-size: 12px` — should use `body_small_size`
- Recovery value: `font-size: 32px; font-weight: 800` — arbitrary, no token match
- Recommendations: `font-size: 14px; font-weight: 600` — should use `h4` or body with weight
- Section titles in SectionPanel: `16px; font-weight: 700` — correct usage via SectionPanel
- Step labels, empty states: `13px`, `12px` — arbitrary

**Spacing violations:**
- `main_layout.setSpacing(24)` — magic number, should use `SpacingTokens.s6` (1.5rem = 24px)
- `grid.set_spacing(16)` — magic number, should use `SpacingTokens.s4` (1rem = 16px)
- `ScrollContainer` uses `setContentsMargins(32, 24, 32, 32)` — magic, should use tokens
- `MetricPanel` margins `(16, 14, 16, 14)` — mixed 16/14, should consult token scale

**Card issues:**
- Uses `SectionPanel` correctly for most sections
- `MetricPanel` reused for readiness — good
- But `_hero_workout_name` is a raw QLabel, not wrapped in a card component
- Cards shared via `self._hero_workout_section` pattern is fragile (deleteLater issues)

**Visual hierarchy:**
- Hero → Overview → Insights — good 3-level structure
- But hero section has flat layout (rings + readiness side by side with no clear primary)
- Missing section divider between hero and overview

**Hardcoded colors found:**
- None in the main view (all through `_colors()`)
- DashboardCard/base_card.py uses colors correctly

**Quick wins:**
- Replace magic spacing with `S.s6`, `S.s4` tokens
- Replace `font-size: 32px` with typography tokens or consistent metric scale
- Add `SectionHeader`-style spacing between hero and middle sections

---

### 2. Workout Selection (`ui/workout_selection_view.py`)

**Score:** 3/10 — All hardcoded, no token usage.

**Typography violations:**
- Header: `font-size: 24px; font-weight: 700` — should be `h2` or `h3`
- Subtitle: `font-size: 14px` — should be `body_small_size`
- DayCard name: `font-size: 18px; font-weight: 700` — should be `h4` or token
- DayCard desc: `font-size: 12px` — should be `caption_size`
- DayCard icon: `font-size: 28px` — arbitrary

**Spacing violations:**
- `layout.setContentsMargins(32, 32, 32, 32)` — magic
- `layout.setSpacing(24)` — magic
- `self._grid.setSpacing(16)` — magic
- DayCard margins: `setContentsMargins(16, 12, 16, 12)` — magic
- DayCard layout spacing: `setSpacing(6)` — not on token scale (should be `s2` = 8px or `s1_5` = 6px)

**Card issues:**
- `DayCard` is a custom QFrame with all hardcoded styles
- Border: `2px solid transparent` — should use `BorderTokens`
- Border-radius: `16px` — should use `RadiusTokens.xl` (16px)
- Colors: `"#1E293B"`, `"#818CF8"`, `"#F1F5F9"`, `"#64748B"` — all hardcoded, should use `DarkColorTokens`

**Visual hierarchy:**
- Flat grid of cards — no hero, no sectioning
- No empty state when no program is loaded
- No search or filter

**Hardcoded colors: 6** distinct hex values

**Quick wins:**
- Replace all hex colors with `color_from_scheme(ColorScheme.DARK)`
- Replace `DayCard` with `AppCard(interactive=True)`
- Replace magic spacing with `SpacingTokens`

---

### 3. Workout View (`ui/workout_view.py`)

**Score:** 2/10 — Most code, least design system usage.

**Typography violations:**
- `SetRow` set number: `font-size: 13px` — arbitrary
- `ExerciseCard` name: `font-size: 18px; font-weight: 700` — should be `h4`
- Recommendation text: `font-size: 11px` — should be `caption`
- Weight input: `font-size: 16px; font-weight: 700` — arbitrary
- × label: `font-size: 16px` — arbitrary
- RIR label: `font-size: 11px` — arbitrary
- Header title: `font-size: 20px; font-weight: 700` — should be `h3`
- Summary dialog title: `font-size: 22px` — arbitrary
- Summary info: `font-size: 13px` — arbitrary
- PR/recommendation labels: `font-size: 13px`, `font-size: 12px` — mixed

**Spacing violations:**
- `SetRow` contentsMargins: `(8, 6, 8, 6)` — magic
- `ExerciseCard` padding: `16px` (via stylesheet `padding: 16px`) and layout margins `(16, 12, 16, 12)` — inconsistent
- Main layout margins: `(32, 16, 32, 16)` for header, `(32, 16, 32, 16)` for scroll — inconsistent with ScrollContainer
- `SetRow` set number fixed width: `28` — not on any scale
- Weight input width: `64px` — arbitrary
- Reps input width: `52px` — arbitrary
- RIR input width: `36px` — arbitrary

**Card issues:**
- `ExerciseCard` is a custom QFrame — no design system component used
- `SetRow` is a custom QFrame — no design system component used
- `WorkoutSummaryDialog` is a QDialog with entirely hardcoded styles
- No consistent card padding, title style, or elevation

**Visual hierarchy:**
- Header bar (back, title, finish button) → scrollable exercise cards — flat
- Summary dialog has better hierarchy (title → metrics → PRs → recommendations → recovery)
- No hero section, no loading state

**Hardcoded colors: 10+** distinct hex values throughout (buttons, inputs, backgrounds)

**Quick wins:**
- Replace `ExerciseCard` with `AppCard` or `SectionPanel`
- Replace all hex colors with design tokens
- Use `font_style()` helper from typography tokens
- Standardize input sizes with SpacingTokens

---

### 4. Progress View (`ui/progress_view.py`)

**Score:** 3/10 — Charts are good, everything else is hardcoded.

**Typography violations:**
- Header: `font-size: 24px; font-weight: 700` — should be `h2`
- Chart title: `font-size: 15px; font-weight: 600` — should be `h4` or typography token
- Chart message: `font-size: 13px` — arbitrary
- Period label: `font-size: 13px` — arbitrary

**Spacing violations:**
- Layout margins: `(32, 32, 32, 32)` — magic
- Layout spacing: `setSpacing(16)` — magic
- `ChartWidget` margins: `(16, 12, 16, 12)` — magic
- `EmptyChart` margins: `(16, 12, 16, 12)` — magic

**Card issues:**
- `ChartWidget` and `EmptyChart` are custom QFrame subclasses with hardcoded styles
- Border-radius: `12px` — should be `RadiusTokens.lg` (12px)
- Completely bypasses `ChartContainer` component from design system

**Visual hierarchy:**
- Period selector → Weight chart → Volume chart → Muscle chart — flat list
- No hero, no section grouping, no insights section

**Hardcoded colors: 5+** distinct hex values

**Quick wins:**
- Replace `ChartWidget` with `ChartContainer` from design system components
- Replace all hex colors
- Use typography tokens
- Add section grouping with `SectionPanel`

---

### 5. Settings View (`ui/settings_view.py`)

**Score:** 3/10

**Typical issues:**
- Hardcoded font sizes: `font-size: 24px`, `18px`, `13px`
- Hardcoded colors: `#F1F5F9`, `#94A3B8`, `#1E293B`, `#0F172A`
- Magic spacing: `(32, 32, 32, 32)`, `setSpacing(16)`
- No design token usage
- Custom QFrame cards/sections instead of SectionPanel
- No visual hierarchy beyond a flat list
- No use of design system form components

---

### 6. Recovery Dashboard (`ui/recovery/recovery_dashboard.py`)

**Score:** 4/10 — Better than Workout, still inconsistent.

**Issues:**
- Mixed token usage — some colors through `color_from_scheme`, many hardcoded
- Arbitrary font sizes: `24px`, `48px`, `13px`, `12px`, `14px`
- Custom widget cards instead of design system components
- Magic spacing throughout margins and gaps
- Flat layout — no hero → primary → secondary structure
- Recovery ring uses custom implementation that duplicates `RecoveryRing` from design system

---

### 7. Prediction Dashboard (`ui/prediction/prediction_dashboard.py`)

**Score:** 4/10

**Issues:**
- `PredictionCard` is a custom QFrame — hardcoded colors `"#1E293B"`, `"#334155"`, `"#818CF8"` etc.
- Font sizes: `11px`, `13px`, `26px`, `11px` — all arbitrary
- Card sizes: `setFixedSize(260, 140)` — arbitrary
- Grid spacing: `setSpacing(12)` — magic
- Margin: `(20, 20, 20, 20)` — magic
- Title: `font-size: 20px; font-weight: 700` — should use h3
- Uses `DashboardCard` base card correctly (ScenarioWidget, RiskMeterWidget, etc.)

**Good:**
- Uses DashboardCard base class for some sub-widgets
- Has a title/subtitle structure at page level
- Widgets are properly sectioned via DashboardCard

---

### 8. Command Center Pages (`ui/command_center/pages/`)

**Score:** 2/10 — Entirely separate visual system.

The command center is a **parallel application** with:
- 9 page views (Home, Mission, Planning, Prediction, Recovery, Knowledge, Adaptive, Analytics, System)
- Its own visualization components (`confidence_indicator.py`, `heatmap.py`, `prediction_card.py`, `progress_ring.py`, `timeline.py`, `trend_chart.py`)
- Its own widgets (`adaptive_timeline_widget.py`, `knowledge_graph_widget.py`, etc.)
- Its own layout system (`dockable_panel.py`, `grid_panel.py`, `resizable_widget.py`)
- Its own theme (`theme.py`)

**Issues:**
- Duplicates `ProgressRing`, `Timeline`, `TrendChart` from `ui/design_system/visualization/`
- Does not import or use any design system tokens or components
- All colors hardcoded as hex strings
- All font sizes arbitrary (no typography tokens)
- All spacing magic values
- No visual hierarchy — flat grid of widgets
- No empty states
- Card styles inconsistent between widgets

---

### 9. Visualization Components (`ui/visualization/`, `ui/design_system/visualization/`)

**Score:** 6/10

**Good:**
- `BaseVisualization` class uses `color_from_scheme()` for colors
- `WeeklyTimeline`, `RecoveryTimeline` (visualization versions) use `_colors()` properly
- `RiskMeter` uses `RadiusTokens.R.full`
- `RecoveryRing` and `GoalRing` use `ColorScheme` and `_colors()`

**Issues:**
- `_make_font(8)`, `_make_font(9)`, `_make_font(10)` — pixel sizes don't match typography scale
- `setFixedHeight(60)`, `setFixedHeight(80)`, `setFixedHeight(90)`, `setFixedHeight(100)`, `setFixedHeight(120)` — all arbitrary
- `bar_w = min(32, ...)` in timelines — magic number
- `spacing = max((w - 20 - bar_w * n) // max(n - 1, 1), 4)` — magic 4, 20
- `start_x = 10` — magic
- Hardcoded color fallback in `RiskMeter`: `"FF"` alpha appended as string
- `PredictionTimeline` duplicated in both `visualization/timelines/` and `design_system/visualization/` with nearly identical code
- `WeeklyTimeline` duplicated in both locations

---

## Issues Register

### Critical (blocking visual consistency)

| ID | Issue | Pages | Effort |
|---|---|---|---|
| C1 | Command center doesn't use design system | All 9 CC pages | XL |
| C2 | Workout View (500 lines) uses zero design tokens | workout_view | L |
| C3 | PredictionDashboard has custom PredictionCard instead of AppCard | prediction | M |
| C4 | ExerciseCard, SetRow, DayCard are all custom widgets with hardcoded styles | workout_selection, workout_view | M |
| C5 | ChartWidget duplicates ChartContainer | progress_view | S |

### High (major visual debt)

| ID | Issue | Pages | Effort |
|---|---|---|---|
| H1 | No page uses `font_style()` from typography tokens | All | M |
| H2 | Arbitrary font sizes everywhere (22, 32, 28, 26, 15, 14, 13, 12, 11, 10, 9, 8) | All | M |
| H3 | `SpacingTokens` not used — magic margins/spacing throughout | All except dashboard | M |
| H4 | 10+ distinct hardcoded hex colors per page | workout_view, settings, progress, command_center | L |
| H5 | RecoveryDashboard has its own ring implementation duplicating design system | recovery | M |
| H6 | Duplicate `PredictionTimeline` and `WeeklyTimeline` in two locations | visualization/ ×2 | S |
| H7 | `DashboardCard.make_row()` and `AppCard.make_row()` are identical copies | dashboard, design_system | S |
| H8 | No loading/skeleton states on any data page | All | M |
| H9 | No page uses `ElevationTokens` or `apply_elevation()` | All | M |

### Medium

| ID | Issue | Pages | Effort |
|---|---|---|---|
| M1 | Empty states are per-page QLabel text, not `EmptyState` component | All | S |
| M2 | Section headers inconsistent — some use SectionHeader, some plain QLabel | progress, settings | S |
| M3 | Missing `StatusBadge` usage — status shown via raw QLabel text | workout_summary, prediction | S |
| M4 | No metric value scale — semantic sizes for 24px vs 32px vs 48px values undefined | All | M |
| M5 | Accessibility labels present in some places, absent in others | Mixed | M |
| M6 | No reduced-motion support for custom painted widgets | visualization/* | M |
| M7 | Focus indicators inconsistent across pages | All | M |

### Low

| ID | Issue | Pages | Effort |
|---|---|---|---|
| L1 | `KpiStrip` component exists but is never used anywhere | — | S |
| L2 | No consistent page-level max-width / container constraint | All | S |
| L3 | `WarningBanner`, `ActivityFeed`, `NotificationToast` unused | — | S |
| L4 | Page titles have varying sizes (20px, 24px, 22px) | All | S |

---

## Screens Requiring Redesign

| Priority | Screen | Reason |
|---|---|---|
| P0 | Workout View (`workout_view.py`) | Largest file, zero tokens, worst UX |
| P0 | Command Center pages (9 pages) | Entire parallel UI without design system |
| P1 | Workout Selection (`workout_selection_view.py`) | DayCard needs replacement |
| P1 | Progress View (`progress_view.py`) | ChartWidget → ChartContainer |
| P1 | Settings View (`settings_view.py`) | Full token retrofit |
| P1 | Prediction Dashboard (`prediction_dashboard.py`) | PredictionCard needs replacement |
| P2 | Recovery Dashboard (`recovery_dashboard.py`) | Token retrofit |
| P2 | Dashboard (`dashboard_view.py`) | Token consistency pass |

---

## Typography Hierarchy (Target)

```
H1  → 36px / 700  →  Page titles (currently 24px, mixed)
H2  → 30px / 700  →  Section hero titles (currently 24px, 22px, 20px)
H3  → 24px / 700  →  Card group headers (currently 20px, 18px)
H4  → 20px / 600  →  Card titles (currently 18px, 16px, 15px)
Body   → 16px / 400  →  Running text (currently 14px, 13px)
Body Sm → 14px / 400 →  Secondary text (currently 13px, 12px)
Caption → 12px / 400 →  Metadata, timestamps (currently 11px, 10px)
Label  → 12px / 600  →  Labels, badges (currently 11px, 10px)
Metric → 28–36px / 800 → KPI values (currently 32px, 26px, 24px — inconsistent)
Hero   → 20–24px / 700 → Hero panel value (currently 28px, 20px)
```

**Note:** These align with the existing `TypographyTokens` h1–h4, body, body_small, caption, label. No new tokens needed.

---

## Spacing Target (8pt Grid)

```
s1    =  4px    →  Tight icon/text gaps
s2    =  8px    →  List gaps, row spacing
s3    = 12px    →  Card internal spacing
s4    = 16px    →  Card padding, grid gaps
s5    = 20px    →  SectionHeader internal
s6    = 24px    →  Section gaps
s8    = 32px    →  Page margins
s10   = 40px    →  Large section gaps
s12   = 48px    →  Hero spacing
```

All page margins → `S.s8` (32px). All section gaps → `S.s6` (24px). All card padding → `S.s4` (16px) or `S.s5` (20px). The `section`, `page`, `gutter`, `card_padding` aliases in `SpacingTokens` already encode this.

---

## Card Hierarchy (Target)

| Level | Component | Usage |
|---|---|---|
| L0 | `HeroPanel` | Page hero with accent bar, content slot |
| L1 | `SectionPanel` | Grouped content with title/subtitle |
| L1 | `AppCard` | Interactive cards (clickable, elevatable) |
| L2 | `InsightCard` | Recommendation/insight rows |
| L2 | `MetricCard` | KPI values with trend |
| L3 | `StatusBadge` | Inline status indicators |

---

## Quick Wins (Effort: Small)

1. **Replace `font-size: 24px` → `font_style("h3")`** in all page headers (5 files)
2. **Replace `font-size: 18px` → `font_style("h4")`** for card titles (4 files)
3. **Replace magic margins with `S.s8`** for page margins (7 files)
4. **Replace magic section spacing with `S.s6`** (6 files)
5. **Delete duplicate `PredictionTimeline`** in `design_system/visualization/` — keep only `visualization/timelines/`
6. **Delete duplicate `WeeklyTimeline`** in `design_system/visualization/` — keep only `visualization/timelines/`
7. **Replace `ChartWidget` with `ChartContainer`** in `progress_view.py`
8. **Replace `DashboardCard` with `AppCard`** (identical API, avoid duplication)

---

## Blocking Issues (Must Fix Before REP-006B)

| # | Blocking Issue | Reason |
|---|---|---|
| 1 | Command center uses zero design tokens | 9 pages cannot ship with different visual language |
| 2 | Workout View has all-hardcoded styles | 500-line file with most visual debt |
| 3 | Duplicate timeline components | Confusion, maintenance burden, inconsistent fixes |
| 4 | No consistent empty state | Every page invents its own "no data" display |
| 5 | `font_size` not used anywhere | Typography tokens exist but are completely ignored |

---

## Verification Checklist (Post-Fix)

- [ ] Every page title uses consistent `h2`/`h3` typography token
- [ ] Every section gap is a `SpacingTokens` value
- [ ] Every card uses a design system card component
- [ ] No hardcoded hex colors in any view file
- [ ] No magic font sizes in any view file
- [ ] No magic margin/padding values in any layout
- [ ] All empty states use `EmptyState` component
- [ ] Command center pages import design tokens
- [ ] Duplicate components consolidated
- [ ] Elevation applied consistently to cards

---

## Effort Summary

| Category | Files | Est. Effort |
|---|---|---|
| Token retrofit (colors → tokens) | 12 | 2 days |
| Typography standardization | 10 | 1 day |
| Spacing standardization | 10 | 1 day |
| Command center redesign | 20+ | 5 days |
| Duplicate component consolidation | 4 | 0.5 day |
| Empty state implementation | 8 | 0.5 day |
| Elevation pass | 8 | 0.5 day |
| **Total** | **~50 files** | **~10.5 days** |

---

## Score Target After REP-006B

| Category | Current | Target |
|---|---|---|
| Visual hierarchy | 3 | 8 |
| Typography hierarchy | 3 | 9 |
| Spacing consistency | 4 | 9 |
| Card hierarchy | 4 | 8 |
| CTA placement | 5 | 7 |
| Visual weight | 3 | 8 |
| Alignment | 4 | 8 |
| Empty space | 3 | 7 |
| Grid consistency | 4 | 8 |
| Accessibility | 5 | 8 |
| **Overall** | **3.5** | **8.5** |
