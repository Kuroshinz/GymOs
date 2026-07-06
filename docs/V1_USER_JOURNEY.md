# GymOS v1.0 — Documented User Journeys

> Every supported workflow from first launch to long-term use.
> Maps actual code paths in the application.

---

## Journey 1: First Launch

### Entry Point
`main.py:25` → `main()`

### Flow

```
1. Database initialization
   init_db(DB_PATH)                    → creates data/gymos.db if missing
   GymDatabase(DB_PATH)                → opens SQLAlchemy engine + session
   
2. Program initialization
   ProgramManager(DB_PATH)
   ├─ repository.count() == 0?
   │   └─ YES → import first program from program.json (if exists)
   ├─ get_active_program() is None?
   │   └─ YES → switch to first available program

3. Service initialization (silent)
   NutritionRepository + NutritionService
   RecoveryRepository + RecoveryService
   PredictionRepository + PredictionService
   DecisionEngine.from_production()
   EventBus wiring

4. UI initialization
   QApplication(sys.argv)
   app.setStyle("Fusion")
   MainWindow(db, prog_mgr, nutrition_service, recovery_service, prediction_service)
   ├─ ExperienceManager.initialize()
   │   ├─ Register shortcuts (Ctrl+K, Alt+Left, etc.)
   │   ├─ Register command palette entries (7 built-in + page routes)
   │   └─ Register search providers (commands, pages, shortcuts)
   ├─ _build_sidebar()                 → 220px dark sidebar with 7 nav items
   ├─ _build_content()                 → QStackedWidget with 8 views
   │   ├─ DashboardView (0)
   │   ├─ WorkoutSelectionView (1)
   │   ├─ ProgressView (2)
   │   ├─ RecoveryDashboard (3)        → conditional on recovery_service
   │   ├─ PredictionDashboard (4)      → conditional on prediction_service
   │   ├─ PRView (5)
   │   ├─ SettingsView (6)
   │   └─ WorkoutView (7)
   └─ _switch_to(0)                    → shows Dashboard

5. window.show()
   app.exec()
```

### User Experience
- **No splash screen**: 1-2s of black window before UI appears
- **Dashboard loads empty**: "--" values for recovery, readiness, "No Active Program" for workout
- **No onboarding**: User must discover "Import Program" in sidebar
- **Settings shows placeholder data**: "178 cm · 63.4 kg · Lean Bulk → 72-75 kg" hardcoded

### Source Files
- `main.py:25-89` — Full launch sequence
- `ui/main_window.py:61-142` — MainWindow constructor
- `ui/experience/experience_manager.py:58-64` — Experience Platform init
- `ui/command_center/command_center.py` — Alternative entry point

---

## Journey 2: Import a Workout Program

### Trigger
Sidebar "Import Program" button OR Dashboard "Import Program" signal

### Flow

```
ImportWizard(prog_mgr, parent)
├─ Page 1: FileSelectionPage
│   ├─ User clicks "Browse..."
│   │   └─ QFileDialog for .xlsx, .json, .yaml
│   └─ Selected path displayed
│
├─ Page 2: PreviewPage (auto-advance)
│   ├─ prog_mgr.preview(filepath)
│   └─ Shows: name, description, day count, exercise count, day list
│
├─ Page 3: ImportProgressPage (auto-advance)
│   ├─ prog_mgr.import_save_and_activate(filepath)
│   ├─ Success: green "Program imported and activated!" + 100% progress bar
│   └─ Failure: red error message + validation error list
│
└─ Dialog Accepted → DashboardView.refresh(), WorkoutSelectionView.refresh()
```

### Error Handling
- Invalid file: `QMessageBox.critical` with exception message
- Validation errors: listed in `_error_list` with day/exercise context

### Source Files
- `ui/import_wizard.py:186-240` — ImportWizard class
- `ui/import_wizard.py:40-71` — FileSelectionPage
- `ui/import_wizard.py:74-123` — PreviewPage
- `ui/import_wizard.py:126-183` — ImportProgressPage
- `modules/workout_program/manager.py` — prog_mgr implementation

---

## Journey 3: Select and Start a Workout

### Trigger
Sidebar "Workout" → DayCard click

### Flow

```
WorkoutSelectionView.refresh()
├─ prog_mgr.get_active_program_days()
├─ Fallback: db.get_program_days("PPL-UL")  [hardcoded]
└─ Renders DayCard grid

User clicks DayCard
├─ workout_selected.emit(day_name)
└─ MainWindow._on_workout_selected(day_name)
    ├─ WorkoutView.load_day(day_name)
    │   ├─ Sets title label to day_name
    │   ├─ Clears existing exercise cards
    │   ├─ prog_mgr.get_active_program_days()
    │   ├─ Finds matching day data
    │   ├─ For each exercise:
    │   │   ├─ db.get_last_session_for_exercise(name)
    │   │   ├─ ProgressionEngine.get_recommendation(name, reps_range)
    │   │   └─ Creates ExerciseCard(name, target_sets, prev_data, recommendation)
    │   │       └─ Creates N SetRow instances (weight × reps × RIR)
    └─ _content.setCurrentIndex(5)  [BUG: should be 7, workaround in code]
```

### ExerciseCard Structure
```
┌─────────────────────────────────────────┐
│  Bench Press                           │
│  💡 Increase to 67.5 kg (8 reps)       │  ← recommendation (if any)
│  ────────────────────────────────────── │
│  #1  [ 60 ]_kg × [ 8 ]_reps RIR [ 2 ]  │  ← pre-filled from last session
│  #2  [ 60 ]_kg × [ 8 ]_reps RIR [ 2 ]  │
│  #3  [ 60 ]_kg × [ 8 ]_reps RIR [ 2 ]  │
│                        prev: 60×8 RIR2 │  ← previous session hint
└─────────────────────────────────────────┘
```

### Empty State
- No program days: empty grid with no message
- No exercises in day: `return` silently (no error/empty state shown)

### Source Files
- `ui/workout_selection_view.py:74-126` — WorkoutSelectionView
- `ui/workout_view.py:297-482` — WorkoutView, ExerciseCard, SetRow
- `ui/main_window.py:224-226` — Workout selection handler

---

## Journey 4: Log a Workout

### Trigger
ExerciseCards rendered in WorkoutView

### Flow

```
User fills SetRow inputs:
├─ weight_input: QLineEdit with QIntValidator(0, 999)
├─ reps_input: QLineEdit with QIntValidator(0, 100)
└─ rir_input: QLineEdit with QIntValidator(0, 5)

User clicks "Save & Finish"
├─ _finish_workout()
│   ├─ For each ExerciseCard:
│   │   └─ card.get_exercise_data() → {name, sets: [SessionSet, ...]}
│   ├─ Builds WorkoutSession
│   ├─ db.save_session(session)
│   ├─ PREngine.detect_prs(saved)           → PR detection
│   ├─ RecoveryEngine.analyse_session(saved) → recovery impact
│   ├─ ProgressionEngine.analyse_exercise()  → per exercise
│   └─ WorkoutSummaryDialog(saved, prs, recovery, recommendations)
│       ├─ Duration, total volume
│       ├─ PRs (top 5)
│       ├─ Next session recommendations (top 3)
│       └─ Recovery flags (top 2)
│
└─ dialog.exec() → workout_saved.emit → _switch_to(dashboard)
```

### Data Model
```python
SessionSet = {
    set_number: int,
    weight_kg: float,
    reps: int,
    rir: int | None,
    completed: bool,
}

SessionExercise = {
    name: str,
    sets: list[SessionSet],
}

WorkoutSession = {
    day_name: str,
    exercises: list[SessionExercise],
    started_at: datetime,
    completed_at: datetime,
    total_volume: float,        # computed
    duration_minutes: float,    # computed
}
```

### Known Issues
- No validation that at least one set has data
- No loading state during save (PR detection can be slow)
- No "Save without finishing" (e.g., if phone rings mid-workout)
- "Back" button during logging discards all data silently
- Index bug: `_on_workout_selected` sets content to index 5 (PRView) instead of 7 (WorkoutView)

### Source Files
- `ui/workout_view.py:297-482` — Full workout logging flow
- `modules/workout/domain.py` — WorkoutSession, SessionExercise, SessionSet
- `modules/workout/application/pr_engine.py` — PR detection
- `modules/workout/application/recovery_engine.py` — Session recovery analysis
- `modules/workout/application/progression_engine.py` — Progression recommendations
- `modules/workout/infrastructure/repository.py` — DB persistence

---

## Journey 5: View Progress

### Trigger
Sidebar "Progress"

### Flow

```
ProgressView.refresh()
├─ Period: combo box ("Last 30 days", "Last 90 days", "All time")
│   └─ NOTE: selected period has NO EFFECT — all queries use days=90
│
├─ Body Weight Chart (ChartWidget)
│   ├─ db.get_body_weight_history(days=90)
│   ├─ Plots weights over time with green line + dots
│   └─ Shows "Latest: X.X kg" in bottom label
│
├─ Weekly Volume Chart (ChartWidget)
│   ├─ db.get_volume_by_day(days=90)
│   ├─ Groups into weekly buckets (volume / 1000)
│   └─ Plots with indigo line + dots
│
└─ Muscle Volume Chart (ChartWidget)
    ├─ VolumeAnalytics.get_weekly_volume(weeks=1)
    ├─ Bar chart with muscle groups on x-axis
    └─ Color-coded by status (red/yellow/green)
```

### Dependencies
- `pyqtgraph` (optional): if not installed, all charts show "Install pyqtgraph for charts"

### Source Files
- `ui/progress_view.py:90-202` — ProgressView
- `ui/progress_view.py:19-62` — ChartWidget
- `ui/progress_view.py:64-88` — EmptyChart (placeholder)
- `modules/workout/application/volume_analytics.py` — Volume analysis

---

## Journey 6: View Recovery Dashboard

### Trigger
Sidebar "Recovery"

### Flow

```
MainWindow._refresh_recovery()
├─ recovery_service.get_snapshot()             → current state
├─ recovery_service.get_recent_scores(days=7)  → score history
├─ recovery_service.get_trend(days=14)         → trend direction
├─ recovery_service.get_weekly_averages(weeks=4)
├─ recovery_service.get_active_deload()
├─ recovery_service.get_recommendations(days=1)
├─ Builds RecoveryDashboardData with all values
└─ RecoveryDashboard.refresh(data)
    ├─ RecoveryScoreWidget → circular score display
    ├─ ReadinessWidget → readiness level + flags
    ├─ RecoveryTrendWidget → 14-day trend
    ├─ SleepStressWidget → sleep + stress scores
    ├─ FatigueWidget → fatigue level
    ├─ DeloadWidget → deload status
    ├─ RecoveryTimelineWidget → 7-day score chart
    └─ WeeklyRecoveryWidget → weekly averages
```

### Widgets
```
┌─────────────────────────────────────────────────────────┐
│ Top Row (3-column grid):                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Recovery │  │Readiness │  │  Trend   │              │
│  │  Score   │  │  Level   │  │  Chart   │              │
│  │   85.2   │  │   HIGH   │  │ ↗↗→→    │              │
│  └──────────┘  └──────────┘  └──────────┘              │
│ Middle Row (3-column):                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Sleep /  │  │ Fatigue  │  │  Deload  │              │
│  │  Stress  │  │          │  │  Status  │              │
│  └──────────┘  └──────────┘  └──────────┘              │
│ Bottom Row (2-column):                                  │
│  ┌──────────────────┐  ┌──────────────────┐            │
│  │   Timeline (7d)  │  │     Weekly Avg   │            │
│  └──────────────────┘  └──────────────────┘            │
└─────────────────────────────────────────────────────────┘
```

### Source Files
- `ui/recovery/recovery_dashboard.py:46-116` — RecoveryDashboard
- `ui/main_window.py:240-273` — Recovery refresh handler
- `modules/recovery/application/__init__.py` — RecoveryService
- `modules/recovery/engines/__init__.py` — Recovery engines
- `modules/recovery/infrastructure/repository.py` — Recovery DB

---

## Journey 7: View Predictions

### Trigger
Sidebar "Predictions"

### Flow

```
MainWindow._refresh_predictions()
├─ prediction_service.generate_all_predictions()
│   └─ Runs all prediction engines sequentially
├─ PredictionFormatter.prediction_result_to_view_model(result)
│   └─ Converts to PredictionViewModel with display data
├─ Builds PredictionDashboardData(view_model, has_data, result)
└─ PredictionDashboard.refresh(data)
    ├─ Renders 8 prediction cards in 2×4 grid:
    │   PR Probability | Plateau Risk | Recovery Forecast | Bodyweight Trend
    │   Goal ETA       | MRV Risk     | Deload Risk       | Consistency
    ├─ ScenarioWidget → "what-if" simulations
    ├─ RiskMeterWidget → overall overtraining risk
    ├─ ExplainabilityWidget → prediction explanations
    ├─ ConfidenceBreakdownWidget → per-prediction confidence
    └─ ReasonTreeWidget → decision reasoning tree
```

### Prediction Card
```
┌─────────────────────────────┐
│ PR PROBABILITY        ↔ ↗   │  ← title + trend
│ 82%                         │  ← value + color
│ Probability: High           │  ← probability label
│ Confidence: 90%             │  ← confidence label
└─────────────────────────────┘
```

### Source Files
- `ui/prediction/prediction_dashboard.py:71-169` — PredictionDashboard
- `ui/main_window.py:228-238` — Prediction refresh handler
- `modules/prediction/application/__init__.py` — PredictionService
- `modules/prediction/engines/__init__.py` — Prediction engines
- `modules/prediction/presentation/__init__.py` — PredictionFormatter

---

## Journey 8: View Personal Records

### Trigger
Sidebar "Records"

### Flow

```
PRView.refresh()
├─ PREngine.get_best_prs()
├─ Empty? → "No PRs yet. Complete a workout to start tracking!"
└─ Renders PRCard grid (2 columns) with:
    ├─ Exercise name
    ├─ PR type badge (Weight PR, Rep PR, Volume PR, Est. 1RM)
    ├─ Display value + improvement text
    └─ Date achieved + days ago
```

### Source Files
- `ui/pr_view.py:83-143` — PRView
- `ui/pr_view.py:12-81` — PRCard
- `modules/workout/application/pr_engine.py` — PR detection

---

## Journey 9: Settings & Export

### Trigger
Sidebar "Settings"

### Flow

```
SettingsView.refresh()
├─ Info section (hardcoded):
│   ├─ Application: GymOS v0.1.0 MVP
│   ├─ User: 178 cm · 63.4 kg · Lean Bulk → 72-75 kg  [PLACEHOLDER]
│   ├─ Database: SQLite (offline, local)
│   ├─ Focus: Shoulders · Upper Chest · Back Width · Arms
│   └─ Split: active program name + day names (from DB)
│
├─ Preferences section (no persistence):
│   ├─ Unit System: kg/cm | lbs/ft     → QComboBox
│   └─ Theme: Dark | Light             → QComboBox
│
├─ Data Export section:
│   ├─ Export as JSON → QFileDialog → writes gymos_export.json
│   └─ Export as CSV  → QFileDialog → writes gymos_export.csv
│
└─ Both exports include: sessions (up to 1000) + body weight history (365 days)
```

### Export Format

**JSON:**
```json
{
  "exported_at": "2026-07-06T...",
  "version": "0.1.0",
  "workouts": [
    {
      "day": "Push",
      "date": "2026-07-05T...",
      "duration_min": 65,
      "volume_kg": 12450,
      "exercises": [
        {
          "name": "Bench Press",
          "sets": [
            {"set": 1, "weight_kg": 60, "reps": 8, "rir": 2},
            ...
          ]
        }
      ]
    }
  ],
  "body_weight": [
    {"date": "2026-07-01", "weight_kg": 75.0},
    ...
  ]
}
```

**CSV:**
```
date,day,exercise,set_number,weight_kg,reps,rir
2026-07-05,Push,Bench Press,1,60,8,2
```

### Source Files
- `ui/settings_view.py:39-282` — SettingsView
- `ui/settings_view.py:14-36` — SettingRow helper

---

## Journey 10: Command Center Workspaces

### Trigger
CommandCenter (secondary navigation) or Ctrl+K

### Flow

```
CommandCenter.build_ui()
├─ Navigation rail (vertical icons + labels)
├─ Breadcrumb widget
├─ Quick search bar
└─ QStackedWidget with 10 workspace pages:
    ├─ Executive Dashboard (home)
    ├─ Goal Workspace (mission)
    ├─ Planning Studio (planning)
    ├─ Forecast Studio (prediction)
    ├─ Recovery Center (recovery)
    ├─ Knowledge Explorer (knowledge)
    ├─ Optimization Center (adaptive)
    ├─ Performance Lab (analytics)
    ├─ Platform Console (system)
    └─ AI Briefing Center (intelligence)

User selects workspace
├─ Emits workspace_changed signal
├─ CommandCenter._switch_workspace() sets page index
├─ CommandCenterController fetches page data
└─ Page's update_data(data) called
```

### Data Flow
```
EventBus → CommandCenterController → page.update_data()
```

Each page uses `_dict_val(key, data, default)` helper for safe attribute access from the generic data dict.

### Page Signatures
Each workspace page has a unique editorial layout with hero treatment, main content area, side panels, and activity feed (see REP-001B for layout details).

### Source Files
- `ui/command_center/command_center.py` — Main container
- `ui/command_center/controller.py` — Data flow controller
- `ui/command_center/pages/*.py` — 10 workspace pages
- `ui/command_center/theme.py` — Navigation items and labels

---

## Journey 11: Dashboard View (Legacy)

### Trigger
Sidebar "Dashboard" (primary entry point)

### Flow

```
DashboardView.refresh()
├─ DashboardController.refresh()
│   ├─ dashboard_data_service.fetch_all(db, prog_mgr, decision_engine, pr_engine)
│   └─ Emits data_updated(DashboardData)
│
└─ _on_data_updated(data)
    ├─ Hero Section:
    │   ├─ RecoveryRing (0-100)
    │   ├─ GoalRing (current vs target)
    │   ├─ Readiness metric
    │   ├─ Next Workout section (day name + exercise count + duration)
    │   └─ Top Recommendation section
    │
    ├─ Middle Section (3-column):
    │   ├─ Recovery: score + level
    │   ├─ Prediction: RiskMeter + confidence label
    │   └─ Weekly Volume: WeeklyTimeline chart + total
    │
    └─ Bottom Section (2-column):
        ├─ Recommendations list (top 3)
        └─ Milestones/Recent PRs list (top 3)
```

### Actions from Dashboard
- "Start Workout" → Workout selection
- "View All PRs" → Records page
- "View Recommendations" → Progress page
- "Weekly Review" → Progress page
- "Log Weight" → Settings page (BUG: no weight input there)
- "Import Program" → ImportWizard

### Source Files
- `ui/dashboard/dashboard_view.py:32-317` — DashboardView
- `ui/dashboard/dashboard_controller.py` — Controller
- `ui/dashboard/dashboard_models.py:13-67` — DashboardData model
- `ui/dashboard/dashboard_services/dashboard_data_service.py` — Data service

---

## Journey 12: Long-term Use Patterns

### Weekly Cycle

```
Monday:    Launch → Dashboard → Workout → Select Push Day → Log Sets → Save
Tuesday:   Rest / View Recovery
Wednesday: Launch → Workout → Select Pull Day → Log Sets → Save
Thursday:  Rest / View Progress
Friday:    Launch → Dashboard → Workout → Select Legs Day → Log Sets → Save
Saturday:  View Predictions, Review Weekly
Sunday:    View PRs, Check Progress Charts
```

### Recurring Actions

| Frequency | Action | Workflow |
|-----------|--------|----------|
| Daily | View Dashboard | Refresh → see recovery, readiness, today's workout |
| Per workout | Log workout | Select day → fill sets → save → see summary |
| Weekly | View progress | Check body weight trend, volume, muscle balance |
| Weekly | Review predictions | Check PR probability, plateau/deload risks |
| Bi-weekly | Update body weight | Navigate to Settings → no weight input (BUG) |
| Monthly | Export data | Settings → Export JSON/CSV |
| Per program change | Import new program | Import Wizard → select file → preview → import |

### Data Accumulation

| After | What becomes meaningful |
|-------|----------------------|
| 1 workout | First PR detected, first volume data |
| 1 week | Weekly volume chart, progress data |
| 2 weeks | Recovery trend, body weight trend |
| 4 weeks | Prediction confidence improves, deload risk detectable |
| 8+ weeks | All analytics meaningful, long-term trends visible |

### Source Files
- `main.py` — Application lifecycle
- `ui/main_window.py` — Navigation + view switching
- `ui/dashboard/dashboard_services/dashboard_data_service.py` — Data aggregation

---

## Journey 13: Keyboard Navigation

### Global Shortcuts (always active)

| Key | Action | Implementation |
|-----|--------|----------------|
| `Ctrl+K` | Open command palette | `CommandPaletteEngine.open_palette()` |
| `Ctrl+Shift+F` | Toggle focus mode | `FocusMode.toggle()` — hides sidebar |
| `Alt+Left` | Navigate back | `NavigationEngine.go_back()` |
| `Alt+Right` | Navigate forward | `NavigationEngine.go_forward()` |
| `Ctrl+Shift+P` | Global search | Opens command palette (same as Ctrl+K) |
| `Ctrl+R` | Refresh current view | Emits `data_updated` signal |
| `Escape` | Exit focus mode | `FocusMode.exit()` |

### Context-Specific (in command palette)
- Navigate to any registered page
- Clear notifications (no-op — notifications never created)
- Mark all read (no-op — notifications never created)

### Non-existent Shortcuts (potential additions)
- `Ctrl+N` — New workout
- `Ctrl+S` — Save current workout
- `Ctrl+E` — Export data
- `F1` — Help / shortcuts reference
- `?` — Toggle shortcut overlay
- Arrow keys — Navigate between workspace pages

### Source Files
- `ui/experience/shortcut_manager.py:25-110` — ShortcutManager
- `ui/experience/experience_manager.py:66-93` — Built-in shortcut/command registration
- `ui/experience/command_palette_engine.py:148-213` — CommandPaletteEngine

---

## Appendices

### A. All Application Views

| View | Class | File | Index | Data Source |
|------|-------|------|-------|-------------|
| Dashboard (legacy) | DashboardView | `ui/dashboard/dashboard_view.py` | 0 | DashboardController |
| Workout Selection | WorkoutSelectionView | `ui/workout_selection_view.py` | 1 | prog_mgr/DB |
| Progress | ProgressView | `ui/progress_view.py` | 2 | DB (sync) |
| Recovery Dashboard | RecoveryDashboard | `ui/recovery/recovery_dashboard.py` | 3 | RecoveryService |
| Prediction Dashboard | PredictionDashboard | `ui/prediction/prediction_dashboard.py` | 4 | PredictionService |
| Personal Records | PRView | `ui/pr_view.py` | 5 | PREngine |
| Settings | SettingsView | `ui/settings_view.py` | 6 | DB/prog_mgr |
| Workout Logging | WorkoutView | `ui/workout_view.py` | 7 | DB/prog_mgr |

### B. Command Center Workspaces

| Workspace | File | Layout Signature |
|-----------|------|-----------------|
| Executive Dashboard | `pages/home_page.py` | Full-bleed hero + KPI bar + magazine spread |
| Goal Workspace | `pages/mission_page.py` | Goal card hero + progress ribbon + decision timeline |
| Planning Studio | `pages/planning_page.py` | Cycle timeline hero + volume chart + sessions grid |
| Forecast Studio | `pages/prediction_center_page.py` | Confidence splash hero + scenario grid |
| Recovery Center | `pages/recovery_center_page.py` | Score monument hero + 3-column vitals + trend |
| Knowledge Explorer | `pages/knowledge_center_page.py` | Graph header + insight cards + updates |
| Optimization Center | `pages/adaptive_center_page.py` | Flow hero + decision log + strategy |
| Performance Lab | `pages/analytics_center_page.py` | Data wall hero + metric clusters + charts |
| Platform Console | `pages/system_center_page.py` | Status bar hero + capability grid + runtime |
| AI Briefing Center | `intelligence/narrative_page.py` | AI persona hero + briefing cards |

### C. Data Flow Architecture

```
[SQLite DB] ← → [Repository Layer]
                    ↓
              [Service Layer]
              ├─ RecoveryService
              ├─ PredictionService
              ├─ DecisionEngine
              └─ NutritionService
                    ↓
              [EventBus] ← → [Subscribers]
                    ↓
              [DashboardController / CommandCenterController]
                    ↓
              [View Layer]
              ├─ DashboardView (legacy)
              ├─ CommandCenter workspaces
              ├─ RecoveryDashboard
              ├─ PredictionDashboard
              └─ PRView / ProgressView / SettingsView
```

---

*End of V1_USER_JOURNEY.md — maps actual code paths, not aspirational flows*
