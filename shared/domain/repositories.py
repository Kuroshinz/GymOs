
from shared.domain.models import ExerciseData, MuscleData, ProgramData
from shared.knowledge_loader import KnowledgeLoader


class ExerciseRepository:
    def __init__(self, loader: KnowledgeLoader):
        self._loader = loader

    def get_by_id(self, exercise_id: str) -> ExerciseData | None:
        raw = self._loader.get_exercise(exercise_id)
        return ExerciseData.from_dict(raw) if raw else None

    def get_by_name(self, name: str) -> ExerciseData | None:
        raw = self._loader.get_exercise_by_name(name)
        return ExerciseData.from_dict(raw) if raw else None

    def get_all(self) -> dict[str, ExerciseData]:
        return {
            eid: ExerciseData.from_dict(raw)
            for eid, raw in self._loader.get_all_exercises().items()
        }

    def get_by_category(self, category: str) -> list[ExerciseData]:
        return [
            ExerciseData.from_dict(raw)
            for raw in self._loader.get_exercises_by_category(category)
        ]

    def get_by_muscle(self, muscle_id: str) -> list[ExerciseData]:
        return [
            ExerciseData.from_dict(raw)
            for raw in self._loader.get_exercises_by_muscle(muscle_id)
        ]


class MuscleRepository:
    def __init__(self, loader: KnowledgeLoader):
        self._loader = loader

    def get_by_id(self, muscle_id: str) -> MuscleData | None:
        raw = self._loader.get_muscle(muscle_id)
        return MuscleData.from_dict(raw) if raw else None

    def get_all(self) -> dict[str, MuscleData]:
        return {
            mid: MuscleData.from_dict(raw)
            for mid, raw in self._loader.get_all_muscles().items()
        }

    def get_by_group(self, group: str) -> list[MuscleData]:
        return [
            MuscleData.from_dict(raw)
            for raw in self._loader.get_muscles_by_group(group)
        ]


class ProgramRepository:
    def __init__(self, loader: KnowledgeLoader):
        self._loader = loader

    def get_program(self) -> ProgramData | None:
        raw = self._loader.load_program()
        return ProgramData.from_dict(raw) if raw else None

    def get_exercise_ids(self) -> list[str]:
        return self._loader.get_program_exercise_ids()
