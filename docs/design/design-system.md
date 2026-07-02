# NEXUS Design System

## Principles

1. **Consistency**: Single source of truth for all visual properties
2. **Accessibility**: WCAG AA minimum contrast
3. **Responsive**: Works across desktop, mobile, wearable
4. **Themeable**: Light/dark mode with token swapping
5. **Minimal**: Every token has a purpose

## Design Tokens

### Colors

| Token | Light | Dark | Usage |
|-------|-------|------|-------|
| `primary` | `#6366F1` | `#818CF8` | Buttons, links, active states |
| `background` | `#FFFFFF` | `#0F172A` | Page background |
| `surface` | `#F9FAFB` | `#1E293B` | Cards, panels |
| `text_primary` | `#111827` | `#F1F5F9` | Body text |
| `text_secondary` | `#6B7280` | `#94A3B8` | Secondary text |
| `success` | `#22C55E` | `#4ADE80` | Positive states |
| `error` | `#EF4444` | `#F87171` | Errors, destructive |
| `border` | `#E5E7EB` | `#475569` | Dividers, outlines |

### Typography

| Token | Value |
|-------|-------|
| Font Family | `Inter, -apple-system, sans-serif` |
| Mono Font | `JetBrains Mono, Fira Code, monospace` |
| H1 | `2.25rem` |
| H2 | `1.875rem` |
| H3 | `1.5rem` |
| Body | `1rem` |
| Small | `0.875rem` |

### Spacing Scale

`xs(4px)` → `sm(8px)` → `md(16px)` → `lg(24px)` → `xl(32px)` → `xxl(48px)`

### Border Radius

`sm(4px)` → `md(8px)` → `lg(12px)` → `full(rounded)`

## Component Guidelines

### Buttons
- Primary: `primary` background, `text_inverse` text
- Secondary: transparent, `primary` border
- Ghost: no border/background, `text_secondary`
- Danger: `error` background
- Sizes: sm(32px), md(40px), lg(48px)

### Cards
- Background: `surface`
- Border: `border` 1px
- Radius: `radius.md`
- Shadow: `shadows.sm`
- Padding: `spacing.lg`

### Inputs
- Background: `surface`
- Border: `border`
- Focus: `primary` ring
- Height: 40px (md)
- Label: `text_secondary`, small

### Layout
- Max content width: 1200px
- Sidebar: 280px
- Gutter: `spacing.lg`
- Section padding: `spacing.section`

## Usage

```python
from core.theme import ThemeManager

tm = ThemeManager()
theme = tm.current

# Access tokens
bg = theme.current_colors.background
heading = theme.typography.h2
padding = theme.spacing.lg
```

## Dark Mode

Toggle via `ThemeManager.toggle_dark_mode()`. The theme automatically swaps color tokens when `is_dark` is True.
