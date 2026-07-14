# RFC-039: Motion System 2.0

**Status:** IMPLEMENTATION  
**Priority:** CRITICAL  
**Dependencies:** RFC-034 (Design System 3.0), REP-007E (DS Consolidation)  
**Target:** `ui/design_system/motion/`

---

## Table of Contents

1. [Motion Philosophy](#1-motion-philosophy)
2. [Animation Inventory](#2-animation-inventory)
3. [Timing Table](#3-timing-table)
4. [Curve Table](#4-curve-table)
5. [ASCII Timing Diagrams](#5-ascii-timing-diagrams)
6. [Reduced Motion](#6-reduced-motion)
7. [Performance Rules](#7-performance-rules)
8. [Architecture](#8-architecture)
9. [Implementation Decisions](#9-implementation-decisions)

---

## 1. Motion Philosophy

### Principles

1. **Motion must communicate, not decorate.** Every animation answers a question:
   - "What changed?" → Opacity/duration signals importance
   - "Where did it go?" → Translate signals spatial relationship
   - "What can I interact with?" → Scale/press signals affordance
   - "What is happening?" → Progress draw signals computation

2. **The user should never notice animations.** They should only feel the application is alive. If a user says "nice animation," it's too prominent.

3. **One unified system.** No page invents its own animation. Every animation is a `MotionPreset` composed from `MotionTokens`.

4. **Reduced motion is not an afterthought.** Every animation has a zero-duration path. The switch is respected everywhere, no exceptions.

### Hierarchy Communication

| Duration | Meaning |
|----------|---------|
| 80ms | Instant feedback (button press, hover) |
| 140ms | Fast confirmation (toast, badge) |
| 220ms | Normal transition (standard reveal) |
| 320ms | Slow emphasis (hero, important state) |
| 450ms | Heroic entrance (achievement, milestone) |

### Curve Communication

| Curve | Feeling | Use Case |
|-------|---------|----------|
| OutCubic | Natural, calm | Most UI animations |
| InOutCubic | Professional, deliberate | Page transitions |
| OutQuart | Pronounced, premium | Hero reveals, achievements |
| Spring | Energetic, playful | Button release, feedback |
| Linear | Mechanical, precise | Progress bars, countdowns |

---

## 2. Animation Inventory

### Page-Level

| Animation | Preset | Duration | Curve |
|-----------|--------|----------|-------|
| Page enter | `fadeSlideIn` | 220ms | OutCubic |
| Page exit | `fadeOut` | 150ms | InOutCubic |
| Sidebar expand | `animateWidth` | 200ms | OutCubic |
| Sidebar collapse | `animateWidth` | 200ms | OutCubic |

### Card-Level

| Animation | Preset | Duration | Curve |
|-----------|--------|----------|-------|
| Card reveal (single) | `fadeSlideIn` | 200ms | OutCubic |
| Card reveal (list) | `staggerReveal` | 200ms each, 60ms stagger | OutCubic |
| Card hover | `hoverElevation` | 150ms | OutQuad |
| Card press | `pressScale` | 80ms / 120ms spring back | OutCubic |

### Component-Level

| Animation | Preset | Duration | Curve |
|-----------|--------|----------|-------|
| Button hover | `hoverBackground` | 150ms | OutQuad |
| Button press | `pressScale` (0.98) | 80ms | OutCubic |
| Dialog enter | `dialogEnter` (fade + scale 0.96→1.0) | 220ms | OutCubic |
| Backdrop fade | `fadeIn` | 220ms | Linear |
| Toast enter | `slideFromRight` | 250ms | OutCubic |
| Toast exit | `fadeOut` | 200ms | InOutCubic |

### Data-Level

| Animation | Preset | Duration | Curve |
|-----------|--------|----------|-------|
| Count up | `countUp` | 300ms | OutCubic |
| Progress bar fill | `fillBar` | 250ms | OutCubic |
| Chart draw | `chartDraw` | 400ms | OutQuart |
| Timeline reveal | `timelineReveal` | 300ms | OutCubic |

### Feedback-Level

| Animation | Preset | Duration | Curve |
|-----------|--------|----------|-------|
| Achievement glow | `achievementGlow` | 450ms | OutQuart |
| Achievement scale | `scaleIn` | 300ms | Spring |
| Rest timer pulse | `pulse` | 1000ms (last 10s only) | InOutSine |
| Coach fade | `fadeIn` | 200ms | OutCubic |
| Empty state | `fadeIn` | 200ms | OutCubic |

---

## 3. Timing Table

| Token | Value (ms) | Visual Intent |
|-------|-----------|---------------|
| `instant` | 80 | Button press, hover tint |
| `fast` | 140 | Badge update, toast |
| `normal` | 220 | Standard card reveal, page enter |
| `slow` | 320 | Hero reveal, important state |
| `hero` | 450 | Achievement, milestone |

| Stagger Token | Value (ms) | Use |
|---------------|-----------|-----|
| `stagger_fast` | 40 | Dense lists |
| `stagger_normal` | 60 | Card grids |
| `stagger_slow` | 100 | Hero sections |

| Delay Token | Value (ms) | Use |
|-------------|-----------|-----|
| `delay_none` | 0 | Immediate |
| `delay_short` | 50 | Sequential start |
| `delay_medium` | 100 | Sequential mid |
| `delay_long` | 200 | Sequential end |

---

## 4. Curve Table

| Curve Name | Control Points | QEasingCurve Type | Feeling |
|------------|---------------|-------------------|---------|
| Linear | (0,0)→(1,1) | `Linear` | Mechanical |
| OutQuad | (0.25,0.46)→(0.45,0.94) | `OutQuad` | Gentle |
| OutCubic | (0.215,0.61)→(0.355,1) | `OutCubic` | Natural |
| InOutCubic | (0.645,0.045)→(0.355,1) | `InOutCubic` | Deliberate |
| OutQuart | (0.165,0.84)→(0.44,1) | `OutQuart` | Pronounced |
| OutQuint | (0.23,1)→(0.32,1) | `OutQuint` | Dramatic |
| OutBounce | Bounce formula | `OutBounce` | Playful |
| InOutSine | (0.37,0)→(0.63,1) | `InOutSine` | Smooth |

### Visual Curve Shapes

```
Linear            OutCubic          InOutCubic
  1|─ ─ ─ ─ ─      1|   ╱            1|     ╱╲
   |               |  ╱              |   ╱    ╲
   |               | ╱               |  ╱      ╲
   |               |╱                | ╱        ╲
  0|─ ─ ─ ─ ─      0|─ ─ ─ ─ ─      0|─ ─ ─ ─ ─
   0      1        0      1         0      1

OutQuart          Spring            OutBounce
  1|  ╱             1|  ╱╲            1|  ╱╲  ╱╲
   | ╱              | ╱  ╲           | ╱  ╲╱  ╲╲
   |╱               |╱    ╲          |╱         ╲╲
  0|─ ─ ─ ─ ─      0|─ ─ ─ ─ ─      0|─ ─ ─ ─ ─ ─
```

---

## 5. ASCII Timing Diagrams

### Stagger Reveal (3 cards)

```
Time (ms):   0    60    120    180    240    300
Card 1:      [▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓]────────────
Card 2:      ──────[▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓]──────
Card 3:      ────────────[▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓]
```

### Page Transition

```
Time (ms):   0     75     150     225     300     375
Old Page:    [▓▓▓▓▓▓▓▓▓▓]──────────────────────────
Midpoint:    ──────────────◆────────────────────────
New Page:    ───────────────────[▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓]
```

### Dialog Enter

```
Time (ms):   0     55     110     165     220
Backdrop:    [▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓]────────────────
Dialog:      ─────[▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓]
```

### Button Press

```
Time (ms):   0     40      80     120     160     200
Press:       [▓▓▓▓▓▓▓▓]────────────────────────────
Release:     ──────────[▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓]
             scale 0.98  └──spring back──┘
```

---

## 6. Reduced Motion

### Global Switch

One switch (`AccessibilityManager.reduced_motion`) controls everything.

When enabled:
- All durations → 0ms (instant)
- All delays → 0ms
- All stagger → 0ms
- All curves → Linear (unused, since duration is 0)
- All loops → 1 iteration
- All opacity effects removed immediately
- `QGraphicsOpacityEffect` never applied

### Implementation

```python
class MotionAccessibility(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._reduced = False
        self._widgets: list[QWidget] = []

    @property
    def reduced(self) -> bool:
        return self._reduced

    def enable(self) -> None:
        self._reduced = True
        for w in self._reduced_widgets:
            if hasattr(w, 'set_reduced_motion'):
                w.set_reduced_motion(True)

    def register(self, widget: QWidget) -> None:
        self._reduced_widgets.append(widget)
```

### No-Animation Path

Every `MotionManager` method has this pattern:
```python
def fade_in(self, widget, duration=220):
    if self.accessibility.reduced:
        return  # skip entirely
    # ... create animation
```

This means zero overhead when reduced motion is enabled — no effects created, no timers started.

---

## 7. Performance Rules

### Hard Rules

1. **60 FPS target.** Any animation that drops below 55 FPS on reference hardware must be optimized or removed.

2. **No layout thrashing.** Never animate `geometry` when `pos` + `size` would suffice. Never trigger layout reflow during animation.

3. **No nested animations on the same widget.** Two `QPropertyAnimation` objects animating different properties of the same widget is acceptable. Two animations animating the same property will conflict.

4. **No blocking repaint.** `QPropertyAnimation` runs on the UI thread. Keep all animations lightweight. Heavy computation during animation → move to worker thread.

5. **`DeleteWhenStopped` always.** Every animation must set `DeleteWhenStopped` to avoid memory leaks from forgotten handles.

### Soft Rules

6. **Max 3 concurrent opacity animations.** `QGraphicsOpacityEffect` forces software rendering on the affected widget and its children. More than 3 concurrent opacity effects will drop FPS.

7. **Stagger limit: 12 items.** Beyond 12, the stagger delay makes the reveal feel slow. Batch into groups of 6-8.

8. **Sidebar width animation: 200ms max.** Longer feels sluggish to users who frequently expand/collapse.

---

## 8. Architecture

```
┌─────────────────────────────────────────────────────┐
│                   MotionTokens                       │
│  Duration: instant(80), fast(140), normal(220),      │
│            slow(320), hero(450)                      │
│  Curves: OutCubic, InOutCubic, OutQuart, Spring...  │
│  Stagger: fast(40), normal(60), slow(100)            │
└──────────────────────┬──────────────────────────────┘
                       │ used by
         ┌─────────────┼──────────────┐
         ▼             ▼              ▼
┌──────────────┐ ┌────────────┐ ┌──────────────┐
│AnimationFactory│ │MotionPresets│ │TransitionMgr│
│ - from_tokens │ │ - fadeIn   │ │ - transition │
│ - create_opacity│ │ - slideUp  │ │ - replace    │
│ - create_translate│ │ - stagger  │ │ - crossfade │
└──────┬───────┘ └─────┬──────┘ └──────┬───────┘
       │                │               │
       └────────────────┼───────────────┘
                        ▼
               ┌────────────────┐
               │  MotionManager  │
               │ - compose       │
               │ - orchestrate    │
               │ - stop_all      │
               │ - reduced       │
               └────────────────┘
                        │
               ┌────────┴────────┐
               ▼                 ▼
        ┌────────────┐   ┌──────────────┐
        │  Pages     │   │MotionAccess.│
        │ (consumers)│   │ (reduced)   │
        └────────────┘   └──────────────┘
```

---

## 9. Implementation Decisions

### Decision 1: MotionTokens are QEasingCurve-based, not CSS-string-based

The existing `ui/design_system/tokens/motion.py` contains CSS-style strings (e.g., `"cubic-bezier(0.42, 0, 0.58, 1)"`). These are useless for `QPropertyAnimation`. The new tokens expose actual `QEasingCurve.Type` values plus int durations.

### Decision 2: MotionManager wraps AnimationManager

Rather than replacing `ui/experience/animation_manager.py` (which has test coverage), the new `MotionManager` wraps it and adds high-level presets, orchestration, and reduced-motion integration.

### Decision 3: AnimationFactory is stateless

`AnimationFactory` is a collection of `@staticmethod` methods. It takes tokens and returns configured `QPropertyAnimation` objects. No state, no side effects.

### Decision 4: TransitionManager handles crossfade

Page transitions use `MotionService.transition_page()` under the hood. `TransitionManager` provides a simplified API with sensible defaults.

### Decision 5: MotionAccessibility is a thin adapter

It wraps `AccessibilityManager.reduced_motion` and provides a consistent API for all motion components. It does not duplicate the widget registration logic from `AccessibilityManager`.

### Decision 6: All new files are in `ui/design_system/motion/`

This places motion alongside the other design system tokens (color, spacing, typography, radius, shadow). It's importable as `from ui.design_system.motion import MotionManager, fadeIn`.
