from typing import Optional

from shared.domain.models import ExerciseData, MuscleData, ProgramData
from shared.domain.repositories import (
    ExerciseRepository,
    MuscleRepository,
    ProgramRepository,
)
from shared.domain.tags import TagEngine
from shared.domain.validator import KnowledgeValidator, ValidationError
from shared.domain.volume import VolumeEngine, VolumeResult
from shared.knowledge_loader import KnowledgeLoader


class KnowledgeService:
    def __init__(self, loader: Optional[KnowledgeLoader] = None):
        self._loader = loader or KnowledgeLoader()
        self._loader.load_all()
        self.exercises = ExerciseRepository(self._loader)
        self.muscles = MuscleRepository(self._loader)
        self.programs = ProgramRepository(self._loader)
        self.volume = VolumeEngine()
        self.tags = TagEngine(self.exercises)
        self.validator = KnowledgeValidator(self._loader)

    def resolve_alias(self, name: str) -> list[str]:
        return self._loader.resolve_alias(name)

    def get_exercise_volume(
        self,
        exercise_id: str,
        sets: int,
    ) -> list[VolumeResult]:
        ex = self.exercises.get_by_id(exercise_id)
        if not ex:
            return []
        return self.volume.calculate_effective_volume(ex, sets)

    def get_weekly_volume(
        self,
        exercise_set_pairs: list[tuple[str, int]],
    ) -> dict[str, float]:
        exercises = []
        for eid, sets in exercise_set_pairs:
            ex = self.exercises.get_by_id(eid)
            if ex:
                exercises.append((ex, sets))
        return self.volume.calculate_total_weekly_volume(exercises)

    def get_exercises_with_tag(
        self,
        tag: str,
    ) -> list[ExerciseData]:
        return self.tags.filter_by_tag(
            list(self.exercises.get_all().values()),
            tag,
        )

    def validate(self) -> list[ValidationError]:
        return self.validator.validate_all()
