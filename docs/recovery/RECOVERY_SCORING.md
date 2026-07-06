# Recovery Scoring

## Recovery Score (0-100)

The composite recovery score is computed as:

```
raw = (100 - training_fatigue) * 0.25  +
      sleep_score            * 0.35  +
      (100 - stress_score)   * 0.15  +
      bodyweight_trend       * 0.05  +
      nutrition_adherence    * 0.10  +
      consistency            * 0.05  +
      deload_benefit         * 0.05

muscle_adjustment = muscle_recovery / 100.0  (0.0-1.0)
overall = raw * (0.85 + muscle_adjustment * 0.15)
overall = clamp(overall, 0, 100)
```

## Readiness Score

```
readiness = overall_score - training_fatigue * 0.3 * 0.1
readiness = clamp(readiness, 0, 100)
```

## Readiness Levels

| Score Range | Level | Volume Modifier | Intensity Modifier |
|-------------|-------|-----------------|--------------------|
| 80-100 | READY | 1.0 | 1.0 |
| 60-79 | GOOD | 0.95 | 0.95 |
| 40-59 | CAUTION | 0.80 | 0.85 |
| 20-39 | FATIGUED | 0.60 | 0.70 |
| 0-19 | DELOAD | 0.40 | 0.50 |

## Fatigue Score

Composite fatigue is the inverse of recovery:

```
fatigue = training_fatigue * 0.30 +
          (100 - sleep_score) * 0.25 +
          stress_score * 0.20 +
          soreness_score * 0.15 +
          subjective_score * 0.10
```

## Sleep Score

```
duration_score = 0-60 (based on hours vs sleep_need)
quality_score = 0-40 (based on SleepQuality enum)
total = (duration + quality) * sensitivity
```

## Stress Score

```
base = {VERY_LOW: 5, LOW: 15, MODERATE: 35, HIGH: 60, VERY_HIGH: 85}
total = base * sensitivity
```

## Deload Benefit

| Days Since Deload | Benefit Score |
|-------------------|---------------|
| 0-7 | 100 |
| 8-14 | 80 |
| 15-21 | 60 |
| 22-42 | 40 |
| 43+ | 20 |
