from __future__ import annotations

from typing import Any

from modules.gymbrain.models.recommendations import (
    Recommendation,
    RecommendationAction,
    RecommendationCategory,
    RecommendationPriority,
)
from modules.gymbrain.providers.data_provider import DataProvider
from modules.gymbrain.rules.base import BaseRule, RuleResult


class VolumeRule(BaseRule):
    """If a priority muscle's weekly volume is below MEV, recommend increasing volume."""

    def __init__(self) -> None:
        super().__init__(
            name="volume_rule",
            description="Recommends increasing volume when muscles are below MEV",
            priority=80,
        )

    def evaluate(self, provider: DataProvider, context: dict[str, Any] | None = None) -> RuleResult:
        priority_ids = provider.get_priority_muscles()
        if not priority_ids:
            return RuleResult()

        deficits: list[str] = []
        for muscle_id in priority_ids:
            muscle = provider.get_muscle(muscle_id)
            if not muscle:
                continue
            landmarks = muscle.get("weekly_volume_landmarks", {}) if isinstance(muscle, dict) else getattr(muscle, "weekly_volume_landmarks", {})
            mev = landmarks.get("mev", {}) if isinstance(landmarks, dict) else getattr(landmarks, "mev", {})
            mev_min = mev.get("min_sets") if isinstance(mev, dict) else None
            if mev_min is None:
                continue

            session_exercises = self._get_weekly_exercises(provider)
            if not session_exercises:
                continue

            effective_volume_map = provider.calculate_total_weekly_volume(session_exercises)
            current_sets = effective_volume_map.get(muscle_id, 0)

            if current_sets < mev_min:
                display_name = muscle.get("display_name", muscle_id) if isinstance(muscle, dict) else getattr(muscle, "display_name", muscle_id)
                deficits.append(f"{display_name}: {current_sets:.1f} sets vs MEV {mev_min} sets")

        if not deficits:
            return RuleResult()

        ev = deficits
        reason = f"{len(deficits)} muscle(s) below minimum effective volume: {'; '.join(deficits)}"
        return RuleResult(
            triggered=True,
            recommendation=Recommendation(
                category=RecommendationCategory.VOLUME,
                priority=RecommendationPriority.HIGH.value,
                title="Increase volume for under-trained muscles",
                description=f"Some priority muscles are below their minimum effective volume threshold. "
                            f"Add sets or exercises targeting: {', '.join(d.split(':')[0] for d in deficits)}",
                reason=reason,
                confidence=0.85,
                evidence=ev,
                action=RecommendationAction(
                    type="increase_volume",
                    params={"muscles": deficits},
                    display="Add 2-4 weekly sets for under-trained muscles",
                ),
            ),
            evidence=ev,
            confidence=0.85,
            reason=reason,
        )

    def _get_weekly_exercises(self, provider: DataProvider) -> list[tuple[Any, list[Any]]]:
        sessions = provider.get_recent_sessions(days=7)
        result = []
        for s in sessions:
            if hasattr(s, "exercises"):
                for ex in s.exercises:
                    if hasattr(ex, "sets") and hasattr(ex, "name"):
                        ex_data = provider.get_exercise_by_name(ex.name)
                        if ex_data:
                            result.append((ex_data, ex.sets))
        return result


class VolumeExcessRule(BaseRule):
    """If a muscle's weekly volume exceeds MRV, recommend reducing volume."""

    def __init__(self) -> None:
        super().__init__(
            name="volume_excess_rule",
            description="Recommends reducing volume when muscles exceed MRV",
            priority=75,
        )

    def evaluate(self, provider: DataProvider, context: dict[str, Any] | None = None) -> RuleResult:
        muscles = provider.get_all_muscles()
        if not muscles:
            return RuleResult()

        excess: list[str] = []
        session_exercises = self._get_weekly_exercises(provider)
        if not session_exercises:
            return RuleResult()

        effective_volume_map = provider.calculate_total_weekly_volume(session_exercises)

        for muscle_data in muscles:
            if isinstance(muscle_data, dict):
                muscle_id = muscle_data.get("id", "")
                landmarks = muscle_data.get("weekly_volume_landmarks", {})
            else:
                muscle_id = getattr(muscle_data, "id", "")
                landmarks = getattr(muscle_data, "weekly_volume_landmarks", {})
            mrv = (landmarks.get("mrv") if isinstance(landmarks, dict) else {}) or {}
            mrv_max = mrv.get("max_sets") if isinstance(mrv, dict) else None
            if mrv_max is None:
                continue

            current_sets = effective_volume_map.get(muscle_id, 0)
            if current_sets > mrv_max:
                display = muscle_data.get("display_name", muscle_id) if isinstance(muscle_data, dict) else getattr(muscle_data, "display_name", muscle_id)
                excess.append(f"{display}: {current_sets:.1f} sets vs MRV {mrv_max} sets")

        if not excess:
            return RuleResult()

        return RuleResult(
            triggered=True,
            recommendation=Recommendation(
                category=RecommendationCategory.VOLUME,
                priority=RecommendationPriority.HIGH.value,
                title="Reduce volume for over-trained muscles",
                description=f"Some muscles exceed maximum recoverable volume. Reduce sets to avoid overtraining: "
                            f"{', '.join(e.split(':')[0] for e in excess)}",
                reason=f"{len(excess)} muscle(s) above maximum recoverable volume",
                confidence=0.80,
                evidence=excess,
                action=RecommendationAction(
                    type="decrease_volume",
                    params={"muscles": excess},
                    display="Reduce 1-2 weekly sets for over-trained muscles",
                ),
            ),
            evidence=excess,
            confidence=0.80,
        )

    def _get_weekly_exercises(self, provider: DataProvider) -> list[tuple[Any, list[Any]]]:
        sessions = provider.get_recent_sessions(days=7)
        result = []
        for s in sessions:
            if hasattr(s, "exercises"):
                for ex in s.exercises:
                    if hasattr(ex, "sets") and hasattr(ex, "name"):
                        ex_data = provider.get_exercise_by_name(ex.name)
                        if ex_data:
                            result.append((ex_data, ex.sets))
        return result


class FrequencyRule(BaseRule):
    """If a priority muscle is trained less than recommended frequency, suggest increasing."""

    def __init__(self) -> None:
        super().__init__(
            name="frequency_rule",
            description="Recommends increasing training frequency for under-trained muscles",
            priority=60,
        )

    def evaluate(self, provider: DataProvider, context: dict[str, Any] | None = None) -> RuleResult:
        priority_ids = provider.get_priority_muscles()
        if not priority_ids:
            return RuleResult()

        sessions = provider.get_recent_sessions(days=7)
        muscle_session_counts: dict[str, int] = {}

        for muscle_id in priority_ids:
            muscle = provider.get_muscle(muscle_id)
            if not muscle:
                continue
            recommended_freq = (muscle.get("recommended_frequency") if isinstance(muscle, dict) else getattr(muscle, "recommended_frequency", None))
            if not recommended_freq:
                continue
            min_freq = (recommended_freq.get("min_times_per_week") if isinstance(recommended_freq, dict) else getattr(recommended_freq, "min_times_per_week", None))
            if min_freq is None:
                continue

            count = 0
            for s in sessions:
                if hasattr(s, "exercises"):
                    for ex in s.exercises:
                        if hasattr(ex, "name"):
                            ex_data = provider.get_exercise_by_name(ex.name)
                            if ex_data:
                                ex_muscles = ex_data.get("primary_muscles", []) if isinstance(ex_data, dict) else getattr(ex_data, "primary_muscles", [])
                                if muscle_id in ex_muscles:
                                    count += 1
                                    break

            muscle_session_counts[muscle_id] = count
            if count >= min_freq:
                continue

            display_name = muscle.get("display_name", muscle_id) if isinstance(muscle, dict) else getattr(muscle, "display_name", muscle_id)
            return RuleResult(
                triggered=True,
                recommendation=Recommendation(
                    category=RecommendationCategory.FREQUENCY,
                    priority=RecommendationPriority.MEDIUM.value,
                    title=f"Increase {display_name} training frequency",
                    description=f"{display_name} is trained {count}x/week but needs at least {min_freq}x/week. "
                                f"Add another session targeting this muscle group.",
                    reason=f"Current frequency {count}x/week is below recommended minimum {min_freq}x/week",
                    confidence=0.75,
                    evidence=[f"Current frequency: {count}x/week", f"Recommended minimum: {min_freq}x/week"],
                    action=RecommendationAction(
                        type="increase_frequency",
                        params={"muscle_id": muscle_id, "current_frequency": count, "recommended_minimum": min_freq},
                        display=f"Add 1 more weekly session for {display_name}",
                    ),
                ),
                evidence=[f"Current frequency: {count}x/week", f"Recommended minimum: {min_freq}x/week"],
                confidence=0.75,
            )

        return RuleResult()
