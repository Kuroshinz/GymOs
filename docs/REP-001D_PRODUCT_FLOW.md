# REP-001D — GymOS Product Flow Validation

**Status:** Draft  
**Date:** 2026-07-06  
**Auditor:** OpenCode  
**Method:** Source code trace of every user-facing path

---

## Table of Contents

1. [First Run Journey](#1-first-run-journey)
2. [User Journey Maps](#2-user-journey-maps)
3. [Interaction Layer Audit](#3-interaction-layer-audit)
4. [Visual Consistency Audit](#4-visual-consistency-audit)
5. [Product Experience by Persona](#5-product-experience-by-persona)
6. [Dead Ends & UX Blockers](#6-dead-ends--ux-blockers)
7. [Missing Screens & Dialogs](#7-missing-screens--dialogs)
8. [Confusing Interactions](#8-confusing-interactions)
9. [Prioritized Fixes](#9-prioritized-fixes)

---

## 1. First Run Journey

### Launch Sequence (main.py)

```
main()
  ├─ init_db(DB_PATH)                                    → creates data/gymos.db
  ├─ GymDatabase(DB_PATH)                                → opens SQLite
  ├─ ProgramManager(DB_PATH)
  │   ├─ repository.count() == 0? → YES (first run)
  │   └─ CANONICAL_PROGRAM exists? → YES if program.json present
  │       └─ import_save_and_activate()                  → imports seed data
  ├─ NutritionRepository, NutritionService, EventBus     → wired silently
  ├─ RecoveryRepository, RecoveryService                 → wired silently
  ├─ PredictionRepository, PredictionService             → wired silently
  ├─ DecisionEngine.from_production()                    → wired silently
  ├─ NutritionSubscriber, RecoverySubscriber             → wired silently
  ├─ QApplication(sys.argv)                              → Fusion style set
  ├─ MainWindow(db, prog_mgr, nutrition, recovery, prediction)
  │   ├─ ExperienceManager(self)
  │   │   ├─ AnimationManager, LayoutEngine, NavigationEngine
  │   │   ├─ ShortcutManager, CommandPaletteEngine, SearchProvider
  │   │   ├─ NotificationCenter, LoadingStateManager, EmptyStateManager
  │   │   ├─ FocusMode, WindowLayoutManager, WorkspaceManager
  │   │   ├─ WorkflowEngine, ThemeTransitionManager
  │   │   └─ initialize()
  │   │       ├─ _register_builtin_shortcuts()           → Ctrl+K, Alt+Left/Right, etc.
  │   │       ├─ _register_builtin_commands()            → 7 commands
  │   │       └─ _register_search_providers()            → commands, pages, shortcuts
  │   ├─ _build_sidebar()                                → 220px dark sidebar
  │   ├─ _build_content()                                → QStackedWidget
  │   │   ├─ DashboardView (index 0)                     → FULL WIDGET CREATION
  │   │   │   ├─ DashboardController                     → fetches DB data synchronously
  │   │   │   └─ 11 child widgets created immediately
  │   │   ├─ WorkoutSelectionView (index 1)
  │   │   ├─ ProgressView (index 2)
  │   │   ├─ RecoveryDashboard (index 3)                 → if recovery_service
  │   │   ├─ PredictionDashboard (index 4)               → if prediction_service
  │   │   ├─ PRView (index 5)
  │   │   ├─ SettingsView (index 6)
  │   │   └─ WorkoutView (index 7)
  │   ├─ integrate_with_command_center(experience)       → routes registered
  │   └─ _switch_to(0)                                   → shows Dashboard
  ├─ window.show()
  └─ app.exec()
```

### First-Run Experience (No program.json, no data)

| Step | What Happens | User Sees | Issue |
|------|-------------|-----------|-------|
| 1 | Launch | ~1-2s black window, then dark UI appears | No splash screen |
| 2 | Dashboard renders | Hero: "Today's Mission" with "--" values, Recovery Ring at 0, "No Active Program" in Next Workout, "No recommendations" | All empty states are bare text labels |
| 3 | Sidebar shows | GymOS logo, 7 nav items, Import Program button, "v0.1.0 MVP" | No welcome message |
| 4 | Click "Workout" | Empty grid — no day cards (no active program) | User has no path forward |
| 5 | Click "Import Program" | 3-step wizard opens | Good UX |
| 6 | After import | Dashboard refreshes, workout days appear | Functional |
| 7 | Click Settings | Hardcoded user info: "178 cm · 63.4 kg · Lean Bulk → 72-75 kg" | Fake/placeholder data shown as real |

### Launch UX Issues

| # | Issue | Severity |
|---|-------|----------|
| L1 | No splash screen — user sees black window for 1-2s | Medium |
| L2 | All workspace pages created upfront (8+ views with widgets) — slow startup | Medium |
| L3 | No loading indicator during DB/program initialization | High |
| L4 | Dashboard renders all child widgets on construction, not on data arrival | Medium |
| L5 | No first-run dialog, tour, or "Getting Started" guide | **Critical** |
| L6 | Settings shows hardcoded placeholder user data as if real | **High** |
| L7 | No indication that Import Program is the required first action | High |
| L8 | No error state if `program.json` missing and no program imported — app is stuck in empty state | High |

---

## 2. User Journey Maps

### 2.1 Workout Journey

```
SIDEBAR "Workout"
  ↓
WorkoutSelectionView.refresh()
  ├─ Has active program? → YES → shows DayCard grid (Push, Pull, Legs, etc.)
  ├─ Has active program? → NO  → falls back to "PPL-UL" hardcoded query
  └─ Still no days? → empty grid  [DEAD END]
  ↓
User clicks DayCard
  ↓
WorkoutView.load_day(day_name)
  ├─ Fetches program day exercises
  ├─ ProgressionEngine.get_recommendation() for each exercise  [SYNC DB CALL]
  └─ ExerciseCard × N with SetRow × target_sets
      ↓
User fills Weight × Reps × RIR for each set
  ↓
User clicks "Save & Finish"
  ├─ Builds WorkoutSession
  ├─ db.save_session(session)
  ├─ PREngine.detect_prs(saved)
  ├─ RecoveryEngine.analyse_session(saved)
  ├─ ProgressionEngine.analyse_exercise() per exercise
  └─ WorkoutSummaryDialog (PRs, Recommendations, Recovery Flags)
      ↓
User clicks OK → navigated back to Dashboard
```

### Workout Journey Issues

| # | Issue | Severity |
|---|-------|----------|
| W1 | No rest timer between sets | Medium |
| W2 | No superset grouping support | Low |
| W3 | No warmup set distinction (all sets logged as working sets) | Medium |
| W4 | No ability to edit a past workout | **High** |
| W5 | No ability to see the current workout mid-session (if app closed) | **Critical** |
| W6 | Weight/reps fields require exact input — no partial set logging | Medium |
| W7 | "Back" button during workout discards all input silently | **High** |
| W8 | No confirmation dialog on "Save & Finish" — one-click save | Medium |
| W9 | Progression recommendations computed synchronously on UI thread — can lag with many exercises | Medium |
| W10 | Exercise list scroll area has no "jump to exercise" feature | Low |
| W11 | No "complete this exercise early" option | Low |
| W12 | No visual indicator of which exercises are done | Low |

### 2.2 Progress Journey

```
SIDEBAR "Progress"
  ↓
ProgressView.refresh()
  ├─ Period selector: "Last 30 days", "Last 90 days", "All time"
  │   └─ NOTE: period selector does NOT actually change query — all queries use `.get_body_weight_history(days=90)`
  │       [BUG: period selection is cosmetic]
  ├─ Body Weight Chart (pyqtgraph required)
  │   └─ No pyqtgraph? → "Install pyqtgraph for charts" placeholder
  ├─ Weekly Volume Chart (pyqtgraph required)
  └─ Muscle Volume Chart (pyqtgraph required)
```

### Progress Journey Issues

| # | Issue | Severity |
|---|-------|----------|
| P1 | Period selector has no effect — all charts use hardcoded 90-day window | **Bug** |
| P2 | pyqtgraph is optional dependency — charts silently fail if not installed | **High** |
| P3 | No loading state while queries execute | Medium |
| P4 | No exercise-level progress tracking (PR history over time) | Medium |
| P5 | No strength curve visualization (estimated 1RM over time) | Low |
| P6 | No body composition tracking (BF%, measurements) | Low |
| P7 | No export of chart data (right-click save) | Low |
| P8 | ChartWidget.plot() called on every refresh — no diff/update optimization | Low |

### 2.3 Recovery Journey

```
SIDEBAR "Recovery"
  ↓
MainWindow._refresh_recovery()
  ├─ recovery_service.get_snapshot()
  ├─ recovery_service.get_recent_scores(days=7)
  ├─ recovery_service.get_trend(days=14)
  ├─ recovery_service.get_weekly_averages(weeks=4)
  ├─ recovery_service.get_active_deload()
  ├─ recovery_service.get_recommendations(days=1)
  └─ Builds RecoveryDashboardData → RecoveryDashboard.refresh()
      └─ 8 child widgets updated
```

### Recovery Journey Issues

| # | Issue | Severity |
|---|-------|----------|
| R1 | Recovery view is **not created** if `recovery_service` is None — but it's always created in main.py | Low |
| R2 | No loading state during 6 sequential service calls | Medium |
| R3 | No empty state — widgets render with 0.0 values and empty flag lists | Medium |
| R4 | Recovery data is fetched every time user clicks "Recovery" — no caching | Medium |
| R5 | `hasattr(snapshot, "readiness_level")` defensive checks suggest fragile API contract | Medium |
| R6 | No deload scheduling action — deload status is read-only | Medium |

### 2.4 Prediction Journey

```
SIDEBAR "Predictions"
  ↓
MainWindow._refresh_predictions()
  ├─ prediction_service.generate_all_predictions()
  ├─ PredictionFormatter.prediction_result_to_view_model(result)
  ├─ Builds PredictionDashboardData
  └─ PredictionDashboard.refresh()
      ├─ 8 prediction cards rendered
      └─ 5 child widgets updated (scenario, risk, explainability, confidence, reason tree)
```

### Prediction Journey Issues

| # | Issue | Severity |
|---|-------|----------|
| D1 | `generate_all_predictions()` is synchronous and potentially slow — blocks UI | **High** |
| D2 | No loading indicator during prediction computation | High |
| D3 | No empty/error state for missing prediction data | Medium |
| D4 | Prediction dashboard requires `prediction_service` — silently skipped if absent | Low |
| D5 | Cards grid has no scroll — 8 cards in 2×4 layout may overflow on small screens | Medium |

### 2.5 Settings Journey

```
SIDEBAR "Settings"
  ↓
SettingsView.refresh()
  ├─ Shows hardcoded user info ("178 cm · 63.4 kg")
  ├─ Unit System combo (kg/lbs)  → NO PERSISTENCE
  ├─ Theme combo (Dark/Light)    → NO PERSISTENCE
  ├─ Export JSON button          → functional
  └─ Export CSV button           → functional
```

### Settings Journey Issues

| # | Issue | Severity |
|---|-------|----------|
| S1 | **No preferences are saved** — unit system and theme changes are lost on restart | **Critical** |
| S2 | Hardcoded placeholder user info presented as real data (height, weight, goal, focus muscles) | **High** |
| S3 | No user profile editing — cannot change name, weight, height | High |
| S4 | No body weight logging — "Log Weight" button on Dashboard navigates here but there's no logging UI | **Bug** |
| S5 | Export uses `list_sessions(limit=1000)` — silently truncates if >1000 sessions | Medium |
| S6 | No import/restore functionality | High |
| S7 | No backup button or automated backup | High |

### 2.6 Command Center Journey

```
(available via sidebar or Ctrl+K)
  ↓
CommandCenter.build_ui()
  ├─ Navigation rail with workspace names
  ├─ Breadcrumb widget
  ├─ Quick search bar
  └─ Workspace pages (executive dashboard, goal workspace, etc.)
  ↓
User selects a workspace
  ├─ CommandCenter._switch_workspace() sets QStackedWidget index
  ├─ CommandCenterController handles data flow
  └─ Workspace page's update_data() called
```

### Command Center Journey Issues

| # | Issue | Severity |
|---|-------|----------|
| C1 | Pages use `_dict_val()` helper to safely access attributes — suggests API contract instability | Medium |
| C2 | No loading/error/empty states per workspace page | **High** |
| C3 | No animation during page transitions | Low |
| C4 | `command_center.py` has `_sidebar` → `_nav_rail` rename inconsistency with old tests | Low |

---

## 3. Interaction Layer Audit

### 3.1 Keyboard

| Shortcut | Action | Wired? | Notes |
|----------|--------|--------|-------|
| `Ctrl+K` | Open command palette | ✅ | Works globally |
| `Ctrl+Shift+F` | Toggle focus mode | ✅ | Sidebar hidden but `_top_bar` never set → partial |
| `Alt+Left` | Go back (navigation history) | ✅ | Only works if `register_default_page_routes()` called |
| `Alt+Right` | Go forward | ✅ | Same |
| `Ctrl+Shift+P` | Global search | ✅ | Opens same command palette (not separate search UI) |
| `Ctrl+R` | Refresh | ✅ | Emits `data_updated` signal |
| `Escape` | Exit focus / close | ✅ | Only exits focus mode |
| Arrow keys | Navigate workspace pages | ❌ | Not implemented |
| `Ctrl+N` | New workout | ❌ | Not implemented |
| `Ctrl+S` | Save workout | ❌ | Not implemented |
| `Ctrl+E` | Export data | ❌ | Not implemented |
| `F1` | Help / shortcuts reference | ❌ | Not implemented |
| `?` | Show keyboard shortcuts | ❌ | Not implemented |

### 3.2 Search

- Search is wired through `SearchProvider` with 3 registered providers (commands, pages, shortcuts)
- Search UI is the command palette dialog — not a dedicated search interface
- **No content search** — cannot search workouts, exercises, PRs, or notes
- Search only works in-memory against registered routes and commands

### 3.3 Command Palette

- Contents: 7 built-in commands + N page navigation commands (registered by `register_default_command_palette_pages`)
- UI: Modal dialog with search filter, category grouping, keyboard navigation
- **No dynamic commands** — workout actions, export, etc. are not registered
- `open_palette` and `_open_global_search` both call `command_palette.open_palette()` — identical behavior

### 3.4 Navigation

- **Dual navigation system:**
  - `MainWindow._sidebar` (legacy) — 7 nav buttons, active highlighting, manual `_switch_to` dispatch
  - `NavigationEngine` (experience platform) — route-based, history stack, back/forward, breadcrumb
  - **These two are NOT connected** — sidebar clicks don't go through NavigationEngine
  - Command palette routes go through NavigationEngine but don't update the sidebar active state
- Workspace switching via `CommandCenter` has its own workspace registry (third navigation system)
- Three separate navigation systems operate independently

### 3.5 Notifications

- `NotificationCenter` fully built: toast rendering, priority system, auto-dismiss, history, list view
- **Never triggered by any application code** — no event subscriber wires notifications
- `NotificationToast` uses QTimer for auto-dismiss but animation is instant (no fade)
- `NotificationList` and `NotificationCenter` are orphan classes

### 3.6 Loading States

- `LoadingStateManager`, `SkeletonWidget`, `SkeletonBlock`, `LoadingOverlay`, `ProgressIndicator` — all built
- **Never used by any page or view** — no widget calls `loading.show_overlay()` or `loading.show_skeleton()`
- All workspace pages render immediately with stale/empty data

### 3.7 Empty States

- `EmptyStateManager` and `EmptyStateWidget` fully built with dashed borders, icon, title, description, action button
- **Never registered or shown** — pages use bare `QLabel("No X available")` instead
- `EmptyStateWidget` is production-quality but completely unused

### 3.8 Error Recovery

| Scenario | Behavior | Issue |
|----------|----------|-------|
| DB query fails | Silent `except Exception: pass` in DashboardController and DashboardDataService | User sees stale -- values |
| Program import fails | Error dialog with exception message | Acceptable |
| Recovery service fails | Silent attribute fallback via `hasattr()` | User sees 0.0 values |
| Prediction service fails | `generate_all_predictions()` could throw — unhandled | **Crash** |
| No network | No network features (all local) | N/A |
| Corrupted database | SQLAlchemy raises on first query — unhandled | **Crash** |

### 3.9 Undo

- **Zero undo support** anywhere in the application
- No confirmation dialog for any destructive action
- Workout save is one-click with no "are you sure"
- Export overwrites files without confirmation

---

## 4. Visual Consistency Audit

### 4.1 Typography

| Element | Usage | Issues |
|---------|-------|--------|
| `QFont` | Minimal usage — most text sized via `setStyleSheet("font-size: Xpx")` | **No typographic scale** — sizes vary: 11px, 12px, 13px, 14px, 15px, 16px, 18px, 20px, 22px, 24px, 26px, 28px, 32px, 36px, 48px |
| Font weights | `400`, `500`, `600`, `700`, `800` used inconsistently | `font-weight: 700` on labels that are not headings |
| System fonts | No custom fonts loaded — uses OS default | Acceptable for MVP |
| `Font` class in `C` theme | Defines `LABEL`, `MUTED`, `CAPTION`, `SUBHEADING` styles | Only used by Experience Platform classes, NOT by any workspace page or dashboard widget |

### 4.2 Spacing

| Pattern | Issues |
|---------|--------|
| Contents margins | Inconsistent: `main_window.py` uses 12px sidebar margins, `command_center/` uses 24-32px, `design_system/` uses defined tokens |
| `SpacingTokens` | Defined in design_system but not consistently used |
| `setContentsMargins(32, 32, 32, 32)` | Appears in 5+ views — but each view re-declares it independently |
| Padding in widgets | 16px, 12px, 8px, 20px all used — no consistent rhythm |

### 4.3 Color Palette

| Token | Used? |
|-------|-------|
| `#0F172A` (darkest bg) | ✅ Root background, sidebar, dialogs |
| `#1E293B` (card bg) | ✅ Cards, sections, combo boxes |
| `#818CF8` (accent/indigo) | ✅ Active indicators, primary buttons |
| `#F1F5F9` (text primary) | ✅ Headings, labels |
| `#94A3B8` (text secondary) | ✅ Subtitles, muted text |
| `#64748B` (text disabled) | ✅ Placeholders, captions |
| `#475569` (border) | ✅ Borders, dividers |
| `#4ADE80` (green) | ✅ Success, PRs, positive |
| `#FBBF24` (amber) | ✅ Warnings, recommendations |
| `#F87171` (red) | ✅ Danger, critical flags |
| `#60A5FA` (blue) | ✅ Info, recovery scores |

Colors are **visually consistent** despite being hardcoded rather than token-based in most views.

### 4.4 Information Density

- Dashboard: Low density, generous padding, large hero section — appropriate
- Workout logging: Medium density — exercise cards with set rows, reasonable spacing
- Progress: Low density — three charts with lots of whitespace
- Recovery: Medium-high density — 8 widgets on screen simultaneously
- Prediction: High density — 8 cards + 5 widgets in scroll view
- Settings: Very low density — 2 preference controls, 2 buttons
- Command Center pages: Medium density — editorial layouts with varied spacing

### 4.5 Responsive Behavior

| Aspect | Status |
|--------|--------|
| Window minimum size | Hardcoded `1024×768` in MainWindow |
| Layout reflow | None — fixed layouts, no `QSplitter` except in QStackedWidget |
| HiDPI | No `Qt.AA_EnableHighDpiScaling` — untested |
| Font scaling | No support — fixed pixel sizes |
| Sidebar width | Fixed 220px — no collapse/expand |
| Content margins | Fixed 32px — no breakpoint adaptation |

### 4.6 Dark Mode

- Application is dark-only — "Light" theme option in Settings has no effect
- No `palette.setColor()` usage — all colors via inline stylesheets
- Theme colors are hardcoded hex values in every view
- `DesignSystem` token system (`ColorTokens`, `DarkColorTokens`) exists but is only used by `DashboardView`

---

## 5. Product Experience by Persona

### 5.1 New User (Never used GymOS)

**Can they understand GymOS?**

| Criterion | Verdict | Issue |
|-----------|---------|-------|
| First launch tells them what to do | ❌ | Empty dashboard with "--" values |
| Can find how to import a program | ✅ | "Import Program" in sidebar |
| Can figure out workout logging | ✅ | Day cards, exercise cards, set inputs are intuitive |
| Understands recovery scores | ❌ | No explanation of what scores mean |
| Understands predictions | ❌ | "PR Probability", "Plateau Risk" — no context |
| Can find settings | ✅ | Settings item in sidebar |
| Can find help | ❌ | No help menu, no tooltips, no documentation link |

**Verdict:** A new user will be confused by the empty dashboard but can figure out the workout logging loop. All analytical features (recovery, prediction) lack onboarding context.

### 5.2 Intermediate User (Used for a week)

**Can they complete a full week?**

| Criterion | Verdict | Issue |
|-----------|---------|-------|
| Log 4 workouts in a week | ✅ | Workflow is solid |
| See their progress | ✅ | Charts render with data |
| Understand recovery trends | ⚠️ | Possible but no onboarding |
| Use predictions | ⚠️ | Data accumulates, predictions become meaningful |
| Export their data | ✅ | JSON/CSV export works |
| Change preferences | ❌ | Preferences don't persist |

**Verdict:** Functional for the core loop. Data export works. Analytics improve with data. Preferences not persisting is the main frustration.

### 5.3 Advanced User (Trusts recommendations)

**Can they trust recommendations?**

| Criterion | Verdict | Issue |
|-----------|---------|-------|
| Progression recommendations are based on history | ✅ | Uses ProgressionEngine with DB data |
| Recovery scores are accurate | ⚠️ | Depends on input quality — no validation shown |
| Prediction confidence shown | ✅ | Dashboard shows confidence/probability per prediction |
| Recommendations explain reasoning | ⚠️ | Brief text only — no detailed explainability |
| Can audit decision logic | ❌ | No way to see why a specific recommendation was made |

**Verdict:** Progression recommendations are trustworthy (based on logged data). Recovery/prediction scores are opaque — advanced users will want explainability.

### 5.4 Coach (Daily use)

**Can a coach use it daily?**

| Criterion | Verdict | Issue |
|-----------|---------|-------|
| Quick workout logging | ⚠️ | Good but no supersets/rest timers |
| Athlete overview | ❌ | Single-user only |
| Trend analysis | ⚠️ | Basic charts, no comparison |
| Program adjustment | ❌ | Cannot modify active program |
| Communication | ❌ | No notes, no messaging |
| Multi-athlete | ❌ | Single-user application |
| Export/backup | ✅ | JSON/CSV export works |

**Verdict:** Not suitable for coach use — single-user, no program editing, no athlete management.

---

## 6. Dead Ends & UX Blockers

| # | Location | Dead End | Impact |
|---|----------|----------|--------|
| DE1 | First launch + no program.json | Dashboard shows "--" everywhere, no workout days, no path forward | **High** — user may close app |
| DE2 | Settings → Unit/Theme changes | Changes have no effect on restart | **High** — user expects persistence |
| DE3 | Dashboard → "Log Weight" | Navigates to Settings, but Settings has no weight logging UI | **Bug** — silent redirection to nowhere |
| DE4 | Progress → period selector | All periods show same 90-day window | **Bug** — user thinks they're changing view |
| DE5 | Workout → Back button during logging | All input silently discarded | **High** — no confirmation dialog |
| DE6 | Any → Notification | Notifications are never triggered — system appears broken | Medium |
| DE7 | Any → Search (Ctrl+Shift+P) | Opens command palette, not a search UI | Medium |
| DE8 | Workout → "Save & Finish" | No confirmation — one click saves permanently | Medium |
| DE9 | Settings → export path | No error handling if save path is unwritable | Low |
| DE10 | Dashboard → "View All PRs" | Navigates to Records page — empty if no PRs | Low |

---

## 7. Missing Screens & Dialogs

| # | Missing | Impact | Effort |
|---|---------|--------|--------|
| MS1 | **First-run wizard** (welcome, import program, set goals) | Critical | 2-3d |
| MS2 | **User profile dialog** (name, height, weight, goals, focus muscles) | High | 1d |
| MS3 | **Body weight logging dialog** | **Bug fix** | 4h |
| MS4 | **Workout history view** (list past sessions, view details) | High | 2d |
| MS5 | **Edit past workout dialog** | High | 1d |
| MS6 | **Exercise library browser** (search/explore exercises) | Medium | 2d |
| MS7 | **Help/About dialog** (shortcuts reference, documentation link) | High | 4h |
| MS8 | **Notification panel** (bell icon, history list, dismiss) | Medium | 1d |
| MS9 | **Keyboard shortcut reference screen** | Medium | 1d |
| MS10 | **Backup dialog** (backup database, restore from backup) | High | 1d |
| MS11 | **Confirmation dialogs** for destructive actions (discard workout, delete data) | High | 1d |
| MS12 | **Loading indicators** for all data-fetching views | High | 2d |
| MS13 | **Goal management screen** (set/update weight goal, target date) | Medium | 1d |
| MS14 | **Nutrition log screen** (if NutritionService is wired) | Medium | 2d |
| MS15 | **Deload scheduling UI** (schedule/confirm deload week) | Low | 1d |
| MS16 | **Program management screen** (view/manage/switch programs) | Medium | 1d |
| MS17 | **Splash screen** (while database loads) | Low | 4h |
| MS18 | **Error dialog** for unhandled exceptions (friendly crash reporter) | Critical | 2d |

---

## 8. Confusing Interactions

| # | Interaction | Why It's Confusing |
|---|-------------|-------------------|
| C1 | Dashboard "Log Weight" → Settings | User expects a weight input, not a settings screen |
| C2 | Progress period selector does nothing | User selects "All time" but still sees 90 days — thinks app is broken |
| C3 | Recovery scores shown without context | Numbers like "72.5" with no explanation of scale (0-100?) |
| C4 | Prediction "Probability: 65%" | What does 65% mean? 65% chance of what happening? When? |
| C5 | Two sidebar navigation systems | MainWindow sidebar AND CommandCenter nav rail — which one to use? |
| C6 | "Import Program" in sidebar among regular nav items | Imports a new program when clicked — not a navigation action |
| C7 | "Save & Finish" button visible even when no data entered | Can save an empty workout with all 0s |
| C8 | Workout back arrow vs sidebar navigation | Back arrow returns to workout selection. Sidebar Dashboard goes to dashboard. Data stays unsaved. |
| C9 | Hardcoded "PPL-UL" fallback when no active program | User sees workout days that don't match their imported program |
| C10 | Theme combo "Dark (default)" / "Light" | Switching to "Light" does nothing — no theme change occurs |

---

## 9. Prioritized Fixes

### P0 — Critical (Blocking v1.0)

| # | Fix | Effort | Corresponding Issues |
|---|-----|--------|---------------------|
| F1 | Remove hardcoded placeholder user data from Settings; show real data or "Not configured" | 1h | S2, S3 |
| F2 | Fix body weight logging — add input UI to Settings or Dialog | 4h | S4, DE3 |
| F3 | Fix progress period selector to actually filter data | 2h | P1, DE4 |
| F4 | Add confirmation dialog before discarding unsaved workout | 2h | DE5, W7 |
| F5 | Preference persistence — save unit system and theme changes via QSettings | 2h | S1, DE2 |
| F6 | First-run welcome/onboarding — at minimum a dialog explaining the app | 2d | L5, L7, L8, DE1 |

### P1 — High

| # | Fix | Effort |
|---|-----|--------|
| F7 | Wire `NotificationCenter` to real application events (workout saved, PR achieved) | 1d |
| F8 | Wire `LoadingStateManager` overlay/skeleton to data-fetching views | 2d |
| F9 | Wire `EmptyStateManager` to all workspace pages with action buttons | 2d |
| F10 | Add About dialog with version and shortcuts reference | 4h |
| F11 | Replace all static "No X available" labels with `EmptyStateWidget` instances | 1d |
| F12 | Add undo-safe confirmation to workout save | 1d |
| F13 | Wire focus mode `_top_bar` (currently None → only sidebar hides) | 1h |
| F14 | Add loading state to recovery/prediction dashboard fetches | 1d |
| F15 | Add pyqtgraph installation check with actionable error message | 2h |
| F16 | Unify the three navigation systems or at minimum connect them | 2d |
| F17 | Add error boundary for prediction service failures | 2h |
| F18 | Move hardcoded inline stylesheets to shared constants | 2d |

### P2 — Medium

| # | Fix | Effort |
|---|-----|--------|
| F19 | Add rest timer to workout view | 1d |
| F20 | Add workout history view | 2d |
| F21 | Add edit past workout | 2d |
| F22 | Add undo support for workout save (last-session rollback) | 1d |
| F23 | Add help/shortcut reference dialog | 1d |
| F24 | Add backup/restore functionality | 1d |
| F25 | Add splash screen | 4h |
| F26 | Add crash handler with friendly dialog | 2d |
| F27 | Add delay to data refresh on startup (don't query DB immediately) | 1h |
| F28 | Add visual distinction between warmup and working sets | 1d |

### P3 — Low

| # | Fix | Effort |
|---|-----|--------|
| F29 | Add page transition animations | 2d |
| F30 | Add HiDPI support (`AA_EnableHighDpiScaling`) | 1h |
| F31 | Add light theme implementation | 2d |
| F32 | Add responsive breakpoints for <1024px widths | 2d |
| F33 | Implement unified typographic scale | 1d |
| F34 | Switch all inline hex colors to theme token references | 3d |
| F35 | Add exercise search/filter in workout view | 1d |
| F36 | Add "complete exercise early" button | 4h |

---

## Appendix: Journey Map Legend

```
→  Navigation path
├─  Branched path
↓  Next step
❌  Dead end / blocker
⚠️  Partial or confusing
✅  Functional
```

## Appendix: Flow Diagram (Text)

```
[Launch] → [DB Init] → [Program Load] → [MainWindow]
  │                                │
  │  No program.json?              │
  │  └→ [Empty Dashboard] ←───────┘
  │       │
  │       └→ [Import Program] → [Dashboard with Data]
  │
  ├→ [Dashboard] ← → [Workout] ← → [Exercise Logging]
  │       │              │              │
  │       │              │              └→ Save → Summary Dialog → Dashboard
  │       │              └→ Back (no confirm) → DE5
  │       ├→ [Progress]
  │       ├→ [Recovery]
  │       ├→ [Predictions]
  │       ├→ [Records]
  │       └→ [Settings] → [Export] ✓
  │                         [Preferences] → no save → DE2
  │
  └→ [Experience Platform] (exists but mostly unused)
       ├→ Command Palette (Ctrl+K) ✓
       ├→ Shortcuts ✓
       ├→ Notifications → never triggered → DE6
       ├→ Loading States → never used → L4
       ├→ Empty States → never used → L5
       └→ Focus Mode → missing top_bar → F13
```

---

*End of REP-001D*
