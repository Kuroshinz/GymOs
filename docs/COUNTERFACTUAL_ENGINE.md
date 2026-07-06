# Counterfactual Engine

## Overview

The Counterfactual Engine generates deterministic alternatives for any recommendation or decision. Every alternative includes expected outcome, risk assessment, and confidence score — all computed without AI or LLM.

## CounterfactualAction

| Action | Description |
|---|---|
| `INCREASE_VOLUME` | Increase training volume (e.g., sets, reps) |
| `MAINTAIN_VOLUME` | Keep current volume unchanged |
| `DECREASE_VOLUME` | Decrease training volume |
| `INCREASE_FREQUENCY` | Increase sessions per week |
| `DECREASE_FREQUENCY` | Decrease sessions per week |
| `MODIFY_EXERCISE` | Substitute exercises for different stimulus |
| `ADJUST_NUTRITION` | Change nutrition targets |
| `ADJUST_RECOVERY` | Enhance recovery protocols |
| `ADJUST_INTENSITY` | Change load/RPE targets |
| `ADJUST_GOAL` | Reprioritize goals |

## Counterfactual

```python
@dataclass
class Counterfactual:
    counterfactual_id: str
    action: CounterfactualAction
    label: str
    description: str
    current_value: str
    proposed_value: str
    expected_outcome: str
    risk: float          # 0.0 (safe) to 1.0 (critical)
    confidence: float    # 0.0 to 1.0
    delta: dict
    timestamp: str
```

### Properties

| Property | Returns |
|---|---|
| `is_safe` | `risk < 0.5` |
| `risk_label` | Low (< 0.25), Moderate (< 0.5), High (< 0.75), Critical |

## Risk Assessment

| Action | Risk Level |
|---|---|
| MAINTAIN_VOLUME | 0.1 (Very Low) |
| DECREASE_FREQUENCY | 0.1 (Very Low) |
| ADJUST_RECOVERY | 0.1 (Very Low) |
| DECREASE_VOLUME | 0.15 (Very Low) |
| ADJUST_GOAL | 0.2 (Low) |
| ADJUST_NUTRITION | 0.25 (Low) |
| MODIFY_EXERCISE | 0.3 (Low) |
| INCREASE_FREQUENCY | 0.5 (Moderate) |
| ADJUST_INTENSITY | 0.55 (Moderate) |
| INCREASE_VOLUME | 0.6 (Moderate) |

## CounterfactualEngine API

| Method | Description |
|---|---|
| `generate(action, current, context)` | Generate a single counterfactual |
| `generate_all(current, context)` | Generate all 10 alternatives (sorted by confidence) |
| `generate_for_volume(current)` | Volume alternatives (increase, maintain, decrease) |
| `generate_for_frequency(current)` | Frequency alternatives |
| `generate_for_adjustment(current)` | Adjustment alternatives |
| `compare(counterfactuals)` | Sort by confidence descending |
| `get_history()` | All generated counterfactuals |
| `clear_history()` | Clear generation history |

## Deterministic Proposal Computation

When `current_value` is numeric (e.g., "12 sets", "4 sessions"):
- **Increase**: proposed = current × 1.15
- **Decrease**: proposed = current × 0.85
- **Adjust Intensity**: proposed = current × 1.05
- **Maintain**: proposed = action label

## Example

```python
from shared.explainability import create_explainability_platform

platform = create_explainability_platform()

# Generate all alternatives for current volume
alternatives = platform.counterfactual.generate_all(current_value="12 sets")

for alt in alternatives:
    print(f"{alt.action.label}: {alt.proposed_value} | Risk: {alt.risk_label} | Confidence: {alt.confidence:.0%}")

# Get only volume alternatives
volume_opts = platform.counterfactual.generate_for_volume("12 sets")
```
