# REP-002 — Product Stabilization Sprint

**Status:** Draft  
**Date:** 2026-07-06  
**Author:** AI Steward  
**Version:** GymOS v0.5.0 (Release Candidate 1)

---

## Executive Summary

GymOS v0.5.0-rc1 was audited across six dimensions: UX friction, visual consistency, interaction quality, performance, accessibility, and micro polish. The codebase is **architecturally ambitious but user-experience immature**.

**Key metrics:**
- **50+ known test failures** (48 documented + 2 new in latest run)
- **974 mypy errors** across 204 files
- **2118 ruff violations** (1789 auto-fixable)
- **~50 silent `except: pass` blocks** suppressing errors
- **~30 known limitations** (2 High severity)
- **105 release checklist items**, **0% complete**
- **2 competing navigation systems** (MainWindow sidebar + CommandCenter nav rail)
- **3 chart rendering approaches** (pyqtgraph, custom QPainter, QProgressBar)
- **2 theme systems** (design system tokens + command_center hardcoded theme)
- **3 duplicate color/value definitions** across views

**Net assessment:** The application is functionally capable but feels like a prototype. Users will encounter confusing dead ends, inconsistent styling, silent failures, and missing feedback loops. The stabilization sprint must focus on **eliminating silent failures, unifying visual language, fixing navigation, and adding interaction feedback**.

---

## Priority 1 — UX Friction: First-Time User Walkthrough

### Walkthrough: Fresh Launch to First Workout

```
1. Launch GymOS
   ├── [ISSUE #1] Splash screen shows "v{APP_VERSION}" in footer
   │   but sidebar shows hardcoded "v0.1.0 MVP"
   │   → User sees TWO different version numbers
   │
   ├── [ISSUE #2] Splash progress bar jumps in coarse steps
   │   (5%, 15%, 25%, 40%...) — feels stuttery, not smooth
   │
   └── [ISSUE #3] No first-launch delay explanation for what each
       step does — "Initializing infrastructure..." is meaningless
       to a user

2. Onboarding Wizard (WelcomeWizard)
   ├── [ISSUE #4] Name entered on Step 2 is NEVER PERSISTED
   │   to any database or config file — only used in a log line
   │
   ├── [ISSUE #5] Goal and experience level from Steps 2-3
   │   are NEVER used anywhere after the wizard closes
   │
   ├── [ISSUE #6] "Load demo data" checkbox has no visual
   │   indication of what data will be loaded — user doesn't
   │   know what they're getting
   │
   ├── [ISSUE #7] "Skip" button abandons ALL configuration
   │   with no confirmation — user loses all entered data
   │
   └── [ISSUE #8] After Finish → wizard closes, window shows
       immediately — no transition, no "Welcome" message,
       no tooltip hint. User is dropped into Dashboard cold.

3. Dashboard (first view)
   ├── [ISSUE #9] ALL metrics show "--" or "N/A" on first
   │   launch — Recovery Ring at 0%, Goal Ring empty,
   │   Readiness shows "N/A", Prediction risk at 0.0,
   │   Weekly Volume all zeros
   │   → This is technically correct but feels broken
   │
   ├── [ISSUE #10] "No active program" subtitle in Next Workout
   │   section — but no call-to-action to import/create one
   │
   ├── [ISSUE #11] "No recommendations available" / "No recent PRs"
   │   — these empty states are text-only, no icon, no action btn
   │
   ├── [ISSUE #12] Dashboard shows Recovery section and Prediction
   │   section even when no data exists — both show "--"
   │
   └── [ISSUE #13] The "Start Workout" button exists but clicking
       it when no program is loaded shows empty Workout Selection

4. Workout Selection
   ├── [ISSUE #14] If no program loaded, shows empty grid
   │   with no error message, no prompt to import
   │
   ├── [ISSUE #15] DayCards use mousePressEvent override
   │   instead of QPushButton or click signal — breaks
   │   keyboard accessibility completely
   │
   ├── [ISSUE #16] No "Back to Dashboard" button
   │   → user must click sidebar again
   │
   └── [ISSUE #17] Grid layout wraps every 3 cards but
       doesn't center when fewer than 3 days exist

5. Active Workout View
   ├── [ISSUE #18] **NAVIGATION BUG:** _on_workout_selected
   │   does `self._content.setCurrentIndex(5)` but WorkoutView
   │   is at index 7 → navigates to PRView instead
   │   (ui/main_window.py:226)
   │   SEVERITY: CRITICAL — workout view cannot be reached
   │
   ├── [ISSUE #19] ExerciseCard shows previous session hint
   │   ("prev: 60x10 RIR2") but styling is identical to
   │   other text — users may not notice it's a hint
   │
   ├── [ISSUE #20] RIR input has yellow (#FBBF24) text
   │   while other inputs use white (#F1F5F9) — inconsistent
   │
   ├── [ISSUE #21] No validation feedback when inputs are empty
   │   → Save & Finish saves zeros silently
   │
   ├── [ISSUE #22] "Save & Finish" button has no confirmation
   │   dialog — one click commits everything
   │
   └── [ISSUE #23] Duration is calculated as now - now (both
       from datetime.now()) → always 0 minutes
       (ui/workout_view.py:438-442)

6. Workout Summary Dialog
   ├── [ISSUE #24] Only "OK" button — no "Review Details"
   │   or "Back to Dashboard" — user is returned to Dashboard
   │   after closing
   │
   ├── [ISSUE #25] Separators use Unicode "─────" characters
   │   rather than styled QFrame dividers — inconsistent
   │
   └── [ISSUE #26] PR display depends on pr.label and
       pr.display_value — if these attributes don't exist,
       crashes silently

7. Progress View
   ├── [ISSUE #27] If pyqtgraph not installed, shows
   │   "Install pyqtgraph for charts" — dead end for user
   │
   ├── [ISSUE #28] Period selector ("Last 30/90 days/All time")
   │   doesn't actually filter — always queries 90 days
   │   (ui/progress_view.py:156-159)
   │
   ├── [ISSUE #29] No empty state handling for individual
   │   charts — if no body weight data, chart area is blank
   │
   └── [ISSUE #30] Axis labels are empty string — user cannot
       tell what the X/Y axes represent

8. Recovery Dashboard
   ├── [ISSUE #31] **Dashboard is optional** — only created
   │   if recovery_service is provided (often None)
   │   → User sees blank page
   │
   ├── [ISSUE #32] All widgets show "--" or 0 when no data
   │
   └── [ISSUE #33] No explanation of what recovery score means
       — just a number

9. Prediction Dashboard
   ├── [ISSUE #34] **Same optional issue** — silently blank
   │
   ├── [ISSUE #35] PredictionCard has hardcoded 260x140 fixed
   │   size — doesn't resize with window
   │
   └── [ISSUE #36] "Predictive Intelligence" subtitle is loaded
       with jargon — "Forecast engine — predicting athlete state
       across time horizons"

10. Settings
    ├── [ISSUE #37] "User" info hardcoded to a specific person
    │   (178 cm · 63.4 kg · Lean Bulk) — not read from profile
    │
    ├── [ISSUE #38] Theme dropdown exists but THEME TOGGLE
    │   DOES NOTHING — no event handler connected
    │
    ├── [ISSUE #39] Unit system dropdown exists but DOES NOTHING
    │   — no event handler connected
    │
    └── [ISSUE #40] Version shown as "GymOS v0.1.0 MVP" — should
        be v0.5.0 from shared.version

11. Import Wizard
    ├── [ISSUE #41] No file validation before clicking Next
    │   → preview page shows error, user must go Back
    │
    ├── [ISSUE #42] Uses QWizard default styling — inconsistent
    │   with the rest of the application's visual language
    │
    └── [ISSUE #43] No visual preview of exercises within days
        — just day names with counts
```

**Additional friction findings:**

| # | Location | Issue | Severity |
|---|----------|-------|----------|
| 44 | sidebar.py:189 | Hardcoded "v0.1.0 MVP" — wrong version | High |
| 45 | main.py:123-130 | Nutrition service starts even if irrelevant | Low |
| 46 | ui/dashboard/dashboard_view.py:201-210 | Goal ring shows 0/100 with no data — confusing | Medium |
| 47 | ui/dashboard/dashboard_view.py:253 | Risk derived from recovery score (100-rec)/100 — conflates two domains | Medium |
| 48 | ui/recovery/recovery_dashboard.py:54 | Title "RECOVERY DASHBOARD" — inconsistent capitalization with other views | Low |
| 49 | ui/prediction/prediction_dashboard.py:86-91 | Title/subtitle use different font sizes than other views | Medium |
| 50 | ui/command_center/command_center.py:82-92 | Uses emoji icons — inconsistent with rest of app | Low |

---

## Priority 2 — Visual Consistency Audit

### Color & Theme Inconsistencies

| # | Issue | Location | Detail |
|---|-------|----------|--------|
| V1 | Sidebar uses hardcoded colors not design tokens | `ui/main_window.py:38-58,74-77,147-148,156-157` | `#0F172A`, `#1E293B`, `#94A3B8`, `#818CF8` hardcoded instead of `DarkColorTokens` |
| V2 | Sidebar height fixed at 48px but no design token reference | `ui/main_window.py:36` | `setFixedHeight(48)` — no `SpacingTokens` or constant |
| V3 | PredictionCard uses hardcoded colors | `ui/prediction/prediction_dashboard.py:37-43` | `#1E293B`, `#334155`, `#818CF8` hardcoded |
| V4 | WelcomeWizard creates its own theme instance | `ui/experience/welcome_wizard.py:55,65-66` | Calls `color_from_scheme()` directly, bypasses global theme |
| V5 | ImportWizard uses completely separate QSS string | `ui/import_wizard.py:14-37` | `STYLE` constant defines its own color scheme — no `global_stylesheet()` |
| V6 | Two duplicate theme definitions | `ui/design_system/theme.py` vs `ui/command_center/theme.py` | `global_stylesheet()` and `Style/ C` class define overlapping styles |
| V7 | SemanticColorTokens defined but never used | `ui/design_system/tokens/color.py:182-207` | Dead code |
| V8 | HighContrastColorTokens defined but theme switching never wired up | `ui/design_system/tokens/color.py:127-179` | No code calls `color_from_scheme(ColorScheme.HIGH_CONTRAST)` |
| V9 | Dashboard uses `DashboardCard` (QFrame) but RecoveryDashboard subclasses it | `ui/recovery/recovery_dashboard.py:46` vs `ui/prediction/prediction_dashboard.py:71` | PredictionDashboard extends QWidget directly — different base class for same concept |

### Typography Inconsistencies

| # | Issue | Values |
|---|-------|--------|
| V10 | Page headers: 3 different sizes across views | 24px (WorkoutSelection, Progress, PR, Settings), 22px (WorkoutSummary title), 20px (Dashboard header in MainWindow) |
| V11 | Card titles: 4 different sizes | 18px (ExerciseCard, DayCard), 16px (setting section title), 15px (ChartWidget, PRCard), 14px (MetricCard) |
| V12 | Metric values: no consistent scale | 32px (Dashboard recovery score, QLabel), 26px (PredictionCard value), 22px (PRCard value), 20px (KPI) |
| V13 | Body text: 4 different sizes | 14px (sidebar buttons), 13px (most labels), 12px (descriptions, metadata), 11px (badges, date labels) |
| V14 | WelcomeWizard uses QFont("Inter", ...) directly | Bypasses `TypographyTokens` from design system |
| V15 | PredictionCard uses `text-transform: uppercase` | No other view uses uppercase styling — inconsistent |

### Spacing & Padding Inconsistencies

| # | Issue | Values |
|---|-------|--------|
| V16 | Card padding varies | 20px (DayCard), 16px (ExerciseCard, ChartWidget, PRCard, EmptyChart), 14px (PredictionCard), 12px (AppCard, dialog buttons) |
| V17 | Content margins vary per view | 32px (WorkoutSelection, Progress, PR, Settings), 32/24/32/32 (Dashboard), 20px (PredictionDashboard), 0px (WorkoutView) |
| V18 | Grid spacing varies | 16px (WorkoutSelection, Dashboard editorial grid), 12px (PRView grid, Prediction cards) |
| V19 | Layout spacing varies | 24px (WorkoutSelection, Settings), 16px (Progress, PR), 12px (WorkoutSummary dialog) |

### Border Radius Inconsistencies

| # | Element | Radius |
|---|---------|--------|
| V20 | DayCard | 16px |
| V21 | ExerciseCard, ChartWidget, EmptyChart, PRCard, info_card | 12px |
| V22 | DashboardCard | 8px (inherited from AppCard) |
| V23 | AppCard | 8px |
| V24 | Buttons | 8px |
| V25 | Input fields | 6px |
| V26 | Sidebar buttons | 8px |
| V27 | ImportWizard progress bar | 8px (while global QProgressBar uses 4px) |

### Alignment & Sizing Inconsistencies

| # | Issue | Detail |
|---|-------|--------|
| V28 | PredictionCard fixed size 260x140 | Doesn't resize with window — vs DayCard minimum 200x140 |
| V29 | ChartWidget creates 2-column grid but no responsive behavior | Progress charts stack vertically rather than side-by-side |
| V30 | RecoveryDashboard columns unequal width | Score/Readiness/Trend in one row, SleepStress/Fatigue/Deload in next — no proportional sizing |
| V31 | WorkoutSelection grid wraps at 3 columns but doesn't center | Empty area on right when 1-2 days |
| V32 | Sidebar and CommandCenter nav rail exist simultaneously | Two competing nav systems with different visual language |
| V33 | Dashboard section titles use SectionHeader class | But Recovery/Prediction dashboards don't use it — different styling approach |
| V34 | EmptyState component exists but NOT USED anywhere | Dashboard uses plain QLabel for "No recommendations" etc. |
| V35 | StatusBadge component exists but NOT USED in PR cards | PR type badges use custom QLabel with inline styling instead |
| V36 | NotificationToast component exists but NOT WIRED | Notification system never calls it |
| V37 | SkeletonLoader component exists but NOT USED | No loading skeleton on any page |
| V38 | DialogTemplate component exists but NONE of the 13 dialogs use it | All implement custom QDialog with inline styling |
| V39 | InsightCard component exists but NOT USED | Never instantiated |
| V40 | WarningBanner component exists but NOT USED | Never instantiated |

---

## Priority 3 — Interaction Audit

### Navigation Issues

| # | Issue | Location | Detail |
|---|-------|----------|--------|
| I1 | **WorkoutView unreachable** | `ui/main_window.py:226` | `_on_workout_selected` sets index to 5 (PRView) — should be 7 |
| I2 | **Command Center + MainWindow sidebar = 2 navigation systems** | Both | User can use either — state can desync. No unified navigation |
| I3 | WorkoutView "Back" goes to selection, not dashboard | `ui/main_window.py:134-136` | Extra click required |
| I4 | Import wizard not connected from dashboard if no prog_mgr | `ui/main_window.py:178-185` | Import button only shows when prog_mgr exists — chicken/egg |
| I5 | Breadcrumb shows incorrect parent mapping | `ui/command_center/command_center.py:205-211` | "mission" parent is "intelligence" — unintuitive |
| I6 | No keyboard navigation between sidebar items | `ui/main_window.py` | Tab skips directly to content area |
| I7 | Import Wizard `QWizard.Accepted` redefined as `Done` | `ui/import_wizard.py:189` | Unnecessary alias |

### Button & Click Issues

| # | Issue | Detail |
|---|-------|--------|
| I8 | DayCard uses mousePressEvent override | Breaks keyboard/spatial navigation — should be QPushButton |
| I9 | Save & Finish has no confirmation | One-click save with no validation — risk of saving zeros |
| I10 | Finish button green (#4ADE80) — different from primary (#818CF8) | Inconsistent button hierarchy |
| I11 | Theme/Unit dropdowns do nothing | Connected to no event handler — user confusion |
| I12 | Dashboard "Start Workout" button goes to empty grid if no program | No error message or redirect |
| I13 | No keyboard shortcuts for any MainWindow view | Only Ctrl+K for Command Center |
| I14 | "Import Program" sidebar button uses thin separator line styling | Different visual treatment — looks like secondary action |
| I15 | Export buttons do not show progress | JSON/CSV export blocks UI with no progress bar |

### Feedback & State Issues

| # | Issue | Detail |
|---|-------|--------|
| I16 | No loading states on any page | Database queries cause visible frame-freeze but no spinner |
| I17 | Silent error suppression (~50 `except: pass`) | Data silently shows "--" with no log or toast |
| I18 | No success animation after saving workout | Dialog closes, user is on dashboard — no confirmation |
| I19 | No hover state on some clickable elements | DayCard has hover border but PRCard does not |
| I20 | No focus state on custom elements | `QSS: QWidget:focus { outline: none }` removes all focus indicators |
| I21 | Period selector triggers refresh but doesn't filter | Confusing — user expects data to change |
| I22 | Recovery dashboard refreshes ALL widgets even on single update | No incremental update — full re-render |
| I23 | Command palette Ctrl+K opens QDialog — not inline | Blocks interaction with main window |
| I24 | No undo mechanism anywhere | Accidental actions (save, export) are irreversible |
| I25 | No error toast on failed database writes | Failures suppressed silently |

### Dialog Issues

| # | Issue | Detail |
|---|-------|--------|
| I26 | WorkoutSummary only has "OK" | No "Review" or "View PRs" action |
| I27 | 13 dialogs exist, 0 use DialogTemplate | Massive code duplication |
| I28 | WelcomeWizard has Skip + Back + Next — Back implementation checks step > 0 but initial step is 0 | Works but fragile |
| I29 | LogWeightDialog uses hardcoded current_weight=70.0 | Should read actual current weight |
| I30 | GoalAdjustmentDialog shows QMessageBox on adjustment | No actual persistence — mock dialog |

---

## Priority 4 — Performance Observations

| # | Observation | Detail |
|---|-------------|--------|
| P1 | Dashboard fetch exceeds 100ms budget | `tests/ui/test_dashboard.py:287` — avg 137ms |
| P2 | All infrastructure initialized at startup | Nutrition, Recovery, Prediction engines loaded even if unused |
| P3 | DecisionEngine imported at Dashboard construction | `dashboard_view.py:60-63` — heavy import chain |
| P4 | ProgressView creates pyqtgraph widgets unconditionally | Even when no data exists |
| P5 | CommandCenter refreshes ALL pages every 60s | `command_center.py:192-195` — 10 pages refreshed even if hidden |
| P6 | No lazy loading of expensive widgets | 8 recovery widgets, 6 prediction widgets all created upfront |
| P7 | RecoveryDashboardData created fresh every refresh | No caching of snapshot data |
| P8 | 779 unused imports across codebase | `ruff F401` — import overhead on startup |
| P9 | Empty stub files in shared/ (exceptions, constants, validators, helpers, types) | 5 directories with `__init__.py` only — import cost |
| P10 | Alembic migration check on every startup | `main.py:54-62` — runs compatibility check + migration each launch |

---

## Priority 5 — Accessibility Observations

| # | Observation | Detail |
|---|-------------|--------|
| A1 | No tab order configured on any view | User cannot Tab through form fields logically |
| A2 | DayCard uses mousePressEvent — unreachable by keyboard | Cannot select workout days without mouse |
| A3 | `QWidget:focus { outline: none }` in global theme | Destroys all keyboard focus indicators |
| A4 | No `QAccessible` interfaces set on any widget | Screen readers get no semantic information |
| A5 | No screen reader labels (`setAccessibleName`, `setAccessibleDescription`) | Throughout |
| A6 | Color contrast not verified | Custom color scheme not checked against WCAG AA |
| A7 | Font sizes in px — may not respect OS scaling | `font-size: 13px` etc. should use pt |
| A8 | Custom QPainter charts have no text alternative | Rings, gauges, meters are visual-only |
| A9 | No reduced-motion media query or option | Animations (splash spinner) cannot be disabled |
| A10 | No Large Text mode support | All fonts scale from same base |
| A11 | Sidebar has no Alt+letter shortcuts | Ctrl+1..7 or Alt+D, W, P etc. not implemented |
| A12 | Tooltips not used on any icon-only element | Unicode emoji icons have no accessible name |
| A13 | No High Contrast theme wired up | Theme definition exists but never applied |
| A14 | Error messages use color-only indicators | Red text without icon or text prefix |
| A15 | LoadingOverlay component exists but blocks interaction | No cancel/escape handling |

---

## Priority 6 — Micro Polish

### Wording & Messaging

| # | Current | Suggestion |
|---|---------|------------|
| M1 | "v0.1.0 MVP" | "v{APP_VERSION}" from shared.version |
| M2 | "Initializing infrastructure..." | "Setting up database..." |
| M3 | "No active program" (subtitle) | "No program loaded — import one to get started" |
| M4 | "No recommendations available." | "Complete a workout to receive personalized recommendations" |
| M5 | "No recent PRs." | "Push yourself — PRs will appear here after your best sessions" |
| M6 | "Predictive Intelligence" | "Forecast & Insights" |
| M7 | "Forecast engine — predicting athlete state across time horizons" | "Predict your progress, manage risk, and explore what-if scenarios" |
| M8 | "RECOVERY DASHBOARD" (all caps) | "Recovery Dashboard" (title case) |
| M9 | "Load Demo Data?" | "Start with sample data?" (less technical) |
| M10 | Duration shows "0 min" after first workout | Track actual elapsed time |
| M11 | "GymOS v0.1.0 MVP" in settings | "GymOS v{actual version}" |
| M12 | "Export as JSON" button label | Add icon or description of what gets exported |
| M13 | "No data" empty state | Context-specific messages per section |

### Animation & Transition

| # | Current | Suggestion |
|---|---------|------------|
| M14 | No page transition when switching views | Add subtle fade or slide between pages |
| M15 | Splash progress jumps in coarse steps | Animate smoothly between declared progress points |
| M16 | No success animation after workout save | Brief checkmark or confetti before summary dialog |
| M17 | No loading spinner during database queries | Use SkeletonLoader or LoadingOverlay |
| M18 | No theme transition animation | Gradual color transition when switching dark/light |

### Visual Hierarchy

| # | Current | Suggestion |
|---|---------|------------|
| M19 | All sidebar buttons same weight | Active page should have stronger visual distinction |
| M20 | PredictionCard value and PRCard value same size (22px/26px) | Differentiate by importance |
| M21 | Dashboard hero and middle sections use same spacing | Hero should have more visual breathing room |
| M22 | Separator lines use bottom-border on items | Consistent divider component |
| M23 | Settings cards have no icon or visual hierarchy | Add icons to section headers |

---

## Quick Wins (<30 minutes each)

| Ref | Fix | Effort | Impact | File |
|-----|-----|--------|--------|------|
| QW1 | Fix version string in sidebar | 2 min | Medium | `ui/main_window.py:189` |
| QW2 | Fix WorkoutView navigation index (5→7) | 2 min | **Critical** | `ui/main_window.py:226` |
| QW3 | Set `QAccessibleName` on sidebar buttons | 5 min | Low | `ui/main_window.py` |
| QW4 | Replace hardcoded colors in sidebar with tokens | 10 min | Medium | `ui/main_window.py:38-58,147-148` |
| QW5 | Remove `outline: none` from global QWidget:focus | 2 min | **High** | `ui/design_system/theme.py:57-59` |
| QW6 | Fix subtitle wording on prediction page | 2 min | Low | `ui/prediction/prediction_dashboard.py:90-91` |
| QW7 | Add accessible names to DayCard | 5 min | Medium | `ui/workout_selection_view.py` |
| QW8 | Add _clear_grid protection during refresh | 5 min | Low | `ui/workout_selection_view.py:102` |
| QW9 | Remove unused `SemanticColorTokens` | 2 min | Low | `ui/design_system/tokens/color.py:182-207` |
| QW10 | Fix "RECOVERY DASHBOARD" capitalization | 2 min | Low | `ui/recovery/recovery_dashboard.py:54` |
| QW11 | Replace Unicode separators with QFrame in WorkoutSummary | 5 min | Low | `ui/workout_view.py:224,238,258` |
| QW12 | Remove unnecessary `ImportWizard.Done` alias | 2 min | Low | `ui/import_wizard.py:189` |
| QW13 | Change "MVP" version label to use shared.version | 5 min | Medium | `ui/settings_view.py:64` |
| QW14 | Remove hardcoded user info from settings | 5 min | Medium | `ui/settings_view.py:65-67` |
| QW15 | Fix splash progress step sizes (smooth interpolation) | 10 min | Medium | `ui/splash/splash_screen.py` |
| QW16 | Add placeholder text to empty ComboBoxes | 2 min | Low | `ui/progress_view.py` |
| QW17 | Connect theme dropdown to actually change theme | 15 min | Medium | `ui/settings_view.py` |
| QW18 | Fix mousPressEvent spelling in DayCard (no override) | 5 min | Low | `ui/workout_selection_view.py:115` |
| QW19 | Remove empty `resources/` package files | 2 min | Low | `resources/*/__init__.py` |
| QW20 | Fix 1789 auto-fixable ruff violations | 15 min | High | Run `ruff check --fix .` |

**Total estimated quick-win effort:** ~2 hours  
**Estimated impact on user experience:** Significant (fixes 6 UX frictions, 4 visual inconsistencies, 1 critical bug)

---

## Medium Tasks (30 min – 2 hours each)

| Ref | Task | Effort | Impact |
|-----|------|--------|--------|
| M1 | Add EmptyState component usage to Dashbaord sections | 1 hr | Medium |
| M2 | Wire theme toggle to switch dark/light | 1 hr | Medium |
| M3 | Wire unit system toggle | 1 hr | Medium |
| M4 | Add confirmation dialog before Save & Finish | 30 min | High |
| M5 | Add tab order to WorkoutView exercise form | 1 hr | High |
| M6 | Connect period selector to actually filter data | 30 min | Medium |
| M7 | Add loading skeleton to Dashboard | 1.5 hr | Medium |
| M8 | Extract shared button styles to design system | 1 hr | Medium |
| M9 | Standardize card border-radius (unify to 12px) | 30 min | Low |
| M10 | Add error toast for silent `except: pass` locations | 2 hr | High |
| M11 | Implement workout duration tracking | 30 min | High |
| M12 | Add "Review PRs" button to WorkoutSummaryDialog | 30 min | Medium |
| M13 | Unify color usage across views to design tokens | 2 hr | Medium |
| M14 | Add Alt+number shortcuts to sidebar | 1 hr | Medium |
| M15 | Implement stub page state for Recovery/Prediction when service is None | 30 min | High |
| M16 | Create content area between hero and middle sections | 30 min | Low |
| M17 | Add hover elevation effect to cards | 1 hr | Low |
| M18 | Fix 50 `except: pass` blocks (log at minimum) | 2 hr | Critical |
| M19 | Add user data persistence from WelcomeWizard | 1 hr | Medium |
| M20 | Remove duplicate CommandCenter theme in favor of design tokens | 1 hr | Medium |

**Total estimated medium-task effort:** ~24 hours  
**Estimated impact:** Transforms app from "prototype" to "polished" feel

---

## Large Tasks (2+ hours each)

| Ref | Task | Effort | Impact |
|-----|------|--------|--------|
| L1 | Unify MainWindow sidebar and CommandCenter navigation | 8 hr | **Highest** |
| L2 | Add full keyboard navigation to all views | 6 hr | High |
| L3 | Resolve 974 mypy errors systematically | 12 hr | High |
| L4 | Resolve 48 test failures | 8 hr | High |
| L5 | Add proper empty/loading/error states to all 10 CommandCenter pages | 6 hr | Medium |
| L6 | Replace all 13 custom dialogs with DialogTemplate | 4 hr | Medium |
| L7 | Implement WCAG AA color contrast across all themes | 3 hr | Medium |
| L8 | Add QAccessible interfaces to all interactive elements | 6 hr | Medium |
| L9 | Implement responsive layout for Dashboard and views | 4 hr | Medium |
| L10 | Performance optimization: lazy-load expensive widgets | 4 hr | Medium |
| L11 | Implement Undo for workout save | 3 hr | Medium |
| L12 | Add comprehensive error boundary + recovery UX | 4 hr | High |
| L13 | Remove pyqtgraph dependency — use custom QPainter consistently | 4 hr | Medium |
| L14 | Add font scaling support (settings → large text) | 2 hr | Low |
| L15 | Unified event log / notification system connected to toasts | 4 hr | Medium |

**Total estimated large-task effort:** ~80 hours  
**Estimated impact:** Production-ready quality

---

## Performance Benchmarks

| Metric | Current | Target | Delta |
|--------|---------|--------|-------|
| App startup time | Not measured | < 3s | ? |
| Dashboard fetch time | 137ms avg | < 100ms | -27% |
| Page switch latency | Not measured | < 100ms | ? |
| Dialog open time | Not measured | < 200ms | ? |
| Workout save + PR detection | Not measured | < 500ms | ? |
| Command palette open | Not measured | < 200ms | ? |
| Memory usage (idle) | Not measured | < 200MB | ? |
| Database query (100 sessions) | Not measured | < 50ms | ? |

**Recommendation:** Profile startup time and dashboard fetch before/after optimization.

---

## Accessibility Compliance Gap

| WCAG Criterion | Status | Notes |
|----------------|--------|-------|
| 1.1.1 Non-text Content | FAIL | Custom rings/charts have no text alternative |
| 1.3.1 Info and Relationships | FAIL | No semantic structure (ARIA roles) |
| 1.4.1 Use of Color | FAIL | Status indicators are color-only |
| 1.4.3 Contrast (Minimum) | NOT TESTED | Custom color scheme not audited |
| 1.4.4 Resize Text | FAIL | px font sizes don't scale |
| 1.4.10 Reflow | FAIL | Fixed-size PredictionCard breaks at zoom |
| 2.1.1 Keyboard | FAIL | DayCard not keyboard accessible |
| 2.4.3 Focus Order | FAIL | No tab order defined |
| 2.4.7 Focus Visible | FAIL | `outline: none` removes focus ring |
| 3.3.1 Error Identification | FAIL | Silent `except: pass` hides errors |
| 4.1.2 Name, Role, Value | FAIL | No QAccessible interfaces |

---

## Summary of Impact Estimates

| Category | Quick Wins (<30m) | Medium (30m-2h) | Large (2h+) | Total Estimated Impact |
|----------|------------------|-----------------|-------------|----------------------|
| UX Friction | 8 fixes | 6 fixes | 3 fixes | Eliminates 80% of first-launch confusion |
| Visual Consistency | 5 fixes | 5 fixes | 2 fixes | Unifies visual language across all views |
| Interaction | 4 fixes | 6 fixes | 4 fixes | Fixes critical navigation bug, adds keyboard support |
| Performance | 1 fix | 3 fixes | 4 fixes | Reduces startup + fetch latency by ~30% |
| Accessibility | 4 fixes | 4 fixes | 4 fixes | Achieves partial WCAG A compliance |
| Micro Polish | 6 fixes | 4 fixes | 2 fixes | Professional-grade feel |
| Code Quality | 2 fixes | 4 fixes | 3 fixes | Resolves 50% of mypy/ruff/test issues |

**Total tasks:** 20 quick + 20 medium + 15 large = **55 tasks**  
**Total estimated effort:** ~106 hours  
**Overall impact:** Transforms GymOS from technology demo to production-quality desktop application

---

## Recommended Sprint Order

### Sprint A — Critical Bugs & Silent Failures (~8 hours)
1. Fix WorkoutView navigation (QW2) — **2 min, CRITICAL**
2. Add logging to all `except: pass` blocks (M18) — **2 hr**
3. Fix `outline: none` focus removal (QW5) — **2 min**
4. Auto-fix 1789 ruff violations (QW20) — **15 min**
5. Fix workout duration tracking (M11) — **30 min**
6. Wire stub pages for missing Recovery/Prediction services (M15) — **30 min**
7. Add confirmation before Save & Finish (M4) — **30 min**
8. Fix import wizard file validation (part of M1) — **30 min**
9. Fix Period selector/Muscle chart data filter (M6) — **30 min**
10. Connect empty state texts to use EmptyState component (M1) — **1 hr**

### Sprint B — Visual Unification (~8 hours)
1. Migrate sidebar to design tokens (QW4) — **10 min**
2. Unify card border-radius to 12px (M9) — **30 min**
3. Extract shared button styles (M8) — **1 hr**
4. Unify color usage across views (M13) — **2 hr**
5. Remove duplicate CommandCenter theme (M20) — **1 hr**
6. Replace ImportWizard hardcoded QSS with design system — **30 min**
7. Fix version strings throughout (QW1, QW13) — **10 min**
8. Fix WelcomeWizard font usage to use TypographyTokens — **30 min**
9. Standardize font sizes across views — **1 hr**
10. Remove dead code (QW9, QW12, QW19) — **10 min**

### Sprint C — Interaction & Navigation (~8 hours)
1. Add keyboard shortcuts to sidebar (M14) — **1 hr**
2. Add tab order to WorkoutView (M5) — **1 hr**
3. Add "Review" button to WorkoutSummaryDialog (M12) — **30 min**
4. Wire theme toggle (M2) — **1 hr**
5. Wire unit toggle (M3) — **1 hr**
6. Add hover elevation to cards (M17) — **1 hr**
7. Add accessible names to all interactive elements (QW3, QW7) — **30 min**
8. Fix DayCard to use click signal (QW18) — **5 min**
9. Add status feedback to export buttons — **30 min**
10. Fix settings hardcoded user data (QW14) — **5 min**

### Sprint D — Polish & Performance (~8 hours)
1. Recover from unavailable services gracefully — **1 hr**
2. Add loading skeletons (M7) — **1.5 hr**
3. Persist user data from WelcomeWizard (M19) — **1 hr**
4. Smooth splash progress (QW15) — **10 min**
5. Fix all inactive UI controls — **1 hr**
6. Add error toast to suppressed exceptions — **2 hr**
7. Profile and optimize Dashboard fetch — **1 hr**
8. Lazy-load CommandCenter pages — **2 hr**

---

## Appendix: Tool Output References

- **Test failures:** `tests_out3.txt` (2 failed, 299 passed)
- **Full test audit:** `docs/TEST_FAILURE_AUDIT.md` (48 known failures)
- **Mypy errors:** Run `mypy . --ignore-missing-imports` (974 errors)
- **Ruff violations:** Run `ruff check .` (2118 violations)
- **Known limitations:** `docs/KNOWN_LIMITATIONS.md` (30 items)
- **Release checklist:** `docs/V1_RELEASE_CHECKLIST.md` (105 items, 0% complete)
- **Exception audit:** `docs/EXCEPTION_HANDLING_AUDIT.md` (~50 suppressed)
