# GymOS — UI Guidelines

## Principles

1. **Gym-ready UI.** Large buttons, high contrast, readable from 2+ feet. The user is standing, possibly sweating, and needs to tap quickly between sets.
2. **Minimal taps to log.** Target: 2 taps to log a completed set. No scrolling, no typing required during workout.
3. **Dark mode default.** Gym lighting is dim. Dark background reduces glare.
4. **Keyboard-navigable.** All actions accessible via keyboard for desktop use.
5. **One primary action per screen.** Every screen answers "What should I do next?"

## Layout

```
┌─────────────────────────────────────────┐
│ Header: Logo, Date, Streak, Weight      │  ← Always visible
├──────────┬──────────────────────────────┤
│ Sidebar  │   Main Content Area          │
│ 280px    │                              │
│          │                              │
│ Today    │   (varies by screen)         │
│ Workout  │                              │
│ Progress │                              │
│ Nutrition│                              │
│ Settings │                              │
└──────────┴──────────────────────────────┘
```

## Key Screens

### Active Workout Screen
- Current exercise name (large, bold)
- Previous session: weight × reps (reference line)
- Set logging buttons: large tap targets, "✅" for complete, "⏭" for skip
- Weight/reps picker: up/down steppers, not text input
- Rest timer: countdown visible, auto-start after set logged
- Progress: sets completed / total sets

### Dashboard
- Today's scheduled workout (or "Rest Day" / "Quick Start")
- Daily calories & protein: target vs actual (progress bar)
- Current body weight with trend arrow
- Last PR achieved (congratulatory)
- Workout streak (fire icon 🔥 for 5+ days)

### Progress Charts
- Weight trend: 30/90 day line chart
- Volume trend: weekly bar chart
- Strength trend: estimated 1RM per lift
- Frequency: sessions/week bar chart

## Typography

| Element | Size | Weight |
|---------|------|--------|
| Exercise name (active) | 24px | Bold |
| Set number | 18px | Medium |
| Weight/Reps | 16px | Regular |
| Timer | 48px | Bold (mono) |
| Body text | 14px | Regular |
| Labels | 12px | Medium |

## Colors (Dark Theme)

| Token | Hex | Usage |
|-------|-----|-------|
| background | `#0F172A` | Page background |
| surface | `#1E293B` | Cards, panels |
| primary | `#818CF8` | Buttons, active states, PR highlight |
| success | `#4ADE80` | Completed set, positive trend |
| warning | `#FBBF24` | Warning, approaching limit |
| error | `#F87171` | Missed session, negative trend |
| text_primary | `#F1F5F9` | Body text |
| text_secondary | `#94A3B8` | Secondary, labels |
| border | `#475569` | Dividers |

## Interaction Patterns

- **Logging a set:** Tap "Complete" → weight pre-filled from last session → adjust if needed → tap "Log" (2 taps total)
- **Skipping an exercise:** Long-press → "Skip Exercise" confirmation
- **Ending workout:** Tap "Finish" → summary modal → confirm
- **Viewing history:** Scrollable list, grouped by week, expandable

## Responsive Behavior

- Minimum window size: 1024×768
- Sidebar collapses to icons at < 1200px
- Active workout screen goes full-width when sidebar is collapsed
- All functionality accessible at minimum window size
