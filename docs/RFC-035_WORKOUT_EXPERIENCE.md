# RFC-035: Workout Experience 2.0 — Premium Coaching Interface

**Status:** IMPLEMENTATION  
**Priority:** CRITICAL  
**Author:** Design System Team  
**Date:** 2026-07-14  
**Depends on:** RFC-034 (Design System 3.0)  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [User Journey](#2-user-journey)
3. [Workout Flow](#3-workout-flow)
4. [Information Hierarchy](#4-information-hierarchy)
5. [ASCII Wireframes](#5-ascii-wireframes)
6. [Interaction Map](#6-interaction-map)
7. [Motion Map](#7-motion-map)
8. [Component Tree](#8-component-tree)
9. [State Machine](#9-state-machine)
10. [Implementation Decisions](#10-implementation-decisions)
11. [Verification Checklist](#11-verification-checklist)

---

## 1. Executive Summary

The Workout Experience is GymOS's most critical screen. Users spend the majority of their session here. The current implementation presents exercises as a vertical form with spreadsheet-like weight × reps inputs. REP-007F replaces this with a premiere coaching interface that answers four questions at every moment:

| Question | Answer Location |
|----------|----------------|
| What exercise am I doing? | Hero + Exercise Card (dominant) |
| How many sets remain? | Set Timeline + Journey |
| How am I performing? | Coach narrative + Previous comparison |
| What should I do next? | Recommendation + Next Exercise preview |

### Design Principles

1. **Answers, not forms** — Every element answers a user question
2. **Timeline, not spreadsheet** — Sets are visualized as progress blocks
3. **Coach, not database** — Narrative language replaces raw numbers
4. **Motion with purpose** — 100ms for set completion, 220ms for transitions, pulse only when needed
5. **Keyboard-first** — Tab, Enter, Space, Arrow. Mouse optional.

### Preserved API

| Element | Status |
|---------|--------|
| `workout_saved` signal | ✅ Identical |
| `back_clicked` signal | ✅ Identical |
| `load_day(day_name)` method | ✅ Identical |
| `_finish_workout()` internal | ✅ Same logic path |
| `WorkoutSession` domain model | ✅ Unchanged |
| `PREngine.detect_prs()` | ✅ Unchanged |
| `RecoveryEngine.analyse_session()` | ✅ Unchanged |
| `ProgressionEngine` | ✅ Unchanged |
| `GymDatabase.save_session()` | ✅ Unchanged |

---

## 2. User Journey

### 2.1 Main Flow

```
Workout Selection → Select Day → Workout View → Complete Sets → Finish → Summary
```

### 2.2 Detailed Steps

**Step 1: Workout Selection** (unchanged — already redesigned in earlier sprint)
- User sees editorial-quality day cards
- Selects a training day

**Step 2: Workout Hero** (new)
- Workout name displayed prominently
- Elapsed timer starts immediately
- Current exercise highlighted
- Progress shown as journey (not ring)
- Finish Workout CTA available at all times

**Step 3: Exercise Focus** (new)
- Current exercise card is large, dominant
- Set timeline shows completed (green), current (highlighted), future (subdued)
- Rest timer appears after each set
- Coach appears if relevant

**Step 4: Exercise Transition** (new)
- Previous exercise shrinks
- Next exercise expands
- Coached narrative: "Great work on bench press. Next up: Incline Dumbbell Press."

**Step 5: Completion** (unchanged logic, new presentation)
- Session saved via GymDatabase
- PRs detected via PREngine
- Recovery analysed via RecoveryEngine
- Summary dialog shown with results

### 2.3 Exit Points

| Action | Behavior |
|--------|----------|
| Finish Workout (CTA) | Save, detect PRs, show summary → return to dashboard |
| Back button | Confirm exit dialog (unsaved data warning) |
| App quit during workout | Workout saved as incomplete in database |

---

## 3. Workout Flow

```
[LOAD DAY]
    │
    ├── Start timer
    ├── Build exercise cards (all exercises pre-loaded)
    ├── Set first exercise as active
    └── Show empty rest timer ("Ready")
    
[EXERCISE LOOP]
    │
    ├── Show exercise card (large, dominant)
    ├── Show set timeline (completed/current/future)
    ├── Show Coach (if relevant)
    │
    ├── [COMPLETE SET]
    │   ├── Record weight × reps × RIR
    │   ├── Play completion animation (100ms)
    │   ├── Advance set timeline block
    │   ├── Start rest timer
    │   └── Show Coach (if relevant)
    │
    ├── [REST TIMER]
    │   ├── Ready (green) → Resting (orange) → Overdue (red, pulse)
    │   ├── Auto-advance after 90s or tap
    │   └── Coach: "Ready for next set"
    │
    ├── [EXERCISE COMPLETE]
    │   ├── Play transition animation (220ms)
    │   ├── Shrink completed exercise
    │   ├── Expand next exercise
    │   └── Coach: "Moving to next exercise"
    │
    └── [ALL EXERCISES COMPLETE]
        └── Show "Workout Complete" state → trigger finish
    
[FINISH]
    ├── Save session
    ├── Detect PRs
    ├── Analyse recovery
    ├── Show summary dialog
    └── Emit workout_saved signal
```

---

## 4. Information Hierarchy

### 4.1 Visual Priority (top to bottom)

```
1. Workout Hero (Viewport anchor)
   ├── Workout name
   ├── Current exercise name (large, bold)
   ├── Elapsed time
   ├── Overall journey progress
   ├── Muscle group tag
   └── Finish Workout CTA

2. Exercise Card (Primary focus area)
   ├── Exercise name (hero typography)
   ├── Previous performance (subdued reference)
   ├── Target information (reps, weight suggestion)
   ├── Set timeline (visual blocks)
   └── Coach message (contextual)

3. Rest Timer (When active — temporary overlay)
   ├── Timer value (large, central)
   ├── Status: Ready / Resting / Overdue (color-coded)
   └── Tap-to-skip

4. Next Exercise (Preview, not dominant)
   ├── Exercise name
   └── Muscle group

5. Workout Journey (Persistent mini-progress)
   ├── Exercise dots with completion states
   └── Current position indicator
```

---

## 5. ASCII Wireframes

### 5.1 Main Layout

```
┌──────────────────────────────────────────────────────────────┐
│ [WORKOUT HERO]                                                │
│                                                              │
│  Push Day A                        ⏱ 12:34                   │
│                                                              │
│  Barbell Bench Press                                         │
│  ──────────────────                                          │
│  Chest                3 of 10 sets  ████████░░ 80%           │
│                                                              │
│  [Finish Workout]                          Journey: ● ● ○ ○ │
├──────────────────────────────────────────────────────────────┤
│ [EXERCISE CARD]                                               │
│                                                              │
│  ╔══════════════════════════════════════════════════════════╗ │
│  ║  BARBELL BENCH PRESS                        ⚡ PR +5kg  ║ │
│  ║                                                          ║ │
│  ║  Last session:  3 sets × 80kg × 8 reps  RIR 1           ║ │
│  ║  Target:        82.5kg × 6-8 reps                        ║ │
│  ║                                                          ║ │
│  ║  Coach: "Increase weight by 2.5kg. Last session looked   ║ │
│  ║         comfortable — you had more in the tank."          ║ │
│  ║                                                          ║ │
│  ║  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐           ║ │
│  ║  │  1   │ │  2   │ │  3   │ │  4   │ │  5   │           ║ │
│  ║  │80×8  │ │80×8  │ │80×7  │ │  —   │ │  —   │           ║ │
│  ║  │ RIR1 │ │ RIR2 │ │ RIR2 │ │      │ │      │           ║ │
│  ║  │ DONE✓│ │ DONE✓│ │ DONE✓│ │ NEXT │ │      │           ║ │
│  ║  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘           ║ │
│  ║                                                          ║ │
│  ║  ╔══════════════════════════════════════╗                 ║ │
│  ║  ║         02:45                        ║                 ║ │
│  ║  ║         RESTING                      ║                 ║ │
│  ║  ║    [tab to skip]                     ║                 ║ │
│  ║  ╚══════════════════════════════════════╝                 ║ │
│  ╚══════════════════════════════════════════════════════════╝ │
│                                                              │
│ [NEXT EXERCISE]                                               │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  Next: Incline Dumbbell Press  ·  Chest (Shoulders)  │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

### 5.2 Rest Timer States

```
READY:          ╔══════════════════╗
                ║    READY         ║  ← Green background
                ║    00:00         ║
                ╚══════════════════╝

RESTING:        ╔══════════════════╗
                ║    RESTING       ║  ← Orange background
                ║    01:30         ║
                ╚══════════════════╝

OVERDUE:        ╔══════════════════╗
                ║    OVERDUE    ⚡  ║  ← Red background, pulse
                ║    03:00         ║
                ╚══════════════════╝
```

### 5.3 Empty States

```
NO WORKOUT:     ╔══════════════════════════════════╗
                ║    No active workout             ║
                ║    Select a workout day to       ║
                ║    begin your training session.  ║
                ║                                  ║
                ║    [Select Workout]               ║
                ╚══════════════════════════════════╝

COMPLETED:      ╔══════════════════════════════════╗
                ║    🎉 Workout Complete!          ║
                ║    Duration: 45 min              ║
                ║    Volume: 12,450 kg             ║
                ║                                  ║
                ║    [View Summary]                ║
                ╚══════════════════════════════════╝

PAUSED:         ╔══════════════════════════════════╗
                ║    WORKOUT PAUSED               ║
                ║                                  ║
                ║    ⏸ Elapsed: 15:23              ║
                ║                                  ║
                ║    [Resume]    [Finish & Save]    ║
                ╚══════════════════════════════════╝
```

---

## 6. Interaction Map

### 6.1 Keyboard Bindings

| Key | Context | Action |
|-----|---------|--------|
| `Tab` | Any | Move to next interactive element |
| `Shift+Tab` | Any | Move to previous interactive element |
| `Enter` | Set block (current) | Complete set, record data |
| `Enter` | Rest timer | Skip rest, start next set |
| `Space` | Set block (current) | Complete set (same as Enter) |
| `Space` | Rest timer | Skip rest |
| `Escape` | Any | Show pause/quit dialog |
| `→` | Exercise card | Quick-complete with previous weight/reps |
| `←` | After set complete | Undo last set (within 5 seconds) |

### 6.2 Signal Flow

```
User Action → Widget Interaction → Signal Emission → WorkoutView Handler
                                                      ↓
                                              Business Logic (unchanged)
                                                      ↓
                                              Database Write (unchanged)
                                                      ↓
                                              UI Update + Coach Feedback
```

### 6.3 Tab Order

```
Finish CTA Button
  ↓
Set Timeline Block 1 (Set 4 — current)
  ↓
Weight Input
  ↓
Reps Input
  ↓
RIR Dropdown
  ↓
Confirm Set Button
  ↓
Rest Timer (if active)
  ↓
Set Timeline Block 2 (Set 5 — next)
  ...
  ↓
Next Exercise Preview
```

---

## 7. Motion Map

### 7.1 Timing

| Trigger | Duration | Curve | Element |
|---------|----------|-------|---------|
| Set completion | 100ms | Ease Out | Set block fills, status → DONE |
| Exercise transition | 220ms | Ease In Out | Card shrink/expand |
| Rest timer update | 16ms | Linear | Timer number updates |
| Rest timer overdue pulse | 600ms (period) | Ease In Out | Border glow opacity |
| Coach appearance | 150ms | Ease Out | Fade in + slide up |
| Journey progress | 200ms | Ease Out | Dot fill animation |
| Exercise card focus | 200ms | Ease Out | Scale/border emphasis |

### 7.2 Reduced Motion

When `_reduced_motion` is enabled:
- All animations skip to end state
- Transitions are instant
- Pulse effects disabled
- Timer still updates every second

---

## 8. Component Tree

```
WorkoutView (QWidget)
├── WorkoutHero (QFrame)
│   ├── WorkoutName (QLabel) — h2 style
│   ├── CurrentExerciseName (QLabel) — hero style
│   ├── ElapsedTime (QLabel) — body style
│   ├── MuscleGroupBadge (StatusBadge)
│   ├── JourneyProgress (QFrame — painted dots)
│   └── FinishButton (QPushButton — success styled)
│
├── WorkoutContent (QScrollArea)
│   ├── ExerciseCard (QFrame)
│   │   ├── CardHeader
│   │   │   ├── ExerciseName (QLabel) — hero typography
│   │   │   └── PRBadge (StatusBadge) — if applicable
│   │   ├── PreviousPerformance (QLabel) — subdued
│   │   ├── TargetInfo (QLabel)
│   │   ├── CoachMessage (QLabel) — narrative, contextual
│   │   ├── SetTimeline (QFrame)
│   │   │   └── SetBlock[] (QFrame × target_sets)
│   │   │       ├── SetNumber (QLabel)
│   │   │       ├── WeightInput (QLineEdit)
│   │   │       ├── RepsInput (QLineEdit)
│   │   │       ├── RIRInput (QLineEdit)
│   │   │       └── StatusIndicator (QLabel) — DONE/NEXT/—
│   │   └── RestTimer (QFrame)
│   │       ├── TimerLabel (QLabel) — large
│   │       ├── StatusLabel (QLabel) — READY / RESTING / OVERDUE
│   │       └── SkipButton (QPushButton)
│   │
│   └── NextExercisePreview (QFrame)
│       ├── Icon (QLabel)
│       ├── ExerciseName (QLabel)
│       └── MuscleGroup (QLabel)
│
├── EmptyStateWidget (QFrame) — shown when no workout loaded
└── PausedOverlay (QFrame) — shown when Escape pressed
```

### 8.1 Canonical Components Used

| Component | Source | Usage |
|-----------|--------|-------|
| `QFrame` | Qt | All containers |
| `QLabel` | Qt | All text |
| `QLineEdit` | Qt | Weight, reps, RIR inputs |
| `QPushButton` | Qt | Actions |
| `QScrollArea` | Qt | Content scrolling |
| `QTimer` | Qt | Elapsed + rest timer |
| `StatusBadge` | design_system | Muscle group tags, PR badges |
| `SectionHeader` | design_system | Exercise transition headers |
| `EmptyState` | design_system | No workout state |
| `DialogTemplate` | design_system | Pause/quit confirm dialogs |
| `font_style()` | tokens | All typography |
| `color_from_scheme()` | tokens | All colors |
| `SpacingTokens` | tokens | All spacing |
| `RadiusTokens` | tokens | All border radii |

### 8.2 Components NOT Used (removed)

| Removed Component | Reason |
|-------------------|--------|
| `ProgressRing` | Deprecated in RFC-034 |
| `SetRow` class | Replaced by SetBlock timeline blocks |
| `ExerciseCard` class (old) | Replaced by new ExerciseCard with timeline |
| `WorkoutSummaryDialog` class (old) | Simplified to use DialogTemplate |

---

## 9. State Machine

```
                  ┌─────────────┐
                  │   EMPTY     │
                  │  (no day)   │
                  └──────┬──────┘
                         │ load_day()
                         ▼
                  ┌─────────────┐
          ┌──────►│  RESTING    │◄────────────┐
          │       │ (post-set)  │              │
          │       └──────┬──────┘              │
          │              │ skip/timer          │
          │              ▼                     │
          │       ┌─────────────┐              │
          │       │   ACTIVE    │──────────────┘
          │       │ (set ready) │  complete_set()
          │       └──────┬──────┘
          │              │ set_complete
          │              ▼
          │       ┌─────────────┐
          │       │ TRANSITION  │
          │       │ (exercise)  │
          │       └──────┬──────┘
          │              │ all sets complete?
          │              ├──────────────┐
          │              │ yes          │ no
          │              ▼              ▼
          │       ┌─────────────┐  ┌──────────┐
          │       │  COMPLETED  │  │ NEXT EX  │──► RESTING
          │       │ (all done)  │  └──────────┘
          │       └──────┬──────┘
          │              │ finish
          │              ▼
          │       ┌─────────────┐
          │       │  SAVING     │
          │       │ (PR check)  │
          │       └──────┬──────┘
          │              │ done
          │              ▼
          │       ┌─────────────┐
          └───────│  SUMMARY    │──► exit
                  └─────────────┘
```

---

## 10. Implementation Decisions

### 10.1 Architecture

The workout view is a **stateless presentation layer** built on top of unchanged domain logic:

```
WorkoutView (presentation)
    │
    ├── load_day(day_name) → builds UI from program data
    ├── _finish_workout() → orchestrates save + PR + recovery
    │
    ├── Uses: ProgressionEngine (unchanged)
    ├── Uses: PREngine (unchanged)
    ├── Uses: RecoveryEngine (unchanged)
    ├── Uses: GymDatabase (unchanged)
    │
    ├── Emits: workout_saved (unchanged signal)
    └── Emits: back_clicked (unchanged signal)
```

### 10.2 Set Representation

Sets are **timeline blocks**, not form rows. Each block shows:
- Set number (circular indicator)
- Status: DONE (green fill), CURRENT (purple border + pulse), FUTURE (subdued)
- Data: weight × reps on hover or when active
- RIR: shown as badge when relevant

When a set block is the current/focus, it expands to show inputs inline.
Completed sets show a summary: "80kg × 8 reps · RIR 1"

### 10.3 Rest Timer

- Starts automatically after set completion
- Shows in the exercise card as a prominent box
- Counts up from 0 to 90s (configurable)
- Color transitions: green → orange → red
- Overdue state pulses border
- Enter/Space to skip
- Timer continues even when switching exercises (shown in mini form in hero)

### 10.4 Coach Messages

Coach messages are generated from existing recommendations:
- `ProgressionEngine.get_recommendation()` → narrative text
- Previous performance comparison → "Last session 80kg × 8. You're on track."
- RIR feedback → "RIR 2 is solid. Try RIR 0 on last set."
- Rest timer → "Ready when you are." / "Take another 30s."

### 10.5 Journey Progress

Displayed as horizontal dots in the hero:
- Each dot = one set across all exercises
- Color: completed (green), current (purple), future (subdued)
- Labels: exercise name under first dot of each exercise group
- Scaled to fit available width (max ~20 dots visible)

### 10.6 Save and Finish

Identical logic to current implementation:
```
1. Collect all set data from current exercise state
2. Build WorkoutSession domain object
3. Call db.save_session(session)
4. Call PREngine.detect_prs(saved_session)
5. Call RecoveryEngine.analyse_session(saved_session)
6. Call ProgressionEngine.analyse_exercise() for each exercise
7. Show summary dialog (DialogTemplate-based)
8. Emit workout_saved signal
```

---

## 11. Verification Checklist

- [ ] `workout_saved` signal fires after finish
- [ ] `back_clicked` signal fires from back button
- [ ] `load_day(day_name)` creates correct exercise cards
- [ ] Set timeline shows correct number of blocks per exercise
- [ ] Weight × reps × RIR data saves correctly
- [ ] Rest timer starts/stops/skips correctly
- [ ] Finish calls `db.save_session()`
- [ ] Finish detects PRs via `PREngine`
- [ ] Finish analyses recovery via `RecoveryEngine`
- [ ] Summary dialog shows PRs, recommendations, recovery flags
- [ ] Compilation passes with no errors
- [ ] No custom widget classes defined (all canonical components)
- [ ] No hardcoded color/typography/spacing values (all tokens)
- [ ] Keyboard navigation works: Tab, Enter, Space, Escape
- [ ] Empty states display correctly
