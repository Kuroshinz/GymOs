"""ProgramManager — orchestrates import, validation, storage, and activation."""


from modules.workout_program.domain import WorkoutProgram
from modules.workout_program.importer import ProgramImporter
from modules.workout_program.repository import ProgramRepository
from modules.workout_program.validator import ProgramValidator, ValidationResult


class ProgramManager:
    def __init__(self, db_path: str):
        self.importer = ProgramImporter()
        self.validator = ProgramValidator()
        self.repository = ProgramRepository(db_path)

    # ─── Import Pipeline ─────────────────────────────────────

    def import_program(self, filepath: str) -> tuple[WorkoutProgram, ValidationResult]:
        program = self.importer.import_file(filepath)
        result = self.validator.validate(program)
        return program, result

    def import_and_save(self, filepath: str) -> tuple[str | None, ValidationResult]:
        program, result = self.import_program(filepath)
        if not result.passed:
            return None, result

        if self.repository.name_exists(program.name):
            result.add_error("name", f"A program named '{program.name}' already exists.")
            return None, result

        program_id = self.repository.save(program)
        return program_id, result

    def import_save_and_activate(self, filepath: str) -> tuple[str | None, ValidationResult]:
        program_id, result = self.import_and_save(filepath)
        if program_id is not None:
            self.repository.activate(program_id)
        return program_id, result

    # ─── Preview ─────────────────────────────────────────────

    def preview(self, filepath: str) -> dict:
        return self.importer.preview(filepath)

    # ─── Program Listing ─────────────────────────────────────

    def list_programs(self) -> list[dict]:
        return self.repository.get_all()

    def get_active_program(self) -> WorkoutProgram | None:
        return self.repository.get_active()

    def get_active_program_days(self) -> list[dict]:
        program = self.repository.get_active()
        if program is None:
            return []
        return [
            {
                "id": "",
                "name": d.name,
                "sort_order": d.sort_order,
                "exercises": [
                    {
                        "id": "",
                        "name": e.name,
                        "target_sets": e.target_sets,
                        "target_reps": e.target_reps,
                        "sort_order": e.sort_order,
                        "muscle_group": e.muscle_group or "",
                        "exercise_id": e.exercise_id or "",
                    }
                    for e in d.exercises
                ],
            }
            for d in program.days
        ]

    def switch_to_program(self, program_id: str) -> bool:
        program = self.repository.get_by_id(program_id)
        if program is None:
            return False
        self.repository.activate(program_id)
        return True

    def get_active_name(self) -> str:
        program = self.repository.get_active()
        return program.name if program else "No Active Program"

    def get_active_day_count(self) -> int:
        program = self.repository.get_active()
        return len(program.days) if program else 0

    # ─── Cleanup ─────────────────────────────────────────────

    def dispose(self):
        self.repository.dispose()
