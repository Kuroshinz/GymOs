# REP-001E — Product Glue & Workflow Integration

**Status:** Draft  
**Date:** 2026-07-06  
**Auditor:** OpenCode

---

## Table of Contents

1. [The Core Problem](#1-the-core-problem)
2. [Current Workflow Map (AS-IS)](#2-current-workflow-map-as-is)
3. [Desired Workflow Map (TO-BE)](#3-desired-workflow-map-to-be)
4. [Workspace Transition Matrix](#4-workspace-transition-matrix)
5. [Missing Integrations](#5-missing-integrations)
6. [CTA Inventory (Current State)](#6-cta-inventory-current-state)
7. [Suggested Navigation Improvements](#7-suggested-navigation-improvements)
8. [Cross-Workspace Communication Map](#8-cross-workspace-communication-map)
9. [Engine Chain Gap Analysis](#9-engine-chain-gap-analysis)
10. [Implementation Guide](#10-implementation-guide)

---

## 1. The Core Problem

GymOS has **10 workspace pages** and **7 legacy views** — 17 screens total. Every screen renders data correctly, but **none of them know about each other**.

The shell (`command_center.py`) provides navigation via a nav rail and command palette. But from inside a workspace page, there is **zero indication** of:

- Why you're here
- What this data means
- What you should do next
- Which workspace naturally follows
- How this connects to your last action

### The Numbers

| Metric | Value |
|--------|-------|
| Workspace pages | 10 |
| Total buttons across all pages | 20+ |
| Buttons with `.clicked.connect()` | **0** |
| Pages with intra-page navigation to another workspace | **0** |
| Services that emit PySide Signals | **0** |
| Services that publish to EventBus | **0** |
| Cross-references to other workspaces by name | **0** |
| Pages with a bottom CTA bar | **0** |
| Pages that explain "why this matters" | **0** |

---

## 2. Current Workflow Map (AS-IS)

```
                    ┌─────────────────────┐
                    │   SIDEBAR (legacy)  │
                    │  7 buttons → views  │
                    └────────┬────────────┘
                             │
               ┌─────────────┴──────────────┐
               │      SHELL                  │
               │  command_center.py          │
               │  NavRail + Ctrl+K           │
               │                             │
               │  ┌──────────────────────┐   │
               │  │ Controller (pull)     │   │
               │  │ fetch_all() → data    │   │
               │  │ → push to 10 pages    │   │
               │  └──────────────────────┘   │
               └──────┬──────────┬──────────┘
                      │          │
         ┌────────────┘          └────────────┐
         │                                     │
    ┌────▼─────────────────────────────┐  ┌────▼──────────────────────────────┐
    │  10 WORKSPACE PAGES             │  │  7 LEGACY VIEWS                   │
    │  ┌─────────────────────────┐    │  │  ┌──────────────────────────┐     │
    │  │ Home (Executive D.)     │    │  │  │ Dashboard                │     │
    │  │ Mission (Goal W.)       │    │  │  │ WorkoutSelection          │     │
    │  │ Planning (Studio)       │    │  │  │ WorkoutView              │     │
    │  │ Prediction (Forecast)   │    │  │  │ ProgressView             │     │
    │  │ Recovery (Center)       │    │  │  │ PRView                   │     │
    │  │ Knowledge (Explorer)    │    │  │  │ RecoveryDashboard        │     │
    │  │ Adaptive (Opt. Center)  │    │  │  │ PredictionDashboard      │     │
    │  │ Analytics (Perf. Lab)   │    │  │  │ SettingsView             │     │
    │  │ System (Console)        │    │  │  └──────────────────────────┘     │
    │  │ Intelligence (Brief)    │    │  └───────────────────────────────────┘
    │  └─────────────────────────┘    │
    │                                 │
    │  ⚠ EVERY PAGE IS AN ISLAND     │
    │  No page links to another      │
    │  Every page ends with stretch() │
    │  Every button is decorative     │
    └─────────────────────────────────┘
```

### Key Observation

Every page follows the same dead-end pattern:

```
[Data loads] → [User reads data] → [User sees empty placeholders or static text]
                                        ↓
                              addStretch() — no forward action
                                        ↓
                              User must press Ctrl+K or click NavRail
                                        ↓
                              Entire decision of "what to do next"
                              is outsourced to the user's memory
```

---

## 3. Desired Workflow Map (TO-BE)

```
                    NATURAL ENGINE FLOW
                    ──────────────────

    WORKOUT ──→ RECOVERY ──→ PREDICTION ──→ ADAPTIVE ──→ PLANNING ──→ REVIEW ──→ KNOWLEDGE ──→ DASHBOARD
       │           │             │              │            │           │           │             │
       │           │             │              │            │           │           │             │
       ▼           ▼             ▼              ▼            ▼           ▼           ▼             ▼
    Log it    Check score    See forecast   Accept/adj.  Plan next   Weekly      Explore      See results
    (done)    (ready?)      (risk?)        (strategy)   (cycle)     (reflect)   (learn)      (overview)

                    WORKSPACE CONNECTIONS
                    ─────────────────────

    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │  HOME    │◄──►│ MISSION  │◄──►│PLANNING  │◄──►│PREDICTION│
    │  (hub)   │    │ (goals)  │    │ (cycles)  │    │(forecast) │
    └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘
         │               │               │               │
         ▼               ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │RECOVERY  │◄──►│ADAPTIVE  │◄──►│ANALYTICS │◄──►│KNOWLEDGE │
    │(readiness)│    │(strategy)│    │(perf)    │    │(graph)   │
    └──────────┘    └──────────┘    └──────────┘    └──────────┘
                                                    ┌──────────┐
                                                    │SYSTEM    │
                                                    │(console) │
                                                    └──────────┘
                                                    ┌──────────┐
                                                    │INTELLIG. │
                                                    │(briefing)│
                                                    └──────────┘

    Legend: ──→ natural workflow progression
            ◄──► cross-recommendation / related workspace
```

### Every Page Gets a "Next" Guidance Strip

```
┌─────────────────────────────────────────────────┐
│  [page content]                                 │
│                                                  │
│                                                  │
├─────────────────────────────────────────────────┤
│  NEXT: Recovery  │  RELATED: Knowledge          │
│  Check readiness │  Explore recent insights     │
│  before next     │  that impact your            │
│  session →       │  training →                  │
└─────────────────────────────────────────────────┘
```

---

## 4. Workspace Transition Matrix

Each cell = "Can the user reach workspace X from workspace Y?"

### Current State

| From \ To | Home | Mission | Plan | Predict | Recovery | Know | Adapt | Analytics | System | Intel |
|-----------|------|---------|------|---------|----------|------|-------|-----------|--------|-------|
| **Home** | — | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| **Mission** | ✗ | — | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| **Planning** | ✗ | ✗ | — | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| **Prediction** | ✗ | ✗ | ✗ | — | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| **Recovery** | ✗ | ✗ | ✗ | ✗ | — | ✗ | ✗ | ✗ | ✗ | ✗ |
| **Knowledge** | ✗ | ✗ | ✗ | ✗ | ✗ | — | ✗ | ✗ | ✗ | ✗ |
| **Adaptive** | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | — | ✗ | ✗ | ✗ |
| **Analytics** | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | — | ✗ | ✗ |
| **System** | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | — | ✗ |
| **Intel** | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | — |

**100% disconnected.** Every cell is ✗ — no page has a link to any other page.

### Navigation is shell-exclusive

The only way to move between workspaces:

| Method | Source | Scope |
|--------|--------|-------|
| Click nav rail item | `command_center.py` | All 10 pages |
| Ctrl+K → type page name | `command_center.py` | All 10 pages |
| Click sidebar item | `main_window.py` | 7 legacy views |

**No page contains internal navigation.** No "View in Recovery" or "Related: Knowledge Explorer" links.

### Desired State (minimal)

```
Every page → should link to 2-3 natural successors
Every page → should link back to Home (hub)
Home → should suggest 2-3 "recommended next" workspaces
```

---

## 5. Missing Integrations

### 5.1 Service-Layer Gaps

| Integration | Status | What's Needed |
|-------------|--------|---------------|
| Services emit Signals | ❌ | `AdaptiveService`, `MissionService`, `PlanningService`, `PredictionService`, `RecoveryService`, `KnowledgeService`, `AnalyticsService`, `SystemService` all use pull-only `fetch()`. None extend `QObject`. None emit `data_updated` or similar signals. |
| Services publish to EventBus | ❌ | No service publishes domain events (e.g., `GoalUpdated`, `PlanActivated`). Only `DashboardController` subscribes to events. |
| CommandCenterController event-driven | ⚠️ | `CommandCenterController` has `data_updated = Signal(CommandCenterData)` + 14 event subscriptions. The signal exists (confirmed at `ui/command_center/controller.py:15`). However, the 8 sub-services (`MissionService`, `PlanningService`, etc.) are **pull-only** — none extend `QObject`, none emit signals. The controller's signal fires only after a full `fetch_all()`. |
| Pull model creates staleness | ⚠️ | `CommandCenterService.fetch_all()` runs on timer (60s). Pages show data that may be seconds to minutes old with no visual indicator. |

### 5.2 Engine Chain Gaps

| Chain Segment | Status | Details |
|---------------|--------|---------|
| Workout → Recovery | ✅ | `DecisionEngine` receives `RecoveryProvider`. Volume data read from same DB. |
| Recovery → Prediction | ❌ | `PredictionService` uses **hardcoded defaults** (`recovery_score=70.0`, `fatigue=40.0`, `sleep=7.0`) for all recovery-related predictions (deload risk, recovery forecast, fatigue prediction). These engines have parameters wired to receive real data but get placeholders. |
| Prediction → Decision | ❌ | `generate_all_predictions()` is called from `ui/main_window.py:231` when user navigates to Predictions view, but `DecisionEngine` rules (`ProgressionRule`, `DeloadRule`, `PlateauRule`) don't consume prediction probabilities. The system has no predictive intelligence in its recommendations. |
| Decision → Adaptive | ❌ | `DecisionEngine` outputs (recommendations, weekly review) are not fed into `shared/adaptive_programming/`. The adaptive engine exists but receives no decision data. |
| Adaptive → Planning | ❌ | `shared/adaptive_programming/` outputs (strategy decisions) are not fed into `shared/planning/`. The planning engine cannot adapt based on adaptive decisions. |
| Planning → Weekly Review | ⚠️ | `WeeklyReviewGenerator` reads from `DataProvider` which wraps the DB. It can see planning data indirectly. But no formal bridge connects planning outputs to the review generator. |
| Weekly Review → Knowledge | ❌ | Weekly review outcomes (what worked, what didn't) are not recorded in `shared/knowledge_evolution/` as evidence. Knowledge cannot learn from user outcomes. |
| Knowledge → Dashboard | ❌ | `shared/optimization_knowledge/` insights are not rendered as dashboard recommendations. `KnowledgeService` returns hardcoded data. |

### 5.3 UI Layer Gaps

| Component | Status | What's Needed |
|-----------|--------|---------------|
| Bottom action strip per page | ❌ | No page has a "next steps" footer |
| "Why am I here" header | ❌ | No page explains its purpose |
| Empty states with CTAs | ❌ | `EmptyStateManager` exists but unused. Pages show bare "No X available" text. |
| Notification wiring | ❌ | `NotificationCenter` never triggered by any page action |
| Loading states | ❌ | `LoadingStateManager` never called by any page |
| Cross-page breadcrumb | ⚠️ | Breadcrumb widget exists but shows hierarchy (e.g., "home > analytics > recovery"), not workflow progression |

---

## 6. CTA Inventory (Current State)

### 6.1 Workspace Page Buttons

| Page | Button | Type | Connected? | Should Do |
|------|--------|------|------------|-----------|
| Home | Start Workout | Primary | ❌ | Navigate to mission (or legacy workout selection) |
| Home | Log Weight | Secondary | ❌ | Open weight input dialog (or navigate to settings with weight form) |
| Mission | Adjust Goal | Primary | ❌ | Open goal editing interface |
| Mission | View History | Secondary | ❌ | Navigate to analytics (progress view) |
| Planning | Adjust Week | Primary | ❌ | Open planning adjustment interface |
| Planning | View Program | Secondary | ❌ | Show full program details |
| Prediction | Run Scenario | Primary | ❌ | Open scenario engine |
| Prediction | Export Report | Secondary | ❌ | Trigger prediction export |
| Recovery | View Details | Primary | ❌ | Expand recovery detail panel |
| Recovery | View Trends | Secondary | ❌ | Navigate to analytics (trend view) |
| Knowledge | Explore Graph | Primary | ❌ | Open knowledge graph visualization |
| Knowledge | Search Knowledge | Secondary | ❌ | Focus knowledge search bar |
| Adaptive | Review Decision | Primary | ❌ | Show decision details |
| Adaptive | Run Simulation | Secondary | ❌ | Open simulation engine |
| Analytics | Export Report | Primary | ❌ | Trigger analytics export |
| Analytics | Compare Periods | Secondary | ❌ | Open period comparison |
| System | View Logs | Primary | ❌ | Open system logs |
| System | Run Diagnostics | Secondary | ❌ | Run system diagnostics |
| Intelligence | Generate Briefing | Primary | ❌ | Generate AI briefing |
| Intelligence | Configure AI | Secondary | ❌ | Open AI configuration |

**20 buttons. Zero connections.**

### 6.2 Dashboard (Legacy) CTAs

| CTA | Source | Connected? | Action |
|-----|--------|------------|--------|
| Start Workout | DashboardView | ✅ | Navigate to workout selection |
| View All PRs | DashboardView | ✅ | Navigate to PR view |
| View Recommendations | DashboardView | ✅ | Navigate to progress view |
| Weekly Review | DashboardView | ✅ | Navigate to progress view |
| Log Weight | DashboardView | ✅ | Navigate to settings (BUG: no weight input there) |
| Import Program | DashboardView | ✅ | Open ImportWizard |

**Legacy Dashboard has all CTAs wired. Workspace pages have none.** This is the most striking discrepancy.

### 6.3 What Each Button Should Actually Do

Using existing canonical services (no new code):

| Button | Existing Service | Existing Method |
|--------|-----------------|-----------------|
| Start Workout | `prog_mgr.get_active_program_days()` | Returns day list for selection |
| Adjust Goal | `decision_engine.get_goal_progress()` | Returns current goal state (read-only — no write API exists yet) |
| View History | `db.list_sessions(limit=N)` | Returns past sessions |
| Adjust Week | `prog_mgr.get_active_program()` | Returns current program (read-only — no modify API) |
| View Program | `prog_mgr.get_active_program()` | Returns program with days/mesocycles |
| Run Scenario | `prediction_service.generate_all_predictions()` | Already computes scenarios |
| Export Report | `settings_view._export_json()` | Same export logic |
| View Details | `recovery_service.get_snapshot()` | Returns full snapshot |
| View Trends | `recovery_service.get_recent_scores(days=30)` | Already called |
| Explore Graph | `shared/graph/graph.py:KnowledgeGraph` | Returns graph data |
| Search Knowledge | `shared/knowledge_evolution/query.py:KnowledgeQueryEngine` | Returns query results |
| Run Diagnostics | `shared/kernel/kernel_health.py:compute_product_health()` | Returns health metrics |
| Generate Briefing | `ui/narrative/engine.py` or template composers | Already have template files for all briefing types |

---

## 7. Suggested Navigation Improvements

### 7.1 Per-Page "Next Steps" Footer

Each page footer should contain:

```python
class NextStepsFooter(QFrame):
    """Shows 2-3 suggested next actions at the bottom of every workspace page."""
    def __init__(self, suggestions: list[NextStepSuggestion]):
        # Each suggestion: icon + label + "Go to X" button
        # Example: "Your recovery score dropped 12% → Check Recovery Center"
        # Wire: button.clicked → navigation_engine.navigate("recovery", "suggestion")
```

### 7.2 Workspace-Aware Empty States

Replace all `QLabel("No X available")` with:

```python
class WorkspaceEmptyState(QFrame):
    def __init__(self, workspace_id: str, action: str, target_workspace: str):
        # "No training data yet. Start by importing a program →"
        # OR "No predictions available. Complete more workouts first →"
        # OR "Ready to review your week? → Go to Weekly Review"
```

### 7.3 Contextual "Related Workspace" Links

```python
class RelatedWorkspaceLink(QPushButton):
    """A styled link to another workspace with context."""
    # "Related: Analytics (View your Performance Lab)"
    # "Your goal progress affects this — adjust in Mission Center"
```

### 7.4 Recommended Connection Points

| Source Page | Target | Rationale | Trigger Condition |
|-------------|--------|-----------|-------------------|
| Home | Mission | "Set your goal to track progress" | No active goal |
| Home | Planning | "Plan your next training cycle" | Last mesocycle > 4 weeks ago |
| Mission | Analytics | "See your goal progress over time" | Goal progress > 0% |
| Planning | Prediction | "Check if your plan is on track" | Plan activated |
| Prediction | Recovery | "Low recovery affects predictions" | Recovery score < 60 |
| Recovery | Adaptive | "Let the system adapt to your readiness" | Recovery trend declining |
| Adaptive | Knowledge | "Learn why this adaptation was suggested" | Decision made |
| Knowledge | Intelligence | "Get a briefing on recent findings" | Knowledge updated |
| Analytics | Home | "Return to your dashboard" | Always |

---

## 8. Cross-Workspace Communication Map

### 8.1 Data Flow (How data moves between workspaces)

```
                                    ┌─────────────┐
                                    │  EventBus   │
                                    │  (shared)   │
                                    └──────┬──────┘
                                           │ publishes/receives
                    ┌──────────────────────┼──────────────────────┐
                    │                      │                      │
                    ▼                      ▼                      ▼
           ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
           │ DashboardCtrl    │  │ CommandCenterCtrl│  │ RecoveryService  │
           │ (subscribes 10   │  │ (pulls via fetch)│  │ (subscribes to   │
           │  domain events)  │  │  no signals)      │  │  events)         │
           └──────────────────┘  └──────────────────┘  └──────────────────┘
                    │                      │
                    │ data_updated Signal   │ fetch() → CommandCenterData
                    ▼                      ▼
           ┌──────────────────┐  ┌──────────────────┐
           │ DashboardView    │  │ All 10 pages     │
           │ (legacy, wired)  │  │ (no updates)     │
           └──────────────────┘  └──────────────────┘
```

### 8.2 Current Communication Channels

| Channel | Used By | Purpose | Events |
|---------|---------|---------|--------|
| `EventBus` | `DashboardController`, `RecoveryService`, `NutritionService` | Cross-module decoupled messaging | 66 domain events |
| `DashboardController.data_updated` Signal | `DashboardView` | Push new data to legacy dashboard | All 10 subscribed events |
| `CommandCenterController` (pull) | All 10 workspace pages | Poll for updates every 60s | N/A |
| `PySide Signals` | `WorkoutView.workout_saved`, `WorkoutSelectionView.workout_selected` | Intra-view communication | 4 custom signals |

### 8.3 Missing Communication Channels

| Needed Channel | Purpose | Currently Handled By |
|----------------|---------|---------------------|
| `MissionService.data_updated` Signal | Notify pages when goal changes | Nothing |
| `PlanningService.data_updated` Signal | Notify pages when plan changes | Nothing |
| `RecoveryService` → `PredictionService` | Feed real recovery data into predictions | Hardcoded defaults |
| `PredictionService` → `DecisionEngine` | Feed prediction probabilities into rules | Never called |
| `DecisionEngine` → `AdaptiveProgramming` | Feed recommendations into adaptation | No bridge |
| All services → `NotificationCenter` | Notify user of important changes | Nothing |
| All services → `LoadingStateManager` | Show loading during fetch | Nothing |
| All pages → `EmptyStateManager` | Show contextual empty states | Nothing |

---

## 9. Engine Chain Gap Analysis

### 9.1 Natural Chain

```
Workout → Recovery → Prediction → Decision → Adaptive → Planning → Review → Knowledge
   │         │           │            │          │          │        │         │
   │         │           │            │          │          │        │         │
   ▼         ▼           ▼            ▼          ▼          ▼        ▼         ▼
Log it   Check       Forecast    Recommend   Adapt      Plan     Reflect   Learn
(done)   readiness   risk        next step   strategy   next     & review  & store
                     & ETA                  & decide   cycle
```

### 9.2 Current State of Each Connection

| # | Connection | Exists? | Evidence | Fix |
|---|-----------|---------|----------|-----|
| 1 | **Workout → Recovery** | ✅ | Same DB; `RecoveryService` reads volume; `DecisionEngine` gets `RecoveryProvider` | Already works |
| 2 | **Recovery → Prediction** | ❌ | `PredictionService` hardcodes recovery defaults | Pipe `RecoveryService.get_snapshot()` → `PredictionService` call |
| 3 | **Prediction → Decision** | ❌ | `generate_all_predictions()` never called; rules don't use prediction results | Call predictions; pass probabilities into rule evaluation |
| 4 | **Decision → Adaptive** | ❌ | `DecisionEngine` outputs not consumed by `adaptive_programming` | Bridge recommendations into adaptive strategy engine |
| 5 | **Adaptive → Planning** | ❌ | `adaptive_programming` outputs not consumed by `planning` engine | Bridge strategy decisions into planning allocation |
| 6 | **Planning → Review** | ⚠️ | `WeeklyReviewGenerator` reads from shared DB but not from planning domain | Add planning metrics to review input |
| 7 | **Review → Knowledge** | ❌ | Review outcomes not persisted to `knowledge_evolution` | Store review results as knowledge evidence |
| 8 | **Knowledge → Dashboard** | ❌ | `KnowledgeService` returns hardcoded insights; no real knowledge data reaches UI | Wire `KnowledgeQueryEngine` → dashboard recommendation models |

### 9.3 Chain Gap Impact

| Gap | Affected Predictions/Decisions | Severity |
|-----|-------------------------------|----------|
| Recovery→Prediction | Deload risk, recovery forecast, fatigue prediction | High — all wrong by default |
| Prediction→Decision | PR probability, plateau detection, progression recommendations | High — no predictive intelligence |
| Decision→Adaptive | Volume adjustments, frequency changes, deload timing | Medium — manual override needed |
| Adaptive→Planning | Mesocycle structure, exercise selection, periodization | Medium — planning can't adapt |
| Review→Knowledge | Pattern mining, evidence collection, confidence scoring | Low — works with direct DB input |
| Knowledge→Dashboard | Recommendation quality, insight relevance | Medium — hardcoded fallback |

---

## 10. Implementation Guide

### 10.1 No-Code Changes (Documentation Naming)

These recommendations require only adding labels, descriptions, and CTAs to existing pages — no new engines or services:

| Priority | Change | Effort | Pages Affected |
|----------|--------|--------|---------------|
| P0 | Wire all 20 buttons to their target callbacks | 1d | All 10 pages |
| P0 | Add "Next Steps" suggestion footer to every page | 2d | All 10 pages |
| P1 | Add purpose description header to every page | 1d | All 10 pages |
| P1 | Replace static empty labels with EmptyStateWidget (CTA + suggestion) | 2d | All 10 pages |
| P1 | Add "Related workspace" link to bottom of each page | 1d | All 10 pages |
| P2 | Replace `addStretch()` with content-aware bottom bar | 1d | All 10 pages |
| P2 | Name every workspace's successor in the page header | 0.5d | All 10 pages |

### 10.2 Signal Wiring (Service Layer)

| Priority | Change | Effort |
|----------|--------|--------|
| P1 | Add `data_updated = Signal(dict)` to `AdaptiveService`, `MissionService`, `PlanningService`, `PredictionService`, `RecoveryService`, `KnowledgeService`, `AnalyticsService`, `SystemService` | 1d |
| P1 | Wire `CommandCenterController` to listen to service signals (like `DashboardController` does) | 1d |
| P2 | Add `notification` signal to all services to trigger `NotificationCenter` | 1d |

### 10.3 Engine Wiring (Shared Layer)

| Priority | Change | Effort |
|----------|--------|--------|
| P0 | Wire `PredictionService` to consume `RecoveryService.get_snapshot()` for recovery-related predictions | 1d |
| P0 | Call `prediction_service.generate_all_predictions()` in main.py and pipe into `DecisionEngine` rule evaluation | 1d |
| P1 | Bridge `DecisionEngine` recommendations → `shared/adaptive_programming/` strategy engine input | 2d |
| P2 | Bridge `shared/adaptive_programming/` → `shared/planning/` engine | 2d |
| P2 | Wire review outcomes into `shared/knowledge_evolution/` | 2d |
| P2 | Wire `shared/optimization_knowledge/` queries into `KnowledgeService.fetch()` | 1d |

### 10.4 CTA Wire-Up Map (Exact Connections)

| Page | Button | Wire To | Method |
|------|--------|---------|--------|
| Home | Start Workout | `self.parent().navigate("mission")` or legacy `PAGE_INDEX["workout"]` | `navigation.navigate()` |
| Home | Log Weight | Open `QInputDialog.getDouble()` for weight | `db.save_body_weight()` |
| Mission | Adjust Goal | Open `QInputDialog` for goal weight/date | `decision_engine.get_goal_progress()` (read-only — need write) |
| Mission | View History | `navigation.navigate("analytics")` | Existing nav |
| Planning | Adjust Week | `navigation.navigate("mission")` to see goal context | Existing nav |
| Planning | View Program | Open program detail dialog | `prog_mgr.get_active_program()` |
| Prediction | Run Scenario | Call `prediction_service.generate_all_predictions()` | Existing service |
| Prediction | Export Report | Call `SettingsView._export_json()` logic | Reuse export |
| Recovery | View Details | Expand/collapse detail panel in page | Local layout |
| Recovery | View Trends | `navigation.navigate("analytics")` | Existing nav |
| Knowledge | Explore Graph | Open graph visualization | `shared/graph/` API |
| Knowledge | Search Knowledge | Focus search bar | Local widget focus |
| Adaptive | Review Decision | Expand decision detail | Local layout |
| Adaptive | Run Simulation | Call `prediction_service.generate_all_predictions()` with scenario params | Reuse prediction |
| Analytics | Export Report | Call `SettingsView._export_json()` logic | Reuse export |
| Analytics | Compare Periods | Toggle period comparison mode | Local state |
| System | View Logs | Open log viewer dialog | New (observability) |
| System | Run Diagnostics | Call `shared/kernel/kernel_health.py` | Existing engine |

---

## Appendix: Full CTA Inventory by File

```
home_page.py
  ├─ _start_btn "Start Workout"              → DECORATIVE
  └─ _log_weight_btn "Log Weight"            → DECORATIVE

mission_page.py
  ├─ _adjust_btn "Adjust Goal"               → DECORATIVE
  └─ _history_btn "View History"             → DECORATIVE

planning_page.py
  ├─ _adjust_btn "Adjust Week"               → DECORATIVE
  └─ _view_program_btn "View Program"        → DECORATIVE

prediction_center_page.py
  ├─ _scenario_btn "Run Scenario"            → DECORATIVE
  └─ _export_btn "Export Report"             → DECORATIVE

recovery_center_page.py
  ├─ _detail_btn "View Details"              → DECORATIVE
  └─ _trends_btn "View Trends"               → DECORATIVE

knowledge_center_page.py
  ├─ _explore_btn "Explore Graph"            → DECORATIVE
  └─ _search_btn "Search Knowledge"          → DECORATIVE

adaptive_center_page.py
  ├─ _review_btn "Review Decision"           → DECORATIVE
  └─ _simulate_btn "Run Simulation"          → DECORATIVE

analytics_center_page.py
  ├─ _export_btn "Export Report"            → DECORATIVE
  └─ _compare_btn "Compare Periods"         → DECORATIVE

system_center_page.py
  ├─ _logs_btn "View Logs"                   → DECORATIVE
  └─ _diag_btn "Run Diagnostics"            → DECORATIVE

narrative_page.py
  ├─ _brief_btn "Generate Briefing"          → DECORATIVE
  └─ _config_btn "Configure AI"             → DECORATIVE

TOTAL: 20 buttons, 0 connected. Every CTA is a dead end.
```

---

## 11. Per-Workspace Product Glue Matrix

Every workspace page should answer: "Why am I here?", "What now?", "Where next?".

### 11.1 Home — Executive Dashboard

| Question | Answer |
|----------|--------|
| **Current state** | Hero with Recovery Ring (--), Goal Ring (--), KPI strip (all --), empty insights, empty activity feed, static warning. |
| **Why this matters** | This is the command center. If empty, user has no program or data. |
| **Suggested next action** | "Import a program to get started" |
| **Related workspace** | Mission (goal tracking), Recovery (readiness), Analytics (performance) |
| **Recent changes** | None shown — no activity feed wiring |
| **System confidence** | Not displayed |
| **Primary CTA** | "Start Workout" → should navigate to legacy workout selection (PAGE_INDEX["workout"]) |
| **Secondary CTA** | "Log Weight" → should open weight input dialog |

### 11.2 Mission — Goal Workspace

| Question | Answer |
|----------|--------|
| **Current state** | Goal name ("--"), progress bar (0%), KPI strip (--), empty decision timeline, empty insights, static alerts. |
| **Why this matters** | Tracks lean bulk goal progress (63.4 → 72-75 kg). |
| **Suggested next action** | "Set your first goal" if no active goal; "View progress in Analytics" if goal exists. |
| **Related workspace** | Analytics (trend view), Prediction (goal ETA) |
| **Recent changes** | Not shown |
| **System confidence** | Not displayed |
| **Primary CTA** | "Adjust Goal" → should open goal editing dialog |
| **Secondary CTA** | "View History" → should navigate to Analytics |

### 11.3 Planning — Planning Studio

| Question | Answer |
|----------|--------|
| **Current state** | Cycle name ("--"), week progress (0/0), volume chart (flatline), empty sessions, empty recs. |
| **Why this matters** | Shows current mesocycle progress and weekly schedule. |
| **Suggested next action** | "Start your next workout" if sessions remain; "View program details" to review. |
| **Related workspace** | Prediction (forecast), Recovery (readiness for training) |
| **Recent changes** | Not shown |
| **System confidence** | Not displayed |
| **Primary CTA** | "Adjust Week" → should navigate to program adjustment |
| **Secondary CTA** | "View Program" → should show full program dialog |

### 11.4 Prediction — Forecast Studio

| Question | Answer |
|----------|--------|
| **Current state** | Confidence gauge (0%), risk meter (0%), KPI strip (--), flat timeline, empty scenarios/risks. |
| **Why this matters** | Forecasts PR probability, plateau risk, recovery, deload timing, and goal ETA. |
| **Suggested next action** | "View recovery data affects predictions" — link to Recovery center if recovery score < 70. |
| **Related workspace** | Recovery (readiness affects predictions), Adaptive (decision support) |
| **Recent changes** | Not shown |
| **System confidence** | Forecast gauge displays 0% — should show actual prediction confidence |
| **Primary CTA** | "Run Scenario" → should call `prediction_service.generate_all_predictions()` with params |
| **Secondary CTA** | "Export Report" → should reuse settings export logic |

### 11.5 Recovery — Recovery Center

| Question | Answer |
|----------|--------|
| **Current state** | Score monument ("--"), vitals (sleep/stress/fatigue all "--"), flat timeline, empty readiness/ warnings. |
| **Why this matters** | Recovery score determines training readiness. Low score → deload risk. |
| **Suggested next action** | "Check predictions to see if deload is needed" if score declining. |
| **Related workspace** | Prediction (deload forecast), Analytics (trend view) |
| **Recent changes** | Not shown |
| **System confidence** | Not displayed |
| **Primary CTA** | "View Details" → expand recovery breakdown panel |
| **Secondary CTA** | "View Trends" → should navigate to Analytics |

### 11.6 Knowledge — Knowledge Explorer

| Question | Answer |
|----------|--------|
| **Current state** | Node/edge counts ("--"), KPI strip (--), empty updates, empty insights, confidence gauge (0%). |
| **Why this matters** | Domain knowledge graph with pattern mining, evidence, and confidence tracking. |
| **Suggested next action** | "Explore patterns discovered from your training data" |
| **Related workspace** | Intelligence (AI briefings), Adaptive (strategy decisions) |
| **Recent changes** | Not shown (knowledge_updates always empty) |
| **System confidence** | Confidence gauge at 0% — should show actual knowledge confidence |
| **Primary CTA** | "Explore Graph" → should open graph visualization |
| **Secondary CTA** | "Search Knowledge" → should focus search bar |

### 11.7 Adaptive — Optimization Center

| Question | Answer |
|----------|--------|
| **Current state** | Gauge (0%), flow label ("--"), score label ("--"), KPI strip (--), empty decisions/strategies/recs. |
| **Why this matters** | Tracks system adaptations — volume adjustments, frequency changes, deload timing. |
| **Suggested next action** | "Review recent adaptations and their outcomes" |
| **Related workspace** | Prediction (simulation), Knowledge (learn why) |
| **Recent changes** | Not shown (uses hardcoded data) |
| **System confidence** | Decision confidence gauge at 0% |
| **Primary CTA** | "Review Decision" → expand decision detail |
| **Secondary CTA** | "Run Simulation" → call prediction with scenario params |

### 11.8 Analytics — Performance Lab

| Question | Answer |
|----------|--------|
| **Current state** | Primary metric ("--"), volume chart (flatline), compliance gauge (0%), empty PRs, empty muscle balance, empty activity. |
| **Why this matters** | Volume trends, compliance, muscle balance, and performance metrics. |
| **Suggested next action** | "Complete more workouts to populate analytics" |
| **Related workspace** | Home (dashboard), Recovery (score trends) |
| **Recent changes** | Activity feed shows static "No recent activity" |
| **System confidence** | Not displayed |
| **Primary CTA** | "Export Report" → reuse settings export logic |
| **Secondary CTA** | "Compare Periods" → toggle period comparison |

### 11.9 System — Platform Console

| Question | Answer |
|----------|--------|
| **Current state** | Health gauge (0%), KPI strip (--), empty capabilities, empty release data, empty kernel data. |
| **Why this matters** | Platform health, capability progress, release readiness, and kernel runtime. |
| **Suggested next action** | "View diagnostics to check system health" |
| **Related workspace** | Intelligence (briefing), Analytics (reports) |
| **Recent changes** | Not shown |
| **System confidence** | Health gauge at 0% |
| **Primary CTA** | "View Logs" → open log viewer |
| **Secondary CTA** | "Run Diagnostics" → call `shared/kernel/kernel_health.py` |

### 11.10 Intelligence — AI Briefing Center

| Question | Answer |
|----------|--------|
| **Current state** | "AI Briefing: Ready", empty narrative stack, empty updates, empty recs. Has working NarrativeEngine with 9 templates. |
| **Why this matters** | AI-generated coach narratives from training data — morning brief, focus, recovery, prediction, planning, knowledge summaries. |
| **Suggested next action** | "Generate a briefing to see AI insights" |
| **Related workspace** | Knowledge (data source), Recovery/Prediction/Planning (narrative inputs) |
| **Recent changes** | NarrativeEngine renders from current data — most accurate workspace |
| **System confidence** | Not displayed (narratives show "no data" gracefully) |
| **Primary CTA** | "Generate Briefing" → runs NarrativeEngine.render() for all templates |
| **Secondary CTA** | "Configure AI" → AI configuration dialog |

---

## 12. Quick Wins — CTAs That Can Be Wired NOW

These buttons have existing target services — they just need `.clicked.connect()`:

| # | Page | Button | Wire To | One-Liner |
|---|------|--------|---------|-----------|
| Q1 | Home | Start Workout | `parent()._switch_to(PAGE_INDEX["workout"])` | `_start_btn.clicked.connect(lambda: self.parent()._switch_to(1))` |
| Q2 | Mission | View History | Navigate to Analytics workspace in CommandCenter | `_history_btn.clicked.connect(lambda: navigation.navigate("analytics"))` |
| Q3 | Planning | View Program | `prog_mgr.get_active_program()` in dialog | `_view_program_btn.clicked.connect(lambda: show_program_dialog(self._prog_mgr))` |
| Q4 | Prediction | Run Scenario | `prediction_service.generate_all_predictions()` | `_scenario_btn.clicked.connect(lambda: self._run_scenario())` |
| Q5 | Prediction | Export Report | Reuse `SettingsView._export_json()` | `_export_btn.clicked.connect(lambda: self._export_report())` |
| Q6 | Recovery | View Trends | Navigate to Analytics workspace | `_trends_btn.clicked.connect(lambda: navigation.navigate("analytics"))` |
| Q7 | Knowledge | Search Knowledge | Focus search bar | `_search_btn.clicked.connect(lambda: self._search_bar.setFocus())` |
| Q8 | Adaptive | Run Simulation | `prediction_service.generate_all_predictions()` with scenario params | `_simulate_btn.clicked.connect(lambda: self._run_simulation())` |
| Q9 | Analytics | Export Report | Reuse `SettingsView._export_json()` | `_export_btn.clicked.connect(lambda: self._export_report())` |
| Q10 | System | Run Diagnostics | `shared/kernel/kernel_health.py:compute_product_health()` | `_diag_btn.clicked.connect(lambda: self._run_diagnostics())` |
| Q11 | Intelligence | Generate Briefing | `NarrativeEngine.render()` all templates | Already works via existing NarrativeEngine |

These 11 CTAs require only signal wiring — no new services, no new engines, no new business logic.

---

## 13. What to Remove

| Component | Location | Reason |
|-----------|----------|--------|
| Legacy sidebar navigation 7 views | `ui/main_window.py` | Duplicates CommandCenter NavRail. Two navigation systems confuse users. |
| Standalone RecoveryDashboard | `ui/recovery/recovery_dashboard.py` | Superseded by RecoveryCenterPage in CommandCenter. Same data, different render. |
| Standalone PredictionDashboard | `ui/prediction/prediction_dashboard.py` | Superseded by PredictionCenterPage in CommandCenter. |
| `addStretch()` calls | All 10 workspace pages | Dead-end pattern. Replace with CTA footer. |
| Static "No X available" labels | All 10 workspace pages | Replace with `EmptyStateWidget` (already built, never used). |
| Hardcoded recovery score defaults | `modules/prediction/application/__init__.py` lines 142, 206, 233, 343, 363 | Replace with real `RecoveryService.get_snapshot()` data. |
| Decorative buttons (20 total) | All 10 pages | Wire or remove. Buttons that don't do anything destroy trust. |

---

*End of REP-001E — Product Glue & Workflow Integration*
