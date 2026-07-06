# GymOS Accessibility Guide

## Keyboard Accessibility

All features MUST be operable via keyboard alone:

| Feature | Shortcut | Scope |
|---------|----------|-------|
| Command palette | `Ctrl+K` | Global |
| Focus mode | `Ctrl+Shift+F` | Global |
| Navigate back | `Alt+Left` | Global |
| Navigate forward | `Alt+Right` | Global |
| Refresh | `Ctrl+R` | Global |
| Exit focus/modal | `Escape` | Global |
| Tab navigation | `Tab` / `Shift+Tab` | Within panels |

## Visual Accessibility

### Color Contrast

All text/background combinations meet WCAG AA standards:

| Token Pair | Contrast Ratio | Usage |
|-----------|---------------|-------|
| `C.TEXT_PRIMARY` on `C.BG` | >7:1 | Body text |
| `C.TEXT_SECONDARY` on `C.BG` | >4.5:1 | Secondary text |
| `C.ACCENT` on `C.BG` | >4.5:1 | Interactive elements |
| `C.TEXT_MUTED` on `C.BG` | >3:1 | Labels, captions |

### Focus Indicators

- All interactive elements have visible focus rings
- Default `QFocusFrame` styling maintained
- Command palette search has persistent focus indicator

### Screen Reader Support

- `QLabel` text content is accessible by default
- Buttons have descriptive text (emoji icons supplemented by text labels)
- Status changes are announced via `QApplication.notify()`

## Motion Sensitivity

- Animations respect the system "Reduce motion" setting (future)
- All animations are under 500ms duration
- No flashing or strobing effects
- Skeleton loaders use subtle opacity pulses (1.5s), not rapid changes

## Focus Management

- Command palette traps focus while open
- Dialogs are modal with focus forced to content
- Escape returns focus to the previously active element
- Tab order follows visual layout (left-to-right, top-to-bottom)
