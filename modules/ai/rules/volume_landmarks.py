def calculate_volume_landmarks(muscle_group: str, weekly_sets: int) -> dict:
    """Calculates hypertrophy volume landmarks status based on target muscle and weekly sets."""
    landmarks = {
        "chest": {"MEV": 10, "MAV_min": 12, "MAV_max": 20, "MRV": 22},
        "back": {"MEV": 10, "MAV_min": 12, "MAV_max": 22, "MRV": 25},
        "quads": {"MEV": 8, "MAV_min": 10, "MAV_max": 18, "MRV": 20},
        "hamstrings": {"MEV": 6, "MAV_min": 8, "MAV_max": 15, "MRV": 18},
        "biceps": {"MEV": 8, "MAV_min": 10, "MAV_max": 20, "MRV": 22},
        "triceps": {"MEV": 6, "MAV_min": 8, "MAV_max": 16, "MRV": 18},
    }
    
    muscle_lower = muscle_group.lower()
    data = landmarks.get(muscle_lower, {"MEV": 8, "MAV_min": 10, "MAV_max": 18, "MRV": 20})
    
    mrv = data["MRV"]
    mev = data["MEV"]
    
    if weekly_sets < mev:
        status = "Below MEV (Maintenance/Under-training)"
    elif weekly_sets <= data["MAV_max"]:
        status = "Within MAV (Optimal Hypertrophy)"
    elif weekly_sets < mrv:
        status = "Near MRV (High Volume)"
    else:
        status = "Above MRV (Overreaching/Over-training)"
        
    return {
        "muscle_group": muscle_group,
        "weekly_sets": weekly_sets,
        "MEV": mev,
        "MAV_range": f"{data['MAV_min']}-{data['MAV_max']}",
        "MRV": mrv,
        "status": status
    }
