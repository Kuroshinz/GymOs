# Design System — RFC-026

Single canonical visual foundation for NEXUS.

## Structure

```
ui/design_system/
├── __init__.py              # Public API — re-exports everything
├── tokens/
│   ├── __init__.py
│   ├── color.py             # Color tokens (Light / Dark / High Contrast)
│   ├── typography.py        # Font families, sizes, weights, line heights
│   ├── spacing.py           # 8-point grid spacing system
│   ├── elevation.py         # Shadow / elevation levels 0–5
│   ├── radius.py            # Border radius tokens
│   ├── motion.py            # Duration, delay, easing curves
│   ├── icon.py              # Icon sizing system
│   └── layout.py            # Breakpoints, container widths, layout constants
└── components/
    ├── __init__.py
    ├── app_card.py           # AppCard — generic card container
    ├── metric_card.py        # MetricCard — key-value metric display
    ├── section_header.py     # SectionHeader — title + subtitle + action
    ├── status_badge.py       # StatusBadge — colored status indicator
    ├── progress_ring.py      # ProgressRing — circular progress indicator
    ├── chart_container.py    # ChartContainer — chart wrapper with header
    ├── toolbar.py            # Toolbar — action bar
    ├── navigation_rail.py    # NavigationRail — icon-based side navigation
    ├── sidebar_item.py       # SidebarItem — sidebar navigation button
    ├── search_bar.py         # SearchBar — search input field
    ├── command_bar.py        # CommandBar — command palette overlay
    ├── skeleton_loader.py    # SkeletonLoader/SkeletonBlock — loading placeholder
    ├── empty_state.py        # EmptyState — no-data placeholder
    ├── notification_toast.py # NotificationToast — transient notification
    └── dialog_template.py    # DialogTemplate — modal dialog
```

## Design Principles

1. **Zero hardcoded values** — every visual property references a design token.
2. **8-point grid** — all spacing is a multiple of `0.25rem` (4px at 16px base).
3. **Token-driven theming** — components receive a `ColorScheme` (LIGHT/DARK/HIGH_CONTRAST).
4. **Single source of truth** — `ui/design_system` is the only place where visual primitives are defined.
5. **Backward compatible** — existing `ui/command_center/theme.py` is a bridge to the design system.

## Color System

Three color schemes:

| Scheme | Class | Use Case |
|--------|-------|----------|
| `ColorScheme.LIGHT` | `ColorTokens` | Light mode |
| `ColorScheme.DARK` | `DarkColorTokens` | Dark mode (default) |
| `ColorScheme.HIGH_CONTRAST` | `HighContrastColorTokens` | Accessibility |

Each color token set includes:
- **Primary** / **Secondary** / **Accent** action colors
- **Success** / **Warning** / **Error** / **Info** semantic colors (each with `*_surface`, `*_border` variants)
- **Background** / **Surface** / **Border** structural colors
- **Text** primary / secondary / disabled / inverse / link
- **Scrollbar**, **Focus ring**, **Overlay** utility colors

```python
from ui.design_system import color_from_scheme, ColorScheme, resolve_alpha

colors = color_from_scheme(ColorScheme.DARK)
bg = colors.background          # "#0F172A"
text = colors.text_primary      # "#F1F5F9"
rgba = resolve_alpha("#6366F1", 0.4)  # "rgba(99, 102, 241, 0.4)"
```

## Typography

`TypographyTokens` provides full type scale, weights, and line heights:

```python
from ui.design_system import font_style

style = font_style("h1", weight="bold")
# "font-family: Inter,...; font-size: 2.25rem; font-weight: 700; ..."
```

Size scale: `h1` (2.25rem) → `h4` (1.25rem) → `body` (1rem) → `caption` (0.75rem) → `overline` (0.625rem).

## Spacing — 8-Point Grid

All spacing is a multiple of 0.25rem (1 spacing unit = 4px):

```python
from ui.design_system import spacing_step, SpacingTokens

margin = spacing_step(4)        # "1rem" (16px)
padding = spacing_step(2)       # "0.5rem" (8px)
gap = SpacingTokens().section   # "1.5rem" (24px)
```

Named spacing fields follow the pattern `s<N>` where N is the step number (e.g., `s1`, `s2`, `s4`, `s8`, `s16`).

## Elevation

Five shadow levels (0–5) plus dark-mode variants:

```python
from ui.design_system import elevation_style

shadow = elevation_style(2, is_dark=True)  # dark-mode level 2 shadow
```

| Level | Light Shadow | Dark Shadow |
|-------|-------------|-------------|
| 0 | `none` | `none` |
| 1 | Subtle | Slightly more opaque |
| 2 | Standard card | Deeper |
| 3 | Raised | Deeper |
| 4 | Modal / dialog | Deeper |
| 5 | Highest emphasis | Deepest |

## Motion

Duration tokens and cubic-bezier curves:

```python
from ui.design_system import easing_style, MotionTokens

m = MotionTokens()
transition = easing_style(
    duration=m.duration_normal,   # "200ms"
    curve=m.curve_ease_out,       # "cubic-bezier(0, 0, 0.58, 1)"
    delay=m.delay_short,          # "50ms"
    property="opacity",
)
```

## Reusable Components

### AppCard
Generic card container. Backward-compatible with `DashboardCard`:
- `add_content(widget)`, `add_layout(layout)` — populate the body
- `make_row(label, value, value_color)` — static label/value row
- `make_separator()` — horizontal divider
- `status_color(severity)` — maps severity strings to theme colors
- Supports `interactive=True` for hover effects

### MetricCard
Display a key metric with value, unit, trend:
```python
MetricCard(label="Volume", value="12,500", unit="kg", trend="+5%")
```

### StatusBadge
Colored label with semantic levels: `SUCCESS`, `WARNING`, `ERROR`, `INFO`, `NEUTRAL`.
Supports `outlined=True` variant.

### ProgressRing
Circular progress indicator with custom-painted arc and center text:
```python
ring = ProgressRing(size=100)
ring.set_progress(75, 100, label="Health", sub_label="Good")
```

### CommandBar
Overlay command palette with filterable list:
```python
bar = CommandBar(commands=[("save", "Save File"), ("open", "Open File")])
bar.command_selected.connect(lambda cmd: print(cmd))
bar.show_command_bar()
```

### DialogTemplate
Modal confirmation dialog. Supports destructive variant and custom content:
```python
confirmed = DialogTemplate.confirm(parent, "Delete?", "This cannot be undone.", destructive=True)
```

### Other Components
- `SectionHeader` — section title with optional subtitle and action button
- `ChartContainer` — chart wrapper with title header
- `Toolbar` — horizontal action bar
- `NavigationRail` — vertical icon-based nav
- `SidebarItem` — active-state navigation button
- `SearchBar` — search input with icon and shortcut hint
- `SkeletonLoader` / `SkeletonBlock` — loading placeholders
- `EmptyState` — icon + title + message + action button
- `NotificationToast` — transient notification with auto-dismiss

## Migration Path

Existing widgets can migrate incrementally:

1. **Replace hardcoded hex values** — use `color_from_scheme(ColorScheme.DARK)` tokens
2. **Replace `DashboardCard`** — extend `AppCard` instead (same API surface)
3. **Replace inline `class C` imports** — use `ui.design_system.tokens.color` directly or continue using the backward-compatible `ui.command_center.theme` bridge
4. **Adopt spacing tokens** — replace hardcoded `px`/`rem` values with `spacing_step(n)`

The backward-compatible `ui/command_center/theme.py` bridge maps `C.BG`, `C.CARD_BG`, `Font.*`, `Style.*` to the design system tokens, so existing code continues to work unchanged.

## Tests

```
tests/ui/test_design_tokens.py        # 58 token tests
tests/ui/test_design_components.py    # 76 component tests
```

Run with: `pytest tests/ui/test_design_tokens.py tests/ui/test_design_components.py -v`
