# Prediction Engine Reference

## Engine Architecture
Each engine is a standalone class in `modules/prediction/engines/__init__.py` with a single `predict()` method returning a `Prediction` domain object.

## Engine Signatures

### PlateauPredictionEngine
```
predict(window, recent_volume_7d, recent_volume_14d, volume_change_percent,
        reps_in_rir_avg, days_since_weight_change, recent_pr_count, 
        session_count_last_14d) -> Prediction
```

### PRPredictionEngine
```
predict(window, recent_prs, recent_volume_trend, consistency_streak,
        average_rir, days_since_last_pr, recovery_score, is_deload_week) -> Prediction
```

### RecoveryPredictionEngine
```
predict(window, recovery_scores, sleep_trend, stress_trend, 
        training_volume_trend, current_recovery_score, days_since_deload) -> Prediction
```

### FatiguePredictionEngine
```
predict(window, current_fatigue, recent_volume_7d, recent_volume_14d,
        sleep_avg, stress_avg, days_since_deload, session_frequency) -> Prediction
```

### BodyweightPredictionEngine
```
predict(window, bodyweight_history, calorie_surplus_avg, 
        current_bodyweight, calorie_adherence) -> Prediction
```

### GoalEtaPredictionEngine
```
predict(current_bodyweight, goal_bodyweight, bodyweight_history,
        calorie_surplus_avg, calorie_adherence, window) -> Prediction
```

### VolumePredictionEngine
```
predict(window, weekly_volumes, estimated_mrv, current_weekly_volume,
        session_count, average_rpe) -> Prediction
```

### ConsistencyPredictionEngine
```
predict(window, current_streak, weekly_consistency, planned_sessions_per_week,
        recent_completion_rate, missed_last_7d, recovery_avg, 
        motivation_score, days_since_last_miss) -> Prediction
```

### DeloadPredictionEngine
```
predict(window, weeks_since_last_deload, recovery_scores, current_fatigue,
        fatigue_trend, volume_ratio_14d_7d, sleep_avg, session_count_7d,
        deload_frequency_weeks) -> Prediction
```

## Prediction Output
Every `predict()` returns a `Prediction` domain object containing:
- `value` — primary predicted metric
- `probability` — confidence in the prediction (0-1)
- `confidence` — `PredictionConfidence` with score, level, factors, sample_size
- `explanation` — `PredictionExplanation` with summary, reasoning, assumptions, risk_factors, evidence
- `forecast` — `Forecast` with `ForecastPoint[]` (date, predicted, lower_bound, upper_bound)
- `scenarios` — `PredictionScenario[]` with best/expected/worst cases
