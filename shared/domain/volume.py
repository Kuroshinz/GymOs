from dataclasses import dataclass, field

from shared.domain.models import ExerciseData


@dataclass
class VolumeResult:
    muscle_id: str
    effective_sets: float
    raw_sets: int
    contribution_pct: float


class VolumeEngine:
    def calculate_effective_volume(
        self,
        exercise: ExerciseData,
        sets: int,
    ) -> list[VolumeResult]:
        if exercise.muscle_contributions:
            return [
                VolumeResult(
                    muscle_id=mc.muscle_id,
                    effective_sets=sets * mc.percentage / 100.0,
                    raw_sets=sets,
                    contribution_pct=mc.percentage,
                )
                for mc in exercise.muscle_contributions
            ]

        primary_count = len(exercise.primary_muscles) or 1
        primary_split = 100.0 / primary_count if primary_count else 0

        results = []
        for pm in exercise.primary_muscles:
            results.append(VolumeResult(
                muscle_id=pm,
                effective_sets=sets * primary_split / 100.0,
                raw_sets=sets,
                contribution_pct=primary_split,
            ))

        if exercise.secondary_muscles:
            secondary_pct = 30.0
            secondary_split = secondary_pct / len(exercise.secondary_muscles)
            for sm in exercise.secondary_muscles:
                results.append(VolumeResult(
                    muscle_id=sm,
                    effective_sets=sets * secondary_split / 100.0,
                    raw_sets=sets,
                    contribution_pct=secondary_split,
                ))

        return results

    def calculate_total_weekly_volume(
        self,
        weekly_exercises: list[tuple[ExerciseData, int]],
    ) -> dict[str, float]:
        totals: dict[str, float] = {}
        for exercise, sets in weekly_exercises:
            for vr in self.calculate_effective_volume(exercise, sets):
                totals[vr.muscle_id] = totals.get(vr.muscle_id, 0) + vr.effective_sets
        return totals
