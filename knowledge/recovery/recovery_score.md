# Recovery Score

## Concept

A composite metric that estimates the user's readiness to train.  
Combines multiple recovery signals into a single score (1-10).

Higher score = more recovered = more intense session possible.

## Components

| Factor | Weight | Source | Notes |
|--------|--------|--------|-------|
| Sleep quality | 30% | User log / wearable | Hours + subjective quality |
| Sleep duration | 20% | User log / wearable | 7-9h optimal |
| HRV (if available) | 20% | Wearable | Morning readiness |
| Subjective fatigue | 15% | User input | 1-5 scale |
| Muscle soreness | 10% | User input | 1-5 scale |
| Previous day's training | 5% | Workout data | Volume + intensity of last session |

## Score Interpretation

| Score | Meaning | Training Recommendation |
|-------|---------|------------------------|
| 9-10 | Fully recovered | Train as planned, can push intensity |
| 7-8 | Moderately recovered | Train as planned, normal intensity |
| 5-6 | Slightly fatigued | Train but reduce RPE by 1-2 |
| 3-4 | Significantly fatigued | Light session or rest day |
| 1-2 | Severe fatigue | Rest day, consider deload |

## Implementation Notes

- Recovery score is a GUIDELINE, not a prescription
- The user should have final say (they know their body)
- Score improves with consistent sleep, nutrition, and deload management
- Not available in MVP — planned for v0.2 recovery module

## References

- Halson (2014) — monitoring training load and fatigue
- Buchheit (2014) — HRV and training readiness
- Saw et al. (2016) — subjective measures of recovery
