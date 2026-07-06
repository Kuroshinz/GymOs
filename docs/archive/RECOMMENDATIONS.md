# Recommendation System

## Recommendation Model

Every GymBrain output is a structured `Recommendation` object:

```python
@dataclass
class Recommendation:
    id: str                    # UUID hex (12 chars)
    category: RecommendationCategory  # 12 categories
    priority: int              # 10-90 (CRITICAL=90 to INFO=10)
    title: str                 # Short action-oriented title
    description: str           # Detailed explanation
    reason: str                # Why this recommendation exists
    confidence: float          # 0.0-1.0
    evidence: list[str]        # Data points that triggered this
    action: RecommendationAction | None  # Structured action data
    rule_name: str             # Which rule produced this
    created_at: datetime
    expires_at: datetime       # Default: 7 days from creation
```

## Categories

| Category | Value | Example |
|----------|-------|---------|
| TRAINING | training | Adjust exercise selection |
| NUTRITION | nutrition | Increase calories |
| RECOVERY | recovery | Add rest day |
| PROGRESSION | progression | Increase weight |
| TECHNIQUE | technique | Review form |
| EXERCISE_ORDER | exercise_order | Reorder exercises |
| DELOAD | deload | Schedule deload week |
| PROGRAM_ADJUSTMENT | program_adjustment | Change program |
| CONSISTENCY | consistency | Complete sessions |
| EXERCISE_SELECTION | exercise_selection | Add new exercise |
| VOLUME | volume | Adjust set count |
| FREQUENCY | frequency | Add training day |

## Priorities

| Level | Value | Meaning |
|-------|-------|---------|
| CRITICAL | 90 | Immediate action required (deload, injury prevention) |
| HIGH | 70 | Take action this week |
| MEDIUM | 50 | Address soon |
| LOW | 30 | Nice-to-have |
| INFO | 10 | Informational only |

## Action Types

Each recommendation has a structured `action` field:

```python
@dataclass
class RecommendationAction:
    type: str          # Machine-readable action type
    params: dict       # Action-specific parameters
    display: str       # Human-readable action text
```

Common action types:
- `increase_load` — increase weight on an exercise
- `deload` — schedule a deload week
- `increase_volume` — add sets for a muscle group
- `decrease_volume` — reduce sets
- `increase_calories` — eat more
- `reduce_calories` — eat less
- `technique_review` — review exercise form
- `increase_rest` — rest more between sets
- `improve_consistency` — complete sessions
- `programming_change` — modify program
- `monitor_recovery` — keep an eye on things

## Explainability

Every recommendation includes its complete reasoning chain:

```json
{
  "title": "Increase Incline DB Press by 2.5 kg",
  "reason": "All target reps completed for consecutive sessions with RIR >= 2",
  "evidence": ["Current weight: 50kg", "Reps completed: 12", "RIR: 2"],
  "confidence": 0.95,
  "rule_name": "progression_rule"
}
```

## Serialization

All recommendation and analysis models support `to_dict()` for JSON serialization,
making them easy to consume by any UI layer or notification system.
