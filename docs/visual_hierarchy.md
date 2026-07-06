# Visual Hierarchy — RFC-027

Defines the editorial layout system and visual weight distribution used across all GymOS Command Center pages.

## Layout Grid

All pages use a 12-column `EditorialGrid` from the design system (`ui/design_system/layout/editorial_grid.py`). Column spans are defined by `PanelSpan`:

| PanelSpan     | Columns | Usage                         |
|---------------|---------|-------------------------------|
| `FULL`        | 12      | Full-width sections           |
| `HERO`        | 8       | Hero sections                 |
| `TWO_THIRDS`  | 8       | Primary content panels        |
| `HALF`        | 6       | Balanced content split        |
| `THIRD`       | 4       | Tertiary / sidebar panels     |
| `QUARTER`     | 3       | Four-column layouts           |

## Page Structure

Every page follows a three-tier editorial hierarchy:

```
┌──────────────────────────────────────────┐
│  SectionHeader (title + subtitle)        │  ← Title bar (full width)
├──────────────────────────────────────────┤
│  HeroPanel (accent bar + headline)       │  ← Hero section (full width)
├──────────────────┬───────────────────────┤
│                  │                       │
│  SectionPanel    │  SectionPanel         │  ← Content grid (asymmetric)
│  (span: HALF)    │  (span: HALF)         │
│                  │                       │
├──────────────────┴───────────────────────┤
│  SectionPanel (span: FULL)               │  ← Full-width lower section
└──────────────────────────────────────────┘
```

### Tier 1 — Hero
- `SectionHeader`: Page title with breadcrumb-style subtitle (e.g. "Volume · Recovery · Nutrition · PR · Compliance")
- `HeroPanel`: Accent-bar header with page headline, optional gauge/ring, and subtitle

### Tier 2 — Content Grid
- Asymmetric layout using `EditorialGrid` with sections at `HALF`, `THIRD`, or `TWO_THIRDS` span
- Each `SectionPanel` has a title, optional subtitle, and child content (labels, charts, gauges)

### Tier 3 — Lower Sections
- Full-width panels for dense data (knowledge graphs, capability tables, kernel runtime)

## Visual Weight Distribution

| Element            | Weight | Typography                                     |
|--------------------|--------|------------------------------------------------|
| SectionHeader      | High   | `font_style("heading", 2)` + muted subtitle    |
| HeroPanel          | High   | `font_style("heading", 1)` + "heading", 5      |
| SectionPanel title | Medium | `font_style("heading", 4)`                     |
| Metric values      | High   | `font_style("display", 2)` or "display", 1     |
| Body text          | Low    | `font_style("body", 2)` — 13px                 |
| Labels / captions  | Lowest | `font_style("caption")` — 11px muted           |

## Spacing

- Page padding: `32px` horizontal, `24px` vertical, `24px` between sections
- Grid spacing: `16px` between cells
- Inner section padding: `16px`
- Uses 8-point spacing grid (`spacing.s8`, `s16`, `s24`, `s32`)

## Color Usage

| Token                | Usage                              |
|----------------------|------------------------------------|
| `colors.background`  | Page background                    |
| `colors.surface`     | SectionPanel / HeroPanel bg        |
| `colors.border`      | Section borders                    |
| `colors.accent`      | Hero accent bar, active indicators |
| `colors.text_primary`| Headings, metric values            |
| `colors.text_secondary`| Subtitles, secondary text        |
| `colors.text_disabled` | Empty state, placeholder        |
| `colors.accent_success`| Positive trends                 |
| `colors.accent_warning` | Warning thresholds              |
| `colors.accent_danger`  | Critical values                 |

## Page Inventory

### P1 — Core (redesigned)
- **Home**: Hero (RecoveryRing + GoalRing + Readiness Metric) → 3-column (Insights/Prediction/Planning) → 2-column (Recovery/Knowledge)
- **Mission**: Hero (RecoveryRing + intent label) → Intent/Readiness/Adaptive/Decision sections

### P2 — Secondary (redesigned)
- **Prediction Center**: Hero (ConfidenceGauge + RiskMeter) → Prediction Timeline + Accuracy Metrics
- **Recovery Center**: Hero (RecoveryRing + RiskMeter) → Recovery/Readiness/Trend sections
- **Planning**: Hero (GoalRing + cycle name) → Mesocycle/Weekly/Volume sections

### P3 — Tertiary (redesigned)
- **Knowledge Center**: Hero → HALF/HALF (Insights + Updates) → FULL (Knowledge Graph)
- **Adaptive Center**: Hero (ConfidenceGauge) → HALF/HALF (Adaptive + Decision timelines)
- **Analytics Center**: Hero → THIRD/THIRD/THIRD (Volume + Compliance + PRs)
- **System Center**: Hero (ConfidenceGauge) → THIRD/THIRD/THIRD (Health + Product + Release) → HALF/HALF (Capabilities + Kernel)
