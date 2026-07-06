"""Knowledge Loader — centralized access to the GymOS static knowledge base.

All modules MUST access exercise, muscle, and alias data through this loader.
No direct YAML/JSON parsing of knowledge files outside this module.

Usage:
    loader = KnowledgeLoader()
    exercise = loader.get_exercise("chest_bench_press")
    muscle = loader.get_muscle("pectoralis_major")
    ids = loader.resolve_alias("Bench Press")      # -> ["chest_bench_press"]
    program = loader.load_program("data/program.json")
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"
EXERCISES_DIR = KNOWLEDGE_DIR / "exercises"
MUSCLES_DIR = KNOWLEDGE_DIR / "muscles"
ALIASES_PATH = KNOWLEDGE_DIR / "aliases.yaml"
SCHEMAS_DIR = PROJECT_ROOT / "schemas"
DATA_DIR = PROJECT_ROOT / "data"


class KnowledgeLoadError(Exception):
    """Raised when knowledge data cannot be loaded or is invalid."""


def _load_yaml(path: Path) -> dict:
    """Load a YAML file, returning an empty dict on missing file."""
    try:
        import yaml
    except ImportError:
        raise KnowledgeLoadError(
            "PyYAML is required. Install with: pip install pyyaml"
        )
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def _load_json(path: Path) -> dict | list:
    """Load a JSON file."""
    if not path.exists():
        raise KnowledgeLoadError(f"File not found: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class KnowledgeLoader:
    """Singleton-ish loader that caches all knowledge data on first access."""

    def __init__(self):
        self._exercises: dict[str, dict] = {}
        self._muscles: dict[str, dict] = {}
        self._aliases: dict[str, str] = {}
        self._program: dict | None = None
        self._loaded = False

    # ─── Load All ────────────────────────────────────────────

    def load_all(self) -> None:
        """Load all knowledge data into cache."""
        if self._loaded:
            return
        self._load_exercises()
        self._load_muscles()
        self._load_aliases()
        self._loaded = True

    def reload(self) -> None:
        """Force a full reload."""
        self._loaded = False
        self._exercises.clear()
        self._muscles.clear()
        self._aliases.clear()
        self._program = None
        self.load_all()

    # ─── Exercises ───────────────────────────────────────────

    def _load_exercises(self) -> None:
        if not EXERCISES_DIR.exists():
            raise KnowledgeLoadError(f"Exercises directory not found: {EXERCISES_DIR}")
        for path in sorted(EXERCISES_DIR.glob("*.json")):
            if path.name == "_index.json":
                continue
            try:
                ex = _load_json(path)
                if "id" in ex:
                    self._exercises[ex["id"]] = ex
            except (json.JSONDecodeError, KnowledgeLoadError) as e:
                raise KnowledgeLoadError(f"Failed to load {path.name}: {e}") from e

    def get_exercise(self, exercise_id: str) -> dict | None:
        """Get an exercise definition by its stable ID."""
        self.load_all()
        return self._exercises.get(exercise_id)

    def get_exercise_by_name(self, name: str) -> dict | None:
        """Find an exercise by its display name (case-insensitive)."""
        self.load_all()
        name_lower = name.strip().lower()
        for ex in self._exercises.values():
            if ex.get("name", "").strip().lower() == name_lower:
                return ex
        return None

    def get_all_exercises(self) -> dict[str, dict]:
        """Get all exercises keyed by ID."""
        self.load_all()
        return dict(self._exercises)

    def get_exercises_by_category(self, category: str) -> list[dict]:
        """Get all exercises in a given category."""
        self.load_all()
        return [ex for ex in self._exercises.values() if ex.get("category") == category]

    def get_exercises_by_muscle(self, muscle_id: str) -> list[dict]:
        """Get all exercises that target a specific muscle (primary or secondary)."""
        self.load_all()
        results = []
        for ex in self._exercises.values():
            primary = [m.lower() for m in ex.get("primary_muscles", [])]
            secondary = [m.lower() for m in ex.get("secondary_muscles", [])]
            if muscle_id.lower() in primary or muscle_id.lower() in secondary:
                results.append(ex)
        return results

    # ─── Muscles ─────────────────────────────────────────────

    def _load_muscles(self) -> None:
        if not MUSCLES_DIR.exists():
            raise KnowledgeLoadError(f"Muscles directory not found: {MUSCLES_DIR}")
        for path in sorted(MUSCLES_DIR.glob("*.json")):
            if path.name == "_index.json":
                continue
            try:
                m = _load_json(path)
                if "id" in m:
                    self._muscles[m["id"]] = m
            except (json.JSONDecodeError, KnowledgeLoadError) as e:
                raise KnowledgeLoadError(f"Failed to load {path.name}: {e}") from e

    def get_muscle(self, muscle_id: str) -> dict | None:
        """Get a muscle definition by its stable ID."""
        self.load_all()
        return self._muscles.get(muscle_id)

    def get_all_muscles(self) -> dict[str, dict]:
        """Get all muscles keyed by ID."""
        self.load_all()
        return dict(self._muscles)

    def get_muscles_by_group(self, group: str) -> list[dict]:
        """Get all muscles in a given anatomical group."""
        self.load_all()
        return [m for m in self._muscles.values() if m.get("group") == group]

    # ─── Aliases ─────────────────────────────────────────────

    def _load_aliases(self) -> None:
        data = _load_yaml(ALIASES_PATH)
        self._aliases = {}
        for alias_name, exercise_id in data.items():
            if isinstance(alias_name, str) and isinstance(exercise_id, str):
                key = alias_name.strip().lower()
                self._aliases[key] = exercise_id

    def resolve_alias(self, name: str) -> list[str]:
        """Resolve a name to one or more exercise IDs.

        Checks in order:
        1. Exact alias match (case-insensitive)
        2. Exercise name match
        3. Partial alias match (contains)
        4. Returns empty list if no match found
        """
        self.load_all()
        key = name.strip().lower()

        # 1. Exact alias match
        if key in self._aliases:
            return [self._aliases[key]]

        # 2. Exercise name match
        for ex_id, ex in self._exercises.items():
            if ex.get("name", "").strip().lower() == key:
                return [ex_id]

        # 3. Check if any exercise has aliases array containing this name
        for ex_id, ex in self._exercises.items():
            ex_aliases = [a.strip().lower() for a in ex.get("aliases", [])]
            if key in ex_aliases:
                return [ex_id]

        return []

    def get_alias_map(self) -> dict[str, str]:
        """Get full alias-to-ID mapping."""
        self.load_all()
        return dict(self._aliases)

    def get_all_known_names(self) -> set[str]:
        """Get all known exercise names (canonical + aliases)."""
        self.load_all()
        names = set()
        for ex in self._exercises.values():
            names.add(ex.get("name", "").strip().lower())
            for alias in ex.get("aliases", []):
                names.add(alias.strip().lower())
        for alias_key in self._aliases:
            names.add(alias_key.strip().lower())
        return names

    # ─── Program ─────────────────────────────────────────────

    def load_program(self, path: str | None = None) -> dict:
        """Load and cache a workout program JSON file."""
        if self._program is not None and path is None:
            return self._program

        program_path = Path(path) if path else DATA_DIR / "program.json"
        self._program = _load_json(program_path)
        return self._program

    def get_program_exercise_ids(self) -> list[str]:
        """Get all exercise IDs referenced in the active program."""
        program = self.load_program()
        ids: list[str] = []
        for day in program.get("days", []):
            for ex in day.get("exercises", []):
                eid = ex.get("exercise_id", "")
                if eid:
                    ids.append(eid)
        return ids

    # ─── Validation helpers ──────────────────────────────────

    def validate_exercise_references(self) -> list[str]:
        """Check that all exercise references in program resolve to valid IDs.

        Returns a list of error messages (empty if all valid).
        """
        errors: list[str] = []
        program = self.load_program()
        known_ids = set(self._exercises.keys())

        for day in program.get("days", []):
            day_name = day.get("name", "?")
            for ex in day.get("exercises", []):
                eid = ex.get("exercise_id", "")
                if eid and eid not in known_ids:
                    errors.append(
                        f"Program '{program.get('name')}' day '{day_name}': "
                        f"exercise_id '{eid}' does not match any known exercise"
                    )
        return errors

    def validate_muscle_references(self) -> list[str]:
        """Check that all muscle references in exercises resolve to valid muscle IDs.

        Returns a list of error messages (empty if all valid).
        """
        errors: list[str] = []
        known_muscles = set(self._muscles.keys())

        for ex_id, ex in self._exercises.items():
            for m in ex.get("primary_muscles", []):
                if m not in known_muscles:
                    errors.append(f"Exercise '{ex_id}': primary_muscle '{m}' not found in muscle library")
            for m in ex.get("secondary_muscles", []):
                if m and m not in known_muscles:
                    errors.append(f"Exercise '{ex_id}': secondary_muscle '{m}' not found in muscle library")

        return errors


# ─── Module-level convenience functions ──────────────────────

_global_loader: KnowledgeLoader | None = None


def get_loader() -> KnowledgeLoader:
    """Get or create the global KnowledgeLoader singleton."""
    global _global_loader
    if _global_loader is None:
        _global_loader = KnowledgeLoader()
    return _global_loader


def get_exercise(exercise_id: str) -> dict | None:
    return get_loader().get_exercise(exercise_id)


def resolve_alias(name: str) -> list[str]:
    return get_loader().resolve_alias(name)
