"""Volume Analytics — weekly training volume by muscle group.

Tracks total working sets per muscle group per week and compares against
optimal ranges from knowledge/progression/volume.md.

Knowledge source: knowledge/progression/volume.md
"""

from dataclasses import dataclass, field
from datetime import datetime

# Exercise → muscle group mapping
# Based on seed data exercises
EXERCISE_MUSCLE_MAP = {
    "Incline Barbell Press": "chest",
    "Dumbbell Overhead Press": "shoulders",
    "Dips": "chest",
    "Lateral Raise": "shoulders",
    "Tricep Pushdown": "triceps",
    "Face Pull": "shoulders",
    "Barbell Row": "back",
    "Lat Pulldown": "back",
    "Seated Cable Row": "back",
    "Barbell Curl": "biceps",
    "Hammer Curl": "biceps",
    "Barbell Squat": "quads",
    "Leg Press": "quads",
    "Romanian Deadlift": "hamstrings",
    "Leg Extension": "quads",
    "Leg Curl": "hamstrings",
    "Standing Calf Raise": "calves",
    "Barbell Bench Press": "chest",
    "Overhead Press": "shoulders",
    "Pull-Up": "back",
    "Dumbbell Row": "back",
    "EZ Bar Curl": "biceps",
    "Tricep Overhead Extension": "triceps",
    "Deadlift": "back",
    "Hack Squat": "quads",
    "Bulgarian Split Squat": "quads",
    "Seated Calf Raise": "calves",
    "Hyperextension": "back",
}


# Optimal weekly sets per muscle group from knowledge/progression/volume.md
VOLUME_LANDMARKS = {
    "chest": {"min": 8, "optimal_min": 14, "optimal_max": 18, "max": 22},
    "back": {"min": 10, "optimal_min": 16, "optimal_max": 20, "max": 25},
    "shoulders": {"min": 8, "optimal_min": 14, "optimal_max": 18, "max": 22},
    "biceps": {"min": 6, "optimal_min": 12, "optimal_max": 16, "max": 20},
    "triceps": {"min": 6, "optimal_min": 12, "optimal_max": 16, "max": 20},
    "quads": {"min": 6, "optimal_min": 12, "optimal_max": 16, "max": 20},
    "hamstrings": {"min": 6, "optimal_min": 10, "optimal_max": 14, "max": 18},
    "calves": {"min": 4, "optimal_min": 8, "optimal_max": 12, "max": 16},
    "abs": {"min": 4, "optimal_min": 8, "optimal_max": 12, "max": 16},
}


@dataclass
class MuscleVolume:
    """Volume data for a single muscle group in a week."""

    muscle_group: str
    total_sets: int = 0
    total_volume_kg: float = 0.0
    landmark_min: int = 0
    landmark_optimal_min: int = 0
    landmark_optimal_max: int = 0
    landmark_max: int = 0

    @property
    def status(self) -> str:
        """Traffic light status."""
        if self.total_sets < self.landmark_min:
            return "low"  # Red — below minimum
        elif self.total_sets < self.landmark_optimal_min:
            return "building"  # Yellow — approaching optimal
        elif self.total_sets <= self.landmark_optimal_max:
            return "optimal"  # Green — in optimal zone
        elif self.total_sets <= self.landmark_max:
            return "maintenance"  # Blue — above optimal but safe
        else:
            return "high"  # Red — above maximum, risk of overtraining

    @property
    def status_color(self) -> str:
        colors = {
            "low": "#F87171",
            "building": "#FBBF24",
            "optimal": "#4ADE80",
            "maintenance": "#60A5FA",
            "high": "#F87171",
        }
        return colors.get(self.status, "#94A3B8")

    @property
    def status_label(self) -> str:
        labels = {
            "low": "Too Low",
            "building": "Building",
            "optimal": "Optimal",
            "maintenance": "Maintenance",
            "high": "Too High",
        }
        return labels.get(self.status, "Unknown")


@dataclass
class WeeklyVolumeReport:
    """Complete weekly volume analysis."""

    week_label: str
    muscles: list[MuscleVolume] = field(default_factory=list)
    total_sets: int = 0
    total_volume_kg: float = 0.0


class VolumeAnalytics:
    """Calculates weekly training volume by muscle group."""

    def __init__(self, db) -> None:
        self._db = db

    def get_weekly_volume(self, weeks: int = 4) -> list[WeeklyVolumeReport]:
        """Get weekly volume broken down by muscle group.

        Args:
            weeks: Number of past weeks to analyse

        Returns:
            List of WeeklyVolumeReport, one per week
        """
        sessions = self._db.list_sessions(limit=200)
        weekly_data: dict[str, dict[str, dict]] = {}

        for s in sessions:
            if not s.started_at:
                continue

            week_key = s.started_at.strftime("%Y-W%V")

            if week_key not in weekly_data:
                weekly_data[week_key] = {}

            for ex in s.exercises:
                muscle = self._get_muscle_group(ex.name)

                completed_sets = [
                    st for st in ex.sets if st.completed and st.reps > 0
                ]
                if not completed_sets:
                    continue

                if muscle not in weekly_data[week_key]:
                    weekly_data[week_key][muscle] = {
                        "sets": 0,
                        "volume": 0.0,
                    }

                weekly_data[week_key][muscle]["sets"] += len(completed_sets)
                weekly_data[week_key][muscle]["volume"] += sum(
                    st.weight_kg * st.reps for st in completed_sets
                )

        # Convert to report objects
        reports = []
        sorted_weeks = sorted(weekly_data.keys(), reverse=True)[:weeks]

        for week in reversed(sorted_weeks):
            muscles = []
            total_sets = 0
            total_volume = 0.0

            for muscle_name, data in sorted(
                weekly_data[week].items(),
                key=lambda x: x[1]["sets"],
                reverse=True,
            ):
                landmarks = VOLUME_LANDMARKS.get(muscle_name, {})
                mv = MuscleVolume(
                    muscle_group=muscle_name,
                    total_sets=data["sets"],
                    total_volume_kg=data["volume"],
                    landmark_min=landmarks.get("min", 0),
                    landmark_optimal_min=landmarks.get("optimal_min", 0),
                    landmark_optimal_max=landmarks.get("optimal_max", 10),
                    landmark_max=landmarks.get("max", 20),
                )
                muscles.append(mv)
                total_sets += data["sets"]
                total_volume += data["volume"]

            reports.append(WeeklyVolumeReport(
                week_label=week,
                muscles=muscles,
                total_sets=total_sets,
                total_volume_kg=total_volume,
            ))

        return reports

    def get_current_week_volume(self) -> WeeklyVolumeReport:
        """Get volume for the current week only."""
        reports = self.get_weekly_volume(weeks=1)
        return reports[0] if reports else WeeklyVolumeReport(
            week_label=datetime.now().strftime("%Y-W%V")
        )

    @staticmethod
    def _get_muscle_group(exercise_name: str) -> str:
        """Map an exercise name to its primary muscle group."""
        # Direct lookup
        if exercise_name in EXERCISE_MUSCLE_MAP:
            return EXERCISE_MUSCLE_MAP[exercise_name]

        # Fuzzy match by keywords
        name_lower = exercise_name.lower()
        keyword_map = {
            "chest": ["chest", "bench", "fly", "pec"],
            "back": ["row", "pulldown", "pull", "deadlift", "back", "lat"],
            "shoulders": ["shoulder", "raise", "press", "ohp", "overhead",
                          "face pull", "lateral", "rear delt"],
            "biceps": ["curl", "bicep", "preacher"],
            "triceps": ["tricep", "pushdown", "extension", "skull", "dip"],
            "quads": ["squat", "leg press", "leg extension", "quad",
                      "lunges", "step-up", "hack"],
            "hamstrings": ["leg curl", "hamstring", "rdl", "romanian",
                           "good morning", "glute"],
            "calves": ["calf", "calf raise"],
            "abs": ["crunch", "plank", "ab", "leg raise", "pallof"],
        }

        for muscle, keywords in keyword_map.items():
            for kw in keywords:
                if kw in name_lower:
                    return muscle

        return "other"

    @staticmethod
    def get_all_muscle_groups() -> list[str]:
        """Get all tracked muscle groups."""
        return list(VOLUME_LANDMARKS.keys())
