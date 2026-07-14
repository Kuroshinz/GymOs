# RFC-036: Progress Experience 2.0 — Your Training Story

**Status:** IMPLEMENTATION  
**Priority:** CRITICAL  
**Author:** Design System Team  
**Date:** 2026-07-14  
**Depends on:** RFC-034 (Design System 3.0), RFC-035 (Workout Experience 2.0)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [User Journey](#2-user-journey)
3. [Information Hierarchy](#3-information-hierarchy)
4. [ASCII Wireframes](#4-ascii-wireframes)
5. [Narrative Flow](#5-narrative-flow)
6. [Chart Inventory](#6-chart-inventory)
7. [Component Tree](#7-component-tree)
8. [Motion Map](#8-motion-map)
9. [Empty States](#9-empty-states)
10. [Implementation Decisions](#10-implementation-decisions)
11. [Verification Checklist](#11-verification-checklist)

---

## 1. Executive Summary

The Progress Experience is GymOS's long-term memory. It answers one question: **"Am I becoming stronger?"**

The current page is a data dashboard — charts, grids, KPIs. It tells the user *what* happened but not *why it matters*.

REP-007G transforms the page into a **narrative journey**. Every section tells a story. Charts support the story; they don't replace it.

### Design Principles

1. **Story first** — Every section answers "So what?" with narrative text
2. **Celebration over statistics** — PRs are achievements, not data points
3. **Journey over snapshot** — Milestones show progression over time
4. **Coach guidance** — Every trend has an explanation
5. **Canonical components only** — AppCard, CoachCardStack, SectionHeader, StatusBadge, TrendChart, WeeklyTimeline

### Preserved API

| Element | Status |
|---------|--------|
| `refresh()` method | ✅ Identical |
| `ProgressExperience(db)` constructor | ✅ Identical |
| `VolumeAnalytics` usage | ✅ Unchanged |
| `PREngine` usage | ✅ Unchanged |
| Same signals | ✅ No new signals |
| Same database queries | ✅ Unchanged |

---

## 2. User Journey

### Page Flow (top-to-bottom)

```
┌──────────────────────────────────────────────────────────────┐
│ HERO                                                          │
│ "You've completed 43 workouts.                                │
│  You're stronger than you were 6 weeks ago."                  │
│                                                              │
│  45 Workouts    12 PRs    7d Streak    8,400 kg Volume        │
├──────────────────────────────────────────────────────────────┤
│ YOUR JOURNEY                                                  │
│ ● Started GymOS  ─── ● First PR  ─── ● Bench 60kg  ─── ● Now│
├──────────────────────────────────────────────────────────────┤
│ STRENGTH                                                      │
│ ┌────────────────┐ ┌────────────────┐ ┌────────────────┐     │
│ │ Bench PR      │ │ Squat PR      │ │ Deadlift PR    │     │
│ │ +7.5kg (12%)  │ │ +10kg (8%)   │ │ No change      │     │
│ │ Improved!     │ │ Keep going!   │ │ Plateau        │     │
│ └────────────────┘ └────────────────┘ └────────────────┘     │
│                                                              │
│ Coach: "Bench improved by 12%. Last session looked smooth.   │
│         Squat is progressing. Deadlift needs a reset week."   │
├──────────────────────────────────────────────────────────────┤
│ BODY                                                         │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Body Weight Trend                                        │ │
│ │ [chart: smooth line, gradual decline]                     │ │
│ │ Coach: "Down 2.3kg in 6 weeks. Consistent progress.      │ │
│ │         On track for -5kg goal by September."             │ │
│ └──────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────┤
│ CONSISTENCY                                                  │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ M   T   W   T   F   S   S                               │ │
│ │ █   █   █   ░   █   ░   ░   71% this week               │ │
│ │                                                          │ │
│ │ Weekly heatmap: 4/5 weeks above 60%                      │ │
│ │ Best week: Week 26 (5 sessions)                          │ │
│ └──────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────┤
│ COACH                                                        │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ 1. Training consistency increased  →  4x/week             │ │
│ │ 2. Lower body volume falling      →  Add 2 sets squats  │ │
│ │ 3. Sleep correlates with PRs      →  Prioritise recovery │ │
│ └──────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────┤
│ ACHIEVEMENTS                                                 │
│ ┌────────────────┐ ┌────────────────┐ ┌────────────────┐     │
│ │ 🏆 12 PRs     │ │ 🔥 7d Streak  │ │ 💪 10k Volume │     │
│ │ Earned Jun 14 │ │ Active         │ │ Earned Jun 10 │     │
│ └────────────────┘ └────────────────┘ └────────────────┘     │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. Information Hierarchy

### Visual Weight (scrolls through all)

```
1. HERO (viewport anchor, 25% viewport)
   ├── Primary narrative message (largest text)
   ├── Secondary narrative (subtitle)
   └── KPI strip (compact, 4 metrics)

2. YOUR JOURNEY (15% viewport)
   ├── Timeline header
   └── Milestone dots + labels

3. STRENGTH (30% viewport)
   ├── Section header with coach sub-narrative
   ├── PR cards (3-column grid)
   └── Narrative summary

4. BODY (20% viewport)
   ├── Section header
   ├── Weight trend chart (1 chart, not 2)
   └── Coach explanation below chart

5. CONSISTENCY (20% viewport)
   ├── Section header
   ├── Weekly bar timeline
   ├── Adherence percentage
   └── Monthly summary text

6. COACH (25% viewport)
   ├── Section header
   ├── 3 CoachCards with narrative insights
   └── Action items

7. ACHIEVEMENTS (20% viewport)
   ├── Section header
   └── Glowing card grid
```

---

## 4. ASCII Wireframes

### 4.1 Hero Section

```
┌──────────────────────────────────────────────────────────────────┐
│ ╔══════════════════════════════════════════════════════════════╗ │
│ ║  "You've completed 45 workouts.                             ║ │
│ ║   You're stronger than you were last month."                ║ │
│ ║                                                              ║ │
│ ║  45        12        7d         8.4k                         ║ │
│ ║  Workouts  PRs      Streak     Volume                        ║ │
│ ╚══════════════════════════════════════════════════════════════╝ │
└──────────────────────────────────────────────────────────────────┘
```

### 4.2 Your Journey Section

```
┌──────────────────────────────────────────────────────────────────┐
│  Your Journey                                                    │
│  From first workout to today — every milestone matters           │
│                                                                  │
│  ●─────●─────●─────●─────●─────●─────●                          │
│  │     │     │     │     │     │     │                          │
│ Start PR   60kg  -2kg  PR   Now                                  │
│ GymOS Bench Bench  BW  Squat                                    │
└──────────────────────────────────────────────────────────────────┘
```

### 4.3 Strength Section

```
┌──────────────────────────────────────────────────────────────────┐
│  Strength                                                        │
│  "Bench improved by 12% this month."                             │
│                                                                  │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐    │
│  │ Barbell Bench   │ │ Barbell Squat   │ │ Deadlift        │    │
│  │                 │ │                 │ │                 │    │
│  │ 87.5kg          │ │ 120kg           │ │ 140kg           │    │
│  │ ▲ +7.5kg (12%)  │ │ ▲ +10kg (9%)   │ │ — No change     │    │
│  │ Improved!       │ │ Keep going!     │ │ Plateau         │    │
│  │ Jun 14          │ │ Jun 12          │ │ Last: May 30    │    │
│  │                 │ │                 │ │                 │    │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

### 4.4 Body Section

```
┌──────────────────────────────────────────────────────────────────┐
│  Body                                                           │
│  Weight trend and composition tracking                          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  Body Weight                                             │   │
│  │  82 ┤╭╮                                                   │   │
│  │  81 ┤╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱                                │   │
│  │  80 ┤╱           ╲╱                                     │   │
│  │     └────────────────────────                             │   │
│  │      May 14         Jun 14                                │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Coach: "Down 2.3kg in 6 weeks. Consistent progress."           │
│         "On track for -5kg goal by September. Keep going!"       │
└──────────────────────────────────────────────────────────────────┘
```

### 4.5 Coach Section

```
┌──────────────────────────────────────────────────────────────────┐
│  Coach                                                           │
│  Personalised insights from your training data                   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 🔵 Training consistency increased                        │   │
│  │  You're training 4x per week, up from 3x. This is       │   │
│  │  excellent progress. Your consistency is building        │   │
│  │  real momentum.                                          │   │
│  │  → Keep this pace for 2 more weeks                       │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 🟡 Lower body volume is falling                          │   │
│  │  Your squat volume dropped 40% this month. Consider      │   │
│  │  adding 2 sets of squats to maintain progress.           │   │
│  │  → Add 2 sets of squats per week                        │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 🟢 Sleep correlates with PRs                             │   │
│  │  Your best training days follow 7+ hours of sleep.       │   │
│  │  Prioritise recovery for continued gains.                │   │
│  │  → Aim for 7+ hours of sleep per night                  │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 5. Narrative Flow

### 5.1 Hero Narratives

Generated from existing data, no new calculations:

| Condition | Narrative |
|-----------|-----------|
| Has 10+ workouts | "You've completed {n} workouts. You're building real momentum." |
| Has PRs | "You've set {n} personal records. Keep pushing your limits." |
| Has streak 5+ | "Your {n}-day streak shows incredible dedication." |
| New user (< 5 workouts) | "Welcome! Every workout builds a stronger you." |
| Returning after break | "Welcome back. Consistency is the key to progress." |

### 5.2 Strength Narratives

| Condition | Narrative |
|-----------|-----------|
| PR improvement > 10% | "{exercise} improved by {pct}%! Outstanding progress." |
| PR improvement 5-10% | "{exercise} improved by {pct}%. Solid gains." |
| PR improvement < 5% | "{exercise} is trending up. Keep pushing." |
| No improvement | "{exercise} — no change yet. Try adjusting your approach." |
| Plateau (no PR in 14d) | "{exercise} plateau detected. Consider a deload or rep scheme change." |

### 5.3 Body Narratives

| Condition | Narrative |
|-----------|-----------|
| Weight down > 2kg in period | "Down {delta}kg in {weeks} weeks. Consistent progress. On track for your goal." |
| Weight stable | "Weight is stable. Perfect environment for strength gains." |
| Weight up > 2kg in period | "Up {delta}kg. Great for strength building." |

### 5.4 Consistency Narratives

| Condition | Narrative |
|-----------|-----------|
| Adherence > 80% | "Excellent consistency! You're training {avg}x/week." |
| Adherence 60-80% | "Good consistency. {avg}x/week — try to add one more session." |
| Adherence < 60% | "Building consistency. Every session counts." |

---

## 6. Chart Inventory

### Removed Charts

| Old Chart | Reason for Removal |
|-----------|-------------------|
| RadarChart (Muscle Balance) | Overly complex, no clear "so what" |
| BarChart (Weekly Volume) | Replaced by narrative strength section |
| Muscle detail list | Replaced by coach section |
| Compliance timeline (duplicate) | Merged into Consistency section |

### Retained (refined)

| Chart | Section | Purpose |
|-------|---------|---------|
| TrendChart (Body Weight) | Body | Show weight trend with coach explanation |

### New Elements

| Element | Section | Description |
|---------|---------|-------------|
| Journey timeline | Your Journey | Horizontal milestone dots with labels |
| PR cards (AppCard) | Strength | Large cards with animated values, improvement text |
| Weekly bar chart | Consistency | WeeklyTimeline + adherence percentage |
| Achievement cards (AppCard) | Achievements | Glowing cards with icon, date, description |

---

## 7. Component Tree

```
ProgressExperience (QWidget)
│
├── ScrollContainer
│   └── VBoxLayout
│       │
│       ├── [Section 1: Hero]
│       │   └── AppCard (elevated=false)
│       │       ├── HeroNarrative (QLabel) — large typography, "You've completed..."
│       │       ├── HeroSubtitle (QLabel)
│       │       └── KpiStrip (compact 4-item metrics)
│       │
│       ├── [Section 2: Your Journey]
│       │   ├── SectionHeader(title="Your Journey", subtitle="From first workout to today")
│       │   └── JourneyTimeline (QFrame — painted dots + labels)
│       │
│       ├── [Section 3: Strength]
│       │   ├── SectionHeader(title="Strength", subtitle=narrative)
│       │   ├── PRCard[] (AppCard, interactive=false) × 3-6
│       │   │   ├── ExerciseName (QLabel)
│       │   │   ├── Value (QLabel) — large
│       │   │   ├── Improvement (StatusBadge) — % change
│       │   │   ├── Narrative (QLabel)
│       │   │   └── Date (QLabel)
│       │   └── StrengthNarrative (QLabel) — coach summary
│       │
│       ├── [Section 4: Body]
│       │   ├── SectionHeader(title="Body", subtitle="Weight trend and composition")
│       │   ├── ChartContainer
│       │   │   └── TrendChart (Body Weight)
│       │   └── BodyNarrative (QLabel) — coach explains trend
│       │
│       ├── [Section 5: Consistency]
│       │   ├── SectionHeader(title="Consistency", subtitle="Your training rhythm")
│       │   ├── WeeklyTimeline (7-day bar chart)
│       │   ├── AdherenceLabel (QLabel) — "71% this week"
│       │   ├── MonthlySummary (QLabel) — narrative
│       │   └── StatusBadge[] — streak badges
│       │
│       ├── [Section 6: Coach]
│       │   ├── SectionHeader(title="Coach", subtitle="Personalised insights")
│       │   └── CoachCardStack (max 3 cards)
│       │
│       └── [Section 7: Achievements]
│           ├── SectionHeader(title="Achievements", subtitle="Celebrate your wins")
│           └── AppCard[] (interactive=false, elevated) × 6
│               ├── Icon (QLabel)
│               ├── Title (QLabel)
│               ├── Description (QLabel)
│               └── Date (QLabel)
```

### 7.1 Canonical Components Used

| Component | Source | Usage |
|-----------|--------|-------|
| `AppCard` | design_system/components | Hero, PR cards, Achievement cards |
| `SectionHeader` | design_system/components | All 7 section headers |
| `ChartContainer` | design_system/components | Body weight chart wrapper |
| `TrendChart` | visualization/charts | Body weight line chart |
| `WeeklyTimeline` | design_system/visualization | Consistency bar chart |
| `StatusBadge` | design_system/components | Improvement indicators, streak badges |
| `CoachCard` | narrative/cards | Coach insights |
| `CoachCardStack` | narrative/cards | Coach section container |
| `ScrollContainer` | design_system/layout | Page scroll |
| `KpiStrip` | design_system/layout | Hero metrics KPI row |

---

## 8. Motion Map

### 8.1 Timing

| Trigger | Duration | Curve | Element |
|---------|----------|-------|---------|
| Page reveal | 300ms | Ease Out | Fade in entire content |
| PR values | 200ms | Ease Out | Animate number display |
| Coach appearance | 200ms | Ease Out | Fade in + slide up |
| Journey timeline | 250ms | Ease Out | Left-to-right dot reveal |
| Achievement glow | 300ms | Ease Out | Glow effect pulse |
| Chart draw | 400ms | Ease Out | Progressive line draw |

### 8.2 Reduced Motion

When Qt's accessibility reduced-motion is detected:
- All animations skip to end state
- Page reveal is instant
- PR values shown immediately
- Coaches fade without slide

---

## 9. Empty States

### 9.1 No Workouts

```
┌──────────────────────────────────────────────────────────────┐
│  💪                                                          │
│  Welcome to Progress                                         │
│  Complete your first workout to unlock progress tracking,    │
│  PR detection, and personalised insights.                    │
│                                                              │
│  [Start a Workout]                                           │
└──────────────────────────────────────────────────────────────┘
```

### 9.2 No PRs

```
┌──────────────────────────────────────────────────────────────┐
│  🏆                                                          │
│  No PRs Yet                                                  │
│  Push yourself in your next workout!                         │
│  Every rep is a step toward a new personal record.           │
└──────────────────────────────────────────────────────────────┘
```

### 9.3 No Body Weight History

```
┌──────────────────────────────────────────────────────────────┐
│  ⚖                                                           │
│  No Weight Data                                              │
│  Log your body weight in Settings to track changes           │
│  and see your progress toward your goal.                     │
└──────────────────────────────────────────────────────────────┘
```

### 9.4 No Consistency Data

```
┌──────────────────────────────────────────────────────────────┐
│  📅                                                          │
│  No Consistency Data                                         │
│  Complete workouts regularly to build your consistency       │
│  streak and see your training rhythm.                        │
└──────────────────────────────────────────────────────────────┘
```

---

## 10. Implementation Decisions

### 10.1 Architecture

```
ProgressExperience (presentation)
    │
    ├── refresh() → section updates (unchanged API)
    │
    ├── Uses: db.list_sessions (unchanged)
    ├── Uses: PREngine (unchanged)
    ├── Uses: VolumeAnalytics (unchanged)
    ├── Uses: db.get_body_weight_history (unchanged)
    │
    ├── Builds: Hero → Journey → Strength → Body → Consistency → Coach → Achievements
    └── Emits: No signals (unchanged)
```

### 10.2 Journey Timeline Rendering

The journey timeline is painted programmatically using QPainter, rendering horizontal dots connected by lines with labels underneath. This avoids needing a custom widget library while providing a polished, editorial look.

### 10.3 PR Card Design

PR cards use `AppCard` with forced `interactive=False`. The card body contains:
- Exercise name (heading)
- Current value (large)
- Improvement text with arrow (StatusBadge)
- Narrative line (generated from percentage)
- Date achieved

Cards are arranged in a horizontal row (max 3) that wraps to additional rows.

### 10.4 Achievement Detection

Achievements are derived from existing data:
- **PR milestones**: 1st, 5th, 10th, 25th PR
- **Volume milestones**: 10,000kg, 50,000kg, 100,000kg total
- **Consistency milestones**: 7-day streak, 14-day streak, 30-day streak
- **Workout milestones**: 10, 25, 50, 100 workouts completed
- **Body weight milestones**: First weight log, first 2kg change

### 10.5 Coach Insights

Coach insights come from existing data with narrative formatting:
- **Volume trend**: VolumeAnalytics → narrative ("Lower body volume is falling")
- **PR frequency**: PREngine → narrative ("You've set 3 PRs this month")
- **Consistency**: Session data → narrative ("Training 4x/week consistently")
- **Body weight**: Weight history → narrative ("Down 2.3kg this month")
- **Recovery**: Recovery benchmarks → narrative ("Sleep correlates with performance")

---

## 11. Verification Checklist

- [ ] `refresh()` method works identically
- [ ] `ProgressExperience(db)` constructor unchanged
- [ ] Hero shows primary narrative message
- [ ] Journey timeline renders milestones
- [ ] Strength section shows PRs with improvement percentages
- [ ] Body section shows weight trend chart + coach explanation
- [ ] Consistency section shows timeline + adherence
- [ ] Coach section shows max 3 narrative insights
- [ ] Achievements show milestone cards with glow
- [ ] Empty states display for all sections with no data
- [ ] All components are canonical (AppCard, SectionHeader, etc.)
- [ ] No hardcoded colors, spacing, or typography
- [ ] Compilation passes with no errors
- [ ] App launches without regressions
