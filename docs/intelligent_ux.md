# Intelligent UX — RFC-028

## Overview

The Intelligent UX layer transforms raw platform metrics into concise, coach-like narratives. It is a deterministic template engine — no AI, no calculations — that consumes existing `CommandCenterData` and renders it as structured `Narrative` objects displayed in `CoachCard` widgets with progressive disclosure.

## Architecture

```
ui/narrative/
├── __init__.py          # Public API — re-exports everything
├── engine.py            # NarrativeEngine + Narrative dataclass + Tone/Length enums
├── templates/           # 12 template functions (one per briefing type)
│   ├── __init__.py
│   ├── morning_brief.py
│   ├── today_focus.py
│   ├── recovery_summary.py
│   ├── prediction_summary.py
│   ├── planning_summary.py
│   ├── knowledge_summary.py
│   ├── adaptive_summary.py
│   ├── weekly_review.py
│   ├── milestone_celebration.py
│   ├── risk_alerts.py
│   ├── achievement_feed.py
│   └── decision_feed.py
├── cards.py             # CoachCard (expand/collapse) + CoachCardStack
└── micro.py             # CelebrationOverlay, AchievementBadge, MilestoneIndicator

ui/intelligence/
├── __init__.py
└── narrative_page.py    # IntelligencePage — Command Center integration
```

## Narrative Dataclass

```python
@dataclass
class Narrative:
    title: str                          # Brief title
    summary: str = ""                   # 1-2 sentence summary
    body: str = ""                      # Medium paragraph
    detail: str = ""                    # Full detail
    tone: Tone = Tone.COACH             # COACH or SCIENTIFIC
    action_items: list[str] = []        # Suggested actions
    source_keys: list[str] = []         # Data provenance
    metadata: dict = {}                 # Extensible (e.g., {"severity": "critical"})
```

Three length levels for progressive disclosure: `SHORT` (summary), `MEDIUM` (body), `DETAILED` (detail).

## NarrativeEngine

```python
engine = NarrativeEngine()
engine.register("morning_brief", morning_brief)
n = engine.render("morning_brief", readiness_score=85, sleep_hours=7.5)
```

- Deterministic: same inputs → same outputs
- No business logic, no AI, no calculations
- Unknown template name returns `None` (safe fallback)
- `render_all()` iterates all registered templates

## CoachCard

A `QFrame`-based card that displays a `Narrative` with:

- **Collapsed state**: Title + severity indicator (color dot) + summary + expand button
- **Expanded state**: Full body text + action buttons
- **Signals**: `expand_clicked()`, `action_clicked(str)`

```python
card = CoachCard(narrative)
card.action_clicked.connect(lambda action: print(f"Do: {action}"))
```

`CoachCardStack` manages a vertical list of cards with `add_card()`, `clear()`, `narratives()`.

## Micro UX

- **CelebrationOverlay**: Full-bleed milestone achievement card with icon, title, close button, `closed` signal
- **AchievementBadge**: Compact achievement feed item with name, description, points, hover effect
- **MilestoneIndicator**: Progress bar with label for milestone tracking

## Template Library (12 templates)

| Template | Inputs | Output |
|----------|--------|--------|
| `morning_brief` | readiness_score, recovery_score, fatigue_score, sleep_hours | Morning readiness summary with actions based on thresholds |
| `today_focus` | primary_goal, workout_type, focus_areas, intensity | Today's training focus with day name |
| `recovery_summary` | recovery_score, sleep_hours, hrv, muscle_soreness | Recovery status with recommendations |
| `prediction_summary` | prediction_label, confidence, target_date | Confidence-based prediction insight |
| `planning_summary` | phase_name, week_number, sessions | Mesocycle planning status |
| `knowledge_summary` | topic, insight, relevance | Domain knowledge insight |
| `adaptive_summary` | adaptation_type, description, applied | Adaptive change applied/recommended |
| `weekly_review` | week_number, sessions, volume, prs | Weekly performance roundup |
| `milestone_celebration` | milestone_name, value, target | Achievement celebration text |
| `risk_alerts` | list of {title, severity, action} | Alert summary with severity tracking |
| `achievement_feed` | list of {name, description, points} | Achievement feed summary |
| `decision_feed` | list of {title, status, reason} | Decision tracking summary |

The `metadata.severity` field on `Narrative` is used by `CoachCard` to color the severity indicator dot (critical=red, warning=yellow, info=blue, success=green).

## IntelligencePage

Registered as `"intelligence"` in the Command Center navigation rail (between Adaptive and Analytics). It:

1. Receives `CommandCenterData` via `update_data()`
2. Extracts nested data: `recovery_overview`, `training_readiness`, `current_mesocycle`, `prediction_summary`, etc.
3. Renders all available templates with extracted data
4. Populates a `CoachCardStack`

The page is auto-refreshed every 60 seconds via the existing CommandCenter refresh timer.

## Key Design Principles

- **No business logic**: Templates only format text, never compute metrics
- **Deterministic**: Same data → same narrative; testable with unit tests
- **Progressive disclosure**: Users see summaries, expand for detail
- **Design system compliant**: All widgets use `color_from_scheme(ColorScheme.DARK)` and the 8-point spacing grid
- **Theme-aware**: Colors adapt automatically via `DarkColorTokens`
- **Keyboard accessible**: Action buttons are `QPushButton` with cursor feedback
