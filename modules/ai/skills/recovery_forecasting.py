def forecast_recovery(
    sleep_hours: float,
    stress_level: int,
    soreness_level: int,
    previous_scores: list[float]
) -> dict:
    """Forecasts recovery and readiness based on sleep, stress, soreness, and previous history."""
    avg_prev = sum(previous_scores) / len(previous_scores) if previous_scores else 70.0
    
    # Sleep bonus/penalty (optimal: 8.0 hours)
    sleep_factor = (sleep_hours - 8.0) * 5.0
    
    # Stress penalty (1: low, 5: high)
    stress_factor = (stress_level - 2) * -6.0
    
    # Soreness penalty (1: low, 5: high)
    soreness_factor = (soreness_level - 2) * -8.0
    
    forecasted = avg_prev * 0.4 + (75.0 + sleep_factor + stress_factor + soreness_factor) * 0.6
    forecasted = max(0.0, min(100.0, forecasted))
    
    if forecasted >= 85:
        level = "Optimal"
        desc = "Your recovery is excellent. You are ready to push high intensity and progressive overload."
    elif forecasted >= 70:
        level = "Good"
        desc = "You are well recovered. Normal training volume is recommended."
    elif forecasted >= 55:
        level = "Moderate"
        desc = "CNS fatigue detected. Consider avoiding training to failure or reduce intensity."
    else:
        level = "Critical"
        desc = "Severe recovery deficit. High risk of injury. Recommend active recovery or rest."
        
    return {
        "forecasted_score": round(forecasted, 1),
        "level": level,
        "description": desc
    }
