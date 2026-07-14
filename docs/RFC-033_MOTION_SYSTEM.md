# RFC-033: Motion System 2.0

- **Status**: Draft
- **Phase**: REP-007E
- **Author**: Product Engineering
- **Created**: 2026-07-14
- **Area**: Experience Layer

---

## 1. Objective

Define and implement a unified motion system for GymOS that replaces ad-hoc `_fade_in()` copy-paste patterns with a centralized `MotionService`, enforces strict timing/easing constraints (<300ms, OutCubic/InOutCubic only), and bakes `prefers_reduced_motion` into every animated interaction.

---

## 2. Motion Principles

1. **Purposeful** — every animation communicates hierarchy, state change, or spatial relationship. No decorative motion.
2. **Fast** — no animation exceeds 300ms. Instant feedback (100–150ms) for micro-interactions, 200–300ms for transitions.
3. **Subtle** — fade-only for reduced motion; no bounce, elastic, spring, or back easing curves.
4. **Choreographed** — card reveals use top-to-bottom stagger (60–80ms delay). Simultaneous fades feel cohesive.
5. **Accessible** — `MotionService` checks `AccessibilityManager.reduced_motion` before every animation and falls back to fade (100ms, OutCubic) when enabled.

---

## 3. Timing Table

| Token         | ms    | Usage                              |
|---------------|-------|------------------------------------|
| Instant       | 0     | State flips, no animation needed   |
| Fast          | 100   | Button press, checkbox toggle, hover elevation |
| Normal        | 200   | Card reveal, page transition (fade), sidebar collapse |
| Slow          | 300   | Chart draw-in, notification slide, dialog appear |

**Rule**: All durations ≤ 300ms. Never exceed Slow token.

---

## 4. Easing Table

| Curve       | QEasingCurve              | Usage                              |
|-------------|---------------------------|------------------------------------|
| OutCubic    | `Type.OutCubic`           | Enter: fade in, slide in, scale in |
| InOutCubic  | `Type.InOutCubic`         | Exit: fade out, slide out          |
| OutQuart    | `Type.OutQuart`           | Chart draw-in, progress bars       |

**Rule**: Only OutCubic, InOutCubic, OutQuart. No bounce, elastic, spring, or back.

---

## 5. Animation Inventory

### 5.1 Page Transitions (AppShell)

| Trigger       | Animation              | Duration | Easing      |
|---------------|------------------------|----------|-------------|
| `switch_to()` | Old page fade out      | 150ms    | InOutCubic  |
|               | New page fade in       | 200ms    | OutCubic    |
| Reduced       | Instant swap           | 0ms      | —           |

No slide offset — content changes are contextual enough that slide would feel disorienting.

### 5.2 Sidebar (ShellSidebar)

| Trigger              | Animation        | Duration | Easing    | Note                          |
|----------------------|------------------|----------|-----------|-------------------------------|
| Collapse/expand      | Width animate    | 200ms    | OutCubic  | 200px ↔ 56px                  |
| Button hover         | Background tint  | 100ms    | OutCubic  | 10% → 15% accent alpha        |
| Active indicator     | Position slide   | 200ms    | OutCubic  | Moves to active button        |
| Reduced              | Instant width    | 0ms      | —         | No width animation            |

### 5.3 Card Reveal (Dashboard, Workout)

| Element              | Animation         | Delay     | Duration | Easing    |
|----------------------|-------------------|-----------|----------|-----------|
| Hero card            | Fade in + slide up 8px | 0ms      | 220ms    | OutCubic  |
| Mission card         | Fade in + slide up 8px | 80ms     | 220ms    | OutCubic  |
| Recovery card        | Fade in + slide up 8px | 160ms    | 220ms    | OutCubic  |
| Coach card           | Fade in + slide up 8px | 240ms    | 220ms    | OutCubic  |
| Progress / others    | Fade in + slide up 8px | 320ms    | 220ms    | OutCubic  |
| Reduced              | Fade only         | 0–80ms   | 100ms    | OutCubic  |

### 5.4 Micro-interactions

| Element        | Trigger       | Animation              | Duration | Easing    |
|----------------|---------------|------------------------|----------|-----------|
| Button         | Press         | Scale 0.98             | 80ms     | OutCubic  |
| Button         | Release       | Scale 1.0              | 120ms    | OutCubic  |
| Card           | Hover enter   | Elevate + glow accent  | 150ms    | OutCubic  |
| Card           | Hover leave   | Restore                | 120ms    | OutCubic  |
| Metric value   | Update        | Count-up (label text)  | 300ms    | OutQuart  |
| Spinner        | Active        | Rotate                 | 800ms/loop| Linear  |

### 5.5 Command Bar (⌘K)

| Trigger         | Animation                    | Duration | Easing    |
|-----------------|------------------------------|----------|-----------|
| Open            | Scale 96% → 100% + fade in   | 200ms    | OutCubic  |
| Close           | Scale 100% → 96% + fade out  | 150ms    | InOutCubic|
| Reduced         | Fade only                    | 100ms    | OutCubic  |

### 5.6 Notifications (Toast)

| Trigger         | Animation                 | Duration | Easing    |
|-----------------|---------------------------|----------|-----------|
| Show            | Slide from top + fade in  | 250ms    | OutCubic  |
| Dismiss         | Fade out + slide up 8px   | 200ms    | InOutCubic|
| Reduced         | Fade only                 | 100ms    | OutCubic  |

### 5.7 Dialog

| Trigger         | Animation                  | Duration | Easing    |
|-----------------|---------------------------|----------|-----------|
| Show backdrop   | Fade in (overlay)         | 200ms    | OutCubic  |
| Show content    | Scale 95% → 100% + fade   | 250ms    | OutCubic  |
| Close           | Fade out + scale 95%      | 150ms    | InOutCubic|
| Reduced         | Fade only                 | 100ms    | OutCubic  |

### 5.8 Chart / Visualization

| Element              | Animation              | Duration | Easing    |
|----------------------|------------------------|----------|-----------|
| Line chart           | Progressive draw       | 300ms    | OutQuart  |
| Bar chart            | Grow from bottom       | 250ms    | OutQuart  |
| Ring / Radial        | Arc animate to target  | 300ms    | OutCubic  |
| Progress bar         | Width to target        | 250ms    | OutCubic  |
| Reduced              | Immediate draw         | 0ms      | —         |

---

## 6. Interaction Map

```
User taps Dashboard nav
  └─ AppShell._on_page_switch()
       ├─ (if reduced_motion) → instant stack index change
       └─ (else) → old page fade out (150ms, InOutCubic)
                 → switch stack index (mid-point)
                 → new page fade in + card stagger (200–320ms, OutCubic)

User collapses sidebar
  └─ ShellSidebar.toggle_collapse()
       └─ (if reduced_motion) → instant resize
       └─ (else) → QPropertyAnimation(width, 200ms, OutCubic)

User hovers a card
  └─ Card.enterEvent
       └─ (if reduced_motion) → no-op
       └─ (else) → elevation: raise 2px + accent glow (150ms, OutCubic)

User presses a button
  └─ Button.mousePressEvent
       └─ (if reduced_motion) → no-op
       └─ (else) → scale 0.98 (80ms, OutCubic) via transform

Data update triggers metric change
  └─ MetricCard.set_value()
       └─ (if reduced_motion) → text update only
       └─ (else) → count-up number sequence (300ms, OutQuart)

User opens command palette (⌘K)
  └─ CommandBar.show()
       └─ (if reduced_motion) → appear at 100% opacity
       └─ (else) → scale 96%→100% + fade in (200ms, OutCubic)

Notification appears
  └─ ToastManager.show()
       └─ (if reduced_motion) → appear at 100% opacity
       └─ (else) → slide -20px from top + fade in (250ms, OutCubic)
```

---

## 7. Motion Hierarchy

```
AppShell (page transitions)
 ├─ Stacked widget swap
 └─ Content area
      ├─ DashboardView (card stagger)
      ├─ WorkoutView (card stagger)
      ├─ CommandBar (scale+fade)
      ├─ NotificationToast (slide+fade)
      └─ DialogTemplate (scale+fade)

ShellSidebar (width transition)
 └─ Buttons (hover tint)

Any card container
 ├─ Card hover (elevation)
 ├─ Button press (scale)
 └─ Metric update (count-up)
```

---

## 8. Reduced-Motion Behavior

When `AccessibilityManager.reduced_motion` is `True`:

| Animation Type      | Fallback                         |
|---------------------|----------------------------------|
| Page transition     | Instant swap, no delay           |
| Card reveal         | Fade only (100ms, OutCubic)      |
| Sidebar collapse    | Instant width change             |
| Hover elevation     | No-op                            |
| Button press        | No-op                            |
| Scale/fade combo    | Fade only (100ms)                |
| Slide/fade combo    | Fade only (100ms)                |
| Chart draw-in       | Immediate draw                   |
| Notification        | Appear at full opacity           |
| Dialog              | Fade only (100ms)                |
| Count-up            | Update text immediately          |

All animations check `AccessibilityManager` at runtime. No code path plays a disallowed animation.

---

## 9. Implementation Roadmap

### Phase 1: Infrastructure (this PR)
| # | Task                          | Files                                      |
|---|-------------------------------|--------------------------------------------|
| 1 | Fix `AnimationManager.fade_in` | `ui/experience/animation_manager.py`       |
| 2 | Create `MotionService`         | `ui/experience/motion_service.py` (new)    |
| 3 | Reduce-motion binding          | `ui/experience/accessibility.py`           |

### Phase 2: Shell Animations (this PR)
| # | Task                          | Files                                      |
|---|-------------------------------|--------------------------------------------|
| 4 | Sidebar width animation        | `ui/shell/sidebar.py`                      |
| 5 | Page transition (fade)         | `ui/shell/app_shell.py`                    |
| 6 | Notification slide+fade        | `ui/shell/app_shell.py`                    |

### Phase 3: View Animations (this PR)
| # | Task                          | Files                                      |
|---|-------------------------------|--------------------------------------------|
| 7 | Card stagger via MotionService | `ui/dashboard/dashboard_view.py`           |
| 8 | Hover elevation on cards       | `ui/dashboard/dashboard_view.py`           |
| 9 | Button press scale             | `ui/dashboard/dashboard_view.py`           |
|10 | Metric count-up animation      | `ui/dashboard/dashboard_view.py`           |

### Phase 4: Cross-cutting Adoption (future PRs)
| # | Task                          | Files                                      |
|---|-------------------------------|--------------------------------------------|
|11 | WorkoutView card stagger       | `ui/workout_view.py`                       |
|12 | WelcomeWizard motion           | `ui/experience/welcome_wizard.py`          |
|13 | Chart progressive draw         | `ui/visualization/`                        |
|14 | CommandBar scale+fade          | `ui/design_system/components/command_bar.py`|
|15 | DialogTemplate scale+fade      | `ui/design_system/components/dialog_template.py`|
|16 | NotificationToast slide+fade   | `ui/design_system/components/notification_toast.py`|

---

## 10. Testing Strategy

- **Unit**: `MotionService` method calls with mocked `AccessibilityManager` to verify reduced-motion fallback
- **Integration**: Animation presence and stagger timing in dashboard card reveal
- **Regression**: All 3373+ existing tests pass with 0 regressions
- **Manual**: Toggle reduced motion in settings; verify no motion occurs for hover/press/transitions

---

## 11. Appendix: Current vs. Proposed

| Aspect            | Current (REP-007C)                          | Proposed (REP-007E)                         |
|-------------------|---------------------------------------------|---------------------------------------------|
| Fade pattern      | `_fade_in()` copy-pasted per view           | `MotionService.fade_in()` single source     |
| Fade mechanism    | `QGraphicsOpacityEffect` + `b"opacity"`     | Same (correct)                              |
| AnimationManager  | Uses `b"windowOpacity"` — broken for widgets| Fixed to `QGraphicsOpacityEffect` + `b"opacity"` |
| Reduced motion    | Not checked                                 | Checked at every animation start            |
| Sidebar animation | Instant resize                              | Width property animation (200ms)            |
| Page transition   | Instant swap                                | Fade out/in (150+200ms)                     |
| Hover effects     | None                                        | Elevation + glow (150ms)                    |
| Button press      | Instant state                               | Scale 0.98 (80ms)                           |
| Stagger delays    | 80ms hardcoded                              | Configurable via `stagger_delay` param      |
| Notification      | Instant appear                              | Slide + fade (250ms)                        |
| Command bar       | Instant appear                              | Scale + fade (200ms)                        |
