# RFC-032 — Cognitive Dashboard

> **Status:** Design Document — No Code Modified
> **Role:** Lead Product Designer
> **Date:** 2026-07-14
> **Depends on:** REP-007C (Dashboard Experience 2.0)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Methodology](#2-methodology)
3. [Section-by-Section Audit](#3-section-by-section-audit)
4. [Before Information Hierarchy](#4-before-information-hierarchy)
5. [After Information Hierarchy](#5-after-information-hierarchy)
6. [Removed Sections](#6-removed-sections)
7. [Moved Sections](#7-moved-sections)
8. [Section Recomposition](#8-section-recomposition)
9. [Eye-Flow Diagram](#9-eye-flow-diagram)
10. [User Decision Map](#10-user-decision-map)
11. [Cognitive Load Analysis](#11-cognitive-load-analysis)
12. [Visual Weight Budget](#12-visual-weight-budget)
13. [Empty State Strategy](#13-empty-state-strategy)
14. [Motion & Transition Design](#14-motion--transition-design)
15. [Acceptance Criteria](#15-acceptance-criteria)

---

## 1. Executive Summary

REP-007C rebuilt the Dashboard visually. REP-007D optimizes it cognitively.

The visual rebuild replaced stacked widgets with an editorial grid and galaxy tokens. The cognitive audit now removes every element that does not serve a single purpose: **answering the user's four questions within five seconds.**

### The Four Questions

| # | Question | Answered By | Max Elements |
|---|----------|-------------|-------------|
| 1 | What am I training today? | Hero - Workout identity | 3 |
| 2 | Am I recovered? | Hero - Recovery status | 2 |
| 3 | How am I progressing? | Coach section | 3 |
| 4 | Anything critical? | Coach section | 2 |

Everything that does not answer one of these four questions is removed from the Dashboard.

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Hero and Mission merge | Both answer "What am I training?" — showing them separately forces the user to read two blocks for one answer |
| Recovery collapses into Hero | Recovery is a single status check, not a full section. The user needs "Am I recovered?" in one glance |
| Coach becomes the sole insight layer | Coach and Predictions both derive from recommendations. Showing both duplicates information and creates confusion |
| Records removed from Dashboard | Personal Records answer "How good was I?" not "What should I do today?" — they belong on the Records page |
| Quick Actions removed from Dashboard | Every action is accessible via ⌘K or the sidebar. Dedicated cards waste screen space for things the user does once per session |
| Metric clusters removed | Readiness, Current Weight, To Goal, Streak — four numbers the user must parse. Only readiness (which also appears in the recovery ring) helps today's decision |
| Goal ring removed | Goal progress is a weeks-to-months metric. It does not change daily. Showing it on every dashboard visit creates visual noise |
| Section headers removed | "Today's Mission" / "Your next training session" is decorative text. The content itself should communicate what it is |
| Duplicate CTAs removed | Start Workout appears in Hero, Mission card, and Quick Actions. Three identical buttons create decision paralysis |

### Expected Improvement

| Metric | Before REP-007C | After REP-007C | After REP-007D | Target |
|--------|----------------|----------------|----------------|--------|
| Elements above fold | 18+ | 12+ | 7 | ≤7 |
| Eye fixations to find workout | 3-4 | 2-3 | 1 | 1 |
| Eye fixations to find readiness | 3-5 | 2-3 | 1 | 1 |
| Seconds to understand situation | 10-15s | 7-10s | 3-5s | <5s |
| Unnecessary labels | 8 | 6 | 2 | 0 |
| Duplicate information | 3 (recovery ring+metric, Start x3, Coach+Predictions) | 2 | 0 | 0 |
| Information density (items/cm²) | High | Medium | Low | Low |

---

## 2. Methodology

### 2.1 Section Audit Criteria

Every section on the Dashboard is evaluated against six questions:

| Question | Weight | Fail Condition |
|----------|--------|----------------|
| Does it answer one of the four questions? | Critical | Remove if no |
| Does it influence today's training decision? | Critical | Remove if no |
| Could it live elsewhere (dedicated page, command palette)? | High | Move if yes |
| Is it duplicating information from another section? | High | Merge or remove |
| Does it require reading more than one line to understand? | Medium | Simplify |
| Does it add visual weight without information value? | Medium | Remove decorative-only elements |

### 2.2 User Profile

The primary user opens GymOS before going to the gym. They have:

- **10–20 seconds** to check in
- Moderate domain knowledge (knows what a Push day is)
- No patience for reading labels or parsing charts
- One goal: confirm today's plan and walk into the gym confident

### 2.3 Assumptions

- The user has at least one active program
- The user has completed at least one workout (some data exists)
- The user is not in their first session
- Empty states are handled gracefully for new users (see Section 13)

---

## 3. Section-by-Section Audit

### 3.1 Hero (REP-007C)

**Current content:** Greeting + user name, program + week + split, RecoveryRing, GoalRing, prediction quote, Readiness metric, Current Weight metric, To Goal metric, Streak metric, Start Workout button, Review Week button.

**Answers what?** Greeting answers nothing. Rings and metrics answer "Am I recovered?" (partially) and "How am I progressing?" (partially). Prediction quote answers nothing (it duplicates Coach). CTAs answer "What should I do?"

**Helps today?** Partially. Recovery ring helps. Goal ring does not. Metrics are split: readiness is useful, others are not.

**Live elsewhere?** Goal ring → Goal page. Streak → Profile. Review Week → Progress page.

**Duplicated?** Recovery score appears as ring AND as "Readiness" metric. Start Workout appears in Hero, Mission, AND Quick Actions. Prediction quote duplicates Coach recommendations.

**Reading required?** Yes. User must scan 10+ elements left-to-right, top-to-bottom.

**Visual weight?** High. Gradient background, two rings, four metric blocks, two CTAs, subtitle, prediction quote — all competing.

**Verdict: STRIP TO ESSENTIALS**

### 3.2 Today's Mission (REP-007C)

**Current content:** Section header ("Today's Mission" + subtitle), workout name, exercise count + duration + recovery hint, muscle group badges, Start Workout button, empty state.

**Answers what?** "What am I training today?" — the most important question.

**Helps today?** Yes — this is the primary decision point.

**Live elsewhere?** No. This is the core Dashboard purpose.

**Duplicated?** Start Workout button duplicates Hero CTA. Workout name/nature partially overlaps with Hero subtitle.

**Reading required?** Yes — separate card requires a separate fixation.

**Visual weight?** Medium. Separate card, large typography.

**Verdict: MERGE INTO HERO**

### 3.3 Recovery (REP-007C)

**Current content:** Section header, narrative label ("Ready for PR 🔥"), score text ("Score: 87/100"), suggested action, empty state.

**Answers what?** "Am I recovered?" — the second most important question.

**Helps today?** Yes.

**Live elsewhere?** Could live on the Recovery page, but the user needs this before deciding to train.

**Duplicated?** Recovery ring in Hero already shows readiness. Score text duplicates the ring's percentage.

**Reading required?** Two lines plus suggestion. Could be one line.

**Visual weight?** Low-medium. Separate card in a two-column row.

**Verdict: COLLAPSE INTO HERO**

### 3.4 Coach (REP-007C)

**Current content:** Section header, CoachCardStack with 2 card items (title, summary, expandable body), empty state.

**Answers what?** "What's important?" / "How am I progressing?" — the third and fourth questions.

**Helps today?** Yes — the coach recommendation is the best single insight.

**Live elsewhere?** No — this is a Dashboard-native function.

**Duplicated?** Recommendations overlap with Predictions content (both derive from the same data).

**Reading required?** Yes — but CoachCardStack uses progressive disclosure (summary visible, body hidden).

**Visual weight?** Medium. Glow effect, two cards, expand/collapse affordances.

**Verdict: RETAIN, STREAMLINE TO ONE CARD**

### 3.5 Predictions (REP-007C)

**Current content:** Section header, prediction headline, detail, confidence label, empty state.

**Answers what?** "What's coming?" — not one of the four critical questions.

**Helps today?** Partially — knowing a PR is coming can motivate, but it does not change today's training decision.

**Live elsewhere?** Yes — the Predictions page is the canonical home.

**Duplicated?** Overlaps heavily with Coach (both use `recommendations` data).

**Reading required?** Low — headline is one line.

**Visual weight?** Low.

**Verdict: MERGE INTO COACH**

If there is a prediction, fold it into the Coach recommendation card. Never show both as separate sections.

### 3.6 Progress (REP-007C)

**Current content:** Section header, goal weight label, goal detail (target, remaining, weeks, rate, quality, estimated date, percent), WeeklyTimeline, weekly total, empty states.

**Answers what?** "How am I progressing?" — the third question.

**Helps today?** Partially. Goal progress helps. Weekly volume detail does not change the user's training decision.

**Live elsewhere?** Yes — the Progress page is the canonical home for all charts and trends.

**Duplicated?** Goal ring in Hero overlaps with goal weight/detail here.

**Reading required?** High — one line of goal detail contains 7 data points.

**Visual weight?** High — full-width card with chart.

**Verdict: STRIP TO ONE LINE**

Keep only: current weight vs target ("72.3 → 77.0 kg"). Remove timeline, weekly total, rate, quality, estimated date, percent.

### 3.7 Personal Records (REP-007C)

**Current content:** Section header, top 5 PRs with star icons, exercise name, type, display value, empty state.

**Answers what?** "What have I achieved?" — does not answer any of the four questions.

**Helps today?** No. PRs are backward-looking. They do not influence today's training decision.

**Live elsewhere?** Yes — the Records page exists.

**Duplicated?** No.

**Reading required?** Low — list of 3-5 items.

**Visual weight?** Medium — full section with star icons.

**Verdict: REMOVE FROM DASHBOARD**

### 3.8 Quick Actions (REP-007C)

**Current content:** 5 stacked action cards (Start Workout, Log Weight, Import Program, View PRs, Review Week).

**Answers what?** Nothing directly. These are task triggers.

**Helps today?** Partially — Start Workout is the primary action. The other four are secondary.

**Live elsewhere?** Yes — every action is available via ⌘K (command palette) or the sidebar.

**Duplicated?** Start Workout duplicates Hero CTA. Review Week duplicates Hero secondary CTA. View PRs duplicates removed Records section.

**Reading required?** Low — each card has icon + label + subtitle.

**Visual weight?** Medium — 5 stacked cards with hover effects.

**Verdict: REMOVE FROM DASHBOARD**

---

## 4. Before Information Hierarchy

### 4.1 REP-007C Layout (current)

```
+------------------------------------------------------------------+
|  HERO                                                             |
|  Good Morning, Nhan · Phase 2 · Week 3 · Push Day                |
|  [RecoveryRing] [GoalRing]                                       |
|  "Your bench press is ready for a 5kg jump."                    |
|  Readiness:87  Current:72.3kg  To Goal:4.7kg  Streak:5d        |
|  [▶ Start Workout]              [✏ Review Week]                  |
+-------------------------------+----------------------------------+
|  TODAY'S MISSION (62%)         | RECOVERY (38%)                  |
|  Push Day                      | Ready for PR 🔥                 |
|  8 exercises · ~45 min · Low  | Score: 87/100 · All systems     |
|  [Chest] [Shoulders] [Triceps]| nominal                         |
|  [▶ Start Workout]             | → Continue your current plan    |
+-------------------------------+----------------------------------+
|  COACH (62%)                   | PREDICTIONS (38%)               |
|  CoachCardStack                | You are on track for a Bench    |
|  Card 1: "...ready for 5kg"   | Press PR within 2 weeks.        |
|  Card 2: "Recovery improving" | Confidence: 82%                 |
+-------------------------------+----------------------------------+
|  PROGRESS (full-width)                                           |
|  72.3 kg → 77.0 kg · 4.7 to go · ~8 weeks · 0.58 kg/wk · Est   |
|  [WeeklyTimeline]  Total: 12,450 kg                              |
|  ⭐ Bench Press +2.5kg · ⭐ Squat +5kg                          |
+-------------------------------+----------------------------------+
|  RECORDS (62%)                 | QUICK ACTIONS (38%)             |
|  ⭐ Bench Press  +2.5kg      | [▶ Start] [⚖ Log] [⬇ Import] |
|  ⭐ OHP          +1.25kg     | [✨ PRs]    [✏ Review]        |
|  ⭐ Squat        +5kg        |                                  |
+-------------------------------+----------------------------------+
```

### 4.2 Information Count

| Element | Count | Necessity |
|---------|-------|-----------|
| Distinct visual sections | 8 | Too many |
| Elements above fold | 14+ | Overwhelming |
| Unique data points | 22+ | Information overload |
| Labels | 9 section headers + metric labels | Redundant |
| CTAs | 3 "Start Workout", 1 "Review Week", 4 quick actions | Scattered |
| Duplicate data | Recovery score (ring + metric), Goal (ring + progress), Coach (card + prediction) | 3 instances |

### 4.3 Attention Flow (Before)

```
① Greeting ──→ ② Rings ──→ ③ Prediction ──→ ④ Metrics
     │                                              │
     ↓                                              ↓
    ⑤ CTAs ──────→ ⑥ Section Headers ──→ ⑦ Mission Card
                                                    │
               ⑩ Progress ←── ⑨ Coach ←── ⑧ Recovery
                    │               │
                    ↓               ↓
               ⑪ Records ←── ⑫ Quick Actions
```

**Problems:**
- Bouncy, non-linear path
- User must return to center after scanning rings (right side)
- Section headers create intermediate stops with no information value
- Progress and Records contain backward-looking data that distracts from today's decision

---

## 5. After Information Hierarchy

### 5.1 Proposed Layout

```
+------------------------------------------------------------------+
|  HERO (answers: What am I training? Am I recovered?)             |
|  Push Day · Week 3                                                |
|  8 exercises · ~45 min · [Chest] [Shoulders] [Triceps]          |
|  Ready for PR 🔥 · Score: 87 · Sleep slightly reduced           |
|  [▶ Start Workout]                                                |
+------------------------------------------------------------------+
|  COACH (answers: How am I progressing? Anything critical?)       |
|  "Your bench press is ready for a 5kg jump."                    |
|  Based on your last 3 sessions showing RIR 1-2.                 |
|  ● Progress:   72.3 → 77.0 kg  ·  4.7 kg to go  ·  ~8 weeks    |
|  ● Consistency: 5-day streak                                     |
|  (If PR forecast) → ⭐ Bench PR likely within 2 weeks (82%)     |
+------------------------------------------------------------------+
```

### 5.2 Information Count (After)

| Element | Count | Necessity |
|---------|-------|-----------|
| Distinct visual sections | 2 | Minimal |
| Elements above fold | 7 | Focused |
| Unique data points | 9 | Essential |
| Labels | 0 (content is self-describing) | Eliminated |
| CTAs | 1 "Start Workout" | Single, clear |
| Duplicate data | 0 | Clean |

### 5.3 What Changed

| Section | Status | Reason |
|---------|--------|--------|
| Hero | Stripped | Removed greeting, GoalRing, prediction quote, 4 metric blocks, Review Week button |
| Today's Mission | Merged into Hero | Workout identity is the hero — no separate card needed |
| Recovery | Collapsed into Hero | Single-line status — no separate card needed |
| Coach | Streamlined | One card instead of stackable two |
| Predictions | Merged into Coach | Prediction becomes a line within Coach if present |
| Progress | Minimal | Stripped to one line: current vs target + remaining + weeks |
| Personal Records | Removed | Backward-looking, does not help today's decision |
| Quick Actions | Removed | Available via ⌘K and sidebar |

### 5.4 Attention Flow (After)

```
① Hero ──────────────→ ② Coach
  │                       │
  ├─ What am I training?  ├─ How am I progressing?
  ├─ Am I recovered?      ├─ Anything critical?
  └─ Primary CTA          └─ (PR forecast, if present)
```

**Improvement:**
- Two fixation points instead of twelve
- Linear, top-to-bottom flow
- Every element answers one of the four questions
- No section headers, no decorative elements, no duplicate data

---

## 6. Removed Sections

### 6.1 Personal Records

**Why:** PRs answer "What have I achieved?" — a backward-looking question. The user does not need to see their best lifts before training. PRs are celebration, not decision support.

**Where it goes:** The Records page (`ui/pr_view.py`) is the canonical home. The "View PRs" signal still exists and is accessible via sidebar navigation.

**Data preserved:** `recent_prs` in `DashboardData` is not modified. The Records page continues to consume it.

**Empty state note:** The existing empty state for PRs ("No Records Yet") is no longer shown on Dashboard. On the Records page, the same empty state is preserved.

### 6.2 Quick Actions

**Why:** Every action in Quick Actions is accessible via ⌘K (command palette), sidebar navigation, or the Hero's single CTA. Dedicated action cards consume 200+ vertical pixels for things the user does once per session.

**Actions relocated:**

| Action | New Access Point |
|--------|-----------------|
| Start Workout | Hero CTA (primary) + Sidebar |
| Log Weight | ⌘K (Command Palette) + Settings page |
| Import Program | ⌘K + Sidebar button |
| View PRs | Sidebar → Records page |
| Review Week | ⌘K + Sidebar → Progress page |

**Signals preserved:** All six signals (`start_workout_clicked`, `log_weight_clicked`, etc.) remain on `DashboardView`. The command palette or other callers can still connect to them.

### 6.3 Metric Cluster (Readiness, Current, To Goal, Streak)

**Why:** Four metrics require four fixations. Readiness duplicates the Recovery ring. Current weight and To Goal duplicate Progress. Streak does not help today's decision.

**What replaces it:** Recovery ring in Hero now carries the readiness information visually. Progress line in Coach carries weight + goal.

### 6.4 Goal Ring

**Why:** A ring is a 72px circle that shows one number (goal percentage) with visual flourish. The same information is more clearly communicated as text ("72.3 → 77.0 kg"). The ring adds decorative weight without information density.

### 6.5 Section Headers

**Why:** "Today's Mission" / "Your next training session" is two lines of text the user must read to understand what follows. If the content is self-describing (which it should be), the header is noise.

**What replaces it:** The content itself communicates its purpose. "Push Day · Week 3" does not need a header above it.

### 6.6 Duplicate CTAs

**Why:** Three identical "Start Workout" buttons create decision paralysis. The user hesitates: "Which one should I press? Is there a difference?"

**Resolution:** One CTA in the Hero. All other Start buttons removed from Dashboard. The signal `start_workout_clicked` is emitted by this single button.

---

## 7. Moved Sections

### 7.1 Recovery → Collapsed into Hero

**Before:** Separate card occupying the right column (38% width) in a two-column row below the mission card.

**After:** A single line within the Hero: `Ready for PR 🔥 · Score: 87 · Sleep slightly reduced`

**Rationale:** Recovery is a single status check. The user needs one answer: "Am I recovered?" — not a full section with narrative label, score, and suggestion. The suggestion ("Continue your current plan") is generic and adds no value.

**Data displayed:**
- Narrative label (e.g., "Ready for PR 🔥", "Take it easy")
- Score (e.g., "87/100")
- One driver if flagged (e.g., "Sleep slightly reduced")
- Suggested action (if non-generic, otherwise omitted)

### 7.2 Predictions → Merged into Coach

**Before:** Separate card occupying the right column (38% width) in a two-column row below Coach.

**After:** A conditional line within the Coach section: `⭐ Bench PR likely within 2 weeks (82% confidence)`

**Rationale:** Coach and Predictions both derive from `recommendations` data. Showing them as separate cards creates the illusion of two independent insights when they are, in fact, the same data expressed differently. The Coach is the authoritative voice. If the rule engine produces a prediction, the Coach delivers it.

**When shown:** Only when a PR forecast exists. Not shown for generic predictions.

### 7.3 Goal Progress → Collapsed into Coach

**Before:** Full-width section with goal weight, timeline, weekly total, and PR list.

**After:** A one-line progress summary within the Coach section: `72.3 → 77.0 kg · 4.7 to go · ~8 weeks`

**Rationale:** Goal progress answers "How am I progressing?" — the third question. It belongs in the insight layer (Coach), not as a separate data-display section.

---

## 8. Section Recomposition

### 8.1 Hero (Recomposed)

```
+------------------------------------------------------------------+
|  Push Day · Week 3                                               |
|  8 exercises · ~45 min · [Chest] [Shoulders] [Triceps]          |
|                                                                  |
|  Ready for PR 🔥 · Score: 87 · Sleep slightly reduced           |
|                                                                  |
|  [▶ Start Workout]                                                |
+------------------------------------------------------------------+
```

**Elements (7 total, down from 14+):**

| Element | Data Source | Type |
|---------|-------------|------|
| Workout + phase | `today_workout_name` + `mesocycle_week` | Text (large, 28px/700) |
| Exercise count + duration | `today_workout_exercise_count` + `today_workout_estimated_duration` | Text (body) |
| Muscle badges | `today_workout_primary_muscles` | Badge pills |
| Recovery narrative | `recovery_level` + `recovery_score` + first driver flag | Text (one line) |
| Start Workout button | CTA | Button (gradient, 52px) |

**Removed from Hero:**
- Greeting ("Good Morning, Nhan" → implied by "Push Day")
- GoalRing → moved to Coach line
- Prediction quote → merged into Coach
- Readiness metric → replaced by Recovery ring (kept) or line text
- Current weight → moved to Coach line
- To Goal metric → moved to Coach line
- Streak metric → moved to Coach line
- Review Week button → removed (accessible via ⌘K / sidebar)

### 8.2 Coach (Recomposed)

```
+------------------------------------------------------------------+
|  "Your bench press is ready for a 5kg jump."                    |
|  Based on your last 3 sessions showing RIR 1-2.                 |
|                                                                  |
|  ● Progress:   72.3 → 77.0 kg  ·  4.7 kg to go  ·  ~8 weeks    |
|  ● Consistency: 5-day streak                                     |
|  (⭐ Bench PR likely within 2 weeks - 82% confidence)           |
+------------------------------------------------------------------+
```

**Elements (5-6 total, down from 10+ across Coach + Predictions + Progress):**

| Element | Data Source | Type |
|---------|-------------|------|
| Coach title + reason | `recommendations[0].title` + `.reason` | Narrative text (quoted) |
| Goal progress | `goal_progress_weight` + `goal_progress_remaining` + `goal_progress_weeks` | Data line |
| Consistency streak | `current_streak` | Data line |
| PR forecast (conditional) | `recommendations` filtered for progression type | Data line |

**Removed:**
- Second recommendation card (CoachCardStack → single card)
- Second recommendation in stack → only show the highest-priority insight
- Weekly timeline → moved to Progress page
- Weekly volume total → moved to Progress page
- PR list → moved to Records page
- CoachCard expand/collapse → always expanded, single insight
- Section header → self-describing content

### 8.3 Visual Comparison

```
BEFORE (REP-007C)                              AFTER (REP-007D)
┌─────────────────────────────────┐            ┌─────────────────────────────┐
│ Hero [14+ elements, 300px]      │            │ Hero [7 elements, 240px]    │
├──────────────┬──────────────────┤            ├─────────────────────────────┤
│ Mission 62%  │ Recovery 38%     │            │ Coach [5-6 elements,         │
├──────────────┼──────────────────┤            │        compact, ~200px]     │
│ Coach 62%    │ Predictions 38%  │            │                             │
├──────────────┴──────────────────┤            │                             │
│ Progress [full, ~200px]         │            │                             │
├──────────────┬──────────────────┤            │                             │
│ Records 62%  │ Quick Actions    │            │                             │
└──────────────┴──────────────────┘            └─────────────────────────────┘

3 viewports of content                      ~1 viewport of content
8 sections                                  2 sections
14+ elements above fold                      7 elements above fold
22+ data points                              9 data points
3 CTAs                                       1 CTA
9 labels (section headers)                   0 labels
```

---

## 9. Eye-Flow Diagram

### 9.1 Before (REP-007C)

```
                              ┌──────────┐
                              │ Greeting │
                              │  (1)     │
                              └────┬─────┘
                                   │
                    ┌───────────────┴────────────────┐
                    │          Rings (2)              │
                    │  ┌──────────┐ ┌──────────┐     │
                    │  │ Recovery │ │   Goal   │     │
                    │  │   Ring   │ │   Ring   │     │
                    │  └──────────┘ └──────────┘     │
                    └───────────────┬────────────────┘
                                    │
                         ┌──────────┴──────────┐
                         │  Prediction (3)      │
                         └──────────┬──────────┘
                                    │
                         ┌──────────┴──────────┐
                         │  4 Metrics (4)       │
                         │  Rdy · Wgt · Goal ·  │
                         │  Str                 │
                         └──────────┬──────────┘
                                    │
                         ┌──────────┴──────────┐
                         │  2 CTAs (5)          │
                         │  Start · Review      │
                         └──────────┬──────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
     ┌────────┴────────┐  ┌────────┴────────┐  ┌────────┴────────┐
     │ Section Header  │  │ Section Header  │  │ Section Header  │
     │ "Today's Miss." │  │ "Recovery &     │  │ "Progress" (10) │
     │ (6)             │  │ Coach" (7)      │  │                 │
     └────────┬────────┘  └────────┬────────┘  └────────┬────────┘
              │                     │                     │
     ┌────────┴────────┐  ┌────────┴────────────────┐    │
     │ Mission Card    │  │ Recovery (8) │ Coach (9) │    │
     │ · Workout name  │  │              │           │    │
     │ · Exercises     │  │ Narrative    │ Card 1    │    │
     │ · Muscles       │  │ Score        │ Card 2    │    │
     │ · CTA           │  │ Suggested    │           │    │
     └─────────────────┘  └──────────────┴───────────┘    │
                                                          │
                                     ┌────────────────────┘
                                     │
                            ┌────────┴────────┐
                            │ Section Header  │
                            │ "Records &      │
                            │ Actions" (11)   │
                            └────────┬────────┘
                                     │
                            ┌────────┴────────────────┐
                            │ Records (12)│ Actions   │
                            │ ⭐ Bench    │ [▶ Start] │
                            │ ⭐ Squat    │ [⚖ Log]  │
                            └─────────────┴───────────┘

Fixations: 12+
Path: Non-linear, bouncing between left and right columns
```

### 9.2 After (REP-007D)

```
                         ┌─────────────────────────────┐
                         │   HERO (1)                  │
                         │   Push Day · Week 3         │
                         │   8 ex · ~45 min            │
                         │   [Chest] [Shoulders] [Tri] │
                         │                             │
                         │   Ready for PR 🔥 · 87     │
                         │   Sleep slightly reduced    │
                         │                             │
                         │   [▶ Start Workout]          │
                         └─────────────┬───────────────┘
                                       │
                         ┌─────────────┴───────────────┐
                         │   COACH (2)                  │
                         │   "Bench press ready for    │
                         │    +5kg jump"               │
                         │   Based on RIR 1-2 trend    │
                         │                              │
                         │   ● 72.3→77.0kg · 4.7 to go │
                         │   ● 5-day streak            │
                         │   ⭐ Bench PR in ~2wks 82%  │
                         └─────────────────────────────┘

Fixations: 2
Path: Linear, top-to-bottom
```

### 9.3 Eye Movement Rules

| Rule | Before | After |
|------|--------|-------|
| Saccades to find workout | 3-4 (greeting→subtitle→rings→mission) | 1 (hero) |
| Saccades to find readiness | 3-5 (rings→metrics→recovery card) | 1 (hero line) |
| Saccades to find progress | 5-7 (scroll past 4 sections) | 2 (hero→coach) |
| Horizontal saccades | 6+ (left-right column scanning) | 0 (single column) |
| Vertical saccades | Scroll past 8 sections | 0-1 (hero visible + coach starts) |
| Section header fixations | 5 (wasted) | 0 |

---

## 10. User Decision Map

### 10.1 The Four-Decision Flow

```
OPEN GYMOS
     │
     ▼
┌──────────────────────────────────────────────────────────┐
│  DECISION 1: TRAINING IDENTITY                           │
│  "What am I training today?"                             │
│                                                          │
│  Visual: Hero top line                                   │
│  Input: today_workout_name + mesocycle_week              │
│  Output: "Push Day · Week 3"                             │
│  Time: <1 second                                         │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│  DECISION 2: READINESS CHECK                             │
│  "Am I recovered enough to train?"                       │
│                                                          │
│  Visual: Hero recovery line                              │
│  Input: recovery_level + recovery_score                  │
│  Output: "Ready for PR 🔥 · Score: 87"                  │
│  Time: <1 second                                         │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
               ┌─────────────────────┐
               │  Am I ready?        │
               │  Decision gate      │
               ├──────────┬──────────┤
               │ YES      │ NO       │
               └────┬─────┴────┬─────┘
                    │           │
                    ▼           ▼
               START          ┌──────────────────────────────┐
               WORKOUT        │  DECISION 2B: ADJUSTMENT     │
                              │  "What should I change?"     │
                              │                              │
                              │  Input: recovery_suggested   │
                              │  action OR coach recommendation
                              │  Output: Modified plan       │
                              │  Time: <3 seconds            │
                              └──────────┬───────────────────┘
                                         │
                                         ▼
                                    START WORKOUT
                    (potentially modified — avoid failure sets,
                     reduce volume, take rest day)

     │
     ▼
┌──────────────────────────────────────────────────────────┐
│  DECISION 3: PROGRESS REVIEW                             │
│  "How am I doing overall?"                               │
│                                                          │
│  Visual: Coach progress line (below insight)             │
│  Input: goal_progress_weight + goal_progress_remaining   │
│         + current_streak                                 │
│  Output: "72.3→77.0 kg · 4.7 to go · ~8 wks · 5d streak"│
│  Time: <1 second                                         │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│  DECISION 4: ATTENTION CHECK                             │
│  "Anything I need to know?"                              │
│                                                          │
│  Visual: Coach insight (quoted text) + optional forecast │
│  Input: recommendations[0].title + .reason               │
│  Output: "Bench press ready for +5kg jump"              │
│  Optional: "⭐ Bench PR likely within 2 weeks (82%)"    │
│  Time: <1-2 seconds                                      │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
                    START WORKOUT
                    (informed, confident)
```

### 10.2 Timing Budget

| Decision | Time | Cumulative |
|----------|------|------------|
| 1: Training identity | 0.5s | 0.5s |
| 2: Readiness check | 0.8s | 1.3s |
| 3: Progress review | 1.0s | 2.3s |
| 4: Attention check | 1.5s | 3.8s |
| **Total** | **3.8s** | **<5s target ✓** |

### 10.3 Error Recovery

| Scenario | User Sees | Decision |
|----------|-----------|----------|
| No workout today | Hero shows empty state: "No training today — import a program or start free" | Import / Skip |
| No recovery data | Hero omits recovery line | Train normally |
| No coach insight | Coach section shows progress + streak only | Train normally |
| First-ever launch | Hero shows welcome + import CTA, Coach shows getting-started | Import / Free workout |

---

## 11. Cognitive Load Analysis

### 11.1 Measurement Framework

Cognitive load is measured across three dimensions:

| Dimension | Definition | Dashboard Metric |
|-----------|------------|-----------------|
| **Intrinsic** | Complexity inherent to the task | Number of decisions required |
| **Extraneous** | Complexity added by interface | Visual noise, duplicate info, unnecessary labels |
| **Germane** | Complexity that aids learning | Coach insights, progressive disclosure |

### 11.2 Per-Section Load

#### Hero (Before vs After)

| Load Factor | Before | After | Reduction |
|-------------|--------|-------|-----------|
| Elements | 14+ | 7 | 50% |
| Decisions required | 3 (identity + readiness + action) | 2 (identity + readiness) | 33% |
| Visual noise items | 4 (GoalRing, prediction quote, streak, Review btn) | 0 | 100% |
| Duplicate info | 2 (recovery ring + metric, CTA x3) | 0 | 100% |
| Section headers | 1 (implied) | 0 | 100% |
| **Estimated load** | **High** | **Low** | **~60% reduction** |

#### Coach (Before vs After)

| Load Factor | Before | After | Reduction |
|-------------|--------|-------|-----------|
| Cards in stack | 2 (expandable) | 1 (always visible) | 50% |
| Distinct sections merged | 3 (Coach + Predictions + Progress) | 1 | 66% |
| Data points shown | 10+ (2 recs + goal detail + timeline + PRs) | 5-6 | 45% |
| Interaction required | Expand/collapse toggle | None | 100% |
| **Estimated load** | **Medium-High** | **Low** | **~55% reduction** |

#### Overall Dashboard

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| Sections | 8 | 2 | ≤3 |
| Elements above fold | 14+ | 7 | ≤7 |
| Number of fixations | 12+ | 2 | ≤3 |
| Decisions required | 5+ | 4 | ≤4 |
| Unique data points | 22+ | 9 | ≤10 |
| Duplicate info instances | 3 | 0 | 0 |
| Wasted saccades (to section headers) | 5 | 0 | 0 |
| **Cognitive load estimate** | **High** | **Low** | **Low** |

### 11.3 The Five-Second Rule Test

| Test | Before | After |
|------|--------|-------|
| Find today's workout | 3-4 fixations, ~2s | 1 fixation, <0.5s |
| Find recovery status | 3-5 fixations, ~2.5s | 1 fixation, <0.5s |
| Find primary action | 3 fixations (3 CTAs), ~1.5s | 1 fixation, <0.5s |
| Find progress | 5-7 fixations + scroll, ~4s | 2 fixations, ~1s |
| Find critical insight | 3-5 fixations, ~3s | 1-2 fixations, ~1.5s |
| **Total time to full understanding** | **~10-15s** | **~3-4s** |

---

## 12. Visual Weight Budget

### 12.1 Allocation Principle

Visual weight is allocated proportionally to decision importance:

| Priority | Decision | Visual Weight | Elements |
|----------|----------|---------------|----------|
| 1 | What am I training? | 35% | Workout name, exercises, muscles |
| 2 | Am I recovered? | 15% | Recovery line |
| 3 | What is the primary action? | 15% | Start Workout button |
| 4 | How am I progressing? | 20% | Progress + streak line |
| 5 | Anything critical? | 15% | Coach insight + forecast |

### 12.2 Visual Hierarchy

```
35% ┌──────────────────────────────────────────────┐
    │  Workout Identity (28px/700, primary)         │
    │  Exercises + duration + badges (body)         │
    ├──────────────────────────────────────────────┤
15% │  Recovery Status (h3, colored by level)       │
    ├──────────────────────────────────────────────┤
15% │  [▶ Start Workout — 52px gradient CTA]       │
    ├──────────────────────────────────────────────┤
20% │  Coach Insight (quoted, 16px/600, accent)     │
    │  Progress + streak (body, secondary)          │
    ├──────────────────────────────────────────────┤
15% │  PR forecast (conditional, caption, success)  │
    └──────────────────────────────────────────────┘
```

### 12.3 Typography Scale

| Element | Token | Size/Weight | Color |
|---------|-------|-------------|-------|
| Workout identity | `h2` | 28px/700 | `text_primary` |
| Exercise count | `body` | 14px/500 | `text_secondary` |
| Recovery narrative | `h3` | 20px/700 | dynamic (success/warning/error) |
| Score detail | `caption` | 12px/500 | `text_disabled` |
| CTA button | `body`/700 | 14px/700 | `#FFFFFF` |
| Coach title (quoted) | `body`/600 | 14px/600 | `primary` |
| Coach reason | `body` | 13px/500 | `text_secondary` |
| Progress line | `body` | 13px/500 | `text_secondary` |
| Streak | `caption` | 12px/500 | `text_disabled` |
| PR forecast | `caption`/600 | 12px/600 | `success` |

---

## 13. Empty State Strategy

### 13.1 Principles

- Every section must be presentable with zero data
- Empty states must educate, not apologize
- Empty states must provide a clear next action
- No "No data" text anywhere

### 13.2 Hero Empty States

| Missing Data | Display | Action |
|-------------|---------|--------|
| No active program | "Welcome to GymOS — import a program to get started" | Import Program button |
| No workout today | "Rest day — your next session is [Next Workout Name]" | View Week button |
| No recovery data | (Omit recovery line entirely) | — |

### 13.3 Coach Empty States

| Missing Data | Display | Action |
|-------------|---------|--------|
| No recommendations | "Coach insights appear after your first workout" | Start Workout (redirects to Hero CTA) |
| No goal data | (Omit progress line) | Set Goal button → Settings |
| No streak | (Omit streak line) | — |

### 13.4 Transition States

| State | Display |
|-------|---------|
| Loading | Skeleton placeholder for Hero text (pulsing 200ms) |
| Error | "Could not load today's data. Pull down to refresh." |
| Offline | Last synced: [timestamp]. Data may be stale. |

---

## 14. Motion & Transition Design

### 14.1 Philosophy

Every animation must answer "where did this come from?" and "where did it go?" — never decorative, always functional.

### 14.2 Section Entry

| Element | Animation | Duration | Easing |
|---------|-----------|----------|--------|
| Hero | Fade in + slide up (10px) | 200ms | OutCubic |
| Coach | Fade in (delayed 100ms) | 200ms | OutCubic |
| PR forecast | Fade in (delayed 150ms, conditional) | 150ms | OutCubic |

### 14.3 Data Update

| Data Change | Animation | Duration |
|-------------|-----------|----------|
| Workout name changes | Cross-fade (old fades, new fades in) | 200ms |
| Recovery score changes | Number count-up from previous to new | 300ms |
| Coach insight changes | Slide old out (100ms), slide new in (200ms) | 300ms total |
| Empty → populated | Content fades in | 200ms |

### 14.4 Reduced Motion

When `accessibility.reduced_motion` is enabled:
- All animations set to 0ms duration
- Sections appear immediately
- No slide or fade transitions

### 14.5 No Staggered Animations

All elements within a section animate simultaneously. Delays between sections are at most 100ms. The user should never perceive "loading" of individual elements.

---

## 15. Acceptance Criteria

### 15.1 Visual

- [ ] The Dashboard fits in approximately one viewport (no scrolling required to see all information)
- [ ] No section headers (labels like "Today's Mission" or "Coach" are removed; content is self-describing)
- [ ] No duplicate CTAs (only one "Start Workout" button on the page)
- [ ] Total elements above fold ≤ 7 (excluding the CTA button)
- [ ] No GoalRing, no metric cluster, no Review Week button in Hero
- [ ] Recovery displayed as a single line within Hero, not a separate card

### 15.2 Cognitive

- [ ] A first-time user can identify today's workout within 1 second
- [ ] A first-time user can identify recovery status within 1 second
- [ ] A first-time user can identify the primary CTA within 1 second
- [ ] Total time to full understanding ≤ 5 seconds (measured by user testing)
- [ ] Eye movement is linear (top-to-bottom, no horizontal bouncing)

### 15.3 Technical

- [ ] All 6 existing signals remain on `DashboardView` (even if some are no longer connected internally)
- [ ] `DashboardData` model is unchanged — no fields added or removed
- [ ] `DashboardController` is unchanged — no method signatures modified
- [ ] `DashboardDataService` is unchanged — no queries modified
- [ ] No new dependencies introduced
- [ ] All existing 3373+ tests pass
- [ ] No production code (domain, application, infrastructure) modified

### 15.4 Regression Prevention

- [ ] Records page still shows PRs (data not lost, just relocated)
- [ ] Command palette still offers all Quick Actions (Log Weight, Import, etc.)
- [ ] Review Week is still accessible via sidebar → Progress page
- [ ] Goal ring still exists on the Goal/Progress page
- [ ] Weekly timeline still exists on the Progress page
- [ ] `start_workout_clicked` signal is emitted from the single hero CTA
- [ ] `view_all_prs_clicked` signal still works (for sidebar/⌘K callers)
- [ ] `weekly_review_clicked` signal still works (for sidebar/⌘K callers)
- [ ] `log_weight_clicked` signal still works (for sidebar/⌘K callers)
- [ ] `import_program_clicked` signal still works (for sidebar/⌘K callers)
- [ ] `view_recommendations_clicked` signal still works

---

*End of RFC-032*
