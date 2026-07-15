from modules.ai.skills.recovery_forecasting import forecast_recovery

def generate_counterfactual(
    baseline_sleep: float,
    baseline_stress: int,
    baseline_soreness: int,
    previous_scores: list[float],
    modified_parameters: dict
) -> dict:
    """Simulates a counterfactual recovery scenario by tweaking input parameters."""
    baseline = forecast_recovery(baseline_sleep, baseline_stress, baseline_soreness, previous_scores)
    
    sim_sleep = modified_parameters.get("sleep_hours", baseline_sleep)
    sim_stress = modified_parameters.get("stress_level", baseline_stress)
    sim_soreness = modified_parameters.get("soreness_level", baseline_soreness)
    
    simulated = forecast_recovery(sim_sleep, sim_stress, sim_soreness, previous_scores)
    
    delta = simulated["forecasted_score"] - baseline["forecasted_score"]
    
    return {
        "baseline_score": baseline["forecasted_score"],
        "simulated_score": simulated["forecasted_score"],
        "delta": round(delta, 1),
        "impact_level": "positive" if delta > 5 else "negative" if delta < -5 else "neutral",
        "baseline_level": baseline["level"],
        "simulated_level": simulated["level"]
    }
