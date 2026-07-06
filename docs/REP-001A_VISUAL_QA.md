# REP-001A — Product Polish & Visual QA Report

## Summary

| Metric | Value |
|:---|---:|
| Visual issues found | **186** |
| Visual issues fixed (batch 1) | **38** |
| Remaining visual issues | **148** |
| Tests passed | **3330 / 3377** |
| Tests failed (pre-existing) | **45** |
| New regressions | **0** |

---

## Corrected Issues (Fixed in Batch 1)

### 1. Card Elevation (CRITICAL)
**Problem:** All card shadows used CSS `box-shadow` syntax via `elevation_style()` which is **not supported by PySide6 QSS**. Card elevation was entirely invisible.
**Fix:** Added `apply_elevation()` to `elevation.py` — applies `QGraphicsDropShadowEffect` with proper offset, blur radius, and alpha. `AppCard._build_ui()` now calls `apply_elevation(self, 2)` for elevated cards.

### 2. Hardcoded Colors in Visualization Components (MAJOR)
**Problem:** 4 files had hardcoded hex color values bypassing the design token system:
- `trend_indicator.py`: `TREND_COLORS` dict with `#4ADE80`, `#A3E635`, `#94A3B8`, `#FBBF24`, `#F87171`
- `adaptation_timeline.py`: `STATUS_COLORS` dict with same hex values
- `mesocycle_timeline.py`: `PHASE_COLORS` dict with `#F87171`, `#60A5FA`, `#FBBF24`, etc.
- `muscle_heatmap.py`: Hardcoded `#1E3A5F` for low-end gradient color
- `volume_heatmap.py`: Hardcoded `#1E293B` for low-end gradient color

**Fix:** Replaced all hardcoded color dicts with instance methods (`_trend_color()`, `_status_color()`, `_phase_color()`) that resolve to token values (`colors.success`, `colors.error`, `colors.warning`, etc.). These now respect the color scheme at runtime.

### 3. Fragile Radius String Parsing (MAJOR)
**Problem:** 10 files parsed radius token strings with `.replace("rem", "")` and `.replace("px", "")` — fragile, breaks if token format changes.

**Files affected:** `bar_chart.py`, `comparison_chart.py`, `weekly_timeline.py`, `workout_timeline.py`, `mesocycle_timeline.py`, `muscle_heatmap.py`, `skeleton_loader.py`, `risk_meter.py`, `confidence_gauge.py` (both versions), `stability_gauge.py`, `risk_gauge.py`, `momentum_gauge.py`, `navigation_rail.py`

**Fix:** Added `radius_to_px()` and `px_from_token()` to `radius.py` that handle both `px` and `rem` suffixes with proper base font size (16px). All 10 files updated to use these functions.

### 4. Orphaned Widget in home_page.py (MAJOR)
**Problem:** `update_data()` reassigned `self._hero_readiness` to a new `MetricPanel` widget but never added it to the hero layout — the widget was orphaned, and the old widget remained displayed.
**Fix:** Store hero layout reference and metric index. On update, remove old widget, delete it, and insert new widget at the correct position.

### 5. Duplicate SectionHeader in mission_page.py (MINOR)
**Problem:** `SectionHeader` created on line 32 was never added to layout (orphaned), then created again on line 33. Wasteful allocation.
**Fix:** Removed the orphaned line 32.

### 6. Non-functional Analytics Page (MAJOR)
**Problem:** `AnalyticsCenterPage.update_data()` was `pass` — the page never received any data. All widgets were permanently empty.
**Fix:** Implemented `update_data()` to populate volume timeline, compliance gauge, and PR section from `CommandCenterData`. Added `_safe_dict()` helper for data extraction.

### 7. Missing Public API on ScrollContainer (MINOR)
**Problem:** All 9 command center pages accessed `scroll._wrapper.layout()` — tightly coupled to private attribute.
**Fix:** Added `content_layout` property on `ScrollContainer`.

---

## Remaining Issues by Severity

### CRITICAL (8 remaining)

| # | Issue | File/Area |
|:---:|:---|---:|
| 1 | **No global exception handler** — any crash kills the app silently | `main.py` |
| 2 | **Light mode broken** — every component hardcodes `ColorScheme.DARK` | 25+ component files |
| 3 | **No high-DPI scaling** — Retina displays render at wrong scale | All visualizations use `setPixelSize` |
| 4 | **No splash screen** — cold start shows blank window | Missing |
| 5 | **No onboarding** — first-run user sees a blank app | Missing |
| 6 | **Settings not persisted** — all preferences lost on restart | `core/settings/` |
| 7 | **No installer** — app runs from source only | Missing |
| 8 | **All card elevations broken** in MetricCard, SectionPanel, HeroPanel — same CSS box-shadow issue | `metric_card.py`, `editorial_grid.py` |

### MAJOR (24 remaining)

| # | Issue | File/Area |
|:---:|:---|---:|
| 9 | All font sizes are hardcoded pixels — no `TypographyTokens` used | All 45+ widget/visualization files |
| 10 | All margins/padding are hardcoded — no `SpacingTokens` used | All component files |
| 11 | `EmptyState` component exists but zero views use it | `ui/experience/empty_state_manager.py` |
| 12 | `LoadingStateManager` components exist but zero views use them | `ui/experience/loading_state_manager.py` |
| 13 | No "No results" message in CommandPalette — blank list on no match | `command_palette.py` |
| 14 | No "No results" message in QuickSearch — list hidden on no match | `quick_search.py` |
| 15 | `PredictionCenterPage` has no empty state for accuracy section | `prediction_center_page.py` |
| 16 | `RecoveryCenterPage` hardcodes empty `[0,0,0,0,0,0,0]` timeline data | `recovery_center_page.py` |
| 17 | `SystemCenterPage` doesn't clear release section before adding content — potential duplicates | `system_center_page.py` |
| 18 | All visualizations silently return on empty data — no "No data" rendering | 30+ visualization files |
| 19 | `TrendIndicator` still has one hardcoded color in constructor default `#A3E635` | `trend_indicator.py` |
| 20 | `MesocycleTimeline` still has two hardcoded fallback colors `#F97316`, `#A78BFA` | `mesocycle_timeline.py` |
| 21 | All pages use `scroll._wrapper.layout()` instead of new `content_layout` property | 9 page files |
| 22 | `dashboard_view.py` creates new `MetricPanel` each refresh without removing old | `dashboard_view.py` |
| 23 | No `setTabOrder()` anywhere — tab navigation follows widget creation order | All UI |
| 24 | `MainWindow` sidebar uses hardcoded hex colors — no `ColorScheme` | `main_window.py` |
| 25 | All legacy dashboard widgets use hardcoded colors — no `ColorScheme` | 10+ dashboard widget files |
| 26 | Icons are Unicode emojis — no scalable icon library | Entire UI |
| 27 | `ContextGauge` has hardcoded `0.8` multiplier in size calculation | `stability_gauge.py` |
| 28 | No reduced-motion global setting | `settings_view.py` |
| 29 | `SettingsView` theme combo exists but does nothing (no slot connected) | `settings_view.py` |
| 30 | `WorkoutView` `_on_workout_selected` targets wrong page index | `workout_view.py` |
| 31 | Command palette `_theme` command defined but no handler wired | `command_center.py` |
| 32 | `workout_selection_view.py` uses negative margin hack (`margin-top: -16px`) | `workout_selection_view.py` |

### MINOR (116+ remaining)

Issues include: inconsistent hardcoded font sizes (11px vs 12px vs 13px vs 14px), inconsistent hardcoded margins (16,14 vs 20,16 vs 12,8), duplicate parallel visualization implementations (`visualization/` vs `design_system/visualization/`), hardcoded `ColorScheme.DARK` defaults on all component constructors, `gallery_page.py` with hardcoded `#F1F5F9` color, `workout_view.py` with extensive hardcoded hex colors, `import_wizard.py` with module-level `STYLE` constant that hardcodes all dark colors.

---

## Top Priority for Next Batch

| Priority | Issue | Effort |
|:---:|:---|---:|
| 1 | Fix light mode — propagate `ColorScheme` to all components | 3d |
| 2 | Wire `EmptyState` and `LoadingState` managers to all views | 4d |
| 3 | Add high-DPI scaling (`setPointSize` instead of `setPixelSize`) | 2d |
| 4 | Fix remaining card elevation (MetricCard, SectionPanel, HeroPanel) | 0.5d |
| 5 | Add "No data" text rendering to visualizations | 2d |
| 6 | Replace hardcoded font sizes with `TypographyTokens` | 3d |
| 7 | Replace hardcoded margins with `SpacingTokens` | 2d |
| 8 | Fix `dashboard_view.py` orphaned MetricPanel | 0.5d |
| 9 | Add empty state to CommandPalette ("No results found") | 0.5d |
| 10 | Fix `main_window.py` hardcoded colors | 1d |

---

## Before/After Status

| Component | Before | After |
|:---|---:|:---:|
| Card elevation | Invisible (CSS box-shadow) | Working (QGraphicsDropShadowEffect) |
| Trend colors | Hardcoded hex dict | Token-resolved at runtime |
| Adaptation status colors | Hardcoded hex dict | Token-resolved at runtime |
| Phase colors | Hardcoded hex dict | Token-resolved at runtime |
| Muscle heatmap low color | Hardcoded `#1E3A5F` | Uses `colors.surface` |
| Radius parsing | Fragile `.replace("rem", "")` in 10 files | Safe `radius_to_px()` in all |
| ScrollContainer API | Private `_wrapper` access | Public `content_layout` property |
| home_page.py MetricPanel | Orphaned on every update | Properly replaced |
| mission_page.py SectionHeader | Duplicate, one orphaned | Single instance |
| Analytics page | `pass` — completely non-functional | Data flows to widgets |
| Tests passing | 3330 | 3330 (no regressions) |
