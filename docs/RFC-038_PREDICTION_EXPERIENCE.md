# RFC-038: Prediction Experience 2.0

**Status:** IMPLEMENTATION  
**Priority:** CRITICAL  
**Dependencies:** RFC-034 (Design System 3.0), REP-007E (DS Consolidation)  
**Target:** `ui/prediction/prediction_dashboard.py`

---

## Table of Contents

1. [User Journey](#1-user-journey)
2. [Information Hierarchy](#2-information-hierarchy)
3. [ASCII Wireframes](#3-ascii-wireframes)
4. [Reasoning Flow](#4-reasoning-flow)
5. [Evidence Hierarchy](#5-evidence-hierarchy)
6. [Counterfactual Design](#6-counterfactual-design)
7. [Component Tree](#7-component-tree)
8. [Motion Map](#8-motion-map)
9. [Implementation Decisions](#9-implementation-decisions)

---

## 1. User Journey

### Primary Question

**"What should I do next?"**

### Journey Map

```
ARRIVAL
  │
  ▼
HERO ──→ "Expected Bench PR within 3 weeks"
  │        Confidence: High
  │        CTA: "Continue Program"
  │
  ▼
SUMMARY ──→ One natural language paragraph
  │          "Current progression indicates a high likelihood
  │           of reaching 82.5kg bench within 3 weeks..."
  │
  ▼
EVIDENCE ──→ Cards that prove WHY
  │          Training Volume ↑ · Sleep Stable
  │          Recovery High · Consistency Excellent
  │
  ▼
REASONING ──→ Visual inference chain
  │          Volume → Recovery → Adaptation → Strength → PR
  │
  ▼
COUNTERFACTUALS ──→ "What if" premium cards
  │                  Sleep +1h → Confidence +6%
  │                  Reduce missed sessions → PR 5 days sooner
  │
  ▼
FORECAST ──→ PredictionTimeline
  │          Week 1 · Week 2 · Week 3
  │          Narrative below: "Expected adaptation window"
  │
  ▼
COACH ──→ Max 3 recommendations
  │         Highest priority first
  │
  ▼
CONFIDENCE ──→ ConfidenceGauge with explanation
  │             "Confidence lower due to: low sample size,
  │              recent program change, insufficient history"
  │
  ▼
ACTION PLAN ──→ Today · This week · Review date
  │              CTA: Continue · CTA: Review Plan
```

### State Machine

```
                ┌─────────────────┐
                │ No Data         │ ← No workouts completed
                └────────┬────────┘
                         │ First workout
                         ▼
                ┌─────────────────┐
                │ Warming Up      │ ← < 3 workouts
                └────────┬────────┘
                         │ 3+ workouts
                         ▼
                ┌─────────────────┐
         ┌─────→│ Active           │ ← Normal prediction
         │      └────────┬────────┘
         │               │ Program change
         │               ▼
         │      ┌─────────────────┐
         └──────│ Recalibrating   │ ← New data patterns
                └─────────────────┘
```

---

## 2. Information Hierarchy

### Content Weight

| Section | Weight | Rationale |
|---------|--------|-----------|
| Hero | 25% | First thing, sets the prediction narrative |
| Coach | 18% | Most actionable, highest value |
| Evidence | 14% | Explains WHY — builds trust |
| Reasoning | 12% | Inference chain — feels like coaching |
| Forecast | 10% | Timeline visualization |
| Counterfactuals | 8% | Decision support, premium feel |
| Summary | 6% | Quick narrative context |
| Confidence | 4% | Explains uncertainty |
| Action Plan | 3% | Concrete next steps |

---

## 3. ASCII Wireframes

### Full Page Layout

```
┌────────────────────────────────────────────────────────────────┐
│  HERO                                                         │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  🏋️  Expected Bench PR                                 │   │
│  │  within 3 weeks                                         │   │
│  │                                                         │   │
│  │  Confidence: ████████░░ 82%      [▶ Continue Program]   │   │
│  │  "Based on your current progression trajectory"          │   │
│  └────────────────────────────────────────────────────────┘   │
├────────────────────────────────────────────────────────────────┤
│  SUMMARY                                                       │
│  "Current progression indicates a high likelihood of reaching │
│  82.5kg bench within the next three weeks. Recovery quality   │
│  has remained stable. Volume progression supports this trend."│
├────────────────────────────────────────────────────────────────┤
│  EVIDENCE                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ 📈 Volume│  │ 😴 Sleep │  │ 🛡️ Recovery│ │ ✅ Consistency│  │
│  │ +15%     │  │ Stable   │  │ High     │  │ Excellent  │     │
│  │ Trending │  │ 7.5h avg │  │ 82/100   │  │ 12-day str│     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
├────────────────────────────────────────────────────────────────┤
│  REASONING                                                     │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  📈 Training Volume  ─────→  💪 Adaptation Stimulus   │   │
│  │                                                       │   │
│  │  🛡️ Recovery Quality  ─────→  🏗️ Muscle Repair      │   │
│  │                                                       │   │
│  │  💪 Expected Strength Gain  ─────→  🏆 Predicted PR   │   │
│  └────────────────────────────────────────────────────────┘   │
├────────────────────────────────────────────────────────────────┤
│  WHAT IF...                                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ 😴 Sleep +1h │  │ 📅 No Misses  │  │ 💧 Hydrate   │         │
│  │ Conf. +6%    │  │ PR 5d sooner │  │ Recovery +4  │         │
│  │ ████████░░   │  │ ██████░░░░   │  │ ████░░░░░░   │         │
│  │ Impact: High │  │ Impact: Med  │  │ Impact: Low  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
├────────────────────────────────────────────────────────────────┤
│  FORECAST TIMELINE                                             │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                       │   │
│  │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓              │   │
│  │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓    │   │
│  │  └──────────────────────────────────────────────┘     │   │
│  │  Week 1        Week 2        Week 3                   │   │
│  │  Expected PR window: Week 3 [Mar 25 - Apr 1]          │   │
│  └────────────────────────────────────────────────────────┘   │
├────────────────────────────────────────────────────────────────┤
│  COACH                                                         │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ ● Continue your current program as planned.            │   │
│  │   Your progression is on track. Maintain RIR 1-2.      │   │
│  ├────────────────────────────────────────────────────────┤   │
│  │ ● Prioritise sleep quality this week.                  │   │
│  │   Aim for 8h. Each hour correlates with +5% PR prob.   │   │
│  ├────────────────────────────────────────────────────────┤   │
│  │ ● Monitor bench form at heavier loads.                 │   │
│  │   Consider adding a technique day.                     │   │
│  └────────────────────────────────────────────────────────┘   │
├────────────────────────────────────────────────────────────────┤
│  CONFIDENCE                                                    │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  ▓▓▓▓▓▓▓▓▓▓░░░░░░  Moderate (62%)                      │   │
│  │                                                         │   │
│  │  Confidence is moderate because:                        │   │
│  │  • Limited data: 8 workouts analyzed                    │   │
│  │  • Recent program change (3 weeks ago)                  │   │
│  │  • Recovery history is still accumulating               │   │
│  └────────────────────────────────────────────────────────┘   │
├────────────────────────────────────────────────────────────────┤
│  ACTION PLAN                                                   │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  Today     → Complete Push workout                     │   │
│  │  This week → Maintain RIR 1-2, sleep 8h                │   │
│  │  Review    → Mar 25 — reassess PR trajectory           │   │
│  │                                                         │   │
│  │  [▶ Continue]  [✏ Review Plan]                         │   │
│  └────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────┘
```

---

## 4. Reasoning Flow

### Inference Chain Visual Design

Each step is a card connected by arrows:
- Left: premise category icon + label
- Center: connecting arrow (→)
- Right: conclusion

```
┌─────────────────────────────────────┐
│  📈 Training Volume  ─────→  Adaptation Stimulus
│  +15% over 3 weeks          Muscles taxed adequately
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│  😴 Sleep Quality  ─────→  Recovery State
│  7.5h avg, stable          High (82/100)
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│  📋 Progressive Overload  ─→  Strength Gain
│  Weight increasing weekly    +2.5kg/2 weeks
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│  🏆 Predicted PR  ←───  Synthesis
│  82.5kg bench within 3 weeks
└─────────────────────────────────────┘
```

---

## 5. Evidence Hierarchy

### Evidence Cards — What Proves This Prediction?

| Evidence Factor | Icon | Good (≥70) | Moderate (40-69) | Poor (<40) |
|-----------------|------|-----------|------------------|------------|
| Training Volume | 📈 | +15% Trending Up | +5% Stable | -10% Declining |
| Sleep | 😴 | Good — 7.5h | Fair — 6.5h | Needs Work — 5.5h |
| Recovery | 🛡️ | High — 82/100 | Moderate — 65/100 | Low — 45/100 |
| Consistency | ✅ | Excellent — 12d streak | Good — 5d streak | Low — 2 missed |
| Progressive Overload | 📋 | Yes — increasing weight | Stable weights | No progression |

---

## 6. Counterfactual Design

### Card Layout

```
┌───────────────────────────────────┐
│ 😴  What if...                    │
│     Sleep +1 hour                  │
│                                   │
│  Confidence +6%                    │
│  ████████░░░░░░  Impact: High     │
└───────────────────────────────────┘
```

### Scenarios

| Scenario | Icon | Impact | Confidence | Priority |
|----------|------|--------|-----------|----------|
| Sleep +1h | 😴 | Confidence +6% | 85% | Always show |
| 0 missed sessions | 📅 | PR 5 days sooner | 65% | If missed > 0 |
| Hydration | 💧 | Recovery +4 | 40% | If fatigue > 30 |
| Deload now | 🔄 | Recovery +12 | 70% | If weeks since deload > 6 |

---

## 7. Component Tree

```
QWidget (PredictionDashboard)
├── ScrollContainer
│   └── QVBoxLayout
│       ├── HeroPanel (custom QFrame)
│       │   ├── QLabel (prediction emoji, h1)
│       │   ├── QLabel (prediction title, h2)
│       │   ├── QLabel ("within N weeks", body)
│       │   ├── QHBoxLayout
│       │   │   ├── StatusBadge (confidence level)
│       │   │   ├── QLabel (percentage)
│       │   │   └── QProgressBar (confidence bar)
│       │   ├── QLabel (narrative subtitle)
│       │   └── QPushButton (primary CTA)
│       │
│       ├── SectionHeader ("Summary")
│       ├── AppCard (summary paragraph)
│       │
│       ├── SectionHeader ("Evidence")
│       ├── EditorialGrid
│       │   ├── AppCard (Volume) — QUARTER
│       │   ├── AppCard (Sleep) — QUARTER
│       │   ├── AppCard (Recovery) — QUARTER
│       │   └── AppCard (Consistency) — QUARTER
│       │
│       ├── SectionHeader ("Reasoning")
│       ├── QVBoxLayout (inference steps)
│       │   ├── _ReasonStep (Volume → Adaptation)
│       │   ├── _ReasonStep (Sleep → Recovery)
│       │   ├── _ReasonStep (Overload → Strength)
│       │   └── _ReasonStep (→ Predicted PR, highlighted)
│       │
│       ├── SectionHeader ("What If...")
│       ├── EditorialGrid
│       │   └── 3× _CounterfactualCard — THIRD span
│       │
│       ├── SectionHeader ("Forecast Timeline")
│       ├── ChartContainer
│       │   ├── PredictionTimeline
│       │   └── QLabel (narrative)
│       │
│       ├── SectionHeader ("Coach")
│       ├── CoachCardStack (max 3)
│       │
│       ├── SectionHeader ("Confidence")
│       ├── AppCard
│       │   ├── ConfidenceGauge
│       │   ├── QLabel (confidence level + percentage)
│       │   └── QLabel (reasons, bullet points)
│       │
│       ├── SectionHeader ("Action Plan")
│       └── AppCard
│           ├── 3× ActionRow (Today, This Week, Review)
│           └── QHBoxLayout (2 CTA buttons)
```

---

## 8. Motion Map

| Element | Trigger | Animation | Duration | Curve |
|---------|---------|-----------|----------|-------|
| Hero | Page load | Fade in | 250ms | ease-out |
| Summary | Page load | Fade in | 200ms | ease-out |
| Evidence cards | Page load | Stagger fade, 100ms apart | 200ms each | ease-out |
| Reasoning steps | Page load | Slide up sequential, 120ms apart | 250ms each | ease-out |
| Counterfactual cards | Page load | Scale + Fade, 100ms apart | 250ms each | ease-out |
| Forecast timeline | Page load | Left → Right draw | 400ms | ease-in-out |
| Coach cards | Page load | Fade, 150ms apart | 200ms | ease-out |
| Confidence | Page load | Gauge fill | 350ms | ease-out |
| Action plan | Page load | Slide up | 200ms | ease-out |
| Reduced motion | All | Instant show | 0ms | none |

---

## 9. Implementation Decisions

### Decision 1: Preserve PredictionDashboardData

The dataclass remains identical (`view_model`, `has_data`, `result`). All existing business logic and main_window.py integration work without changes.

### Decision 2: Derive "One Prediction" from Data

The Hero shows the **most confident** prediction from the data. If PR prediction has `has_data=True`, it becomes the primary hero prediction. Otherwise, plateau or recovery predictions take priority.

### Decision 3: Evidence Cards are Always Shown

Even without data, evidence cards show empty states explaining what data is needed. This educates the user about what the prediction system needs.

### Decision 4: Counterfactuals Use Engine or Defaults

When `PredictionResult.counterfactual_results` is available, use real data. Otherwise, fall back to sensible defaults based on prediction type.

### Decision 5: Coach Uses CoachCardStack

The CoachCardStack from `ui/narrative/cards.py` is used directly with Narrative objects derived from prediction explanations and recommendations.

### Decision 6: Single Scroll Page

All 9 sections in one continuous scroll. No tabs, no sub-navigation.

### Decision 7: Reasoning Chain Steps are Custom Widgets

No canonical component exists for inference chain visualization. `_ReasonStep` is a lightweight QFrame with icon + premise → conclusion layout.

### Decision 8: Confidence Always Has Explanation

Never show ConfidenceGauge without bullet-point reasons for the confidence level. This is enforced by the update method.
