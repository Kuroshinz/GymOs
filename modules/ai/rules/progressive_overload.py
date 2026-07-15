def evaluate_progressive_overload(
    reps: list[int],
    rir: list[int],
    current_weight: float,
    target_reps: int = 10,
    target_rir: int = 2
) -> dict:
    """Evaluates progressive overload rules based on rep & RIR consistency."""
    if not reps or not rir:
        return {
            "should_increase": False,
            "suggested_weight": current_weight,
            "reason": "No set data provided"
        }
    
    # Check if all completed sets meet or exceed the target rep and target RIR criteria
    all_met = all(r >= target_reps for r in reps) and all(ri >= target_rir for ri in rir)
    if all_met:
        suggested = current_weight + 2.5
        return {
            "should_increase": True,
            "suggested_weight": suggested,
            "reason": f"Completed all sets at reps >= {target_reps} and RIR >= {target_rir}. Recommended weight increase to {suggested}kg."
        }
    
    return {
        "should_increase": False,
        "suggested_weight": current_weight,
        "reason": "Progression criteria not met. Maintain current weight."
    }
