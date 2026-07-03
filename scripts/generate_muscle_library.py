"""Generate the GymOS muscle library from authoritative data.

Creates knowledge/muscles/<id>.json for every referenced muscle.
Run from project root:  python scripts/generate_muscle_library.py
"""

import json
from pathlib import Path

MUSCLES_DIR = Path("knowledge/muscles")

MUSCLE_DEFINITIONS = [
    {
        "id": "pectoralis_major",
        "display_name": "Pectoralis Major (Sternal)",
        "group": "chest",
        "synergists": ["anterior_deltoid", "triceps_brachii"],
        "antagonists": ["trapezius", "rhomboids"],
        "weekly_volume_landmarks": {
            "mev": {"min_sets": 6, "max_sets": 8, "description": "Minimum 6-8 weekly sets to maintain"},
            "mav": {"min_sets": 10, "max_sets": 16, "description": "Optimal growth at 10-16 sets per week"},
            "mrv": {"min_sets": 18, "max_sets": 22, "description": "Beyond 20 sets risks recovery failure"}
        },
        "recommended_frequency": {"min_times_per_week": 2, "max_times_per_week": 2},
        "recovery_characteristics": {
            "recovery_time_hours": {"min": 48, "max": 72},
            "fatigue_factor": "moderate",
            "description": "Recovers in 2-3 days; well-suited for 2x/week frequency"
        },
        "recommended_exercises": [
            "chest_bench_press", "chest_incline_bench_press", "chest_dumbbell_press",
            "chest_incline_dumbbell", "chest_machine_press", "chest_decline_press",
            "chest_push_ups", "chest_cable_crossover", "chest_pec_deck", "chest_dips"
        ]
    },
]

EXTRA_MUSCLES = [
    {
        "id": "core",
        "display_name": "Core (Composite)",
        "group": "core",
        "synergists": [],
        "antagonists": [],
        "weekly_volume_landmarks": {
            "mev": {"min_sets": 4, "max_sets": 6, "description": "Composite indicator; refer to individual core muscles"},
            "mav": {"min_sets": 8, "max_sets": 14, "description": "Composite; varies by individual muscle"},
            "mrv": {"min_sets": 16, "max_sets": 20, "description": "Composite"}
        },
        "recommended_frequency": {"min_times_per_week": 2, "max_times_per_week": 4},
        "recovery_characteristics": {
            "recovery_time_hours": {"min": 24, "max": 48},
            "fatigue_factor": "low",
            "description": "Composite reference; individual core muscles vary"
        },
        "recommended_exercises": [
            "core_plank", "core_crunch", "core_hanging_leg_raise",
            "core_ab_wheel", "core_pallof_press"
        ]
    },
]

ALL_MUSCLES = MUSCLE_DEFINITIONS + EXTRA_MUSCLES


def main():
    MUSCLES_DIR.mkdir(parents=True, exist_ok=True)
    for muscle in ALL_MUSCLES:
        path = MUSCLES_DIR / f"{muscle['id']}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(muscle, f, indent=2, ensure_ascii=False)
            f.write("\n")
    print(f"[OK] Generated {len(ALL_MUSCLES)} muscle files in {MUSCLES_DIR}/")


if __name__ == "__main__":
    main()
