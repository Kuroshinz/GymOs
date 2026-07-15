from __future__ import annotations

from typing import Any

from modules.gymbrain.models.analysis import MuscleAnalysisResult, MuscleStatus
from modules.gymbrain.providers.data_provider import DataProvider


class MuscleAnalyzer:
    """Analyzes each priority muscle's training status.

    Combines effective volume, recovery, frequency, and exercise selection
    to produce a comprehensive muscle analysis.
    """

    def __init__(self, provider: DataProvider) -> None:
        self._provider = provider

    def analyze(self, muscle_ids: list[str] | None = None) -> list[MuscleAnalysisResult]:
        if muscle_ids is None:
            muscle_ids = self._provider.get_priority_muscles()

        if not muscle_ids:
            muscle_ids = [m.get("id", "") for m in self._provider.get_all_muscles() if isinstance(m, dict)]
            if not muscle_ids:
                return []

        results: list[MuscleAnalysisResult] = []
        session_exercises = self._get_weekly_exercises()

        for muscle_id in muscle_ids:
            result = self._analyze_single(muscle_id, session_exercises)
            results.append(result)

        results.sort(key=lambda r: r.status.value)
        return results

    def analyze_single(self, muscle_id: str) -> MuscleAnalysisResult:
        session_exercises = self._get_weekly_exercises()
        return self._analyze_single(muscle_id, session_exercises)

    def _analyze_single(
        self, muscle_id: str, session_exercises: list[tuple[Any, list[Any]]]
    ) -> MuscleAnalysisResult:
        muscle = self._provider.get_muscle(muscle_id)
        if not muscle:
            return MuscleAnalysisResult(
                muscle_id=muscle_id,
                status=MuscleStatus.OPTIMAL,
                progress="No data available",
            )

        display_name = muscle.get("display_name", muscle_id) if isinstance(muscle, dict) else getattr(muscle, "display_name", muscle_id)

        # Volume landmarks
        landmarks = muscle.get("weekly_volume_landmarks", {}) if isinstance(muscle, dict) else getattr(muscle, "weekly_volume_landmarks", {})
        if isinstance(landmarks, dict):
            mev = landmarks.get("mev", {}) or {}
            mav = landmarks.get("mav", {}) or {}
            mrv = landmarks.get("mrv", {}) or {}
            min_sets = mev.get("min_sets", 0) if isinstance(mev, dict) else 0
            max_sets = mrv.get("max_sets", 20) if isinstance(mrv, dict) else 20
            optimal_min = mav.get("min_sets", min_sets) if isinstance(mav, dict) else min_sets
            optimal_max = mav.get("max_sets", max_sets) if isinstance(mav, dict) else max_sets
        else:
            min_sets = 0
            max_sets = 20
            optimal_min = 0
            optimal_max = 20

        # Current volume
        effective_volume_map = {}
        if session_exercises:
            effective_volume_map = self._provider.calculate_total_weekly_volume(session_exercises)
        current_sets = effective_volume_map.get(muscle_id, 0.0)

        # Status
        if current_sets < min_sets:
            status = MuscleStatus.LOW
            weakness = f"Below minimum effective volume ({current_sets:.0f}/{min_sets} sets)"
        elif current_sets < optimal_min:
            status = MuscleStatus.BUILDING
            weakness = f"Building toward optimal range ({current_sets:.0f}/{optimal_min} sets)"
        elif current_sets <= optimal_max:
            status = MuscleStatus.OPTIMAL
            weakness = ""
        elif current_sets <= max_sets:
            status = MuscleStatus.MAINTENANCE
            weakness = f"At maintenance level, room to increase ({current_sets:.0f}/{max_sets} sets)"
        else:
            status = MuscleStatus.HIGH
            weakness = f"Above maximum recoverable volume ({current_sets:.0f}/{max_sets} sets)"

        # Progress
        progress = self._estimate_progress(muscle_id, current_sets)

        # Suggested exercises
        suggested = self._get_suggested_exercises(muscle_id)

        # Weekly frequency
        frequency = self._count_weekly_frequency(muscle_id, session_exercises)

        # Recommended frequency
        recommended_freq = muscle.get("recommended_frequency", {}) if isinstance(muscle, dict) else getattr(muscle, "recommended_frequency", {})
        if isinstance(recommended_freq, dict):
            freq_str = f"{recommended_freq.get('min_times_per_week', '?')}-{recommended_freq.get('max_times_per_week', '?')}x/week"
        else:
            freq_str = "?"

        # Recovery status
        recovery_status = self._estimate_recovery(muscle_id, current_sets, max_sets)

        return MuscleAnalysisResult(
            muscle_id=muscle_id,
            display_name=display_name,
            current_sets=current_sets,
            recommended_min_sets=optimal_min,
            recommended_max_sets=optimal_max,
            status=status,
            progress=progress,
            weakness=weakness,
            suggested_exercises=suggested,
            weekly_frequency=frequency,
            recommended_frequency=freq_str,
            recovery_status=recovery_status,
        )

    def _get_weekly_exercises(self) -> list[tuple[dict[str, Any], list[Any]]]:
        sessions = self._provider.get_recent_sessions(days=7)
        result: list[tuple[dict[str, Any], list[Any]]] = []
        for s in sessions:
            if hasattr(s, "exercises"):
                for ex in s.exercises:
                    if hasattr(ex, "sets") and hasattr(ex, "name"):
                        ex_data = self._provider.get_exercise_by_name(ex.name)
                        if ex_data:
                            result.append((ex_data, ex.sets))
        return result

    def _estimate_progress(self, muscle_id: str, current_sets: float) -> str:
        last_week_sessions = self._provider.get_recent_sessions(days=14)
        previous_sets = 0.0
        mid = len(last_week_sessions) // 2
        first_half = last_week_sessions[:mid] if mid > 0 else []
        second_half = last_week_sessions[mid:] if mid > 0 else last_week_sessions

        for sessions_batch, target in [(first_half, "previous"), (second_half, "current")]:
            batch_exercises = []
            for s in sessions_batch:
                if hasattr(s, "exercises"):
                    for ex in s.exercises:
                        if hasattr(ex, "sets") and hasattr(ex, "name"):
                            ex_data = self._provider.get_exercise_by_name(ex.name)
                            if ex_data:
                                batch_exercises.append((ex_data, ex.sets))
            if batch_exercises:
                vol_map = self._provider.calculate_total_weekly_volume(batch_exercises)
                if target == "previous":
                    previous_sets = vol_map.get(muscle_id, 0)
                else:
                    current_sets = vol_map.get(muscle_id, 0)

        if previous_sets == 0:
            return "Maintaining"
        change = ((current_sets - previous_sets) / previous_sets) * 100
        if change > 15:
            return "Improving"
        if change > 5:
            return "Slightly improving"
        if change > -5:
            return "Stable"
        if change > -15:
            return "Slightly declining"
        return "Declining"

    def _get_suggested_exercises(self, muscle_id: str) -> list[str]:
        exercises = self._provider.get_exercises_by_muscle(muscle_id)
        return [ex.get("name", "") if isinstance(ex, dict) else getattr(ex, "name", "") for ex in exercises[:5]]

    def _count_weekly_frequency(self, muscle_id: str, session_exercises: list[tuple[Any, list[Any]]]) -> int:
        days_trained = set()
        sessions = self._provider.get_recent_sessions(days=7)
        for s in sessions:
            if not hasattr(s, "exercises") or not hasattr(s, "started_at"):
                continue
            for ex in s.exercises:
                if not hasattr(ex, "name"):
                    continue
                ex_data = self._provider.get_exercise_by_name(ex.name)
                if not ex_data:
                    continue
                primary = ex_data.get("primary_muscles", []) if isinstance(ex_data, dict) else getattr(ex_data, "primary_muscles", [])
                secondary = ex_data.get("secondary_muscles", []) if isinstance(ex_data, dict) else getattr(ex_data, "secondary_muscles", [])
                if muscle_id in primary or muscle_id in secondary:
                    days_trained.add(s.started_at.date() if hasattr(s.started_at, "date") else s.started_at)
                    break
        return len(days_trained)

    def _estimate_recovery(self, muscle_id: str, current_sets: float, max_sets: float) -> str:
        if max_sets == 0.0:
            return "Unknown"
        ratio = current_sets / max_sets
        if ratio > 1.0:
            return "Overtrained — reduce volume"
        if ratio > 0.8:
            return "Adequate — nearing limit"
        if ratio > 0.6:
            return "Good"
        if ratio > 0.3:
            return "Optimal"
        return "Under-trained — can increase volume"
