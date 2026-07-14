# RFC-031 — GymOS 2.0 Product Blueprint

> **Status:** Pre-Implementation — No Code Modified
> **Role:** Lead Product Designer
> **Date:** 2026-07-14
> **Supersedes:** REP-007 (Dashboard Experience)
> **Depends on:** RFC-030 (Visual Language 2.0)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problems](#2-problems)
3. [Goals](#3-goals)
4. [Part 1: Application Shell](#4-part-1-application-shell)
5. [Part 2: Information Architecture](#5-part-2-information-architecture)
6. [Part 3: User Journey](#6-part-3-user-journey)
7. [Part 4: Wireframes](#7-part-4-wireframes)
8. [Part 5: Component Hierarchy](#8-part-5-component-hierarchy)
9. [Part 6: Visual Hierarchy](#9-part-6-visual-hierarchy)
10. [Part 7: Product Identity](#10-part-7-product-identity)
11. [Part 8: Implementation Roadmap](#11-part-8-implementation-roadmap)
12. [Success Criteria](#12-success-criteria)

---

## 1. Executive Summary

GymOS has reached architectural maturity. The backend, domain models, prediction engine, recovery algorithms, testing infrastructure, and data pipelines are production-ready. The weakest link is now the user experience.

The current UI was built widget-by-widget as features were added. The result is a functional but undifferentiated desktop application — vertically stacked sections, equal visual weight everywhere, no product shell, no editorial rhythm, and a pervasive "Qt Layout" feeling.

This blueprint defines GymOS 2.0: a complete product transformation that turns a PySide application into a premium commercial fitness operating system.

**The transformation is structural, not decorative.** Every section in this document changes how pages are composed, how users flow between tasks, how information is weighted, and how the product feels. Nothing is "just a restyle."

**Key decisions:**

| Decision | Rationale |
|----------|-----------|
| Single-window shell with overlay system | Eliminates dialog fragmentation, enables command palette |
| Editorial grid replaces stacked widgets | Creates visual hierarchy through asymmetry and weighted columns |
| Coach as the primary narrative layer | Differentiates GymOS from every tracker — guidance before data |
| Hero-first every page | First-screen impact sets emotional tone before the user commits to a task |
| Command palette as primary navigation | Reduces sidebar reliance, enables keyboard-driven power use |
| Motion as a communication tool | Every animation answers "where did this come from?" |

---

## 2. Problems

### 2.1 Vertically Stacked Sections

Every page is a linear column of widgets. The user scrolls past equal-sized blocks with no visual distinction between "most important" and "supporting."

```
[Header]
[Card 1]
[Card 2]
[Card 3]
[Card 4]
...scroll...
```

**Consequence:** The user cannot determine priority from layout. All decisions require reading.

### 2.2 Equal Visual Weight

Every card uses the same radius, same elevation, same background, same padding. A recovery score card and a prediction insight card are visually identical despite serving fundamentally different roles.

**Consequence:** The interface is flat. Nothing draws attention first. The user's eye wanders.

### 2.3 Weak Hero

The dashboard hero is cramped, crowded with rings and metrics, and lacks emotional impact. The greeting, phase info, prediction, and metrics compete in the same space.

**Consequence:** The user's first impression is "data" rather than "guidance."

### 2.4 Widget-First Thinking

Pages are assembled from reusable widget components rather than designed as editorial compositions. The layout serves component reuse, not user attention flow.

**Consequence:** Pages feel like dashboards rather than destinations. The user is managing widgets, not progressing through a workout.

### 2.5 No Product Shell

There is no cohesive shell — no global header, no consistent overlay layer, no notification system, no command palette. Each dialog and modal is ad-hoc.

**Consequence:** Every interaction feels like it was bolted on. The product lacks a unified interaction model.

### 2.6 Inconsistent Composition

Some pages use `EditorialGrid`, some use `QGridLayout`, some use stacked `QVBoxLayout`. The CommandCenter pages have a different layout system from the MainWindow pages.

**Consequence:** The user re-learns layout on every page.

### 2.7 Cards That All Look Identical

`AppCard`, `MetricCard`, `InsightCard`, `SectionPanel` — all use the same surface color, same radius, same border. An insight from the coach and a metric from the progress tracker are visually interchangeable.

**Consequence:** Cards don't communicate their purpose. The user reads every card to understand what it is.

### 2.8 Qt Layout Feeling

Grids with fixed spacing, scroll areas with visible scrollbars, windows that feel like windows rather than surfaces — the underlying toolkit leaks through.

**Consequence:** The product feels like software, not an operating system.

---

## 3. Goals

### 3.1 Primary Goals

| Goal | Success Metric |
|------|---------------|
| First-screen impact | Every page communicates its primary purpose without scrolling |
| Attention flow | The user's eye moves in the intended order on every page |
| Task completion | The primary action on every page is identifiable in <1 second |
| Coach-centric | Coaching guidance appears before raw data on every page |
| Consistent shell | All pages share the same chrome, overlay, and interaction model |

### 3.2 Secondary Goals

| Goal | Success Metric |
|------|---------------|
| Keyboard-navigable | All primary actions accessible via command palette |
| Reduced cognitive load | No more than 7 information blocks per viewport |
| Emotional connection | Users describe the app as "premium" and "calm" |
| Motion confidence | Animations feel intentional, not decorative |

---

## 4. Part 1: Application Shell

### 4.1 Shell Architecture

```
+------------------------------------------------------------------+
|  SIDEBAR (collapsible, 56px/200px)                               |
|  +--------+  +-------------------------------------------------+ |
|  | Icon   |  | HEADER                                          | |
|  | nav    |  |  Breadcrumb · Page title · Global actions       | |
|  |        |  +-------------------------------------------------+ |
|  |        |  | CONTENT                                          | |
|  |        |  |  (EditorialGrid / Hero / Sections)              | |
|  |        |  |                                                  | |
|  |        |  |                                                  | |
|  +--------+  +-------------------------------------------------+ |
|              | STATUS BAR (optional, micro)                       |
+------------------------------------------------------------------+

OVERLAY LAYER      → Command palette (⌘K), modals
NOTIFICATION LAYER → Toasts, snackbars (top-right, stackable)
DIALOG LAYER       → System dialogs (centered, backdrop blur)
FLOATING SURFACES  → Tooltips, popovers, context menus
```

### 4.2 Sidebar

**Purpose:** Application navigation + status overview.

**Behavior:**
- Default: collapsed (56px, icons only) — maximizes content width
- Hover/click: expands to 200px — shows labels + micro-status (streak, readiness dot)
- Collapsed shows: icon + unread indicator dot (if applicable)
- Expanded shows: icon + label + active indicator + micro-metric
- Keyboard: `⌘[1-9]` navigates directly, `⌘\` toggles expand

**Visual:**
- Darker than content area (`background_alt`)
- Active item: subtle glow on icon (not background highlight)
- Items grouped semantically (Training, Data, System) with tiny section labels
- Bottom: user avatar/initial + streak counter + settings gear

**Why:** The sidebar is a navigation tool, not a content area. When collapsed, it gives maximum space to the content. When expanded, it provides context without overwhelming.

### 4.3 Header

**Purpose:** Page identity + global actions.

**Content:**
- Left: Page title (large editorial heading) + optional breadcrumb for sub-pages
- Right: Global action buttons (⌘K palette trigger, notifications bell, theme toggle)

**Visual:**
- Not a separate bar — the page title IS the header
- No background box — title floats on the content surface
- Actions are icon-only, subtle, secondary to page content

**Why:** Separating the header from the page title creates unnecessary chrome. The content begins with the title. Actions are available but invisible until needed.

### 4.4 Content Area

**Purpose:** The editorial canvas.

**Behavior:**
- Fills remaining space after sidebar + header
- Scrolls vertically (horizontal scroll is forbidden)
- Uses `EditorialGrid` as the single layout primitive
- Every page starts with a hero section (see Part 6)

**Visual:**
- Single-column by default, multi-column via `EditorialGrid`
- Sections separated by whitespace, not lines or dividers
- Maximum content width: 1200px (centered on ultrawide)

### 4.5 Overlay Layer

**Purpose:** Modal interactions without losing context.

**Includes:**
- **Command Palette** (`⌘K`): Global search + action launcher. Semi-transparent backdrop, centered input, results list with keyboard navigation. Categories: Pages, Actions, Settings, Exercises.
- **Quick Actions**: Inline popovers for secondary tasks (log weight, import program) — not full dialogs.

**Why:** Dialogs break flow. The overlay layer keeps the page visible underneath, reducing cognitive dislocation.

### 4.6 Notification Layer

**Purpose:** Surface events without demanding attention.

**Includes:**
- **Toasts**: Non-blocking, auto-dismiss (4s), stackable, top-right
- **Snackbars**: Action-optional (e.g., "Workout saved · Undo")
- **Badge dots**: Unread indicators on sidebar items

**Types:**
| Type | Color | Example |
|------|-------|---------|
| Achievement | Aurora glow | "New PR: Bench Press +2.5kg" |
| Reminder | No color | "Time to log your weight" |
| Warning | Starlight | "Recovery score dropping" |
| Error | Cosmic rose | "Program import failed" |
| Success | Aurora | "Workout saved" |

### 4.7 Dialog Layer

**Purpose:** System-level interactions that need focus.

**When to use:**
- Setup wizards (first-run)
- Import dialogs
- Confirmation prompts (delete, reset)
- Settings that require restart

**Visual:**
- Centered, max 480px wide
- Backdrop: blur + semi-transparent overlay
- No title bar — dialog title IS the first text element
- Primary action right-aligned, secondary left

### 4.8 Floating Surfaces

**Purpose:** Contextual information without navigation.

**Includes:**
- Tooltips: Delayed (500ms), content-rich (can include mini-charts)
- Popovers: Click-triggered, arrow-positioned, dismiss-on-click-outside
- Context menus: Right-click, keyboard-navigable

**Why:** These surfaces prevent the user from leaving their current context to find supplementary information.

---

## 5. Part 2: Information Architecture

### 5.1 Dashboard

| Attribute | Definition |
|-----------|-----------|
| **Purpose** | Answer "What should I do today?" |
| **Primary task** | Start today's workout |
| **Secondary task** | Review coach guidance |
| **Information hierarchy** | 1. Identity + greeting → 2. Coach prediction → 3. Today's mission → 4. Recovery status → 5. Key metrics → 6. Quick actions |
| **User attention flow** | Greeting → Prediction → "Start Workout" CTA → Coach insight → Recovery → Metrics → Actions |
| **What belongs** | Today's workout, coach message, recovery readiness, goal progress, streak, quick actions, one prediction insight |
| **What does NOT belong** | History, charts, settings, nutrition, detailed analytics, PR list, weekly volume, compliance data |

### 5.2 Workout

| Attribute | Definition |
|-----------|-----------|
| **Purpose** | Execute today's training session |
| **Primary task** | Log sets (weight, reps, RIR) |
| **Secondary task** | View workout structure, navigate exercises |
| **Information hierarchy** | 1. Workout name + phase → 2. Current exercise → 3. Exercise history (mini) → 4. Set table → 5. Progress summary |
| **User attention flow** | Workout header → Current exercise name → Last session comparison → Set entry → Next exercise → Completion |
| **What belongs** | Exercise list, set logging interface, weight/reps/RIR inputs, rest timer, progress ring, completion summary |
| **What does NOT belong** | Program selection, recovery data, predictions, unrelated metrics |

### 5.3 Progress

| Attribute | Definition |
|-----------|-----------|
| **Purpose** | Answer "Am I getting stronger?" |
| **Primary task** | View body weight trend |
| **Secondary task** | Review volume, PRs, compliance |
| **Information hierarchy** | 1. Body weight chart (largest) → 2. Volume trend → 3. PR highlights → 4. Compliance calendar → 5. Muscle balance |
| **User attention flow** | Weight chart → Current vs goal → Volume → PRs → Compliance |
| **What belongs** | Body weight chart, weekly volume chart, PR cards, compliance timeline, muscle group radar |
| **What does NOT belong** | Daily workout details, recovery scores, predictions, nutrition |

### 5.4 Recovery

| Attribute | Definition |
|-----------|-----------|
| **Purpose** | Answer "How ready am I to train?" |
| **Primary task** | Check readiness score |
| **Secondary task** | Understand recovery factors (sleep, stress, fatigue) |
| **Information hierarchy** | 1. Readiness score (large, narrative) → 2. Coach recommendation → 3. Driver breakdown (sleep/stress/fatigue) → 4. Trend → 5. Suggested action |
| **User attention flow** | Score → Coach text → Weakest driver → Trend → Action |
| **What belongs** | Readiness score with narrative, sleep score, stress score, fatigue score, 7-day trend, coach recommendation, deload indicator |
| **What does NOT belong** | Workout details, PRs, nutrition, predictions, settings |

### 5.5 Prediction

| Attribute | Definition |
|-----------|-----------|
| **Purpose** | Answer "What will happen if I keep going?" |
| **Primary task** | View forecast for key exercises |
| **Secondary task** | Explore what-if scenarios |
| **Information hierarchy** | 1. Forecast headline → 2. Key exercise predictions → 3. Confidence breakdown → 4. Risk factors → 5. Scenario explorer |
| **User attention flow** | Headline prediction → Most relevant exercise → Confidence → Risk → Scenarios |
| **What belongs** | Prediction timeline for main lifts, confidence gauge, risk factors, scenario sliders, reasoning chain |
| **What does NOT belong** | Recovery scores, workout history, nutrition data, settings |

### 5.6 Records

| Attribute | Definition |
|-----------|-----------|
| **Purpose** | Celebrate achievement |
| **Primary task** | Browse personal records |
| **Secondary task** | Compare PRs across time |
| **Information hierarchy** | 1. Latest PR (hero) → 2. PR grid by exercise → 3. Filter by type |
| **User attention flow** | Newest PR → PR cards → Filter controls |
| **What belongs** | PR cards (weight/reps/volume/e1RM), PR timeline, filter by exercise, filter by type |
| **What does NOT belong** | Recovery data, workout logging, settings, nutrition |

### 5.7 Nutrition

| Attribute | Definition |
|-----------|-----------|
| **Purpose** | Answer "Am I hitting my macros?" |
| **Primary task** | Log meals / check daily totals |
| **Secondary task** | View weekly trend |
| **Information hierarchy** | 1. Daily summary (calories/protein/carbs/fat) → 2. Remaining vs target → 3. Recent meals → 4. Weekly trend |
| **User attention flow** | Summary → Gaps → Recent meals → Trend |
| **What belongs** | Daily macro progress bars, meal log, weekly macro chart, protein/carb/fat breakdown |
| **What does NOT belong** | Workout data, recovery scores, predictions, exercise library |

### 5.8 Settings

| Attribute | Definition |
|-----------|-----------|
| **Purpose** | Configure the operating system |
| **Primary task** | Adjust profile (weight, goals) |
| **Secondary task** | Configure preferences (theme, units) |
| **Information hierarchy** | 1. Profile section → 2. Preferences → 3. Data management → 4. About |
| **User attention flow** | Profile → Goals → Preferences → Data → About |
| **What belongs** | Body weight entry, goal weight, theme toggle, unit system, data export/import, about/version |
| **What does NOT belong** | Any training, recovery, prediction, or nutrition data |

### 5.9 Analytics (New)

| Attribute | Definition |
|-----------|-----------|
| **Purpose** | Deep-dive data exploration |
| **Primary task** | Analyze training trends |
| **Secondary task** | Compare periods, export data |
| **What belongs** | Long-term volume chart, exercise comparison, period-over-period analysis, data export |

### 5.10 History (New)

| Attribute | Definition |
|-----------|-----------|
| **Purpose** | Browse past sessions |
| **Primary task** | Review a specific workout |
| **Secondary task** | Find patterns |
| **What belongs** | Session list with date/name/volume, expandable workout detail, notes |

---

## 6. Part 3: User Journey — First 10 Minutes

### 6.1 Opening the App (0:00–0:05)

```
+-----------------------------------------------------------+
|  Splash (500ms)                                           |
|  Logo centered, fade-in, no loading bar                   |
|  Transition: cross-fade to Dashboard, 300ms               |
+-----------------------------------------------------------+
```

**User sees:** Logo → Dashboard hero
**User feels:** Instant, premium, calm
**What happens:** Data loads silently in background during splash

### 6.2 Dashboard (0:05–1:00)

```
EYE MOVEMENT:
1. Greeting + user name (top-left)       ← First fixation
2. Coach prediction (center)             ← Second fixation
   "Your bench press is ready for +5kg"
3. "Start Workout" button (below)        ← Action point
4. Readiness score (top-right cluster)   ← Secondary check
5. Goal progress + streak (right side)   ← Motivation
6. Quick actions (bottom)                ← Optional
```

**Attention allocation:**
| Element | Visual weight | Purpose |
|---------|--------------|---------|
| Coach prediction | 40% | Primary guidance |
| Start Workout CTA | 25% | Primary action |
| Readiness + metrics | 20% | Context |
| Quick actions | 10% | Secondary tasks |
| Page chrome | 5% | Navigation |

**Decision:** User either starts workout or reviews coach insight.

### 6.3 Starting a Workout (1:00–4:00)

```
TRANSITION:
1. User clicks "Start Workout"
2. Dashboard slides left (200ms ease-out)
3. Workout slides in from right (200ms ease-out)
4. First exercise is pre-selected and highlighted

EYE MOVEMENT ON WORKOUT:
1. Workout name + exercise count (top)   ← Context
2. Current exercise name (large)         ← Focus
3. Last session comparison bar           ← Reference
4. Set table with input fields           ← Action area
5. Progress ring (corner)                ← Motivation
```

**Attention allocation:**
| Element | Visual weight | Purpose |
|---------|--------------|---------|
| Current exercise | 35% | Focus |
| Set input area | 35% | Action |
| Last session data | 15% | Reference |
| Progress ring | 10% | Motivation |
| Workout meta | 5% | Context |

### 6.4 Logging Sets (4:00–7:00)

```
FLOW:
1. Enter weight (auto-focused, numeric)
2. Tab to reps (or Enter)
3. Tab to RIR (or Enter)
4. Enter → logs set, auto-advances to next set
5. After last set → next exercise animates in

FEEDBACK:
- Set logged: brief green flash on the row (100ms)
- Last set of exercise: subtle completion glow
- All exercises done: workout summary overlay
```

**Attention:** Entirely on the set input fields. No interface chrome distracts.

### 6.5 Post-Workout Recovery Check (7:00–8:30)

```
TRANSITION:
1. Workout summary overlay with total volume, PRs, duration
2. "View Recovery" button
3. Recovery page slides in

EYE MOVEMENT ON RECOVERY:
1. Readiness score (large, center)       ← Primary
2. Coach recommendation                  ← Guidance
3. Sleep/stress/fatigue breakdown         ← Context
4. Trend line                            ← Trajectory
```

### 6.6 Progress Review (8:30–9:30)

```
TRANSITION:
1. From Recovery, user clicks "Progress"
2. Progress page slides in

EYE MOVEMENT ON PROGRESS:
1. Body weight chart (dominant, center)  ← Primary
2. Current weight vs goal (right)        ← Motivation
3. Weekly volume trend                    ← Secondary
4. Recent PRs                             ← Achievement
```

### 6.7 Exit (9:30–10:00)

```
CLOSING ACTIONS:
1. User optionally checks streak
2. Glance at tomorrow's prediction
3. Close window

FINAL IMPRESSION:
- "I know what to do tomorrow"
- "I'm making progress"
- "The coach has my back"
```

---

## 7. Part 4: Wireframes

### 7.1 Dashboard

```
+------------------------------------------------------------------+
|  ◉ Nhan · Phase 2 · Week 3                       🔥5d  ⚡87%   |
|                                                                  |
|  "Your bench press is ready for a 5kg jump."                    |
|  Based on your last 3 sessions showing RIR 1-2.                 |
|                                                                  |
|  [▶ Start Workout]                              [✏ Log Weight]  |
+------------------------------------------------------------------+
+--------------------------------------------+---------------------+
|                                            |  RECOVERY           |
|  TODAY'S MISSION                           |  Ready for PR 🔥   |
|  Push Day                                  |  Score: 87/100     |
|  8 exercises · ~45 min · High readiness    |  Sleep · Stress ·  |
|  [Chest] [Shoulders] [Triceps]             |  Fatigue balanced   |
|                                            |  → Full details     |
|  [▶ Start Workout]                         |                     |
+--------------------------------------------+---------------------+
+-----------------------------------------------------------+
|  COACH INSIGHT                                            |
|  📣 "Your bench press progression is accelerating.       |
|     Consider adding 2.5kg next session."                  |
|  💡 "Recovery trend is improving. Good sleep hygiene."   |
+-----------------------------------------------------------+
+----------------------------+-------------------------------+
|  PROGRESS                  |  PREDICTION                   |
|  72.3kg → 77.0kg          |  ● Squat PR likely in 2 wks  |
|  ████████████████░░ 72%   |  ● Bench +5kg by week 4      |
|  ~8 weeks remaining        |  ● Fatigue risk: medium      |
|  Total: 12,450kg this week |                               |
+----------------------------+-------------------------------+
|  [▶] [⚖] [⬇] [✨] [✏]                                     |
+------------------------------------------------------------------+
```

### 7.2 Workout

```
+------------------------------------------------------------------+
|  ◀ Back                                  Push Day · Phase 2     |
|                                                           🔵78% |
+------------------------------------------------------------------+
|  BENCH PRESS (BARBELL)                                          |
|  Last session: 72.5kg × 8, 8, 7 · RIR 1                       |
+------------------------------------------------------------------+
|  Set │ Weight   │ Reps │ RIR │ ✓                                |
|  1   │ [72.5]   │ [8]  │ [1] │ [✓]                             |
|  2   │ [72.5]   │ [8]  │ [1] │ [✓]                             |
|  3   │ [72.5]   │ [8]  │ [1] │ [ ] ← current                   |
|  4   │ [72.5]   │ [8]  │ [1] │ [ ]                             |
+------------------------------------------------------------------+
|  Rest: 0:45 ◼━━━━━━━━━━━━━━━━━━  (auto-timer)                   |
+------------------------------------------------------------------+
|  [Done with set]  [Skip exercise]  [Finish workout]              |
+------------------------------------------------------------------+
```

### 7.3 Progress

```
+------------------------------------------------------------------+
|  Progress                                          72.3 → 77kg  |
+------------------------------------------------------------------+
|  +----------------------------------------------------------+   |
|  |  BODY WEIGHT (4WK)                                       |   |
|  |  74 ┤⠀⡠⠤⠤⠤⠤⡤⠤⠤⠤⠤⠤⠤⡤⠤⠤⠤⠤⠤⡤⠤⠤⢤                 |   |
|  |  72 ┤⠤⠤⠤⠤⠤⠤⠤⠤⠤⠤⠤⠤⠤⠤⠤⠤⠤⠤⠤⠤⠤⠤⠤            |   |
|  |  70 ┤                                              |   |   |
|  |     └───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───  |   |   |
|  |        W1  W2  W3  W4                             |   |   |
|  +----------------------------------------------------------+   |
+----------------------------+-----------------------------------+
|  VOLUME (4WK)              |  PRs                              |
|  15K ┤⠀⡠⠤⠤⠤           |  ⭐ Bench Press  +2.5kg  (3d ago)  |
|  10K ┤⠤⠤⠤⠤⠤⠤          |  ⭐ OHP          +1.25kg (5d ago)  |
|  5K  ┤                     |  ⭐ Squat          +5kg    (1w ago) |
+----------------------------+-----------------------------------+
|  COMPLIANCE                                                |
|  [Mon] [Tue] [Wed] [Thu] [Fri] [Sat] [Sun]                 |
|   ✓     ✓     ✓     -     ✓     -     ✓                     |
|  85% consistency                                           |
+------------------------------------------------------------------+
```

### 7.4 Recovery

```
+------------------------------------------------------------------+
|  Recovery                                        ◉ 87 Readiness  |
+------------------------------------------------------------------+
|  +----------------------------------------------------------+   |
|  |  87                                                       |   |
|  |  Ready for PR 🔥                                         |   |
|  |  All systems nominal. Sleep and stress are in check.     |   |
|  +----------------------------------------------------------+   |
+----------------------------+-----------------------------------+
|  SLEEP                      |  STRESS                          |
|  7.8h · 92% quality        |  3.2/10 · Low                   |
|  ████████████░░  ██████████ |  ████░░░░░░░░  ██░░░░░░░░░░     |
|  ████████████░░  ██████████ |  ████░░░░░░░░  ██░░░░░░░░░░     |
|  Trend: stable ↑            |  Trend: improving ↓             |
+----------------------------+-----------------------------------+
|  FATIGUE                     |  RECOMMENDATION                 |
|  4.1/10 · Moderate          |  Train as planned. Consider    |
|  ██████░░░░░░░░░░░░░░░░░░  |  deload in 2 weeks if trend    |
+----------------------------+-----------------------------------+
```

### 7.5 Prediction

```
+------------------------------------------------------------------+
|  Predictions                                    Next 4 weeks     |
+------------------------------------------------------------------+
|  "You are on track for a squat PR within 2 weeks."              |
|  Confidence: High (82%)                                          |
+------------------------------------------------------------------+
+----------------------------+-----------------------------------+
|  BENCH PRESS               |  SQUAT                            |
|  72.5 → 77.5kg (+5kg)     |  85 → 92.5kg (+7.5kg)            |
|  ████████████████░░░░ 82%  |  ██████████████████░░ 91%         |
|  Likely in 3-4 weeks       |  Likely in 2 weeks               |
+----------------------------+-----------------------------------+
+-----------------------------------------------------------+
|  WHAT IF...                                               |
|  [Increase volume +10%] → PR in 4 weeks (↓confidence)     |
|  [Add rest day]         → PR in 5 weeks (↑confidence)     |
|  [Current plan]         → PR in 3 weeks                   |
+-----------------------------------------------------------+
|  RISK FACTORS                                             |
|  ● Fatigue accumulation:   Medium  ·  Monitor              |
|  ● Sleep trend:            Stable  ·  No action            |
|  ● Stress load:            Low     ·  Clear                |
+------------------------------------------------------------------+
```

### 7.6 Settings

```
+------------------------------------------------------------------+
|  Settings                                                        |
+------------------------------------------------------------------+
|  PROFILE                                                         |
|  Current weight     [72.3 kg]                                    |
|  Goal weight        [77.0 kg]                                    |
|  Height              [175 cm]                                    |
+------------------------------------------------------------------+
|  PREFERENCES                                                     |
|  Theme              [● Dark  ○ Light  ○ System]                  |
|  Units              [● Metric  ○ Imperial]                       |
|  Rest timer         [90 seconds]                                 |
+------------------------------------------------------------------+
|  DATA                                                            |
|  [Export data]  [Import program]  [Reset all data]              |
+------------------------------------------------------------------+
|  ABOUT                                                           |
|  GymOS 0.5.0 · 3373 tests passing                               |
+------------------------------------------------------------------+
```

---

## 8. Part 5: Component Hierarchy

### 8.1 Categories

| Category | Role | Examples |
|----------|------|----------|
| **Hero** | First-screen impact, establishes page identity | Greeting block, readiness score, prediction headline |
| **Metric** | Precise numerical data display | Body weight, readiness score, volume total, streak count |
| **Chart** | Temporal data visualization | Body weight chart, volume trend, compliance calendar |
| **Narrative** | Coaching guidance in natural language | Coach prediction, recovery recommendation, insight text |
| **Status** | Current state at a glance | Readiness level, recovery score, phase indicator |
| **Coach** | The GymOS differentiator — actionable guidance | Insight cards with emoji prefix, recommendation blocks |
| **Action** | Primary and secondary task triggers | Start Workout button, Log Weight, command cards |
| **Navigation** | Movement between pages | Sidebar, command palette, back button |
| **Container** | Structural grouping of content | AppCard, SectionPanel, EditorialGrid column |

### 8.2 Component Priority

| Priority | Definition | Examples |
|----------|-----------|----------|
| **Primary** | First visual fixation, communicates page purpose | Hero headline, readiness score, coach prediction |
| **Secondary** | Supporting information, second fixation | Metrics, charts, detailed insights |
| **Supporting** | Contextual data, read on demand | PR details, compliance, trend lines |
| **Decorative** | Visual enhancement, no information content | Ambient gradient, subtle separator lines, icon accents |

### 8.3 Visual Weight by Page

| Page | Primary (40%) | Secondary (30%) | Supporting (20%) | Decorative (10%) |
|------|--------------|-----------------|-------------------|------------------|
| Dashboard | Coach prediction | Today's mission | Metrics, streak | Hero gradient |
| Workout | Current exercise + sets | Last session ref | Progress ring | Completion glow |
| Progress | Body weight chart | Volume trend | PRs, compliance | Axis labels |
| Recovery | Readiness score | Driver breakdown | Trend, recommendation | Score ring gradient |
| Prediction | Forecast headline | Exercise preds | Risk, scenarios | Timeline markers |
| Records | Latest PR | PR grid | Filters | Achievement stars |
| Settings | Profile form | Preferences | Data management | Section dividers |

---

## 9. Part 6: Visual Hierarchy

### 9.1 Dashboard

| Element | Size/Weight | Role |
|---------|-------------|------|
| Coach prediction text | 24px/700, primary color | **Largest** — first thing user reads |
| "Start Workout" button | 52px height, gradient + glow | **CTA** — most prominent action |
| User greeting | 32px/700, text_primary | **Identity** — establishes ownership |
| Readiness score | 20px/700 metric value | **Status check** — secondary glance |
| Metric clusters | 16px/600 value + 11px label | **Supporting data** — read on demand |
| Quick action cards | 96px height, icon + label | **Secondary actions** — bottom of visual stack |
| Sidebar icons | 20px icon | **Navigation** — intentionally de-emphasised |

### 9.2 Workout

| Element | Size/Weight | Role |
|---------|-------------|------|
| Exercise name | 28px/700 | **Largest** — current focus |
| Set input fields | 20px/600, focus ring | **CTA** — active interaction area |
| Last session comparison | 14px/500, secondary text | **Reference** — above input for context |
| Set table numbers | 16px/600, monospaced | **Data** — the workout record |
| Workout progress ring | 48px diameter | **Motivation** — peripheral awareness |
| Back button | 14px/500, icon + text | **Navigation** — intentionally small |

### 9.3 Progress

| Element | Size/Weight | Role |
|---------|-------------|------|
| Body weight chart | 60% of viewport height | **Largest** — dominant visual |
| Goal weight annotation | 20px/700, accent color | **Motivation** — target line on chart |
| Volume trend chart | 30% of viewport | **Secondary** — scroll-down content |
| PR cards | 16px radius, subtle border | **Achievement** — recognisable but not loud |
| Compliance calendar | Small dot grid | **Supporting** — glanceable habit check |

### 9.4 Recovery

| Element | Size/Weight | Role |
|---------|-------------|------|
| Readiness score number | 64px/800, hero metric | **Largest** — immediate status |
| Readiness narrative | 18px/500 | **Interpretation** — what the score means |
| Driver cards (sleep/stress/fatigue) | Equal thirds below hero | **Breakdown** — why the score is what it is |
| Trend sparkline | Small inline chart | **Trajectory** — where it's heading |
| Recommendation | 14px/500, info accent | **Action** — what to do |

### 9.5 Prediction

| Element | Size/Weight | Role |
|---------|-------------|------|
| Headline prediction | 24px/700, primary | **Largest** — the forecast |
| Exercise prediction bars | 16px/600 | **Detail** — per-lift breakdown |
| Confidence gauge | Visual bar + percentage | **Trust** — how reliable the prediction is |
| What-if scenarios | Secondary section | **Exploration** — interactive but de-emphasised |
| Risk factors | Small text, bullet list | **Caveats** — read only if forecasting matters |

### 9.6 Principles Applied to All Pages

1. **The largest element is always the answer to the page's question**
2. **The CTA is always the most visually prominent interactive element**
3. **Navigation is always the smallest visible element**
4. **Charts dominate their section but not the page**
5. **Text hierarchy uses size + weight only — never color alone**
6. **Supporting information uses text_secondary or text_disabled**
7. **Decorative elements never compete with content**

---

## 10. Part 7: Product Identity

### 10.1 GymOS in Five Words

**Calm · Precise · Athletic · Premium · Intelligent**

### 10.2 Color Personality

The palette communicates **depth, focus, and premium calm.**

- **Deep space background** (`#060818`): The surface recedes. Content floats. The interface disappears behind data.
- **Amethyst primary** (`#7C3AED`): Royal, intelligent, not aggressive. Indicates importance without urgency.
- **Aurora success** (`#34D399`): Achievement is calm green, not bright green. Goals feel earned, not gamified.
- **Starlight warning** (`#FBBF24`): Warm gold like a sunrise — alerts are gentle, not alarming.
- **Cosmic rose error** (`#FB7185`): Errors are soft pink, not red. Mistakes are recoverable.
- **No blue**: Blue = utility (links, info). Every other fitness app uses blue. GymOS uses none.

**The palette is not "dark mode."** It is a night-sky editorial surface. The difference is intentionality.

### 10.3 Typography Personality

The typography communicates **editorial confidence, athletic precision, calm authority.**

- **Inter** (sans-serif): Clean, neutral, highly legible at every size. No personality that distracts from content.
- **Editorial sizing**: Headings are large (28-32px) and bold (700). Body text is small (13-14px) and light (400).
- **Metrics are display typography**: Large (20-24px), bold (700), tight letter-spacing (-0.03em). Numbers should feel significant.
- **Coach text is narrative**: Sentence case, comfortable line height (1.5), warm tone. Not UI copy.
- **No uppercase for headings**: Sentence case everywhere. Uppercase implies shouting.
- **No monospace for data**: Numbers in body font, not monospace. Monospace feels like a terminal.

### 10.4 Motion Personality

Motion communicates **confidence, intentionality, and calm.**

- **Fast entry**: 200ms ease-out. Content arrives confidently.
- **Slow exit**: 300ms ease-in. Content leaves deliberately.
- **Sliding pages**: Horizontal slide for page transitions (200ms). Direction implies relationship (right = deeper, left = back).
- **Fade for overlays**: 150ms cross-fade. Overlays appear from the surface, not from nowhere.
- **No bounce**: Every animation is OutCubic. Bounce feels playful. GymOS is not playful.
- **Content appears, chrome fades**: Cards fade in (200ms opacity). Chrome fades slower (300ms).
- **No staggered animations**: Everything in a section animates simultaneously. Delays feel like loading.

### 10.5 Interaction Personality

Interaction communicates **directness, predictability, and respect for the user's time.**

- **Click is instant**: No artificial delays. Button press → action within 16ms.
- **Hover reveals information**: Hovering a metric shows detail. No click required.
- **Focus is visible**: Every interactive element has a visible focus ring. Keyboard navigation is a first-class citizen.
- **Right-click is meaningful**: Context menus exist everywhere they're expected.
- **Undo is available**: Destructive actions have an undo period (5s snackbar).
- **No confirmation dialogs for common actions**: Starting a workout does not need "Are you sure?"
- **Tab order follows visual hierarchy**: Tab moves through the page in the intended attention flow.

### 10.6 Emotional Personality

The user feels **prepared, in control, and quietly ambitious.**

- **Not gamified**: No badges, no levels, no streaks-as-rewards (streaks are data, not achievements).
- **Not urgent**: No red badges, no "don't lose your streak" notifications.
- **Not social**: No comparison, no sharing, no leaderboards.
- **Not a dashboard manager**: The user does not arrange widgets. The layout is intentional.
- **A tool for a craft**: Using GymOS should feel like a chef using a good knife — the tool disappears, the work remains.
- **Quietly premium**: The app is well-crafted. Details are consistent. Nothing is broken. Nothing is half-implemented.

### 10.7 What GymOS Does NOT Feel Like

| Design Language | Why Not |
|----------------|---------|
| **Qt** | No native widgets, no platform chrome, no exposed scrollbars |
| **Material** | No elevation paper, no ripple, no floating action button |
| **Fluent** | No acrylic, no reveal highlight, no command bar |
| **Bootstrap** | No card decks, no alert boxes, no badge pills |
| **Crypto Dashboard** | No neon gradients, no glassmorphism, no glowing charts |
| **Dribbble Concept** | No impossible shadows, no content-free hero images, no transparent nav bars |

---

## 11. Part 8: Implementation Roadmap

### 11.1 Phase Order

```
Phase 1: Shell         ─ Foundation, no pages work without it
         ↓
Phase 2: Dashboard     ─ First-screen experience, sets editorial standard
         ↓
Phase 3: Navigation    ─ Command palette, sidebar, transitions
         ↓
Phase 4: Workout       ─ Core interaction, highest frequency use
         ↓
Phase 5: Progress      ─ Chart-heavy, data-driven page
         ↓
Phase 6: Recovery      ─ Narrative + metric hybrid
         ↓
Phase 7: Prediction    ─ Complex interaction (what-if scenarios)
         ↓
Phase 8: Remainder     ─ Records, Nutrition, Settings, History, Analytics
         ↓
Phase 9: Motion        ─ Polish pass across all pages
```

### 11.2 Phase Details

#### REP-007B: Application Shell

| Task | Files | Effort |
|------|-------|--------|
| Implement unified sidebar (collapsible) | ~3 files | 1 day |
| Implement global header pattern | ~2 files | 0.5 day |
| Implement overlay layer + command palette | ~4 files | 2 days |
| Implement notification layer (toasts) | ~2 files | 1 day |
| Implement dialog layer (shared backdrop) | ~2 files | 0.5 day |
| Wire sidebar navigation to all pages | ~10 files | 1 day |
| **Total** | **~23 files** | **6 days** |

**Dependencies:** RFC-030 tokens, `EditorialGrid` component
**Validation:** All pages load in shell, sidebar navigation works, ⌘K opens palette

#### REP-007C: Dashboard

| Task | Files | Effort |
|------|-------|--------|
| Design editorial hero (greeting, prediction, CTA) | 1 file | 1 day |
| Implement asymmetric two-column layout | 1 file | 0.5 day |
| Coach insight section (primary narrative block) | 1 file | 1 day |
| Metric clusters (readiness, weight, goal, streak) | 1 file | 0.5 day |
| Quick action command cards | 1 file | 0.5 day |
| Empty states for all sections | 1 file | 0.5 day |
| Fade-in animations on data update | 1 file | 0.5 day |
| **Total** | **1 file** | **4.5 days** |

**Dependencies:** REP-007B (shell)
**Note:** The current `dashboard_view.py` has editorial layout — this phase audits and hardens it.

#### REP-007H: Navigation & Motion

| Task | Files | Effort |
|------|-------|--------|
| Page transition animations (horizontal slide) | ~3 files | 1 day |
| Sidebar collapse/expand with animation | 2 files | 0.5 day |
| Command palette keyboard navigation | 2 files | 0.5 day |
| Focus ring consistency pass | ~20 files | 1 day |
| Reduced motion support | ~5 files | 0.5 day |
| Scrollbar styling consistency | ~10 files | 0.5 day |
| **Total** | **~42 files** | **4 days** |

**Dependencies:** REP-007B (shell), REP-007C (dashboard)
**Note:** Motion is a separate phase because it touches every file.

#### REP-007D: Workout

| Task | Files | Effort |
|------|-------|--------|
| Editorial workout composition (hero, exercise focus, set table) | 1 file | 2 days |
| Set input with auto-advance | 1 file | 1 day |
| Last session reference display | 1 file | 0.5 day |
| Rest timer overlay | 1 file | 0.5 day |
| Exercise completion transitions | 1 file | 0.5 day |
| Workout summary overlay | 1 file | 0.5 day |
| **Total** | **1-2 files** | **5 days** |

**Dependencies:** REP-007B (shell), REP-007H (motion)

#### REP-007E: Progress

| Task | Files | Effort |
|------|-------|--------|
| Editorial progress composition (dominant chart) | 1 file | 1.5 days |
| Body weight chart with goal annotation | 1 file | 1 day |
| Volume trend chart | 1 file | 0.5 day |
| PR highlight cards | 1 file | 0.5 day |
| Compliance calendar | 1 file | 0.5 day |
| **Total** | **1-2 files** | **4 days** |

**Dependencies:** REP-007B (shell)

#### REP-007F: Recovery

| Task | Files | Effort |
|------|-------|--------|
| Editorial recovery composition (score hero) | 1 file | 1 day |
| Driver cards (sleep/stress/fatigue) | 1 file | 1 day |
| Trend sparkline | 1 file | 0.5 day |
| Coach recommendation text | 1 file | 0.5 day |
| **Total** | **1-2 files** | **3 days** |

**Dependencies:** REP-007B (shell)

#### REP-007G: Prediction

| Task | Files | Effort |
|------|-------|--------|
| Editorial prediction composition (headline, bars) | 1 file | 1.5 days |
| What-if scenario controls | 1 file | 1 day |
| Confidence gauge | 1 file | 0.5 day |
| Risk factor display | 1 file | 0.5 day |
| **Total** | **1-2 files** | **3.5 days** |

**Dependencies:** REP-007B (shell)

#### REP-007J: Remaining Pages

| Task | Files | Effort |
|------|-------|--------|
| Records (PR hero + grid) | 1 file | 1 day |
| Nutrition (macro bars + meal log) | 1 file | 1.5 days |
| Settings (profile, prefs, data) | 1 file | 0.5 day |
| Analytics (long-term charts) | 1 file | 1 day |
| History (session list) | 1 file | 0.5 day |
| New: Page for each | ~5 files | 4.5 days |

**Dependencies:** REP-007B (shell), editorial patterns established

### 11.3 Total Effort Estimate

| Phase | Effort | Dependencies |
|-------|--------|-------------|
| REP-007B: Shell | 6 days | — |
| REP-007C: Dashboard | 4.5 days | Shell |
| REP-007H: Navigation & Motion | 4 days | Shell, Dashboard |
| REP-007D: Workout | 5 days | Shell, Motion |
| REP-007E: Progress | 4 days | Shell |
| REP-007F: Recovery | 3 days | Shell |
| REP-007G: Prediction | 3.5 days | Shell |
| REP-007J: Remainder | 4.5 days | Shell |
| **Total** | **~34.5 days** | |

### 11.4 Parallelisation

| Track 1 (Shell + Infrastructure) | Track 2 (Page Content) |
|---------------------------------|------------------------|
| REP-007B: Shell (6 days) | — |
| REP-007H: Motion (4 days) | REP-007C: Dashboard (4.5 days) |
| — | REP-007D: Workout (5 days) |
| — | REP-007E: Progress (4 days) |
| — | REP-007F: Recovery (3 days) |
| — | REP-007G: Prediction (3.5 days) |
| — | REP-007J: Remainder (4.5 days) |

**Parallel timeline:** ~19 days with 2 engineers, ~34 days with 1 engineer.

---

## 12. Success Criteria

### 12.1 Visual Consistency

- [ ] All pages share the same sidebar + header shell
- [ ] All pages use `EditorialGrid` as the single layout primitive
- [ ] No `QGridLayout` or raw `QVBoxLayout` for page composition
- [ ] Every page has a hero section as the first visual element
- [ ] Hero-to-content ratio is approximately 40:60 on every page
- [ ] No hardcoded border-radius, padding, or margin values
- [ ] All cards use the same elevation level (2) with one exception per page (hero)
- [ ] Coach narrative appears above raw data on every page that has both

### 12.2 Attention Flow

- [ ] The largest element on each page answers the page's primary question
- [ ] The CTA is the second-largest element (or third, below narrative)
- [ ] Navigation elements are the smallest visible elements
- [ ] Supporting information uses `text_disabled` or `text_secondary`
- [ ] Charts occupy their section but do not dominate unrelated sections

### 12.3 Interaction

- [ ] Command palette accessible from every page via ⌘K
- [ ] All primary actions have keyboard shortcuts
- [ ] Tab order matches visual hierarchy
- [ ] All interactive elements have visible focus rings
- [ ] Page transitions are horizontal slides (200ms, OutCubic)

### 12.4 Emotional

- [ ] Users describe the app as "calm" or "premium" in testing
- [ ] No red badges, no urgent notifications, no gamification elements
- [ ] The coach is the dominant voice, not the data
- [ ] The interface recedes behind the content

### 12.5 Technical

- [ ] No new dependencies introduced
- [ ] All existing 3373+ tests pass
- [ ] No production code (domain, application, infrastructure) modified
- [ ] Zero regressions in backend or data pipeline
- [ ] All new code is in `presentation/` layer only

---

*End of RFC-031*
