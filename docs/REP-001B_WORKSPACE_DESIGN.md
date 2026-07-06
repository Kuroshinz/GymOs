# REP-001B — Workspace UX Redesign

## Status: Approved

| Field | Value |
|-------|-------|
| **Author** | NEXUS Architect |
| **Date** | 2026-07-06 |
| **Supersedes** | REP-001A (UI Standardization) |
| **Applies to** | `ui/command_center/pages/`, `ui/command_center/command_center.py`, `ui/command_center/navigation/`, `ui/design_system/` |

---

## Philosophy

GymOS should not look like "a dashboard made by developers." It should look like a premium desktop operating system for hypertrophy coaching. Every workspace must have its own visual identity while sharing a consistent token system underneath.

The redesign follows five principles:

1. **Editorial, not dashboard** — asymmetric magazine layouts, not symmetric card grids
2. **Progressive disclosure** — show the headline first, reveal detail on demand
3. **Workspace identity** — each workspace has a unique layout signature, not a template
4. **Visual rhythm** — varying panel sizes, hero treatments, and spacing create flow
5. **Action-oriented** — every workspace has a clear primary and secondary action

---

## Workspace Mapping

| Old Name | New Name | Page ID | Layout Signature |
|----------|----------|---------|-----------------|
| Home | Executive Dashboard | `executive` | Full-bleed hero + magazine spread + KPI bar |
| Mission | Goal Workspace | `goal` | Goal card hero + progress ribbon + timeline |
| Planning | Planning Studio | `planning` | Cycle timeline hero + volume chart + week editor |
| Prediction | Forecast Studio | `forecast` | Confidence splash hero + scenario grid |
| Recovery | Recovery Center | `recovery` | Score monument hero + 3-column vitals |
| Knowledge | Knowledge Explorer | `knowledge` | Graph header hero + insight cards |
| Adaptive | Optimization Center | `optimization` | Adaptation flow hero + decision log |
| Analytics | Performance Lab | `performance` | Data wall hero + metric clusters |
| System | Platform Console | `platform` | Status bar hero + capability grid |
| Intelligence | AI Briefing Center | `briefing` | AI persona hero + briefing cards |

---

## Before / After

### Before (all workspaces)
```
┌──────────────────────────────────────────┐
│  SectionHeader (title + subtitle)        │  ← Same pattern on every page
├──────────────────────────────────────────┤
│  HeroPanel (text + ring/gauge)           │  ← Same HeroPanel on every page
├──────────────────┬───────────────────────┤
│  SectionPanel    │  SectionPanel         │  ← Same 50/50 or 33/33/33 split
│  (THIRD/HALF)    │  (THIRD/HALF)         │
├──────────────────┴───────────────────────┤
│  SectionPanel (FULL)                     │  ← Same full-width bottom
└──────────────────────────────────────────┘
```

### After (unique per workspace)
```
┌─ EXECUTIVE ──────────────────────────────┐
│  ██████████████████████████████████████  │  ← Full-bleed hero with stats overlay
│  ◉ Recovery  ◉ Goal  ▶ Start Workout    │
├───┬───┬───┬───┬───┬───┬───┬───┬───┬───┤  ← KPI bar (score, volume, adherence...)
├──────────────────┬──────────────────────┤
│  Insight Panel   │  Activity Timeline    │  ← Asymmetric content
│  (span: 7)       │  (span: 5)            │
├──────────────────┴──────────────────────┤
│  Recommendations │ Warnings │ Detail     │  ← Bottom ribbon
└──────────────────────────────────────────┘
```

---

## Layout Signatures

### 1. Executive Dashboard (`executive`)

**Layout signature:** Full-bleed hero + KPI bar + magazine spread

```
┌──────────────────────────────────────────┐
│  ◉ Recovery (80)  ◉ Goal (67/75)        │
│  "Ready to train — PPL-UL Week 3/6"     │
│  [Start Workout] [Log Weight]            │  ← Primary/Secondary actions
├───┬───┬───┬───┬───┬───┬───┬───┬───┬───┤
│78%│85%│12 │3/5│72%│ ✓ │67%│+2 │1.2│94%│  ← KPI strip
├──────────────────────┬──────────────────┤
│  Top Insights        │  Recent Activity │
│  • Volume up 12%     │  • PPL-UL W3D1   │
│  • Recovery trending │  • PR: Bench 90kg│
│  • Deload needed W7  │  • Weight logged │
├──────────┬───────────┴──────────────────┤
│ Warn     │ Recommendation                │
│ Fatigue↓ │ Focus on recovery today       │
└──────────┴───────────────────────────────┘
```

**Visual hierarchy:**
- Tier 1: Hero area (recovery ring + goal ring + readiness statement)
- Tier 2: KPI strip (10 metrics in a single horizontal bar, scrollable)
- Tier 3: Asymmetric content split (insights 7 cols, activity 5 cols)
- Tier 4: Bottom ribbon (warning + recommendation)

**Unique elements:** Full-bleed hero background, persistent KPI bar, activity feed

---

### 2. Goal Workspace (`goal`)

**Layout signature:** Goal card hero + progress ribbon + timeline

```
┌──────────────────────────────────────────┐
│  [Build Muscle]                          │
│  ●●●●●●●○○○  67% to target (75kg)      │
│  [Adjust Goal] [View History]            │
├──────────┬───────────┬───────────────────┤
│ Week 3/8 │ +0.4kg/wk │ Projected: Oct 12│
│ Phase:   │ Adherence │ 85% confidence   │
│ Hypertrophy│ 92%     │                   │
├──────────┴───────────┴───────────────────┤
│  Decision Timeline                        │
│  ┌──────────────────────────────────┐    │
│  │ ● Wk1: Started PPL-UL           │    │
│  │ ● Wk2: +2.5kg on bench          │    │
│  │ ● Wk3: Deload pushed to W8      │    │
│  └──────────────────────────────────┘    │
├──────────────────┬──────────────────────┤
│ Insights         │ Warnings              │
│ • Rate on track  │ • Shoulders lagging   │
│ • Nutrition good │ • Sleep dip detected  │
└──────────────────┴───────────────────────┘
```

**Visual hierarchy:**
- Tier 1: Large goal card with progress bar (not a ring)
- Tier 2: 3-column KPI cluster (week, rate, projection)
- Tier 3: Decision timeline (full width)
- Tier 4: Insight + warning split

**Unique elements:** Progress bar hero, decision timeline, projection card

---

### 3. Planning Studio (`planning`)

**Layout signature:** Cycle timeline hero + volume chart + week editor

```
┌──────────────────────────────────────────┐
│  Mesocycle: PPL-UL Block 1              │
│  Week 3 ████████░░░░░░░░░░░░ 6 weeks    │
│  Phase: Hypertrophy                      │
│  [Adjust Week] [View Program]            │
├───────┬───────┬───────┬───────┬─────────┤
│Volume │Sets/wk│  PRs  │Deload │ Recovery│
│ 12,450│  22   │   3   │  W7   │   78%   │
├───────┴───────┴───────┴───────┴─────────┤
│  Weekly Volume Trend                      │
│  ▁▃▅█▇▆▄▃▅▆▇█▅▄▃▃▅▇█▆▅▄▃▅ (chart)       │
├──────────────────────┬──────────────────┤
│ This Week's Sessions │ Recommendations  │
│ ☑ Push (Tue) 45:00  │ • Increase dips  │
│ ☐ Pull (Thu)        │ • Reduce back vol│
│ ☐ Legs (Sat)        │ • Add face pulls │
└──────────────────────┴──────────────────┘
```

**Visual hierarchy:**
- Tier 1: Cycle progress bar hero (not a ring)
- Tier 2: 5-column KPI cluster
- Tier 3: Volume trend chart (full width)
- Tier 4: Sessions checklist + recommendations

**Unique elements:** Week progress bar, program breadcrumb, session checklist

---

### 4. Forecast Studio (`forecast`)

**Layout signature:** Confidence splash hero + scenario grid

```
┌──────────────────────────────────────────┐
│  Forecast Confidence: 85%                 │
│  ████████████████████░░░░░░ 85%         │
│  [Run Scenario] [Export Report]          │
├───┬───┬───┬───┬───┬───┬───┬───┬───┬───┤
│PR  │Vol │BW  │Reco│Adh │Risk│Lo  │Hi  │Trend
│72kg│14.5│64kg│78% │85% │Low │61.5│64.5│ ↑  │
├───────┴───┴───┴───┴───┴───┴───┴───┴───┤
│  Prediction Timeline (area chart)         │
│  ┌──────────────────────────────────┐    │
│  │ ╱╲    ╱╲    ╱╲  BW trend         │    │
│  │╱  ╲  ╱  ╲  ╱  ╲  63.4→64.8      │    │
│  └──────────────────────────────────┘    │
├──────────────────┬──────────────────────┤
│ Scenarios        │ Risk Assessment       │
│ • Conservative   │ • Overtraining: Low   │
│ • Aggressive     │ • Nutrition: Medium   │
│ • Current path   │ • Sleep: Good         │
└──────────────────┴──────────────────────┘
```

**Visual hierarchy:**
- Tier 1: Large confidence bar hero (horizontal, not ring)
- Tier 2: KPI strip (prediction-specific metrics)
- Tier 3: Prediction timeline (area chart)
- Tier 4: Scenario cards + risk grid

**Unique elements:** Horizontal confidence bar, scenario comparison, risk matrix

---

### 5. Recovery Center (`recovery`)

**Layout signature:** Score monument hero + 3-column vitals

```
┌──────────────────────────────────────────┐
│          78                               │
│        RECOVERY SCORE                     │
│     ████████████░░░░ 78/100              │
│  [View Details] [View Trends]             │
├───────────┬───────────┬──────────────────┤
│ Sleep 75  │ Stress 82 │ Fatigue 68       │
│ ███████   │ ████████  │ ██████           │
│ 7.5 hrs   │ Low       │ Moderate         │
├───────────┴───────────┴──────────────────┤
│  7-Day Recovery Trend                     │
│  ┌──────────────────────────────────┐    │
│  │  ▁▃▅▆▇▆▅▄▃▅▆▇▆▅▄▃▅▆▇             │    │
│  └──────────────────────────────────┘    │
├──────────────────┬──────────────────────┤
│ Readiness Detail │ Warnings & Flags      │
│ • Score: 82      │ ⚠ Sleep dip last 3d  │
│ • Level: Good    │ ⚠ Stress elevated    │
│ • Limiting: Sleep │ ⚠ Deload approaching│
└──────────────────┴──────────────────────┘
```

**Visual hierarchy:**
- Tier 1: Large score monument (number + label, no ring)
- Tier 2: 3-column vitals with bars
- Tier 3: 7-day trend chart (full width)
- Tier 4: Readiness detail + warnings

**Unique elements:** Score monument, vitals with horizontal bars, trend chart

---

### 6. Knowledge Explorer (`knowledge`)

**Layout signature:** Graph header hero + insight cards

```
┌──────────────────────────────────────────┐
│  Knowledge Graph: 142 nodes · 389 edges  │
│  [Explore Graph] [Search Knowledge]       │
├───┬───┬───┬───┬───┬───┬───┬───┬───┬───┤
│Ins │Rel │Upd │Con │Pat │New │Chg │Exp │
│ 12 │ 5  │ 23 │87% │ 8  │ 3  │ 2  │1d  │
├───────┴───┴───┴───┴───┴───┴───┴───┴───┤
│  Knowledge Updates (timeline)             │
│  ┌──────────────────────────────────┐    │
│  │ 📝 Nutrition: protein timing     │    │
│  │ 📊 Recovery: sleep + hypertrophy │    │
│  │ 🔬 Training: ROM for hypertrophy │    │
│  └──────────────────────────────────┘    │
├──────────────────────┬──────────────────┤
│ Top Insights         │ Confidence Trend  │
│ • Protein 1.6g/kg    │ ██████████ 95%   │
│ • Sleep 7-9h         │ ████████░░ 78%   │
│ • Volume 10-20 sets/w│ ██████░░░░ 62%   │
└──────────────────────┴──────────────────┘
```

**Visual hierarchy:**
- Tier 1: Knowledge graph summary hero (node/edge count)
- Tier 2: Knowledge-specific KPI strip
- Tier 3: Updates timeline (full width, with timestamps)
- Tier 4: Top insights + confidence breakdown

**Unique elements:** Graph summary hero, knowledge KPI strip, confidence breakdown

---

### 7. Optimization Center (`optimization`)

**Layout signature:** Adaptation flow hero + decision log

```
┌──────────────────────────────────────────┐
│  Optimization Score: 84%                  │
│  Adaptation Flow: Training ▸ Recovery ▸  │
│  [Review Decision] [Run Simulation]      │
├───────┬───────┬───────┬───────┬─────────┤
│Adapts │Decis  │Conf   │Impacts│ Rollback│
│  18   │  12   │ 82%   │   +4  │   0%    │
├───────┴───────┴───────┴───────┴─────────┤
│  Decision Timeline (full width)           │
│  ┌──────────────────────────────────┐    │
│  │ ✓ Wk3: +2.5kg bench approved     │    │
│  │ ✓ Wk2: Nutrition adjusted        │    │
│  │ ✓ Wk1: Started PPL-UL            │    │
│  └──────────────────────────────────┘    │
├──────────────────┬──────────────────────┤
│ Strategy Summary │ Recommendations       │
│ • Progressive    │ • Increase volume     │
│ • Conservative   │ • Monitor recovery    │
│ • Data-driven    │ • Adjust nutrition    │
└──────────────────┴──────────────────────┘
```

**Visual hierarchy:**
- Tier 1: Flow diagram hero (optimization score + chain)
- Tier 2: 5-column KPI cluster
- Tier 3: Decision timeline
- Tier 4: Strategy summary + recommendations

**Unique elements:** Flow hero with chain visualization, decision log, strategy cards

---

### 8. Performance Lab (`performance`)

**Layout signature:** Data wall hero + metric clusters

```
┌──────────────────────────────────────────┐
│  Performance Overview                      │
│  12,450 kg total volume this week         │
│  [Export Report] [Compare Periods]        │
├───────┬───────┬───────┬───────┬─────────┤
│Volume │Comply │  PRs  │  Freq │ Sessions│
│12,450 │  85%  │   5   │  4/wk │   12    │
├───────┴───────┴───────┴───────┴─────────┤
│  Performance Charts (full width)          │
│  ┌──────────────────────────────────┐    │
│  │ Volume ██▄▆▇█▅▄▃▅▇█▆▄▃▄▅▇█▅▄▃  │    │
│  │ Compliance ████████░░░░ 85%     │    │
│  │ PR trend ▃▆▇█▇▆▅▇█▇▆▅▄▅▇█▇▆     │    │
│  └──────────────────────────────────┘    │
├──────────────────────┬──────────────────┤
│ Recent PRs           │ Muscle Balance    │
│ • Bench: +5kg (Jul)  │ ██ Chest         │
│ • Squat: +10kg (Jun) │ ██ Back          │
│ • Deadlift: +8kg (Jun)│ ██ Legs          │
└──────────────────────┴──────────────────┘
```

**Visual hierarchy:**
- Tier 1: Data wall hero (large metric with supporting stats)
- Tier 2: 5-column KPI cluster
- Tier 3: Performance charts (stacked multi-chart)
- Tier 4: PR list + muscle balance

**Unique elements:** Data wall hero, stacked charts, muscle balance visualization

---

### 9. Platform Console (`platform`)

**Layout signature:** Status bar hero + capability grid

```
┌──────────────────────────────────────────┐
│  System Health: 92% ██████████░░        │
│  All systems operational                 │
│  [View Logs] [Run Diagnostics]           │
├───────┬───────┬───────┬───────┬─────────┤
│Arch   │Tests  │Docs   │Caps   │ Runtime │
│ 88%   │92%    │78%    │12/15  │  3.2h   │
├───────┴───────┴───────┴───────┴─────────┤
│  Capability Progress (full width grid)   │
│  ┌──────────────────────────────────┐    │
│  │ Training    ██████████░░ 85%     │    │
│  │ Nutrition   ████████░░░░ 72%     │    │
│  │ Recovery    █████████░░░ 80%     │    │
│  │ Prediction  ██████░░░░░░ 60%     │    │
│  │ Knowledge   █████████░░░ 78%     │    │
│  └──────────────────────────────────┘    │
├──────────────────┬──────────────────────┤
│ Release Readiness│ Kernel Runtime        │
│ v0.5.0           │ • Status: Running    │
│ Blockers: 0      │ • Uptime: 3.2h      │
│ Gap: 1 milestone │ • Plugins: 8 active │
└──────────────────┴──────────────────────┘
```

**Visual hierarchy:**
- Tier 1: Status bar hero (horizontal health bar)
- Tier 2: 5-column KPI cluster
- Tier 3: Capability progress bars
- Tier 4: Release readiness + kernel runtime

**Unique elements:** Health bar hero, capability grid, runtime status

---

### 10. AI Briefing Center (`briefing`)

**Layout signature:** AI persona hero + briefing cards

```
┌──────────────────────────────────────────┐
│  AI Briefing: Thursday, July 6           │
│  "You're on track for 75kg by Oct"       │
│  [Generate Briefing] [Configure AI]      │
├───────────┬───────────┬──────────────────┤
│Confidence │Insights   │ Recommendations  │
│   87%     │    12     │        5         │
├───────────┴───────────┴──────────────────┤
│  Today's Briefing (full width cards)      │
│  ┌──────────────────────────────────┐    │
│  │ 📊 Training: Volume trending up  │    │
│  │ 🥗 Nutrition: Hitting protein    │    │
│  │ 😴 Recovery: Sleep needs work    │    │
│  │ ⚠ Warning: Deload approaching    │    │
│  └──────────────────────────────────┘    │
├──────────────────┬──────────────────────┤
│ Knowledge Updates│ Recommendation Detail │
│ • 3 updates today│ • Focus on sleep     │
│ • 1 new insight  │ • Increase protein   │
│ • 2 patterns     │ • Deload on W7       │
└──────────────────┴──────────────────────┘
```

**Visual hierarchy:**
- Tier 1: AI persona hero (personality + headline)
- Tier 2: 3-column KPI cluster
- Tier 3: Briefing cards (full-width, staggered)
- Tier 4: Knowledge updates + recommendation detail

**Unique elements:** AI persona hero, briefing cards, structured recommendation

---

## Editorial Layout Principles

### Progressive Disclosure

Every workspace reveals information in three depths:

| Depth | What | Access |
|-------|------|--------|
| **Glance** | Hero area + KPI strip | Always visible |
| **Scan** | Insight panel + timeline + primary content | Scroll once |
| **Deep** | Expandable detail panels | Click/expand |

### Visual Rhythm

- **Hero areas** vary between pages: some use rings, some bars, some text
- **KPI strips** have different metric counts (5, 8, or 10)
- **Grid splits** vary: 7/5, 6/6, 8/4 — never the same ratio on adjacent pages
- **Bottom sections** alternate between 2-column, 3-column, and full-width
- **Spacing** varies: 24px between sections, 16px between panels, but hero areas use larger 32px margins

### Color Signatures

Each workspace gets an accent color from the design token system:

| Workspace | Accent | Mood |
|-----------|--------|------|
| Executive | Primary (indigo) | Commanding |
| Goal | Success (green) | Progress |
| Planning | Primary (indigo) | Structural |
| Forecast | Info (blue) | Analytical |
| Recovery | Warning (amber) | Cautious |
| Knowledge | Secondary (violet) | Exploratory |
| Optimization | Success (green) | Optimistic |
| Performance | Primary (indigo) | Data-driven |
| Platform | Neutral (slate) | Technical |
| Briefing | Accent (rose) | Conversational |

---

## New Components

### KpiStrip
A horizontal bar of compact KPI metrics for the second tier of every workspace.

**Location:** `ui/design_system/layout/kpi_strip.py`

**Props:** list of `(label, value, unit, trend, color)` tuples

### InsightCard
A compact card for displaying a single insight with icon, title, and description.

**Location:** `ui/design_system/components/insight_card.py`

### WarningBanner
A horizontal warning/alert banner with icon, message, and optional action.

**Location:** `ui/design_system/components/warning_banner.py`

### ActivityFeed
A vertical list of activity items with timestamp and status.

**Location:** `ui/design_system/components/activity_feed.py`

---

## Navigation Rationale

### Sidebar (NavigationRail)
- Workspace names updated to new naming
- Icons updated to be more descriptive
- Active state uses workspace accent color
- Compact mode available for width-constrained layouts

### Breadcrumb
- Path reflects workspace hierarchy:
  - `Executive Dashboard` (root)
  - `Executive Dashboard > Goal Workspace`
  - `Executive Dashboard > AI Briefing Center > Forecast Studio`

### Command Palette (Ctrl+K)
- Search by new workspace names
- Aliases for old names maintained for backward compatibility

---

## Interaction Flow

1. User clicks sidebar item → workspace loads (no animation on first load)
2. Hero area fades in → KPI strip slides up → content panels stagger in (200ms delay each)
3. Hovering a KPI metric shows tooltip with historical context
4. Clicking an insight card expands it into a detail panel
5. Primary action buttons are prominent (colored, on the hero)
6. Secondary actions are text links below primary
7. Scroll is smooth with section anchors

---

## Remaining Issues

1. **Animation system** — The current `animation_manager.py` needs wiring to the page transitions. The stagger-in animations are defined but not connected to workspace pages yet.
2. **Expandable detail panels** — The underlying `DetailPanel` component needs a slide animation. Currently implemented as a basic show/hide.
3. **KPI strip scrolling** — On narrower windows, the KPI strip should horizontally scroll. Implement with QScrollArea.
4. **Responsive breakpoints** — The current layout uses fixed column spans. At <1200px width, some workspaces should collapse to single-column. This requires `LayoutBreakpoint` integration.
5. **Color signatures** — Per-workspace accent colors are defined in this document but the theme system needs a workspace color mapping API.
6. **IntelligencePage** — Currently lives in `ui/intelligence/` outside the command center page structure. Should be moved to `ui/command_center/pages/` for consistency.

---

## Verification Checklist

- [ ] All 10 pages instantiate without error
- [ ] `update_data()` accepts `CommandCenterData` and renders correctly
- [ ] Navigation switches between all workspaces
- [ ] Breadcrumb shows correct paths
- [ ] No cross-module imports added
- [ ] No business logic modified
- [ ] No platform engines modified
- [ ] All UI tests pass with no regressions
- [ ] Design tokens used throughout (no hardcoded colors)

---

## Migration Path

1. **Phase 1** (this change): Redesign 10 workspace pages, update navigation, create new layout components
2. **Phase 2** (future): Wire animation system, add responsive breakpoints
3. **Phase 3** (future): Move IntelligencePage into command center page structure
4. **Phase 4** (future): Add workspace color signature API to theme system
