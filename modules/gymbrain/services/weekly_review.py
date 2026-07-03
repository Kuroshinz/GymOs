from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from modules.gymbrain.models.analysis import MuscleStatus, WeeklyReview
from modules.gymbrain.providers.data_provider import DataProvider


class WeeklyReviewGenerator:
    """Generates a structured weekly training review.

    Summarizes the past week's training, highlights PRs,
    identifies gaps, and suggests next week's priorities.
    """

    def __init__(self, provider: DataProvider) -> None:
        self._provider = provider

    def generate(self) -> WeeklyReview:
        now = datetime.now()
        week_start = now - timedelta(days=7)
        week_label = f"{week_start.strftime('%b %d')} – {now.strftime('%b %d, %Y')}"

        sessions = self._provider.get_recent_sessions(days=7)
        total_workouts = len(sessions)
        total_sets = 0
        total_volume = 0.0

        for s in sessions:
            if hasattr(s, "exercises"):
                for ex in s.exercises:
                    if hasattr(ex, "sets"):
                        total_sets += len(ex.sets)
                        volume = sum(
                            getattr(se, "weight_kg", 0) * getattr(se, "reps", 0)
                            for se in ex.sets
                        )
                        total_volume += volume

        # Best PR
        best_pr = self._find_best_pr(sessions)

        # Muscle analysis
        muscle_analysis = self._analyze_muscle_volume(sessions)
        most_improved = muscle_analysis.get("most_improved", "")
        lowest_volume = muscle_analysis.get("lowest_volume", "")

        # Missed sessions
        program = self._provider.get_program()
        expected_days = 0
        if program and isinstance(program, dict):
            expected_days = len(program.get("days", []))
        missed = max(0, expected_days - total_workouts)

        # Recovery score
        recovery_score = self._get_recovery_score(sessions)

        # Bodyweight change
        bw_change = self._get_bodyweight_change()

        # Fatigue level
        from modules.gymbrain.analysis.fatigue import FatigueAnalyzer
        fatigue = FatigueAnalyzer(self._provider).analyze(days=7)

        # Next week priorities
        priorities = self._generate_priorities(
            sessions, muscle_analysis, total_workouts, expected_days
        )

        return WeeklyReview(
            week_label=week_label,
            total_workouts=total_workouts,
            total_sets=total_sets,
            total_volume_kg=round(total_volume, 1),
            best_pr=best_pr,
            most_improved_muscle=most_improved,
            lowest_volume_muscle=lowest_volume,
            missed_sessions=missed,
            recovery_score=recovery_score,
            bodyweight_change=round(bw_change, 1),
            next_week_priorities=priorities,
            fatigue_level=fatigue.level.value,
            recommendations_count=0,
        )

    def _find_best_pr(self, sessions: list[Any]) -> str:
        for s in sessions:
            if not hasattr(s, "exercises"):
                continue
            prs = self._provider.detect_prs(s)
            if prs and hasattr(prs[0], "label"):
                return prs[0].label
        return "No PRs this week"

    def _analyze_muscle_volume(self, sessions: list[Any]) -> dict[str, Any]:
        from modules.gymbrain.analysis.muscle import MuscleAnalyzer
        analyzer = MuscleAnalyzer(self._provider)
        results = analyzer.analyze()

        most_improved = ""
        lowest_volume = ""
        best_progress = -999
        worst_volume = 9999

        for r in results:
            if r.progress in ("Improving", "Slightly improving") and r.current_sets > best_progress:
                best_progress = r.current_sets
                most_improved = r.display_name
            if r.current_sets < worst_volume and r.status.value in ("low", "building"):
                worst_volume = r.current_sets
                lowest_volume = r.display_name

        return {
            "most_improved": most_improved,
            "lowest_volume": lowest_volume,
            "results": results,
        }

    def _get_recovery_score(self, sessions: list[Any]) -> str:
        total_flags = 0
        for s in sessions:
            if not hasattr(s, "exercises"):
                continue
            report = self._provider.analyse_session(s)
            if report and hasattr(report, "flags"):
                total_flags += len(report.flags)

        if total_flags == 0:
            return "Excellent"
        if total_flags <= 2:
            return "Good"
        if total_flags <= 5:
            return "Fair"
        return "Poor"

    def _get_bodyweight_change(self) -> float:
        bw_history = self._provider.get_body_weight_history(days=14)
        if not bw_history or len(bw_history) < 2:
            return 0.0

        sorted_bw = sorted(bw_history, key=lambda x: getattr(x, "date", datetime.min) if hasattr(x, "date") else datetime.min)
        weights = [getattr(w, "weight_kg", 0) for w in sorted_bw]
        return weights[-1] - weights[0]

    def _generate_priorities(
        self,
        sessions: list[Any],
        muscle_analysis: dict[str, Any],
        total_workouts: int,
        expected_days: int,
    ) -> list[str]:
        priorities: list[str] = []

        if total_workouts < expected_days:
            priorities.append(f"Complete all {expected_days} scheduled sessions")

        results = muscle_analysis.get("results", [])
        for r in results:
            if r.status == MuscleStatus.LOW:
                priorities.append(f"Increase volume for {r.display_name}")
            elif r.status == MuscleStatus.HIGH:
                priorities.append(f"Reduce volume for {r.display_name}")

        if not priorities:
            priorities.append("Continue current training plan")
            priorities.append("Focus on progressive overload on key lifts")

        return priorities[:5]
