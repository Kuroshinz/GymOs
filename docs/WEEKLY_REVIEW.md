# Weekly Review

## Overview

The `WeeklyReviewGenerator` creates a structured summary of the past 7 days of training. It combines data from sessions, PR engine, muscle analysis, bodyweight tracking, and fatigue analysis.

## Output Model

```python
@dataclass
class WeeklyReview:
    week_label: str                  # "Jun 25 – Jul 2, 2026"
    total_workouts: int              # Sessions completed
    total_sets: int                  # Sets across all sessions
    total_volume_kg: float           # Total volume (weight × reps)
    best_pr: str                     # Best PR achieved this week
    most_improved_muscle: str        # Muscle with largest volume increase
    lowest_volume_muscle: str        # Muscle with lowest volume
    missed_sessions: int             # Expected - completed
    recovery_score: str              # Excellent/Good/Fair/Poor
    bodyweight_change: float         # End - start weight
    next_week_priorities: list[str]  # Top 5 action items
    fatigue_level: str               # From FatigueAnalyzer
    recommendations_count: int       # Active recommendations
```

## Analysis Components

### Muscle Volume Analysis
- Compares current week vs previous week effective volume per muscle
- Identifies most improved and lowest volume muscles
- Uses `VolumeEngine` for contribution-based calculation

### PR Detection
- Queries `PREngine.detect_prs()` for each session
- Returns the most significant PR label

### Recovery Scoring
- Counts recovery flags across all sessions
- 0 flags → Excellent, 1-2 → Good, 3-5 → Fair, 6+ → Poor

### Bodyweight Tracking
- Calculates change over the week
- Uses latest two bodyweight entries

### Priority Generation
- If sessions missed → complete sessions
- If muscle below MEV → increase volume
- If muscle above MRV → reduce volume
- Fallback: continue current plan + progressive overload

## Usage

```python
from modules.gymbrain import WeeklyReviewGenerator

gen = WeeklyReviewGenerator(provider)
review = gen.generate()
print(review.to_dict())
```
