
from shared.domain.models import ExerciseData
from shared.domain.repositories import ExerciseRepository


class TagEngine:
    def __init__(self, exercise_repo: ExerciseRepository):
        self._repo = exercise_repo

    def get_exercises_by_tags(
        self,
        tags: list[str],
        mode: str = "any",
    ) -> list[ExerciseData]:
        all_exercises = list(self._repo.get_all().values())
        tag_set = {t.lower().strip() for t in tags}

        if mode == "any":
            return [
                ex for ex in all_exercises
                if any(t.lower().strip() in tag_set for t in ex.tags)
            ]
        elif mode == "all":
            return [
                ex for ex in all_exercises
                if tag_set.issubset({t.lower().strip() for t in ex.tags})
            ]
        elif mode == "none":
            return [
                ex for ex in all_exercises
                if not tag_set.intersection({t.lower().strip() for t in ex.tags})
            ]
        else:
            raise ValueError(f"Unknown mode '{mode}'; use 'any', 'all', or 'none'")

    def get_all_tags(self) -> set[str]:
        all_exercises = list(self._repo.get_all().values())
        tags: set[str] = set()
        for ex in all_exercises:
            tags.update(t.lower().strip() for t in ex.tags)
        return tags

    def get_exercise_tags(self, exercise: ExerciseData) -> set[str]:
        return {t.lower().strip() for t in exercise.tags}

    def get_tags_for_category(self, category: str) -> set[str]:
        exercises = self._repo.get_by_category(category)
        tags: set[str] = set()
        for ex in exercises:
            tags.update(t.lower().strip() for t in ex.tags)
        return tags

    def filter_by_tag(
        self,
        exercises: list[ExerciseData],
        tag: str,
        include: bool = True,
    ) -> list[ExerciseData]:
        tag_lower = tag.lower().strip()
        if include:
            return [
                ex for ex in exercises
                if tag_lower in {t.lower().strip() for t in ex.tags}
            ]
        else:
            return [
                ex for ex in exercises
                if tag_lower not in {t.lower().strip() for t in ex.tags}
            ]
