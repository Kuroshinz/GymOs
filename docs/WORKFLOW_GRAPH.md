# GymOS Workflow Graph

> Complete graph of how every workspace leads to another.
> Based on existing canonical services — no new engines.

---

## Legend

```
──▶  Natural workflow progression (data flows this direction)
◀──▶  Mutual dependency / cross-reference
══▶  Already wired in code
──▶  NOT wired (gap)
--▶  Indirect connection (via shared DB)
~~▶  Future/aspirational connection
[ ]  Workspace page
{ }  Engine / Service
( )  Legacy view
```

---

## 1. Complete Workflow Graph

```
                                 ┌────────────────────┐
                                 │   {EventBus}        │
                                 │   66 domain events  │
                                 └──┬──┬──┬──┬──┬──┬──┘
                                    │  │  │  │  │  │
                 ┌──────────────────┘  │  │  │  │  └──────────────────┐
                 │          ┌──────────┘  │  └──────────┐            │
                 ▼          ▼             ▼             ▼            ▼
          ┌───────────┐ ┌────────┐ ┌──────────┐ ┌───────────┐ ┌──────────┐
          │ Dashboard │ │Recovery│ │Nutrition│ │Workout    │ │Knowledge │
          │ Controller│ │Service │ │Service  │ │Subscribers│ │Evolution │
          │ (10 subs) │ │(5 subs)│ │(1 sub)  │ │(3 subs)   │ │Events    │
          └─────┬─────┘ └────────┘ └──────────┘ └───────────┘ └──────────┘
                │
     ═══════════╪══════════════════════════════ WIRED
                │
          ┌─────▼─────┐
          │Dashboard  │  (Legacy View — all CTAs wired)
          │View       │
          └──┬──┬──┬──┘
             │  │  │
     ════════╪══╪══╪══════════════════════════ WIRED CTA
     │       │  │  │
     ▼       ▼  │  └──────────────────┐
┌────────┐ ┌──────┐                  │
│Workout │ │ PR   │                  ▼
│Select  │ │View  │            ┌──────────┐
└───┬────┘ └──────┘            │ Progress │
    │                          │ View     │
    ▼                          └──────────┘
┌────────┐
│Workout │
│View    │
└───┬────┘
    │ session saved
    ▼
┌──────────────┐
│WorkoutSummary│  (PRs, recommendations, recovery flags)
│Dialog        │
└──────────────┘
```

---

## 2. Engine Dependency Graph

```
                    ╔══════════════════════════════════════╗
                    ║         SQLite Database              ║
                    ║  (workouts, programs, body weight,   ║
                    ║   nutrition, recovery, predictions)  ║
                    ╚═══════════╤══════════╤══════════════╝
                                │          │
              ┌─────────────────┤          ├──────────────────┐
              ▼                 ▼          ▼                  ▼
     ┌────────────────┐ ┌────────────┐ ┌──────────┐ ┌──────────────┐
     │Workout.Engines │ │Recovery    │ │Nutrition │ │ProgramManager │
     │ (PR, Progres-  │ │Service  ───┤ │Service   │ │  (reads/writes│
     │ sion, Recovery,│ │           │ │          │ │   program)    │
     │ Volume)        │ │           │ │          │ └──────┬───────┘
     └───────┬────────┘ │           │ │          │        │
             │          │           │ │          │        │
             │          ▼           │ │          │        │
             │  ┌──────────────┐    │ │          │        │
             │  │Recovery      │    │ │          │        │
             │  │Engines       │    │ │          │        │
             │  │ (8 classes)  │    │ │          │        │
             │  └──────┬───────┘    │ │          │        │
             │         │            │ │          │        │
             │         │            │ │          │        │
             └────┬────┼────────────┼─┼──────────┼────────┘
                  │    │            │ │          │
                  ▼    ▼            ▼ ▼          ▼
          ┌──────────────────────────────────────────┐
          │      DecisionEngine (GymBrain)            │
          │                                           │
          │  Providers: DataProvider + Production     │
          │  Rules: Fatigue, Recovery, Nutrition,     │
          │    Volume, Plateau, Progression           │
          │  Outputs: recommendations, weekly review, │
          │    goal progress, muscle analysis         │
          └──────┬───────────────────────────────────┘
                 │
                 │  ❌ NEVER CALLED
                 ▼
          ┌──────────────────────────────────────────┐
          │      PredictionService                    │
          │                                           │
          │  ⚠ Uses hardcoded recovery defaults        │
           │  ⚠ generate_all_predictions() only called  │
           │     on Predictions view navigation         │
          │  Engines: 13 classes                       │
          └──────────────────────────────────────────┘
```

---

## 3. Workspace Transition Graph

### AS-IS (Current)

```
[NavRail / Ctrl+K]
      │
      ├──▶ [Home] ──STRETCH──▶ (dead end)
      ├──▶ [Mission] ──STRETCH──▶ (dead end)
      ├──▶ [Planning] ──STRETCH──▶ (dead end)
      ├──▶ [Prediction] ──STRETCH──▶ (dead end)
      ├──▶ [Recovery] ──STRETCH──▶ (dead end)
      ├──▶ [Knowledge] ──STRETCH──▶ (dead end)
      ├──▶ [Adaptive] ──STRETCH──▶ (dead end)
      ├──▶ [Analytics] ──STRETCH──▶ (dead end)
      ├──▶ [System] ──STRETCH──▶ (dead end)
      └──▶ [Intelligence] ──STRETCH──▶ (dead end)

Every path: NavRail → Page → addStretch() → user hits Ctrl+K
```

### TO-BE (Desired)

```
                           ┌───────────────────────────┐
                           │        HOME               │
                           │  Executive Dashboard      │
                           │  "Start Workout" ─────►   │
                           │  "View Recent PRs" ──►    │
                           │  "Check Readiness" ──►    │
                           └────┬──────┬───────┬───────┘
                                │      │       │
              ┌─────────────────┘      │       └──────────────────┐
              │                        │                          │
              ▼                        ▼                          ▼
     ┌────────────────┐    ┌──────────────────┐    ┌───────────────────┐
     │   MISSION      │    │   RECOVERY       │    │   PLANNING        │
     │  Goal Workspace│    │  Recovery Center │    │  Planning Studio  │
     │                │    │                  │    │                   │
     │  "Adjust Goal" │    │  "View Trends"   │    │  "View Program"   │
     │    ──► Analytics│   │    ──► Analytics  │    │    ──► Prediction  │
     │  "View History"│    │  "Check Predict."│    │  "Adjust Week"    │
     │    ──► Analytics│   │    ──► Prediction │    │    ──► Adaptive    │
     └────────┬───────┘    └────────┬─────────┘    └────────┬──────────┘
              │                     │                       │
              │                     │                       ▼
              │                     │              ┌───────────────────┐
              │                     │              │   PREDICTION      │
              │                     └──────────────►  Forecast Studio  │
              │                     │              │                   │
              │                     │              │  "Run Scenario"   │
              │                     │              │    ──► Adaptive    │
              │                     └──────────────►  "Export Report"  │
              │                     │              │    ──► Analytics   │
              │                     │              └────────┬──────────┘
              │                     │                       │
              │                     ▼                       ▼
              │              ┌───────────────────┐  ┌───────────────────┐
              │              │   ADAPTIVE        │  │   ANALYTICS       │
              │              │  Optimization Ctr │  │  Performance Lab  │
              │              │                   │  │                   │
              │              │  "Review Decision"│  │  "Compare Periods"│
              │              │    ──► Knowledge   │  │    ──► Home       │
              │              │  "Run Simulation" │  │  "Export Report"  │
              │              │    ──► Planning    │  │    ──► Settings   │
              │              └────────┬──────────┘  └───────────────────┘
              │                       │
              │                       ▼
              │              ┌───────────────────┐
              │              │   KNOWLEDGE       │
              │              │  Knowledge Exp.   │
              │              │                   │
              │              │  "Explore Graph"  │
              │              │    ──► Intelligence│
              │              │  "Search Knowl."  │
              │              │    ──► Intelligence│
              │              └────────┬──────────┘
              │                       │
              │                       ▼
              │              ┌───────────────────┐
              │              │  INTELLIGENCE     │
              │              │  AI Briefing Ctr  │
              │              │                   │
              │              │  "Generate Brief" │
              │              │    ──► Any         │
              │              │  "Configure AI"   │
              │              │    ──► System      │
              │              └───────────────────┘
              │
              ▼
     ┌──────────────────────┐
     │   SYSTEM             │
     │  Platform Console    │
     │                      │
     │  "View Logs"         │
     │    ──► (observability)│
     │  "Run Diagnostics"   │
     │    ──► System (self) │
     └──────────────────────┘
```

---

## 4. Data Flow Graph (Engine → Service → View)

```
ENGINE LAYER (shared/ and modules/)
═══════════════════════════════════════════════════

  ┌─────────────────────┐    ┌──────────────────────┐
  │ Workout Engines:    │    │ Recovery Engines:     │
  │  PREngine           │    │  SleepAnalyzer        │
  │  ProgressionEngine  │    │  StressAnalyzer       │
  │  RecoveryEngine     │    │  FatigueAggregator    │
  │  VolumeAnalytics    │    │  RecoveryScoreEngine  │
  └────────┬────────────┘    │  ReadinessEngine      │
           │                 │  DeloadEngine         │
           │                 │  TrendAnalyzer        │
           ▼                 │  FactorsCalculator    │
  ┌─────────────────┐        └──────────┬─────────────┘
  │ ProductionData  │                   │
  │ Provider        │                   │
  │ (wraps DB +     │                   │
  │  engines)       │                   ▼
  └────────┬────────┘        ┌──────────────────────┐
           │                 │ RecoveryService      │
           │                 │ (get_snapshot,       │
           ▼                 │  get_recent_scores,  │
  ┌─────────────────┐        │  get_trend, etc.)    │
  │ DecisionEngine   │       └──────────┬───────────┘
  │ (rules engine    │                  │
  │  + providers)    │                  │
  │                  │                  │ ❌ NOT WIRED
  │  get_goal_progress│                 ▼
  │  get_today_recomm.│        ┌──────────────────────┐
  │  get_weekly_review│        │ PredictionService    │
  │  evaluate_rules() │        │ (13 engines)         │
  └────────┬──────────┘        │                      │
           │                   │ generate_all_predict.│
           │                   │ get_summary()        │
           │                   └──────────────────────┘
           │
           │ ❌ NOT WIRED
           ▼
  ┌──────────────────────┐
  │ Shared Runtimes:     │  (all completely unused)
  │  Runtime             │
  │  CognitiveOrchestrator│
  │  PlanningEngine      │
  │  AdaptiveProgramming │
  │  KnowledgeEvolution  │
  │  ProductStateEngine  │
  └──────────────────────┘

SERVICE LAYER (ui/)
═══════════════════════════════════════════════════

  ┌──────────────────────┐    ┌──────────────────────┐
  │ DashboardController   │    │ CommandCenterCtrl   │
  │ (QObject + Signal)   │    │ (no signals)        │
  │                      │    │                      │
  │ EventBus → Signal    │    │ EventBus → fetch()   │
  │ → DashboardView      │    │ → all 10 pages       │
  └──────────┬───────────┘    └──────────┬───────────┘
             │                           │
             ▼                           ▼
  ┌──────────────────────┐    ┌──────────────────────┐
  │ DashboardView        │    │ CommandCenterService  │
  │ (legacy, wired)      │    │ (composite of 8      │
  │                      │    │  sub-services)        │
  │ All 6 CTAs connected │    │                      │
  └──────────────────────┘    │  All fetch() only     │
                              │  No Signal emissions  │
                              └──────────────────────┘

VIEW LAYER (ui/)
═══════════════════════════════════════════════════

  ┌──────────────────────┐    ┌──────────────────────┐
  │ 10 Workspace Pages   │    │ 7 Legacy Views       │
  │                      │    │                      │
  │ 0 CTAs connected     │    │ All CTAs connected   │
  │ 0 cross-references   │    │ Full signal wiring   │
  │ 0 intra-page nav     │    │ EventBus integration │
  └──────────────────────┘    └──────────────────────┘
```

---

## 5. User Journey Flow Graph

### 5.1 New User Onboarding Path

```
[Launch] ─── [No program] ──▶ [Empty Dashboard] ──▶ [Import Program]
                                                         │
                                                         ▼
                                              [Dashboard with data]
                                                         │
                                                         ▼
                                              [Workout Selection]
                                                         │
                                                         ▼
                                              [Log First Workout]
                                                         │
                                                         ▼
                                              [Workout Summary]
                                                    │    │    │
                                                    ▼    ▼    ▼
                                              [PRs] [Rec.] [Prog.]
                                               view  dash.  view
```

### 5.2 Weekly Training Cycle

```
Monday:    [Home] ──▶ [Workout: Push] ──▶ [Summary] ──▶ [Home]
                  ╔══▶ [DashboardView auto-refreshes]
Tuesday:   [Home] ──▶ [Recovery Dashboard] ──▶ [Check scores] ──▶ [Home]
Wednesday: [Home] ──▶ [Workout: Pull] ──▶ [Summary] ──▶ [Home]
Thursday:  [Home] ──▶ [Recovery Dashboard] ──▶ [Trends]
Friday:    [Home] ──▶ [Workout: Legs] ──▶ [Summary] ──▶ [Home]
Saturday:  [Home] ──▶ [Progress View] ──▶ [Weekly charts]
Sunday:    [Home] ──▶ [PR View] ──▶ [Records]
                  ──▶ [Settings] ──▶ [Export data]
```

### 5.3 Goal-Setting Path

```
[Home] ──▶ [Dashboard: "No active goal"] ──▶ [Mission Workspace]
                                                   │
                                                   ▼
                                          [Goal Workspace]
                                          "Set your first goal"
                                                   │
                                                   ▼
                                          [Adjust Goal] → dialog
                                                   │
                                                   ▼
                                          [Mission shows progress]
                                                   │
                                                   ▼
                                          [Analytics: goal progress]
```

### 5.4 Recovery → Prediction Path

```
[Recovery Center]           [Prediction: Forecast Studio]
       │                              │
       │  score dropped 20%           │  deload risk = 65%
       │                              │
       ├──should suggest──▶           │
       │  "Check Predictions"         │  "Your recovery affects
       │                              │   this prediction"
       │                              │
       ▼                              ▼
  [Analytics: trends view]    [Adaptive: optimization]
```

---

## 6. Module Dependency Graph

```
                            ┌──────────────┐
                            │   core/      │
                            │  (DI, config,│
                            │   event_bus, │
                            │   database)  │
                            └──────┬───────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
     ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
     │   modules/      │  │   shared/      │  │    ui/         │
     │                 │  │                 │  │               │
     │ workout/        │  │ events/        │  │ main_window.py│
     │ nutrition/      │  │ interfaces/    │  │ dashboard/    │
     │ prediction/     │  │ domain/        │  │ command_ctr/  │
     │ recovery/       │  │ kernel/        │  │ design_sys/   │
     │ gymbrain/       │  │ runtime/       │  │ experience/   │
     │ settings/       │  │ capabilities/  │  │ recovery/     │
     │ devtools/       │  │ cognitive/     │  │ prediction/   │
     │ workout_program/│  │ graph/         │  │ narrative/    │
     │                 │  │ state/         │  │ visualization/│
     │                 │  │ planning/      │  │ intelligence/ │
     │                 │  │ adaptive_prog/ │  │               │
     │                 │  │ knowledge_evol/│  │               │
     │                 │  │ optim_knowl/   │  │               │
     │                 │  │ intent/        │  │               │
     │                 │  │ evolution/     │  │               │
     │                 │  │ explainability/│  │               │
     │                 │  │ observability/ │  │               │
     └────────┬───────┘  └────────┬───────┘  └───────────────┘
              │                   │
              │     WIRING        │
              │     (main.py)     │
              └────────┬──────────┘
                       │
                       ▼
              ┌────────────────┐
              │   main.py      │
              │                │
              │  Creates:      │
              │  - Database    │
              │  - Services    │
              │  - EventBus    │
              │  - Subscribers │
              │  - QApplication│
              │  - MainWindow  │
              └────────────────┘
```

---

## 7. Gap Heat Map

```
Legend:
  ✅  Connected
  ⚠️  Partial / indirect
  ❌  Not connected
  --- Not applicable

WORKSPACE           Home  Miss  Plan  Pred  Recov Know  Adapt Analy  Syst  Intel
─────────────────────────────────────────────────────────────────────────────────
Home (Executive)    ---   ❌     ❌     ❌     ❌     ❌    ❌    ❌     ❌    ❌
Mission (Goals)     ❌    ---    ❌     ❌     ❌     ❌    ❌    ❌     ❌    ❌
Planning (Studio)   ❌    ❌     ---    ❌     ❌     ❌    ❌    ❌     ❌    ❌
Prediction (Forecast)❌  ❌     ❌     ---    ❌     ❌    ❌    ❌     ❌    ❌
Recovery (Center)   ❌    ❌     ❌     ❌     ---    ❌    ❌    ❌     ❌    ❌
Knowledge (Explorer) ❌   ❌     ❌     ❌     ❌     ---   ❌    ❌     ❌    ❌
Adaptive (Opt.)     ❌    ❌     ❌     ❌     ❌     ❌    ---   ❌     ❌    ❌
Analytics (Lab)     ❌    ❌     ❌     ❌     ❌     ❌    ❌    ---    ❌    ❌
System (Console)    ❌    ❌     ❌     ❌     ❌     ❌    ❌    ❌     ---   ❌
Intelligence (Brief) ❌   ❌     ❌     ❌     ❌     ❌    ❌    ❌     ❌    ---

RESULT: 90/90 cells are ❌ — zero cross-references between any two workspace pages.

─────────────────────────────────────────────────────────────────────────────────

ENGINE CHAIN       Work→Rec  Rec→Pred  Pred→Dec  Dec→Adapt  Adapt→Plan  Plan→Rev  Rev→Know  Know→Dash
───────────────────────────────────────────────────────────────────────────────────────────────────────
Data flow          ✅         ❌         ❌         ❌          ❌           ⚠️         ❌         ❌
Service wiring     ✅         ❌         ❌         ❌          ❌           ⚠️         ❌         ❌
UI connection      ❌         ❌         ❌         ❌          ❌           ❌         ❌         ❌
Notifications      ❌         ❌         ❌         ❌          ❌           ❌         ❌         ❌

─────────────────────────────────────────────────────────────────────────────────

SERVICE LAYER      Signals    EventBus   Loading    Empty      Notification
                   emit       publish    states     states     trigger
─────────────────────────────────────────────────────────────────────────
AdaptiveService    ❌         ❌          ❌         ❌         ❌
AnalyticsService   ❌         ❌          ❌         ❌         ❌
KnowledgeService   ❌         ❌          ❌         ❌         ❌
MissionService     ❌         ❌          ❌         ❌         ❌
PlanningService    ❌         ❌          ❌         ❌         ❌
PredictionService  ❌         ❌          ❌         ❌         ❌
RecoveryService    ❌         ❌          ❌         ❌         ❌
SystemService      ❌         ❌          ❌         ❌         ❌
CommandCenterCtrl  ❌         ❌          ❌         ❌         ❌
DashboardCtrl      ✅         ✅          ❌         ❌         ❌
```

---

## 8. Existing Wiring Reference

### 8.1 Already Wired (Don't Touch)

| Connection | Location | Mechanism |
|-----------|----------|-----------|
| DashboardView → WorkoutSelection | `main_window.py:114-115` | Signal: `start_workout_clicked` → `_switch_to(1)` |
| DashboardView → PRView | `main_window.py:117-118` | Signal: `view_all_prs_clicked` → `_switch_to(5)` |
| DashboardView → ProgressView | `main_window.py:120-125` | Signals → `_switch_to(2)` |
| DashboardView → Settings | `main_window.py:126-128` | Signal: `log_weight_clicked` → `_switch_to(6)` |
| DashboardView → ImportWizard | `main_window.py:129-131` | Signal: `import_program_clicked` → `_open_import_wizard()` |
| WorkoutSelection → WorkoutView | `main_window.py:132-133` | Signal: `workout_selected` → `_on_workout_selected()` |
| WorkoutView → Dashboard | `main_window.py:134-136` | Signal: `workout_saved` → `_switch_to(0)` |
| EventBus → DashboardController | `dashboard_controller.py:70-130` | 10 event subscriptions |
| EventBus → RecoveryService | `modules/recovery/application/__init__.py` | Recovery-specific events |
| EventBus → NutritionService | `modules/nutrition/services/__init__.py` | Nutrition-specific events |
| EventBus → CommandCenterController | `command_center/controller.py:60-120` | 14 event subscriptions → `refresh_section()` |
| NavRail → workspace pages | `command_center.py:168-178` | `_nav_rail.item_selected` → `_navigate()` |
| Ctrl+K → all workspaces | `command_center.py:112-120` | `QShortcut` → `_open_command_palette()` |

### 8.2 Ready to Wire (Connections That Need One Line of Code)

| Connection | Existing API | Line to Add |
|-----------|-------------|-------------|
| Home._start_btn → navigate("mission") | `command_center.py._navigate()` exists | `_start_btn.clicked.connect(lambda: self.parent()._navigate("mission"))` |
| Mission._history_btn → navigate("analytics") | NavigationEngine registered routes | `_history_btn.clicked.connect(lambda: ...)` |
| Recovery._trends_btn → navigate("analytics") | NavigationEngine registered routes | `_trends_btn.clicked.connect(lambda: ...)` |
| Prediction → DecisionEngine data | `prediction_service` exists in main.py | Inject result into `decision_engine.evaluate_rules()` |
| Recovery → Prediction real data | `RecoveryService.get_snapshot()` returns scores | Pass snapshot into `PredictionService.generate_all_predictions()` |

---

## 9. Summary Statistics

| Metric | Count |
|--------|-------|
| Total workspace pages | 10 |
| Total legacy views | 7 |
| Total buttons across all workspace pages | 20 |
| Wired buttons in workspace pages | **0** |
| Wired CTAs in legacy Dashboard | **6** |
| Pages with cross-references to other pages | **0** |
| Pages with next-step suggestions | **0** |
| Pages with purpose description | **0** |
| Services emitting Signals | **0/8** |
| Missing data chain connections | **6/8** |
| Unused shared subsystems | **13** |
| Existing engine chain connections | **1/8** (Workout→Recovery) |

---

## 10. Quick Wins — CTAs Ready for Wiring

These 11 buttons connect to existing services with zero new business logic:

| # | Source Page | Button | Target | Existing Method |
|---|-------------|--------|--------|-----------------|
| 1 | Home | Start Workout | Workout Selection | `prog_mgr.get_active_program_days()` |
| 2 | Mission | View History | Analytics workspace | Navigation engine |
| 3 | Planning | View Program | Program detail dialog | `prog_mgr.get_active_program()` |
| 4 | Prediction | Run Scenario | Prediction engine | `prediction_service.generate_all_predictions()` |
| 5 | Prediction | Export Report | Export to JSON/CSV | `SettingsView._export_json()` |
| 6 | Recovery | View Trends | Analytics workspace | Navigation engine |
| 7 | Knowledge | Search Knowledge | Search focus | `_search_bar.setFocus()` |
| 8 | Adaptive | Run Simulation | Prediction engine | `prediction_service.generate_all_predictions()` |
| 9 | Analytics | Export Report | Export to JSON/CSV | `SettingsView._export_json()` |
| 10 | System | Run Diagnostics | Kernel health check | `shared/kernel/kernel_health.py:compute_product_health()` |
| 11 | Intelligence | Generate Briefing | Narrative engine | `NarrativeEngine.render()` (all 9 templates) |

### Kitchen-Timer Estimates (per button)

- Simple navigation (analytics, mission → analytics): **15 minutes**
- Dialog/input (log weight, adjust goal): **30 minutes**
- Service call + display (run scenario, run diagnostics): **45 minutes**
- Export (reuse existing): **20 minutes**
- **Total: ~4 hours** to wire all 11 CTAs across all 10 pages.

## 11. Low-Hanging Engine Chain Fixes

| Gap | Fix | Lines Changed | Effort |
|-----|-----|---------------|--------|
| Recovery→Prediction | Pass `RecoveryService.get_snapshot()` scores into `PredictionService._generate_recovery_prediction()` | 3 lines in `prediction/application/__init__.py` | 30m |
| Prediction→Decision | Call `prediction_service.get_prediction_result()` from `DecisionEngine.evaluate_rules()` | 3 lines in `gymbrain/services/` | 30m |
| Page loading states | Wire `LoadingStateManager` into `CommandCenterController.refresh()` | 2 lines per page | 2h |
| Page empty states | Replace bare `QLabel("No X available")` with `EmptyStateWidget(cta="...")` | 1 line each, 10 pages | 2h |
| Real-time updates | Replace 60s timer with `EventBus → controller → signal → page` push | Already half-wired (controller has signal + event subs) | 1h |

---

*End of WORKFLOW_GRAPH.md*
