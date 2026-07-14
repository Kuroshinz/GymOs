"""Double Progression Engine — standalone business service.

Recommends whether to increase weight or stay at current weight based on
the Double Progression method from knowledge/progression/double_progression.md.

Rules:
  1. If all sets reach the upper rep target with acceptable RIR → recommend weight increase
  2. Otherwise → recommend keeping current weight
  3. Support configurable rep ranges
  4. Track sessions at current weight to gauge progress

Knowledge sources:
  - knowledge/progression/double_progression.md
  - knowledge/user/training.md
"""

from dataclasses import dataclass, field

from modules.workout.domain import SessionSet, WorkoutSession


@dataclass
class ProgressionRecommendation:
    """Recommendation for a single exercise."""

    exercise_name: str
    current_weight: float
    current_reps: list[int]
    target_reps: str  # e.g., "8-12"
    all_sets_at_top: bool
    should_increase: bool
    suggested_weight: float
    suggested_reps: str
    reason: str
    sessions_at_current_weight: int = 0
    progress_percent: float = 0.0  # 0-100% through the rep range

    @property
    def target_low(self) -> int:
        parts = self.target_reps.split("-")
        return int(parts[0]) if parts else 8

    @property
    def target_high(self) -> int:
        parts = self.target_reps.split("-")
        return int(parts[1]) if len(parts) > 1 else 12


@dataclass
class WorkoutRecommendation:
    """Complete recommendation for an entire workout session."""

    day_name: str
    exercise_recommendations: list[ProgressionRecommendation] = field(default_factory=list)
    all_completed: bool = False


# Default weight increments by exercise type
# From knowledge/user/training.md
WEIGHT_INCREMENT = {
    "upper_compound": 2.5,   # 1.25-2.5 kg
    "lower_compound": 5.0,   # 2.5-5 kg
    "isolation": 1.25,       # 1.25-2.5 kg
    "machine": 2.5,          # 2.5-5 kg
}


def _classify_exercise(name: str) -> str:
    """Classify an exercise into a weight increment category."""
    compound_exercises = [
        "press", "bench", "squat", "deadlift", "row", "pull-up",
        "pullup", "pulldown", "overhead", "dips", "dip",
    ]
    isolation_exercises = [
        "raise", "curl", "extension", "fly", "kickback",
        "shrug", "crunch", "leg extension", "leg curl",
    ]
    machine_keywords = ["machine", "hack", "smith", "seated calf"]

    name_lower = name.lower()
    for kw in machine_keywords:
        if kw in name_lower:
            return "machine"
    for kw in isolation_exercises:
        if kw in name_lower:
            return "isolation"
    for kw in compound_exercises:
        if kw in name_lower:
            return "upper_compound"
    return "isolation"  # default


class ProgressionEngine:
    """Double progression business logic.

    Rules (from knowledge/progression/double_progression.md):
      1. Stay at same weight until hitting top of rep range on ALL sets
      2. Increase weight by smallest increment
      3. Support configurable rep ranges
    """

    def __init__(self, db) -> None:
        self._db = db

    def analyse_exercise(
        self,
        exercise_name: str,
        sets: list[SessionSet],
        target_reps: str = "8-12",
        acceptable_rir: int = 2,
    ) -> ProgressionRecommendation:
        """Analyse a single exercise and return a progression recommendation.

        Args:
            exercise_name: Name of the exercise
            sets: List of completed session sets
            target_reps: Target rep range as "low-high" (e.g., "8-12")
            acceptable_rir: Maximum RIR considered acceptable for progression
                           (default 2 means 0-2 RIR is good)

        Returns:
            ProgressionRecommendation with suggestion
        """
        target_reps = target_reps.replace("\u2013", "-").replace("\u2014", "-")
        parts = target_reps.split("-")
        target_low = int(parts[0]) if parts else 8
        target_high = int(parts[1]) if len(parts) > 1 else 12

        completed_sets = [s for s in sets if s.completed and s.reps > 0]

        if not completed_sets:
            return ProgressionRecommendation(
                exercise_name=exercise_name,
                current_weight=0,
                current_reps=[],
                target_reps=target_reps,
                all_sets_at_top=False,
                should_increase=False,
                suggested_weight=0,
                suggested_reps=target_reps,
                reason="No completed sets to analyse.",
            )

        current_weight = max(s.weight_kg for s in completed_sets)
        current_reps = [s.reps for s in completed_sets]

        # Check if all sets reached the top of the rep range
        all_at_top = all(r >= target_high for r in current_reps)

        # Check RIR is acceptable (if RIR is recorded)
        rir_acceptable = True
        for s in completed_sets:
            if s.rir is not None and s.rir > acceptable_rir:
                rir_acceptable = False
                break

        # Calculate progress percent through the rep range
        avg_reps = sum(current_reps) / len(current_reps)
        range_width = target_high - target_low
        if range_width > 0:
            progress_percent = max(
                0.0, min(100.0, ((avg_reps - target_low) / range_width) * 100)
            )
        else:
            progress_percent = 100.0 if avg_reps >= target_high else 0.0

        # Count sessions at current weight
        sessions_at_weight = self._count_sessions_at_weight(
            exercise_name, current_weight
        )

        # Decide: should we increase?
        should_increase = all_at_top and rir_acceptable

        if should_increase:
            increment = WEIGHT_INCREMENT.get(
                _classify_exercise(exercise_name), 2.5
            )
            suggested_weight = current_weight + increment
            suggested_reps = f"{target_low}-{target_high}"
            reason = (
                f"Hit top of rep range ({target_high}) on all {len(completed_sets)} sets "
                f"with acceptable RIR. Increase to {suggested_weight:.1f} kg."
            )
        else:
            suggested_weight = current_weight
            suggested_reps = target_reps
            if not all_at_top:
                reason = (
                    f"Build reps. Target: {target_reps}. "
                    f"Current: {', '.join(str(r) for r in current_reps)}. "
                    f"Aim for {target_high} on all sets before increasing weight."
                )
            else:
                reason = (
                    "Reps look good. Keep current weight and focus on "
                    "technique and controlled eccentrics."
                )

        return ProgressionRecommendation(
            exercise_name=exercise_name,
            current_weight=current_weight,
            current_reps=current_reps,
            target_reps=target_reps,
            all_sets_at_top=all_at_top,
            should_increase=should_increase,
            suggested_weight=suggested_weight,
            suggested_reps=suggested_reps,
            reason=reason,
            sessions_at_current_weight=sessions_at_weight,
            progress_percent=progress_percent,
        )

    def analyse_workout(
        self,
        session: WorkoutSession,
        target_reps_map: dict[str, str] | None = None,
    ) -> WorkoutRecommendation:
        """Analyse all exercises in a workout and return recommendations.

        Args:
            session: The completed workout session
            target_reps_map: Optional dict mapping exercise names to target rep ranges

        Returns:
            WorkoutRecommendation with per-exercise suggestions
        """
        recommendations = []
        all_completed = True

        for ex in session.exercises:
            ex_name = ex.name
            target = (target_reps_map or {}).get(
                ex_name, self._get_default_rep_range(ex_name)
            )
            rec = self.analyse_exercise(ex_name, ex.sets, target)
            recommendations.append(rec)

            if not rec.should_increase and rec.current_weight > 0:
                all_completed = False  # At least one exercise hasn't maxed out

        return WorkoutRecommendation(
            day_name=session.day_name,
            exercise_recommendations=recommendations,
            all_completed=all_completed,
        )

    def get_recommendation(
        self, exercise_name: str, target_reps: str = "8-12"
    ) -> ProgressionRecommendation:
        """Get a recommendation based on the most recent session data.

        This is used to show recommendations BEFORE the user starts an exercise.
        """
        prev = self._db.get_last_session_for_exercise(exercise_name)
        if not prev:
            return ProgressionRecommendation(
                exercise_name=exercise_name,
                current_weight=0,
                current_reps=[],
                target_reps=target_reps,
                all_sets_at_top=False,
                should_increase=False,
                suggested_weight=0,
                suggested_reps=target_reps,
                reason="No previous data. Start with a comfortable weight.",
            )

        # Convert previous session data to SessionSet objects
        sets = [
            SessionSet(
                set_number=i + 1,
                weight_kg=s.get("weight", 0.0) or 0.0,
                reps=s.get("reps", 0) or 0,
                rir=s.get("rir"),
            )
            for i, s in enumerate(prev.sets)
        ]

        return self.analyse_exercise(exercise_name, sets, target_reps)

    def _count_sessions_at_weight(
        self, exercise_name: str, weight: float
    ) -> int:
        """Count how many sessions this exercise has been done at the given weight."""
        if weight <= 0:
            return 0
        sessions = self._db.list_sessions(limit=200)
        count = 0
        for s in sessions:
            for ex in s.exercises:
                if ex.name != exercise_name:
                    continue
                for st in ex.sets:
                    if st.completed and st.weight_kg == weight:
                        count += 1
                        break
                break  # Only count once per session
        return count

    @staticmethod
    def _get_default_rep_range(exercise_name: str) -> str:
        """Get the default rep range based on exercise type."""
        name_lower = exercise_name.lower()
        compound_keywords = [
            "press", "bench", "squat", "deadlift", "row",
            "pulldown", "pull-up", "pullup", "dip",
        ]
        for kw in compound_keywords:
            if kw in name_lower:
                return "8-12"
        return "10-15"
