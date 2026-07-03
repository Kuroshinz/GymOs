from __future__ import annotations

from datetime import datetime
from typing import Any

from modules.gymbrain.models.analysis import PlateauResult, PlateauType
from modules.gymbrain.providers.data_provider import DataProvider


class PlateauDetector:
    """Detects training plateaus across multiple dimensions.

    Each detection method is independent and returns a PlateauResult.
    """

    def __init__(self, provider: DataProvider) -> None:
        self._provider = provider

    def detect_weight_plateau(self, exercise_name: str, sessions: list[Any] | None = None) -> PlateauResult:
        if sessions is None:
            sessions = self._provider.list_sessions(limit=50)

        weights: list[tuple[datetime, float]] = []
        for s in sessions:
            if not hasattr(s, "exercises") or not hasattr(s, "started_at"):
                continue
            for ex in s.exercises:
                if not hasattr(ex, "name") or ex.name != exercise_name or not hasattr(ex, "sets"):
                    continue
                best_weight = max((getattr(se, "weight_kg", 0) for se in ex.sets), default=0)
                if best_weight > 0 and s.started_at:
                    weights.append((s.started_at, best_weight))

        if len(weights) < 3:
            return PlateauResult(
                plateau_type=PlateauType.WEIGHT,
                exercise_name=exercise_name,
                explanation=f"Not enough data to detect weight plateau for {exercise_name}",
            )

        weights.sort(key=lambda x: x[0])
        recent = weights[-3:]
        unique_weights = set(round(w, 1) for _, w in recent)

        if len(unique_weights) <= 2:
            span_days = (recent[-1][0] - recent[0][0]).days
            severity = "mild" if span_days < 14 else "moderate" if span_days < 28 else "significant"
            return PlateauResult(
                plateau_type=PlateauType.WEIGHT,
                detected=True,
                duration_days=span_days,
                severity=severity,
                exercise_name=exercise_name,
                current_value=recent[-1][1],
                previous_best=max(w for _, w in weights[:-3]) if len(weights) > 3 else recent[-1][1],
                explanation=f"Weight on {exercise_name} has stalled at ~{recent[-1][1]}kg for {span_days} days. "
                            f"Consider a technique deload, rep scheme change, or exercise variation.",
                suggested_action="deload_or_vary" if span_days >= 21 else "monitor",
            )

        return PlateauResult(
            plateau_type=PlateauType.WEIGHT,
            exercise_name=exercise_name,
            explanation=f"Weight is progressing on {exercise_name}",
        )

    def detect_rep_plateau(self, exercise_name: str, sessions: list[Any] | None = None) -> PlateauResult:
        if sessions is None:
            sessions = self._provider.list_sessions(limit=50)

        rep_data: list[tuple[datetime, int]] = []
        for s in sessions:
            if not hasattr(s, "exercises") or not hasattr(s, "started_at"):
                continue
            for ex in s.exercises:
                if not hasattr(ex, "name") or ex.name != exercise_name or not hasattr(ex, "sets"):
                    continue
                max_reps = max((getattr(se, "reps", 0) for se in ex.sets), default=0)
                if max_reps > 0 and s.started_at:
                    rep_data.append((s.started_at, max_reps))

        if len(rep_data) < 3:
            return PlateauResult(
                plateau_type=PlateauType.REP,
                exercise_name=exercise_name,
                explanation=f"Not enough data to detect rep plateau for {exercise_name}",
            )

        rep_data.sort(key=lambda x: x[0])
        recent = rep_data[-3:]
        if len(set(r for _, r in recent)) <= 2:
            span_days = (recent[-1][0] - recent[0][0]).days
            return PlateauResult(
                plateau_type=PlateauType.REP,
                detected=True,
                duration_days=span_days,
                severity="moderate" if span_days >= 21 else "mild",
                exercise_name=exercise_name,
                current_value=float(recent[-1][1]),
                previous_best=float(max(r for _, r in rep_data[:-3])) if len(rep_data) > 3 else float(recent[-1][1]),
                explanation=f"Reps on {exercise_name} stalled at {recent[-1][1]} for {span_days} days. "
                            f"Drop weight by 5-10% to accumulate more reps.",
                suggested_action="back_off_weight",
            )

        return PlateauResult(
            plateau_type=PlateauType.REP,
            exercise_name=exercise_name,
            explanation=f"Reps are progressing on {exercise_name}",
        )

    def detect_volume_plateau(self) -> PlateauResult:
        volume_data = self._provider.get_volume_by_day(days=60)
        if len(volume_data) < 4:
            return PlateauResult(
                plateau_type=PlateauType.VOLUME,
                explanation="Not enough weekly volume data to detect plateau",
            )

        recent_volumes = [v.get("volume", 0) if isinstance(v, dict) else getattr(v, "volume", 0) for v in volume_data[-4:]]
        if len(set(round(v, 0) for v in recent_volumes)) <= 2:
            return PlateauResult(
                plateau_type=PlateauType.VOLUME,
                detected=True,
                duration_days=21,
                severity="moderate",
                current_value=recent_volumes[-1],
                previous_best=max(recent_volumes),
                explanation="Total weekly volume has plateaued. Consider adding sets, increasing weight, "
                            "or adding a new exercise to drive progression.",
                suggested_action="increase_volume_load",
            )

        return PlateauResult(
            plateau_type=PlateauType.VOLUME,
            explanation="Volume is progressing",
        )

    def detect_bodyweight_plateau(self) -> PlateauResult:
        bw_history = self._provider.get_body_weight_history(days=30)
        if not bw_history or len(bw_history) < 4:
            return PlateauResult(
                plateau_type=PlateauType.BODYWEIGHT,
                explanation="Not enough bodyweight data to detect plateau",
            )

        sorted_bw = sorted(bw_history, key=lambda x: getattr(x, "date", datetime.min) if hasattr(x, "date") else datetime.min)
        weights = [getattr(w, "weight_kg", 0) for w in sorted_bw]
        span_days = (getattr(sorted_bw[-1], "date", datetime.now()) - getattr(sorted_bw[0], "date", datetime.now())).days if hasattr(sorted_bw[-1], "date") else 14

        if len(set(round(w, 1) for w in weights[-3:])) == 1 and span_days >= 14:
            return PlateauResult(
                plateau_type=PlateauType.BODYWEIGHT,
                detected=True,
                duration_days=span_days,
                severity="moderate",
                current_value=weights[-1],
                previous_best=weights[0],
                explanation=f"Bodyweight has stalled at {weights[-1]:.1f}kg for {span_days} days. "
                            f"Increase daily calories by 100-200 to resume progress.",
                suggested_action="increase_calories",
            )

        return PlateauResult(
            plateau_type=PlateauType.BODYWEIGHT,
            explanation="Bodyweight is progressing",
        )

    def detect_all(self, compound_exercises: list[str] | None = None) -> list[PlateauResult]:
        results: list[PlateauResult] = []

        if compound_exercises:
            for ex_name in compound_exercises:
                results.append(self.detect_weight_plateau(ex_name))
                results.append(self.detect_rep_plateau(ex_name))

        results.append(self.detect_volume_plateau())
        results.append(self.detect_bodyweight_plateau())

        return [r for r in results if r.detected]
