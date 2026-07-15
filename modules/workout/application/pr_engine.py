"""Personal Record Engine — detects PRs from workout data.

Uses Epley formula from knowledge/progression/rm_estimator.json:
  e1RM = weight * (1 + reps / 30)   (for reps <= 10)
  e1RM = weight * (36 / (37 - reps)) (Brzycki, for reps > 10)

Knowledge source: knowledge/progression/rm_estimator.json
"""

from dataclasses import dataclass
from typing import Any

from modules.workout.domain import WorkoutSession


@dataclass
class PersonalRecord:
    """A personal record achievement."""

    pr_type: str  # "weight", "reps", "volume", "e1rm"
    exercise_name: str
    value: float
    previous_value: float | None = None
    improvement: float | None = None  # percentage improvement
    achieved_at: str | None = None
    session_id: str | None = None

    @property
    def label(self) -> str:
        labels = {
            "weight": "🏆 Weight PR",
            "reps": "🏆 Rep PR",
            "volume": "🏆 Volume PR",
            "e1rm": "🏆 Estimated 1RM PR",
        }
        return labels.get(self.pr_type, "🏆 PR")

    @property
    def display_value(self) -> str:
        if self.pr_type == "e1rm":
            return f"{self.value:.1f} kg"
        return f"{self.value:.0f}"

    @property
    def improvement_text(self) -> str:
        if self.improvement is None:
            return ""
        return f"+{self.improvement:.0f}%"


def _estimate_1rm(weight_kg: float, reps: int) -> float:
    """Estimate 1RM using Epley formula (reps <= 10) or Brzycki (reps > 10)."""
    if reps <= 0 or weight_kg <= 0:
        return 0.0
    if reps <= 10:
        return weight_kg * (1 + reps / 30)
    else:
        return weight_kg * (36 / (37 - reps))


class PREngine:
    """Detects personal records by comparing against historical data."""

    def __init__(self, db: Any) -> None:
        self._db = db

    def detect_prs(self, session: WorkoutSession) -> list[PersonalRecord]:
        """Detect all PRs in a completed session.

        Compares each set against all historical sets for the same exercise.
        Returns a list of PRs found.
        """
        prs: list[PersonalRecord] = []

        for ex in session.exercises:
            if not ex.sets:
                continue

            # Get all historical sets for this exercise (excluding current session)
            historical = self._get_historical_best(ex.name, session.id)

            for s in ex.sets:
                if not s.completed or s.reps <= 0:
                    continue

                # Weight PR
                if s.weight_kg > historical.get("max_weight", 0):
                    prs.append(PersonalRecord(
                        pr_type="weight",
                        exercise_name=ex.name,
                        value=s.weight_kg,
                        previous_value=historical.get("max_weight"),
                        improvement=self._calc_improvement(
                            s.weight_kg, historical.get("max_weight", 0)
                        ),
                    ))

                # Rep PR (at same or higher weight)
                if s.reps > historical.get("max_reps_at_weight", {}).get(s.weight_kg, 0):
                    prs.append(PersonalRecord(
                        pr_type="reps",
                        exercise_name=ex.name,
                        value=float(s.reps),
                        previous_value=float(
                            historical.get("max_reps_at_weight", {}).get(s.weight_kg, 0)
                        ),
                        improvement=self._calc_improvement(
                            float(s.reps),
                            float(historical.get("max_reps_at_weight", {}).get(s.weight_kg, 0)),
                        ),
                    ))

                # Volume PR (weight × reps for this set)
                set_volume = s.weight_kg * s.reps
                if set_volume > historical.get("max_set_volume", 0):
                    prs.append(PersonalRecord(
                        pr_type="volume",
                        exercise_name=ex.name,
                        value=set_volume,
                        previous_value=historical.get("max_set_volume"),
                        improvement=self._calc_improvement(
                            set_volume, historical.get("max_set_volume", 0)
                        ),
                    ))

                # e1RM PR
                e1rm = _estimate_1rm(s.weight_kg, s.reps)
                if e1rm > historical.get("max_e1rm", 0):
                    prs.append(PersonalRecord(
                        pr_type="e1rm",
                        exercise_name=ex.name,
                        value=e1rm,
                        previous_value=historical.get("max_e1rm"),
                        improvement=self._calc_improvement(
                            e1rm, historical.get("max_e1rm", 0)
                        ),
                    ))

        return prs

    def _get_historical_best(self, exercise_name: str,
                             exclude_session_id: str | None = None) -> dict:
        """Get the best historical values for an exercise."""
        sessions = self._db.list_sessions(limit=500)

        result = {
            "max_weight": 0.0,
            "max_reps_at_weight": {},
            "max_set_volume": 0.0,
            "max_e1rm": 0.0,
        }

        for s in sessions:
            if exclude_session_id and s.id == exclude_session_id:
                continue
            for ex in s.exercises:
                if ex.name != exercise_name:
                    continue
                for st in ex.sets:
                    if not st.completed or st.reps <= 0:
                        continue
                    if st.weight_kg > result["max_weight"]:
                        result["max_weight"] = st.weight_kg

                    result["max_reps_at_weight"][st.weight_kg] = max(
                        result["max_reps_at_weight"].get(st.weight_kg, 0),
                        st.reps,
                    )

                    sv = st.weight_kg * st.reps
                    if sv > result["max_set_volume"]:
                        result["max_set_volume"] = sv

                    e1rm = _estimate_1rm(st.weight_kg, st.reps)
                    if e1rm > result["max_e1rm"]:
                        result["max_e1rm"] = e1rm

        return result

    def get_all_prs(self, exercise_name: str) -> list[PersonalRecord]:
        """Get all historical PRs for an exercise."""
        sessions = self._db.list_sessions(limit=500)
        all_prs: list[PersonalRecord] = []

        for s in sessions:
            if not s.completed_at:
                continue
            prs = self.detect_prs(s)
            all_prs.extend(
                p for p in prs if p.exercise_name == exercise_name
            )

        return all_prs

    def get_latest_prs(self, limit: int = 10) -> list[PersonalRecord]:
        """Get the most recent PRs across all exercises."""
        sessions = self._db.list_sessions(limit=200)
        all_prs: list[PersonalRecord] = []

        for s in sessions:
            if not s.completed_at:
                continue
            prs = self.detect_prs(s)
            for p in prs:
                p.achieved_at = (
                    s.started_at.isoformat() if s.started_at else None
                )
                p.session_id = s.id
            all_prs.extend(prs)

        # Deduplicate by keeping the most recent PR per exercise+type
        seen: dict[tuple[str, str], PersonalRecord] = {}
        for p in all_prs:
            key = (p.exercise_name, p.pr_type)
            if key not in seen:
                seen[key] = p

        # Sort by most recent first
        sorted_prs = sorted(
            seen.values(),
            key=lambda p: p.achieved_at or "",
            reverse=True,
        )
        return sorted_prs[:limit]

    def get_best_prs(self) -> list[PersonalRecord]:
        """Get the best PR achieved for each exercise+type combination."""
        sessions = self._db.list_sessions(limit=500)
        best: dict[tuple[str, str], PersonalRecord] = {}

        for s in sessions:
            if not s.completed_at:
                continue
            prs = self.detect_prs(s)
            for p in prs:
                key = (p.exercise_name, p.pr_type)
                if key not in best or p.value > best[key].value:
                    p.achieved_at = (
                        s.started_at.isoformat() if s.started_at else None
                    )
                    p.session_id = s.id
                    best[key] = p

        return sorted(best.values(), key=lambda p: p.exercise_name)

    @staticmethod
    def _calc_improvement(new: float, old: float) -> float:
        if old <= 0:
            return 0.0  # First PR ever — no comparison to show
        return ((new - old) / old) * 100
