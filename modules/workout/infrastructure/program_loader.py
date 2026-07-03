"""Program Loader — reads the canonical program file and provides program data.

The canonical source file (data/program.json) is the ONLY source of truth
for the GymOS workout program. It is generated from
PPL_UL_MASTER_v6_UPDATED_LEGS.xlsx via scripts/parse_excel_program.py.
"""

import json
import os
from typing import Optional


class ProgramLoader:
    """Loads the canonical workout program from a JSON file.

    The default path is data/program.json relative to the project root.
    """

    def __init__(self, program_path: Optional[str] = None) -> None:
        self._program_path = program_path or os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "data", "program.json"
        )
        self._program: Optional[dict] = None

    @property
    def program_path(self) -> str:
        return os.path.abspath(self._program_path)

    def load(self) -> dict:
        """Load and cache the program data from the JSON file."""
        if self._program is not None:
            return self._program

        path = self.program_path
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Canonical program file not found: {path}\n"
                "Generate it by running:\n"
                "  python scripts/parse_excel_program.py"
            )

        with open(path, encoding="utf-8") as f:
            self._program = json.load(f)

        return self._program

    def get_name(self) -> str:
        return self.load().get("name", "Unknown")

    def get_description(self) -> str:
        return self.load().get("description", "")

    def get_days(self) -> list[dict]:
        """Get all days with exercises.

        Returns the raw structure from the JSON:
        [
            {
                "name": "PUSH",
                "exercises": [
                    {"name": "...", "target_sets": 3, "target_reps": "8-10", "muscle_group": "chest"},
                    ...
                ]
            },
            ...
        ]
        """
        return self.load().get("days", [])

    def get_exercise_count(self) -> int:
        return sum(len(d["exercises"]) for d in self.get_days())

    def get_rules(self) -> list[str]:
        return self.load().get("rules", [])

    def get_source_file(self) -> str:
        return self.load().get("source", "")
