# RFC-030 — GymOS Visual Language 2.0

> **Status:** Design RFC — No Code Modified
> **Designer:** RFC-030
> **Date:** 2026-07-14
> **Supersedes:** RFC-026 (Design System), REP-006A (Visual Foundation Audit)

---

## Table of Contents

1. [Mission & Scope](#1-mission--scope)
2. [Design Principles](#2-design-principles)
3. [Visual Language](#3-visual-language)
4. [Background System](#4-background-system)
5. [Card & Surface System](#5-card--surface-system)
6. [Elevation System](#6-elevation-system)
7. [Color System](#7-color-system)
8. [Typography System](#8-typography-system)
9. [Spacing System](#9-spacing-system)
10. [Border System](#10-border-system)
11. [Lighting System](#11-lighting-system)
12. [Motion System](#12-motion-system)
13. [Chart Style](#13-chart-style)
14. [Iconography](#14-iconography)
15. [Component Consistency Report](#15-component-consistency-report)
16. [Token Inventory & Status](#16-token-inventory--status)
17. [Migration Strategy](#17-migration-strategy)
18. [Verification](#18-verification)

---

## 1. Mission & Scope

### Mission

Redefine the visual language of GymOS before continuing REP-006H and subsequent UI redesigns.

The current implementation is technically consistent (tokens exist, helpers exist) but visually feels closer to an enterprise dashboard than a premium consumer fitness application. The token system is solid—the *aesthetic direction* and *enforcement* are missing.

### Out of Scope

- NO page redesigns
- NO business logic changes
- NO controller/service/database changes
- NO implementation of visual changes in code
- NO chart library replacement

### Keywords

Premium · Editorial · Minimal · Athletic · Calm · Luxury · Focused · Soft depth · Modern · Timeless

### Anti-Keywords

Bootstrap · Enterprise dashboard · Medical software · Crypto dashboard · Glassmorphism showcase · Dribbble clone

---

## 2. Design Principles

### P1. Whitespace Is the Layout

Whitespace is the primary structural tool. Group content by proximity, not by boxes. Cards should feel placed on a surface, not fenced in.

### P2. Hierarchy Through Typography, Not Boxes

Create visual hierarchy through size, weight, and letter-spacing—NOT through colored backgrounds, borders, or dividers. A well-set heading needs no background.

### P3. Depth Serves Focus, Not Decoration

Use elevation sparingly. One raised element per viewport. Shadows should feel like ambient occlusion, not drop shadows.

### P4. Lighting Communicates Achievement

Glow is a semantic tool reserved for goals, PRs, and recovery milestones. It is not a decoration.

### P5. Motion Has Purpose

Every animation answers "where did that come from / where did it go?" Motion is confident, fast, and calm. No excessive ornamentation.

### P6. One Visual Focal Point Per Section

Every section (hero, insight, metric) has exactly one element that draws the eye first. Everything else supports it.

### P7. Design Around Content, Not Chrome

The interface disappears behind the data. Backgrounds, cards, and chrome recede. The athlete's numbers and insights are the stars.

### P8. Consistency Over Novelty

When in doubt, use the token. Every component uses the same radius, the same font scale, the same spacing grid. No exceptions.

---

## 3. Visual Language

### Character

GymOS is a premium fitness operating system. It should feel like a finely-tuned instrument—calm, precise, and powerful.

### Editorial Hierarchy

Borrow from editorial design: one hero element dominates, secondary content supports, tertiary content is referenced. Information is organized by importance, not by layout convenience.

```
Page Structure:
┌──────────────────────────────────────┐
│  Hero (1 visual focal point)         │  ← largest, most prominent
├──────────────────────────────────────┤
│  Section Header                      │
│  ┌──────┐ ┌──────┐ ┌──────┐         │  ← equal-weight secondary
│  │ Card │ │ Card │ │ Card │         │
│  └──────┘ └──────┘ └──────┘         │
├──────────────────────────────────────┤
│  Section Header                      │
│  ┌──────────────────────────────┐    │  ← full-width tertiary
│  │ Insight row                  │    │
│  ├──────────────────────────────┤    │
│  │ Insight row                  │    │  ← lower visual weight
│  └──────────────────────────────┘    │
└──────────────────────────────────────┘
```

### Card Density

| Context | Padding | Gap | Visual Weight |
|---------|---------|-----|---------------|
| Hero | 24px | 16px | Highest |
| Primary content cards | 20px | 12px | Medium |
| Secondary/insight rows | 16px | 8px | Low |
| Dense data (charts, tables) | 16px | 8px | Lowest |

### Mixed Card Sizes

Pages use a grid with varied spans (full, half, third, quarter) to create editorial rhythm. Not every card is the same width. Not every section is the same height.

### Compact Hero

The hero is compact—it occupies the top portion of the page but does not waste vertical space. A hero panel is 2-3 lines of content + one primary action, not a full-screen takeover.

---

## 4. Background System

### Design Direction

The background should disappear behind content. It must not compete, pattern, or texture the interface.

### Dark Mode (Default)

```
Layer 0 (page background):    #0B1120   (deep navy, slightly darker than current)
Layer 1 (card surface):       #0F172A   (current background → becomes surface)
Layer 2 (elevated surface):   #1A2235   (for modals, popovers, dialogs)
```

- Add a **very subtle radial vignette** at the page level: a soft darkening toward edges, barely perceptible.
- Add a **very subtle gradient** from the center-top: `rgba(99,102,241,0.02)` sweeping from top-center to bottom. Imperceptible unless compared side-by-side.
- Remove `background_alt: #0B1120` — the alt background becomes the page background itself. The separate alt layer is unnecessary.

### Light Mode

```
Layer 0 (page background):    #F7F8FA   (warm off-white, not pure white)
Layer 1 (card surface):       #FFFFFF
Layer 2 (elevated surface):   #F0F2F5
```

- Subtle warm tint (compared to current `#FFFFFF`) to feel less sterile.
- Subtle shadow vignette at page level.

### What NOT to Do

- No heavy textures
- No wallpaper images
- No obvious gradients
- No glassmorphism backdrop blur
- No noise overlays

---

## 5. Card & Surface System

### Current Problems

Cards feel **separated from the page** — they float with visible borders and independent shadows. The contrast between card background (`#1E293B`) and page background (`#0F172A`) is stark (18% difference), making each card feel like a postage stamp on a dark board.

### Target

Cards should feel **embedded in the page** — they are areas of the same surface with a barely perceptible boundary.

### Dark Mode Surface Hierarchy

| Level | Name | Background | Border | Elevation | Usage |
|-------|------|-----------|--------|-----------|-------|
| 0 | Page | `#0B1120` | none | none | Page background |
| 1 | Surface | `#0F172A` | `1px solid rgba(255,255,255,0.04)` | Level 0 | Card default |
| 2 | Raised | `#1A2235` | `1px solid rgba(255,255,255,0.06)` | Level 1 | Interactive cards |
| 3 | Elevated | `#1E293B` | `1px solid rgba(255,255,255,0.08)` | Level 2 | Modals, dialogs |
| 4 | Overlay | `rgba(0,0,0,0.5)` | none | none | Backdrop |

**Key change:** The current card background `#1E293B` becomes the **Elevated** level (only modals). Cards use `#0F172A` (the current page background), which is the **Surface** level. The page background shifts one step darker to `#0B1120`.

This means cards **blend into the page**. Content boundaries are defined by spacing, internal padding, and very subtle borders/elevation—not by high-contrast card backgrounds.

### Card Density & Padding

| Component | Current Padding | Target Padding | Rationale |
|-----------|----------------|----------------|-----------|
| HeroPanel | 24, 20, 24, 20 | 24, 24, 24, 24 | Consistent vertical |
| SectionPanel | 20, 16, 20, 16 | 20, 20, 20, 20 | Consistent vertical |
| AppCard | 20, 16, 20, 16 | 20, 20, 20, 20 | Consistent vertical |
| MetricCard | 16, 14, 16, 14 | 16, 16, 16, 16 | Consistent vertical |
| InsightCard | 16, 12, 16, 12 | 16, 16, 16, 16 | Consistent vertical |
| ChartContainer | 16, 14, 16, 14 | 16, 16, 16, 16 | Consistent vertical |
| DialogTemplate | 24, 20, 24, 20 | 24, 24, 24, 24 | Consistent vertical |

**Rule:** Top and bottom padding MUST be equal. No more `(16, 14, 16, 14)` asymmetry.

---

## 6. Elevation System

### Current Problems

- Elevation uses black shadows with hardcoded alpha: `rgba(0,0,0,0.4)` etc.
- The shadow color does not adapt to the card color, creating a dirty/grey halo.
- `apply_elevation()` uses `bg_color` parameter inconsistently.
- Only `AppCard` uses elevation at all.

### New Elevation Model

Use **color-matched shadows** — the shadow takes the hue of the surface below, not black. This creates a natural, ambient occlusion feel.

```
Level 0:   No shadow (page background, embedded cards)
Level 1:   Ambient occlusion
           ─ offset: (0, 1), blur: 4px, alpha: 0.15 (dark) / 0.08 (light)
           ─ uses background color, not black
Level 2:   Standard card raise
           ─ offset: (0, 2), blur: 8px, alpha: 0.2 (dark) / 0.12 (light)
Level 3:   Dialog / modal
           ─ offset: (0, 4), blur: 16px, alpha: 0.3 (dark) / 0.15 (light)
Level 4:   Popover / tooltip
           ─ offset: (0, 8), blur: 24px, alpha: 0.35 (dark) / 0.2 (light)
Level 5:   Highest emphasis (notification, alert)
           ─ offset: (0, 12), blur: 32px, alpha: 0.4 (dark) / 0.25 (light)
```

### Elevation Application Rules

| Component | Level | Notes |
|-----------|-------|-------|
| Page background | 0 | Never elevated |
| Embedded cards | 0-1 | Cards that blend into page |
| Interactive cards | 1 | Raised only on hover |
| Hero panel | 1 | Slight presence |
| Section panel | 0 | Belongs to page |
| Metric card | 1 | Slight presence |
| Insight card | 0 | Belongs to section |
| Modal / Dialog | 3 | Clear separation |
| Popover / Tooltip | 4 | Highest on-page |
| Notification toast | 5 | Highest in app |

### Implementation

Replace the current `_ELEVATION_SHADOWS` dictionary with a function that takes `bg_color` and `level` to compute a color-matched shadow:

```python
def compute_shadow(
    bg_color: str,       # the surface color casting the shadow
    level: int = 1,
    is_dark: bool = True
) -> str:
    alpha = _ALPHA[level][is_dark]
    r, g, b = parse_hex(bg_color)
    return f"0 {dy}px {blur}px rgba({r},{g},{b},{alpha})"
```

This ensures shadows inherit the hue of the surface, eliminating the grey/black halo.

---

## 7. Color System

### Current Assessment

The current palette is serviceable but has issues:

| Issue | Detail |
|-------|--------|
| Over-saturated success | `#4ADE80` is too bright for a premium app |
| Primary is cool | `#818CF8` works, but `#A5B4FC` for text_link is too light |
| No accent glow colors | No tokens for glow/highlight effects |
| Semantic colors are bright | All semantic colors are at full saturation |
| Background alt is redundant | `#0B1120` vs `#0F172A` difference is negligible |

### Dark Mode Palette (Revised)

#### Primary

| Token | Current | Target | Rationale |
|-------|---------|--------|-----------|
| `primary` | `#818CF8` | `#818CF8` | Keep — it's distinctive |
| `primary_hover` | `#6366F1` | `#6B7AF5` | Slightly lighter hover for better feel |
| `primary_variant` | `#1E1B4B` | `#141336` | Darker, more subtle variant |

#### Secondary

| Token | Current | Target | Rationale |
|-------|---------|--------|-----------|
| `secondary` | `#22D3EE` | `#38BDF8` | Keep but shift toward primary's family |
| `secondary_hover` | `#06B6D4` | `#2BA0E8` | Slightly desaturated |
| `secondary_variant` | `#083344` | `#0C2236` | Darker variant |

#### Accent

| Token | Current | Target | Rationale |
|-------|---------|--------|-----------|
| `accent` | `#FBBF24` | `#F9A03F` | Warm amber, less yellow |
| `accent_hover` | `#F59E0B` | `#E88D2A` | Darker warm accent |
| `accent_variant` | `#451A03` | `#2D1508` | Dark variant |

#### Semantic Colors (Desaturated)

| Token | Current | Target | Rationale |
|-------|---------|--------|-----------|
| `success` | `#4ADE80` | `#34D399` | Muted emerald, premium feel |
| `success_hover` | `#22C55E` | `#2BBF7D` | |
| `success_surface` | `#052E16` | `#0A2A1A` | Darker, more subtle |
| `success_border` | `#166534` | `#1A4538` | Muted border |
| `warning` | `#FACC15` | `#F5A623` | Amber, not yellow |
| `warning_hover` | `#EAB308` | `#DF931A` | |
| `warning_surface` | `#422006` | `#2E1C0C` | |
| `warning_border` | `#713F12` | `#4D3018` | |
| `error` | `#F87171` | `#F56565` | Softer red, less aggressive |
| `error_hover` | `#EF4444` | `#E53E3E` | |
| `error_surface` | `#450A0A` | `#2D0F0F` | |
| `error_border` | `#7F1D1D` | `#4F1D1D` | |
| `info` | `#60A5FA` | `#60A5FA` | Keep — works well |
| `info_hover` | `#3B82F6` | `#3B82F6` | Keep |
| `info_surface` | `#172554` | `#0F1D40` | Darker |
| `info_border` | `#1E40AF` | `#1A3060` | |

#### Background & Surface

| Token | Current | Target | Rationale |
|-------|---------|--------|-----------|
| `background` | `#0F172A` | `#0B1120` | Shift page down, surface becomes card |
| `background_alt` | `#0B1120` | `#080D18` | Slightly darker for nav rails |
| `surface` | `#1E293B` | `#0F172A` | Old background becomes surface |
| `surface_hover` | `#334155` | `#1A2235` | Raised card variant |
| `surface_active` | `#475569` | `#243045` | Pressed state |

#### Border

| Token | Current | Target | Rationale |
|-------|---------|--------|-----------|
| `border` | `#334155` | `rgba(255,255,255,0.06)` | Semi-transparent, adapts to surface |
| `border_light` | `#1E293B` | `rgba(255,255,255,0.03)` | Barely visible |
| `border_hover` | `#475569` | `rgba(255,255,255,0.12)` | Slightly more visible |

#### Text

| Token | Current | Target | Rationale |
|-------|---------|--------|-----------|
| `text_primary` | `#F1F5F9` | `#F1F5F9` | Keep — high contrast |
| `text_secondary` | `#94A3B8` | `#8899AA` | Slightly warmer grey |
| `text_disabled` | `#64748B` | `#556677` | Lower contrast |
| `text_inverse` | `#0F172A` | `#0B1120` | Match new background |
| `text_link` | `#A5B4FC` | `#A5B4FC` | Keep |

### Light Mode Palette (Revised)

| Token | Current | Target | Rationale |
|-------|---------|--------|-----------|
| `background` | `#FFFFFF` | `#F7F8FA` | Warm off-white |
| `surface` | `#F9FAFB` | `#FFFFFF` | White card on warm page |
| `border` | `#E5E7EB` | `rgba(0,0,0,0.06)` | Semi-transparent |
| `text_primary` | `#111827` | `#0F172A` | Slightly softer black |

### New Tokens to Add

| Token | Purpose | Dark Value | Light Value |
|-------|---------|-----------|-------------|
| `glow_primary` | Primary accent glow | `rgba(129,140,248,0.25)` | `rgba(99,102,241,0.15)` |
| `glow_success` | Achievement glow | `rgba(52,211,153,0.2)` | `rgba(52,211,153,0.12)` |
| `glow_warning` | Goal glow | `rgba(245,166,35,0.2)` | `rgba(245,166,35,0.12)` |
| `glow_error` | Danger glow | `rgba(245,101,101,0.2)` | `rgba(245,101,101,0.12)` |
| `hero_gradient` | Page hero gradient | `linear-gradient(...)` | `linear-gradient(...)` |

---

## 8. Typography System

### Current Assessment

Typography tokens exist and are correct but are universally ignored. Components hardcode `font-size: 13px`, `font-size: 11px`, etc. directly in stylesheet strings.

The existing `TypographyTokens` class has 9 levels, which is too many. We need to reduce to a tighter editorial scale.

### Target Type Scale

| Token | Size | Weight | Line Height | Letter Spacing | Usage |
|-------|------|--------|-------------|----------------|-------|
| `hero` | 32px / 2rem | 700 | 1.2 | -0.03em | Page title (fitness operating system name) |
| `h1` | 24px / 1.5rem | 700 | 1.25 | -0.025em | Page headers, hero values |
| `h2` | 20px / 1.25rem | 700 | 1.3 | -0.02em | Section titles, card group headers |
| `h3` | 16px / 1rem | 600 | 1.4 | -0.015em | Card titles, panel headers |
| `body` | 14px / 0.875rem | 400 | 1.5 | 0em | Primary running text |
| `body_small` | 13px / 0.8125rem | 400 | 1.5 | 0em | Secondary text, descriptions |
| `caption` | 12px / 0.75rem | 400 | 1.5 | 0.025em | Metadata, timestamps, footnotes |
| `label` | 12px / 0.75rem | 600 | 1.25 | 0.05em | Labels, uppercase headers |
| `metric` | 28px / 1.75rem | 800 | 1.1 | -0.02em | KPI values, data emphasis |

Compared to current: removed `overline` (10px — too small, unused), added `hero` (32px) and `metric` (28px), adjusted `body` from 16px to 14px (better density for dashboards), moved `body_small` from 14px to 13px (the most commonly hardcoded size).

### Font Family

Keep: `Inter, -apple-system, BlinkMacSystemFont, sans-serif`

Add system font fallback for CJK:
`"Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"`

### Enforcement Rule

**No component may set `font-size` in QSS.** All font sizes must come from `font_style()` or resolved token values. The `font_style()` helper must be extended to support the new scale.

### Migration of Existing Hardcoded Sizes

| Hardcoded Size | → Replace With |
|----------------|---------------|
| 48px | metric (if KPI) or custom (data viz) |
| 32px | h1 (if page title) or metric (if KPI) |
| 28px | metric |
| 24px | h1 (page header) or metric (if KPI value) |
| 22px | h1 or h2 |
| 20px | h2 |
| 18px | h3 (card title) |
| 16px | h3 (card title) or body |
| 15px | h3 or body with weight |
| 14px | body |
| 13px | body_small |
| 12px | caption or label |
| 11px | caption (old label style — migrate to caption) |
| 10px | caption (was overline — migrate to caption) |

---

## 9. Spacing System

### Current Assessment

The 8-point grid is excellent and should be kept. The current `SpacingTokens` supports steps s1–s64. However, the **semantic aliases** need updating.

### Revised Semantic Aliases

| Alias | Value | Usage |
|-------|-------|-------|
| `page_margin` | 32px (s8) | Page-level margins |
| `section_gap` | 24px (s6) | Gap between sections |
| `card_gap` | 16px (s4) | Gap between cards in a grid |
| `card_padding` | 20px (s5) | Internal card padding (was 16px) |
| `dense_padding` | 16px (s4) | Internal padding for dense components |
| `row_gap` | 12px (s3) | Gap between rows in a card |
| `item_gap` | 8px (s2) | Gap between items in a row |
| `inline_gap` | 4px (s1) | Tight icon/text gap |

### Enforcement Rule

**No component may set `setContentsMargins`, `setSpacing`, or `setFixedWidth` with a raw integer.** All spacing values must reference `SpacingTokens` fields or `spacing_step(n)`.

---

## 10. Border System

### Current Assessment

- Current `border: 1px solid #334155` is too visible (saturation 15%, lightness 26%).
- Borders compete with elevation. Cards with both a visible border AND a shadow feel over-defined.
- Radius usage is inconsistent: lg (12px), md (8px), xl (16px) used interchangeably.

### Direction

**Reduce border visibility dramatically.** Borders should be barely perceptible — they define geometry, not visual weight.

| Token | Current | Target |
|-------|---------|--------|
| `border` | `1px solid #334155` | `1px solid rgba(255,255,255,0.06)` |
| `border_light` | `1px solid #1E293B` | `1px solid rgba(255,255,255,0.03)` |
| `border_hover` | `1px solid #475569` | `1px solid rgba(255,255,255,0.12)` |

### Radius Standardization

| Component | Current | Target | Rationale |
|-----------|---------|--------|-----------|
| HeroPanel | xl (16px) | xl (16px) | Keep — prominent |
| SectionPanel | lg (12px) | lg (12px) | Keep |
| AppCard | lg (12px) | lg (12px) | Keep |
| MetricCard | lg (12px) | lg (12px) | Keep |
| InsightCard | md (8px) | lg (12px) | Promote to match cards |
| ChartContainer | lg (12px) | lg (12px) | Keep |
| DialogTemplate | xl (16px) | xl (16px) | Keep |
| StatusBadge | md (8px) | md (8px) | Keep — smaller component |
| WarningBanner | md (8px) | lg (12px) | Promote |
| NavigationRail | md (8px) | md (8px) | Keep |
| Buttons | 6px (hardcoded) | md (8px) | Standardize |

**Rule:** All card-type components use `RadiusTokens.lg`. Non-card components (badges, buttons) use `RadiusTokens.md`. The only exception is `DialogTemplate` and `HeroPanel` which use `xl`.

---

## 11. Lighting System

### Current State

No lighting/glow system exists. The `ElevationTokens` only handle shadows.

### Glow Tokens

Add a `GlowTokens` class to `tokens/elevation.py`:

```python
@dataclass(frozen=True)
class GlowTokens:
    primary: str = "rgba(129, 140, 248, 0.25)"
    success: str = "rgba(52, 211, 153, 0.2)"
    warning: str = "rgba(245, 166, 35, 0.2)"
    error: str = "rgba(245, 101, 101, 0.2)"
```

### Glow Application Rules

| Context | Token | Usage |
|---------|-------|-------|
| Personal record highlight | `glow_success` | Behind PR badge or value |
| Goal completion | `glow_warning` | Behind goal ring on completion |
| Active workout | `glow_primary` | Behind hero element during workout |
| Danger/deload warning | `glow_error` | Behind warning banner or metric |

### How to Apply

Glow is implemented as a `QGraphicsDropShadowEffect` with:
- `blurRadius = 24px`
- `offset = (0, 2)`
- no border change

This creates a subtle aura without altering the card structure.

### Anti-Patterns

- Do NOT glow every card
- Do NOT use glow as a hover effect
- Do NOT animate glow continuously (no pulsing)
- Glow is a state, not an animation

---

## 12. Motion System

### Current Assessment

Motion tokens exist (`MotionTokens`, `MotionCurves`, `easing_style()`) but are completely unused. No component references them. No transitions are defined in QSS.

### Direction

Motion should feel **confident, fast, and purposeful**.

### Timing

| Context | Duration | Curve | Rationale |
|---------|----------|-------|-----------|
| Hover (card raise) | 100ms | ease_out | Fast, subtle |
| Hover (button) | 100ms | ease_out | Fast feedback |
| Page transition | 200ms | ease_in_out | Smooth, controlled |
| Modal appear | 200ms | emphasize | Confident entrance |
| Modal disappear | 150ms | ease_in | Quick exit |
| Accordion expand | 250ms | spring_gentle | Staggered, natural |
| Notification in | 300ms | spring_standard | Bouncy, noticeable |
| Notification out | 200ms | ease_in | Quick dismiss |
| Value change | 200ms | ease_out | Smooth update |

### Reduced Motion

- All transitions must respect `prefers-reduced-motion`.
- When reduced motion is detected, all durations become `0ms` (instant).
- The `MotionTokens` class should expose a `reduced: bool` flag.

### Enforcement

- Every component with interactive states (hover, active, visibility change) MUST define a CSS transition on the relevant properties.
- No component should animate `left`, `top`, `width`, or `height` (triggers layout). Animate `transform` and `opacity` only.

---

## 13. Chart Style

### Current Assessment

Charts exist in two locations (design system + visualization module). There is no consistent style guide for chart appearance.

### Direction

Define chart visual properties as design tokens. Do NOT redesign chart implementations.

| Property | Dark Mode | Light Mode |
|----------|-----------|------------|
| Grid opacity | 0.1 | 0.08 |
| Axis line width | 1px | 1px |
| Axis color | `rgba(255,255,255,0.12)` | `rgba(0,0,0,0.08)` |
| Label font size | caption (12px) | caption (12px) |
| Label color | `text_secondary` | `text_secondary` |
| Data line width | 2px | 2px |
| Data line accent | primary | primary |
| Fill opacity (area) | 0.15 | 0.08 |
| Point radius | 4px | 4px |
| Point hover radius | 6px | 6px |
| Selection ring | primary glow | primary glow |
| Animation duration | 300ms | 300ms |
| Animation curve | ease_out | ease_out |

### Consistency Rules

- All charts use the **same** grid opacity, axis style, label hierarchy, accent color, and animation.
- Chart accent color = theme primary color (for main data series).
- Secondary series use `secondary` color.
- Semantic contexts (recovery, strain, etc.) use the appropriate semantic color.

---

## 14. Iconography

### Current Assessment

Icons are rendered as text emoji via QLabel (e.g., `font-size: 20px`). There is no consistent icon system.

### Direction

Audit required before implementation. For this RFC:

| Property | Direction |
|----------|-----------|
| Style | Outline (not filled) |
| Corner radius | 2px cap (slightly rounded) |
| Stroke width | 1.5px (regular), 2px (bold variants) |
| Size scale | 16px (inline), 20px (icon button), 24px (decorative) |
| Alignment | Center-aligned within bounding box |

### Size Mapping

| Context | Size | Token |
|---------|------|-------|
| Inline with text | 14px | `icon.sm` |
| Navigation rail | 20px | `icon.lg` |
| Icon button | 20px | `icon.icon_button` |
| Card decorative | 24px | `icon.xl` |
| Status / badge | 12px | `icon.badge_icon` |
| Hero / empty state | 40px | `icon.size_3xl` |

### Icon Sources

Current emoji text approach should be replaced with an icon font (Feather, Lucide, or custom) in implementation. This RFC does not specify which — only the visual properties.

---

## 15. Component Consistency Report

### 15.1 AppCard (`ui/design_system/components/app_card.py`)

| Property | Current | Issue | Recommendation |
|----------|---------|-------|----------------|
| Font sizes | hardcoded 11px, 13px | Doesn't use typography tokens | Use `caption`, `body_small`, `label` |
| Padding | (20, 16, 20, 16) | Asymmetric vertical | Use (20, 20, 20, 20) = S.s5 |
| Spacing | 12px, 8px | Raw numbers | Use S.s3, S.s2 |
| Uppercase title | `title.upper()` | Forces ALL CAPS | Use token with `label` style |
| Badge height | 20px fixed | Magic number | Use S.s5 or let content size |
| Separator | QFrame, 1px | Works | Keep but use `border_light` |
| Elevation | Level 2 always | Too heavy for embedded cards | Use Level 1 |

### 15.2 MetricCard (`ui/design_system/components/metric_card.py`)

| Property | Current | Issue | Recommendation |
|----------|---------|-------|----------------|
| Padding | (16, 14, 16, 14) | Asymmetric vertical | Use (16, 16, 16, 16) = S.s4 |
| Font sizes | hardcoded 11px, 24px, 14px, 13px, 12px | Raw values | Use `label`, `metric`, `body`, `body_small`, `caption` |
| Value font | 24px/700 | Should be `metric` token | Use 28px/800 or new metric token |
| Trend color logic | string-based startswith | Fragile | Use enum or numeric comparison |
| Hover border | `border_hover` | Good pattern | Keep |
| Empty methods | `set_value()`, `set_trend()` | Do nothing | Implement or remove |

### 15.3 InsightCard (`ui/design_system/components/insight_card.py`)

| Property | Current | Issue | Recommendation |
|----------|---------|-------|----------------|
| Radius | md (8px) | Inconsistent with cards | Use lg (12px) |
| Padding | (16, 12, 16, 12) | Asymmetric, too tight for insight | Use (16, 16, 16, 16) |
| Font sizes | 20px (icon), 13px, 12px | Hardcoded | Use `decorative`, `body_small`, `caption` |
| Icon width | 28px fixed | Magic number | Use S.s7 or IconTokens based |
| Cursor | Always pointing hand | Should only be when interactive | Make conditional |

### 15.4 SectionHeader (`ui/design_system/components/section_header.py`)

| Property | Current | Issue | Recommendation |
|----------|---------|-------|----------------|
| Title font | 18px/700 | Should be h2 (20px/700) or h3 (16px/600) | Align to editorial scale |
| Subtitle font | 13px | Should be body_small | Use `body_small` |
| Button font | 13px/500 | Should be body_small | Use `body_small` |
| Button radius | 6px | Hardcoded | Use `RadiusTokens.md` |
| Button padding | `6px 14px` | Raw values | Use spacing tokens |
| Empty methods | `set_title()`, `set_subtitle()` | Do nothing | Implement or remove |

### 15.5 StatusBadge (`ui/design_system/components/status_badge.py`)

| Property | Current | Issue | Recommendation |
|----------|---------|-------|----------------|
| Font size | 11px/600 | Hardcoded | Use `label` token |
| Padding | `2px 8px` | Raw values | Use spacing tokens |
| Fixed height | 22px | Magic number | Use S.s5_5 or dynamic |
| Radius | md (8px) | Appropriate | Keep |
| Color mapping | tuple keys in dict | Works | Keep but add `glow_*` support |

### 15.6 ChartContainer (`ui/design_system/components/chart_container.py`)

| Property | Current | Issue | Recommendation |
|----------|---------|-------|----------------|
| Padding | (16, 14, 16, 14) | Asymmetric | Use (16, 16, 16, 16) |
| Title font | 14px/600 | Hardcoded | Use `h3` or `body` with weight |
| Subtitle font | 12px | Hardcoded | Use `caption` |
| Border radius | lg (12px) | Good | Keep |
| No elevation | none | Charts need subtle elevation | Use Level 1 |

### 15.7 WarningBanner (`ui/design_system/components/warning_banner.py`)

| Property | Current | Issue | Recommendation |
|----------|---------|-------|----------------|
| Radius | md (8px) | Inconsistent with cards | Use lg (12px) |
| Padding | (16, 10, 16, 10) | Asymmetric | Use (16, 16, 16, 16) |
| Icon font | 16px | Hardcoded | Use `icon.md` |
| Message font | 13px/500 | Hardcoded | Use `body_small` |
| Button radius | 4px | Hardcoded | Use `RadiusTokens.md` |
| Button padding | `4px 12px` | Raw values | Use spacing tokens |

### 15.8 NavigationRail (`ui/design_system/components/navigation_rail.py`)

| Property | Current | Issue | Recommendation |
|----------|---------|-------|----------------|
| Logo font | 22px/800 | Hardcoded | Use `h1` or custom token |
| Button font | 13px | Hardcoded | Use `label` |
| Button height | 48px fixed | Should use LayoutTokens | Use layout token |
| Padding | (0, 16, 0, 16) | Works | Keep but use spacing tokens |
| Radius | md (8px) | Appropriate | Keep |
| Spacing | 16px, 2px | Raw values | Use S.s4, S.half |
| Focus border | 2px solid focus_ring | Duplicates border property | Use `outline` if possible |

### 15.9 DialogTemplate (`ui/design_system/components/dialog_template.py`)

| Property | Current | Issue | Recommendation |
|----------|---------|-------|----------------|
| Padding | (24, 20, 24, 20) | Asymmetric | Use (24, 24, 24, 24) |
| Title font | 16px/700 | Hardcoded | Use `h3` |
| Message font | 13px | Hardcoded | Use `body_small` |
| Button radius | md (8px) | Appropriate | Keep |
| Button padding | `8px 20px` | Raw values | Use S.s2, S.s5 |
| Fixed width | 420px | Magic number | Use layout token or min/max |
| No elevation | none | Dialog needs elevation | Use Level 3 |

### 15.10 HeroPanel (`ui/design_system/layout/editorial_grid.py`)

| Property | Current | Issue | Recommendation |
|----------|---------|-------|----------------|
| Padding | (24, 20, 24, 20) | Asymmetric | Use (24, 24, 24, 24) |
| Title font | 20px/700 | Hardcoded | Use `h2` or `hero` |
| Subtitle font | 14px | Hardcoded | Use `body` |
| Radius | xl (16px) | Appropriate | Keep |
| Border | 1px solid border | Use new semi-transparent | Update |
| Accent bar | 4px fixed width | Raw value | Use S.s1 |

### 15.11 SectionPanel (`ui/design_system/layout/editorial_grid.py`)

| Property | Current | Issue | Recommendation |
|----------|---------|-------|----------------|
| Padding | (20, 16, 20, 16) | Asymmetric | Use (20, 20, 20, 20) |
| Title font | 16px/700 | Hardcoded | Use `h3` |
| Subtitle font | 12px | Hardcoded | Use `caption` |
| Radius | lg (12px) | Appropriate | Keep |
| Border hover | On entire panel | Should only be on interactive | Remove hover for static panels |

### 15.12 MetricPanel (`ui/design_system/layout/editorial_grid.py`)

| Property | Current | Issue | Recommendation |
|----------|---------|-------|----------------|
| Padding | (16, 14, 16, 14) | Asymmetric | Use (16, 16, 16, 16) |
| Value font | 28px/800 | Hardcoded | Use `metric` token |
| Label font | 12px/500 | Hardcoded | Use `caption` |
| Icon font | 18px | Hardcoded | Use `icon.lg` |
| Trend font | 12px/600 | Hardcoded | Use `caption` with weight |

### 15.13 KpiStrip (`ui/design_system/layout/kpi_strip.py`)

| Property | Current | Issue | Recommendation |
|----------|---------|-------|----------------|
| Value font | 20px/800 | Hardcoded | Use `h2` or `metric` |
| Unit font | 11px/500 | Hardcoded | Use `caption` |
| Label font | 10px/500 | Hardcoded | Use `caption` (10px is too small) |
| Trend font | 12px/700 | Hardcoded | Use `caption` with weight |
| Padding | (12, 10, 12, 10) | Asymmetric | Use (12, 12, 12, 12) |
| Separator | 1px border | OK but not tokenized | Use `border_light` |
| Inner spacing | 2px, 4px | Raw values | Use S.half, S.s1 |

### 15.14 CoachCard / CoachCardStack (`ui/narrative/cards.py`)

**Outside design system entirely.** Not audited in detail. Needs full migration to design system components.

### 15.15 Cross-Component Inconsistencies

| Inconsistency | Components Affected |
|---------------|-------------------|
| Title font varies: 20px/700, 18px/700, 16px/700, 14px/600 | HeroPanel, SectionHeader, SectionPanel, ChartContainer |
| Label font varies: 11px uppercase, 11px, 12px, 10px | AppCard, MetricCard, StatusBadge, KpiStrip, SectionPanel |
| Value font varies: 28px/800, 24px/700, 20px/800 | MetricPanel, MetricCard, KpiStrip |
| Padding asymmetry varies: (16,14), (20,16), (24,20) | All components |
| Card radius varies: xl(16), lg(12), md(8) | All card components |
| Hover behavior varies: border-only, bg+border, none | AppCard, MetricCard, InsightCard, SectionPanel |
| Elevation usage: only AppCard uses it | AppCard only |
| Color token access: `_colors()` method exists | All design system components |
| Buttons: radius 6px, 8px, 4px | SectionHeader, DialogTemplate, WarningBanner |
| Separator: custom QFrame vs `make_separator()` | AppCard vs everywhere else |

---

## 16. Token Inventory & Status

### Existing Tokens — Status

| Token File | Status | Action |
|------------|--------|--------|
| `tokens/color.py` | ✅ Good structure, needs palette update | Update DarkColorTokens per §7 |
| `tokens/typography.py` | ✅ Good structure, needs scale reduction | Reduce to hero/h1/h2/h3/body/body_small/caption/label/metric per §8 |
| `tokens/spacing.py` | ✅ Excellent | Add/update semantic aliases per §9 |
| `tokens/elevation.py` | Needs rewrite | Replace with color-matched shadow function per §6 |
| `tokens/radius.py` | ✅ Good | Keep |
| `tokens/motion.py` | ✅ Good structure | Add `reduced` flag, add `spring_gentle`/`emphasize` if missing |
| `tokens/icon.py` | ✅ Good | Keep |
| `tokens/layout.py` | ✅ Good | Keep |

### New Tokens Needed

| File | New Content |
|------|-------------|
| `tokens/elevation.py` | Add `GlowTokens` dataclass with primary/success/warning/error glow |
| `tokens/elevation.py` | Add `compute_shadow(bg_color, level, is_dark)` function |
| `tokens/color.py` | Add `glow_*` tokens to all three color schemes |
| `tokens/color.py` | Add `hero_gradient` token |
| `tokens/color.py` | Remove `background_alt` (no longer needed) |
| `tokens/typography.py` | Add `hero` and `metric` to type scale |
| `tokens/typography.py` | Remove `overline` (10px, unused) |

### Dead Code / Redundancies

| Item | Reason | Action |
|------|--------|--------|
| `command_center/theme.py` | Bridge to legacy | Keep for backward compat but mark deprecated |
| `command_center/pages/` | 9 pages not using design system | Full redesign (separate REP) |
| `dashboard/DashboardCard` | Duplicates AppCard | Remove, use AppCard |
| `design_system/visualization/PredictionTimeline` | Duplicates visualization version | Remove |
| `design_system/visualization/WeeklyTimeline` | Duplicates visualization version | Remove |
| `recovery/MetricCard` | Duplicates design system MetricCard | Remove, use design system |
| `narrative/CoachCard` | Outside design system | Migrate to AppCard |
| `KpiStrip` component | Exists but never used | Decide: use or remove |
| `WarningBanner` | Exists but never used | Keep — use in REP-006H |
| `ActivityFeed` | Exists but never used | Keep — use in REP-006H |
| `NotificationToast` | Exists but never used | Keep — use in REP-006H |

---

## 17. Migration Strategy

### Phase 0: Token Updates (No Visual Change)

1. Update `DarkColorTokens` palette per §7
2. Update `ColorTokens` (light) palette per §7
3. Update `HighContrastColorTokens` to match new structure
4. Add `GlowTokens` to `tokens/elevation.py`
5. Add `compute_shadow()` function replacing `apply_elevation()`
6. Add new typography tokens (`hero`, `metric`), remove `overline`
7. Update `SpacingTokens` semantic aliases
8. Add `reduced` flag to `MotionTokens`

**Validation:** All existing tests pass. No visual change visible.

### Phase 1: Component Consistency (Visual Change)

1. **Padding symmetry pass** — All 12 components get symmetric vertical padding
2. **Typography token pass** — All 12 components replace hardcoded font-size with token references
3. **Spacing token pass** — All magic numbers replaced with `SpacingTokens` / `spacing_step()`
4. **Radius consistency pass** — All card components use `RadiusTokens.lg`
5. **Elevation pass** — Apply appropriate elevation level to each component per §6 table
6. **Border update** — Use `rgba(255,255,255,0.06)` style borders
7. **Background shift** — Update `DarkColorTokens.background` → `#0B1120`, `surface` → `#0F172A`

**Validation:** Visual snapshot comparison. Components look more cohesive.

### Phase 2: Layout & Surface

1. **EditorialGrid spacing pass** — Replace `setSpacing(16)` with `S.card_gap`
2. **Page margins** — All pages use `S.page_margin`
3. **SectionPanel consistency** — All pages use `SectionPanel` for grouped content
4. **HeroPanel consistency** — All pages use `HeroPanel` for hero sections

**Validation:** Pages have consistent editorial rhythm.

### Phase 3: Deprecations & Removals

1. Remove `dashboard/DashboardCard` → use `AppCard` where referenced
2. Remove duplicate timeline components
3. Remove `recovery/MetricCard` → use design system `MetricCard`
4. Migrate `narrative/CoachCard` → use `InsightCard` or `AppCard`

**Validation:** No import errors. All tests pass.

### Phase 4: Motion & Polish

1. Add CSS transitions to all interactive components
2. Add glow effects to PR/goal/success states
3. Add reduced-motion support
4. Chart style consistency pass

**Validation:** Motion feels purposeful. Reduced motion respected.

### Effort Estimate

| Phase | Files | Effort |
|-------|-------|--------|
| Phase 0: Token updates | ~6 token files | 1 day |
| Phase 1: Component consistency | ~15 component files | 2 days |
| Phase 2: Layout & surface | ~10 page/layout files | 2 days |
| Phase 3: Deprecations & removals | ~8 files | 1 day |
| Phase 4: Motion & polish | ~20 files | 2 days |
| **Total** | **~59 files** | **~8 days** |

---

## 18. Verification

### Visual Consistency Checklist

- [ ] All cards use same background (`#0F172A`) as the page surface
- [ ] Page background is `#0B1120` (one level darker than cards)
- [ ] All card padding is symmetric (top == bottom)
- [ ] All card-type components use `RadiusTokens.lg` (12px)
- [ ] All non-card components (badges, buttons) use `RadiusTokens.md` (8px)
- [ ] No hardcoded font-size in any component
- [ ] No hardcoded spacing value in any component
- [ ] All borders use `rgba(255,255,255,0.06)` style (semi-transparent)
- [ ] Elevation levels follow the table in §6
- [ ] Glow only appears for achievement states
- [ ] All transitions have `100ms` or `200ms` duration
- [ ] Reduced motion sets all durations to `0ms`
- [ ] Charts share consistent grid/axis/label style
- [ ] KPI values use consistent `metric` font (28px/800)
- [ ] Page headers use consistent `h1` (24px/700) or `hero` (32px/700)

---

*End of RFC-030*
