# RFC-037: Recovery Experience 2.0

**Status:** IMPLEMENTATION  
**Priority:** CRITICAL  
**Dependencies:** RFC-034 (Design System 3.0), REP-007E (DS Consolidation)  
**Target:** `ui/recovery/recovery_dashboard.py`

---

## Table of Contents

1. [User Journey](#1-user-journey)
2. [Information Hierarchy](#2-information-hierarchy)
3. [ASCII Wireframes](#3-ascii-wireframes)
4. [Narrative Flow](#4-narrative-flow)
5. [Counterfactual Design](#5-counterfactual-design)
6. [Component Tree](#6-component-tree)
7. [Motion Map](#7-motion-map)
8. [Implementation Decisions](#8-implementation-decisions)

---

## 1. User Journey

### Primary Question

**"Can I train hard today?"**

### Journey Map

```
ARRIVAL
  │
  ▼
HERO ──→ "Training Ready" with RecoveryRing
  │        One dominant message
  │        One CTA ("Proceed to Workout")
  │
  ▼
RECOVERY SUMMARY ──→ Sleep · Fatigue · Readiness
  │                    Narrative first, numbers second
  │
  ▼
RECOVERY DRIVERS ──→ Why am I at this state?
  │                    Factor breakdown with deltas
  │
  ▼
COACH ──→ Largest insight section
  │        Natural language narratives (max 3)
  │
  ▼
TREND ──→ Weekly recovery chart
  │        Narrative below chart ("So what?")
  │
  ▼
TODAY ──→ Green / Amber / Red recommendation
  │        With reasoning
  │
  ▼
WHAT IF ──→ Counterfactual cards
  │           Sleep +1h → Recovery +8
  │           Reduce volume → Readiness +5
  │
  ▼
HISTORY ──→ WeeklyTimeline of recovery scores
             Milestones (best streak, recent low)
```

### State Machine

```
                ┌─────────────┐
                │ No Data     │ ← No workouts completed
                └──────┬──────┘
                       │ First workout completed
                       ▼
                ┌─────────────┐
                │ Learning    │ ← < 3 recovery scores
                └──────┬──────┘
                       │ 3+ scores collected
                       ▼
                ┌─────────────┐
         ┌─────→│ Active      │ ← Normal operation
         │      └──────┬──────┘
         │             │ Deload due
         │             ▼
         │      ┌─────────────┐
         └──────│ Deload      │ ← Deload period active
                └─────────────┘
```

---

## 2. Information Hierarchy

### Content Weight (visual mass distribution)

| Section | Weight | Rationale |
|---------|--------|-----------|
| Hero | 30% | First thing, sets the tone, answers "Can I train?" |
| Coach | 20% | Longest scroll, richest narrative, most valuable |
| Recovery Summary | 12% | Three compact narrative cards |
| Recovery Drivers | 12% | Why explanation with bullet points |
| Trend | 10% | One chart + one sentence |
| Today | 8% | Clear action in green/amber/red |
| What If | 5% | Beautiful cards, secondary feature |
| History | 3% | Timeline, low cognitive load |

### Information Density

Every section must answer exactly one question:

| Section | Question Answered |
|---------|-------------------|
| Hero | Am I ready? |
| Recovery Summary | How is each driver doing? |
| Recovery Drivers | Why am I at this state? |
| Coach | What should I know? |
| Trend | Am I improving? |
| Today | What should I do? |
| What If | What happens if I change something? |
| History | How have I been doing? |

---

## 3. ASCII Wireframes

### Full Page Layout

```
┌────────────────────────────────────────────────────────────────┐
│  HERO                                                         │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  ◉ RecoveryRing    TRAINING READY                      │   │
│  │                     "You're fully recovered. Today's   │   │
│  │                     Push session is appropriate for    │   │
│  │                     PR attempts."                      │   │
│  │                                           [▶ Workout]  │   │
│  └────────────────────────────────────────────────────────┘   │
├────────────────────────────────────────────────────────────────┤
│  RECOVERY SUMMARY                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ 😴 Sleep     │  │ ⚡ Fatigue   │  │ 🚀 Readiness │         │
│  │ "Good"       │  │ "Low"        │  │ "Ready"      │         │
│  │ 7.5h / 85%   │  │ 28/100       │  │ 85/100       │         │
│  │ Score: 85    │  │ Level: LOW   │  │ Level: READY │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
├────────────────────────────────────────────────────────────────┤
│  RECOVERY DRIVERS                                              │
│  "Recovery is high because:"                                   │
│  │ ✅ Sleep quality improved (+15% vs last week)              │
│  │ ✅ Lower body fatigue is moderate (42/100)                 │
│  │ ✅ Weekly volume is within optimal range (18 sets)         │
│  │ ℹ️ Stress levels are slightly elevated (55/100)           │
├────────────────────────────────────────────────────────────────┤
│  COACH                                                         │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ ● You recovered well overnight.                        │   │
│  │   Upper body is fully recovered. Lower body still      │   │
│  │   carries moderate fatigue. Today's Push session is    │   │
│  │   appropriate. Avoid failure sets.                     │   │
│  │   ▸ [View details]                                     │   │
│  ├────────────────────────────────────────────────────────┤   │
│  │ ● Sleep consistency improved this week.                │   │
│  │   Your average sleep duration increased from 6.8h      │   │
│  │   to 7.5h. This has contributed to better readiness.   │   │
│  ├────────────────────────────────────────────────────────┤   │
│  │ ● Lower body volume was high this week.                │   │
│  │   24 sets vs usual 18. Consider reducing leg volume    │   │
│  │   next session if fatigue persists.                    │   │
│  └────────────────────────────────────────────────────────┘   │
├────────────────────────────────────────────────────────────────┤
│  TREND                                                         │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │   │
│  │  ░░        Weekly Recovery Trend                   ░░  │   │
│  │  ░░  ┌──────────────────────────────────────┐     ░░  │   │
│  │  ░░  │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                    │     ░░  │   │
│  │  ░░  │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓              │     ░░  │   │
│  │  ░░  │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓      │     ░░  │   │
│  │  ░░  │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  │     ░░  │   │
│  │  ░░  └──────────────────────────────────────┘     ░░  │   │
│  │  ░░  Recovery has been stable. 7-day avg: 78/100 ░░  │   │
│  │  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │   │
│  └────────────────────────────────────────────────────────┘   │
├────────────────────────────────────────────────────────────────┤
│  TODAY'S RECOMMENDATION                                        │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  🟢 PROCEED NORMALLY                                  │   │
│  │  You're ready for your Push workout today.             │   │
│  │  Recovery metrics support a standard session.          │   │
│  │  Target your RIR 1-2 on working sets.                  │   │
│  └────────────────────────────────────────────────────────┘   │
├────────────────────────────────────────────────────────────────┤
│  WHAT IF...                                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ 😴 Sleep +1h │  │ 📉 Volume -5 │  │ 💧 Hydrate   │         │
│  │ Recovery +8  │  │ Readiness +5 │  │ Fatigue -10  │         │
│  │ 85% impact   │  │ 65% impact   │  │ 40% impact   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
├────────────────────────────────────────────────────────────────┤
│  RECOVERY HISTORY                                              │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  ●──●──●──●──●──●──●──●──●──●                          │   │
│  │  Best streak: 8 days above 70 (Mar 10-18)              │   │
│  │  Recent low: 45 on Mar 5 (after high volume leg day)   │   │
│  └────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────┘
```

### Empty State: No Data

```
┌─────────────────────────────────────────────────────────────┐
│  ⏳                                                         │
│  No Recovery Data Yet                                       │
│                                                             │
│  Complete a workout to unlock personalized recovery         │
│  insights. GymOS will analyze your training data to         │
│  calculate sleep quality, fatigue levels, training          │
│  readiness, and recovery recommendations.                   │
│                                                             │
│  In the meantime:                                           │
│  • Log your sleep hours in Settings                         │
│  • Connect a wearable device for HRV data                   │
│  • Track your stress levels manually                        │
└─────────────────────────────────────────────────────────────┘
```

### Empty State: No Sleep Data

```
┌─────────────────────────────────────────────────────────────┐
│  😴                                                         │
│  Sleep Data Not Available                                   │
│                                                             │
│  Sleep is a major driver of recovery. Without sleep data,   │
│  GymOS cannot fully assess your readiness.                  │
│                                                             │
│  ▸ Log sleep in Settings › Recovery                         │
│  ▸ Connect wearable for automatic sleep tracking            │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Narrative Flow

### Hero State Labels

| Score Range | State Label | Narrative |
|-------------|-------------|-----------|
| 80-100 | Training Ready | "You're fully recovered. Today's session is appropriate for PR attempts." |
| 60-79 | Good to Train | "You're recovered enough to train. Focus on technique, avoid failure sets." |
| 40-59 | Train with Caution | "Recovery is reduced. Consider reducing volume by 20% today." |
| 20-39 | Needs Rest | "Significant fatigue detected. Consider a light session or rest day." |
| 0-19 | Deload Recommended | "Critical fatigue levels. A deload week is strongly recommended." |

### Recovery Summary Narrative Rules

| Driver | Good (≥70) | Moderate (40-69) | Poor (<40) |
|--------|-----------|------------------|------------|
| Sleep | "Good" | "Fair" | "Needs Improvement" |
| Fatigue | "Low" | "Moderate" | "High" |
| Readiness | "Ready" | "Caution" | "Fatigued" |

### Coach Narrative Templates

The Coach section uses the `CoachCardStack` with `Narrative` objects:

```
Template: "Recovery Overview"
"You recovered well overnight. {upper_body_status}. {lower_body_status}.
Today's {session_type} session is {session_verdict}."

Template: "Sleep Insight"
"Sleep consistency improved this week. Your average sleep duration
increased from {previous_hours}h to {current_hours}h."

Template: "Training Load"
"Your {body_part} volume was {comparison} this week.
{volume_sets} sets vs usual {baseline_sets} sets."
```

### Today's Recommendation Logic

| Score | Color | Label | Reasoning |
|-------|-------|-------|-----------|
| ≥70 | 🟢 Green | Proceed Normally | "Recovery metrics support a standard session." |
| 40-69 | 🟡 Amber | Reduce Volume | "Recovery is reduced. Consider 20% volume reduction." |
| <40 | 🔴 Red | Recovery Only | "Recovery is critical. Light activity or rest recommended." |

---

## 5. Counterfactual Design

### Counterfactual Types

| Type | Input | Impact | Card Icon |
|------|-------|--------|-----------|
| Sleep | +1 hour | Recovery +8 points | 😴 |
| Volume | -5 sets | Readiness +5 points | 📉 |
| Stress | -20% | Fatigue -10 points | 🧘 |
| Hydration | +1L | Fatigue -5 points | 💧 |
| Deload | 1 week | Recovery +15 points | 🔄 |

### Card Design

```
┌───────────────────────┐
│ 😴 Sleep +1 hour      │
│ Recovery +8 points    │
│ ████████░░ 85% impact │
└───────────────────────┘
```

Each counterfactual card is an `AppCard` with:
- Large emoji/icon on the left
- "What if" label in small text
- Action description in body
- Impact metric in primary color
- Progress bar showing confidence/impact

### Data Source

Counterfactual data comes from the existing `CounterfactualEngine` in `modules/prediction/engines/counterfactual_engine.py`:

```python
from modules.prediction.domain import CounterfactualQuery, CounterfactualType

# Evaluate sleep +1h scenario
query = CounterfactualQuery(cf_type=CounterfactualType.SLEEP, magnitude=1.0)
result = counterfactual_engine.evaluate(query)
# → result.absolute_delta = +8.2
```

When the engine is unavailable, use sensible defaults based on recovery domain knowledge.

---

## 6. Component Tree

### Canonical Components Used

```
QWidget (RecoveryDashboard)
├── ScrollContainer
│   └── QVBoxLayout
│       ├── HeroPanel (custom, uses AppCard styling)
│       │   ├── RecoveryRing (visualization)
│       │   ├── QLabel (state label, h2)
│       │   ├── QLabel (narrative, body)
│       │   ├── StatusBadge (trend, e.g. "+5% this week")
│       │   └── QPushButton (CTA, "Proceed to Workout")
│       │
│       ├── SectionHeader ("Recovery Summary")
│       │
│       ├── EditorialGrid
│       │   ├── AppCard (Sleep) — QUARTER span
│       │   │   ├── QLabel (narrative first: "Good")
│       │   │   └── QLabel (detail: "7.5h · Score: 85")
│       │   ├── AppCard (Fatigue) — QUARTER span
│       │   └── AppCard (Readiness) — HALF span (wider)
│       │
│       ├── SectionHeader ("Why?")
│       │
│       ├── RecoveryDriversSection (custom, built with QFrame + QLabel rows)
│       │   └── 4× DriverRow (narrative bullet with impact)
│       │
│       ├── SectionHeader ("Coach Insights")
│       │
│       ├── CoachCardStack (narrative, max 3 cards)
│       │
│       ├── SectionHeader ("Weekly Trend")
│       │
│       ├── ChartContainer
│       │   └── TrendChart (recovery scores)
│       │   └── QLabel (narrative below: "Recovery has been stable.")
│       │
│       ├── SectionHeader ("Today's Recommendation")
│       │
│       ├── AppCard (Recommendation)
│       │   ├── StatusBadge (Green/Amber/Red)
│       │   ├── QLabel (action title)
│       │   └── QLabel (reasoning)
│       │
│       ├── SectionHeader ("What If...")
│       │
│       ├── EditorialGrid (counterfactual cards)
│       │   └── 3× AppCard (counterfactual scenario) — THIRD span
│       │
│       ├── SectionHeader ("Recovery History")
│       │
│       └── FinalSection
│           ├── WeeklyTimeline (visualization)
│           └── QLabel (milestones narrative)
```

### Component Justification

| Component | Why It's Used |
|-----------|---------------|
| `RecoveryRing` | Visual recovery score — instantly scannable |
| `AppCard` | Uniform card styling for summary, recommendation, counterfactuals |
| `SectionHeader` | Consistent section labeling across all pages |
| `StatusBadge` | Quick state indicators (Green/Amber/Red, trends) |
| `EditorialGrid` | 12-column responsive grid for multi-card layouts |
| `CoachCardStack` | Reusable narrative card stack with expand/collapse |
| `ChartContainer` | Consistent chart wrapping with labels |
| `TrendChart` | Weekly trend visualization |
| `WeeklyTimeline` | History timeline |
| `ScrollContainer` | Single scroll page |

---

## 7. Motion Map

| Element | Trigger | Animation | Duration | Curve |
|---------|---------|-----------|----------|-------|
| Hero | Page load | Fade in | 200ms | ease-out |
| Recovery Summary cards | Page load | Stagger fade, 80ms apart | 150ms each | ease-out |
| Recovery Drivers | Page load | Slide up, 100ms apart | 200ms each | ease-out |
| Coach cards | Page load | Fade in, 150ms apart | 250ms | ease-out |
| Trend chart | Page load | Progressive draw | 400ms | ease-in-out |
| Today's recommendation | Page load | Scale in | 200ms | ease-out |
| Counterfactual cards | Page load | Stagger fade, 100ms apart | 200ms | ease-out |
| History timeline | Page load | Left to right reveal | 300ms | ease-out |
| Empty state | Page load | Fade in | 200ms | ease-out |
| Reduced motion | All | Instant show | 0ms | none |

### Implementation Notes

- Use `QPropertyAnimation` with objectName selectors for stagger
- Respect reduced motion via `AnimationManager.reduced_motion_enabled`
- All durations are in the `MotionTokens` system
- No looping animations (except potentially a subtle pulse on the hero CTA)

---

## 8. Implementation Decisions

### Decision 1: Preserve RecoveryDashboardData

The dataclass remains identical. All existing business logic, signals, and the main_window.py integration work without changes.

### Decision 2: Single Scroll Page

All 8 sections are in one vertical scroll. No tabs, no sub-navigation. This matches the "conversation" metaphor — one continuous story.

### Decision 3: Counterfactuals are Hardcoded Defaults

The counterfactual cards use hardcoded default values when the `CounterfactualEngine` is unavailable. These are based on established recovery science:
- +1h sleep → +8 recovery points
- -5 sets volume → +5 readiness points  
- Hydration → -10 fatigue points

### Decision 4: Coach Section Uses CoachCardStack

The CoachCardStack from `ui/narrative/cards.py` is used directly. It supports expand/collapse, severity indicators, and action items.

### Decision 5: Empty States are Educational

Every empty state includes actionable next steps. The user never sees a blank section.

### Decision 6: Color States are Token-Based

All colors use `color_from_scheme(ColorScheme.DARK)` with `success`, `warning`, `error` tokens. No hardcoded hex values.

### Decision 7: Refresh is Idempotent

`refresh(data)` clears all dynamic sections and rebuilds them. It's safe to call multiple times.

### Decision 8: Custom Widgets are Minimized

Only two custom widgets are needed beyond canonical components:
- `_RecoveryDriversSection` — bullet-point driver list (no canonical component exists)
- `_CounterfactualCard` — specialized counterfactual card layout

Both use `AppCard` and tokens internally.

---

## Verification Checklist

- [x] Same `RecoveryDashboardData` dataclass
- [x] Same `RecoveryDashboard()` constructor (no args)
- [x] Same `refresh(data)` method signature
- [x] Same business logic (RecoveryEngine, RecoveryService unchanged)
- [x] Same imports from `modules.*` and `ui.design_system.*`
- [x] Only canonical components used (AppCard, SectionHeader, StatusBadge, etc.)
- [x] No hardcoded colors or typography
- [x] All sections have narrative-first content
- [x] Maximum 2 charts (Trend + History)
- [x] Empty states for all 4 scenarios
- [x] Counterfactuals as beautiful cards
- [x] Keyboard accessible (all interactive elements focusable)
- [x] Reduced motion respected
