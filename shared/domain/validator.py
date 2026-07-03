import json
from pathlib import Path
from typing import Optional

import jsonschema
import yaml

from shared.knowledge_loader import PROJECT_ROOT, KnowledgeLoader


class ValidationError:
    def __init__(self, message: str, category: str = "general"):
        self.message = message
        self.category = category

    def __repr__(self):
        return f"[{self.category}] {self.message}"

    def __eq__(self, other):
        return isinstance(other, ValidationError) and self.message == other.message and self.category == other.category

    def __hash__(self):
        return hash((self.message, self.category))


def _load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class KnowledgeValidator:
    def __init__(self, loader: Optional[KnowledgeLoader] = None):
        self._loader = loader or KnowledgeLoader()
        self._loader.load_all()
        self._exercises_dir = PROJECT_ROOT / "knowledge" / "exercises"
        self._muscles_dir = PROJECT_ROOT / "knowledge" / "muscles"
        self._aliases_path = PROJECT_ROOT / "knowledge" / "aliases.yaml"
        self._schemas_dir = PROJECT_ROOT / "schemas"

    def validate_all(self) -> list[ValidationError]:
        errors: list[ValidationError] = []
        errors.extend(self._check_duplicate_ids("exercise", self._exercises_dir))
        errors.extend(self._check_duplicate_ids("muscle", self._muscles_dir))
        errors.extend(self._check_duplicate_names())
        errors.extend(self._check_file_names_match_ids("exercise", self._exercises_dir))
        errors.extend(self._check_file_names_match_ids("muscle", self._muscles_dir))
        errors.extend(self._check_alias_consistency())
        errors.extend(self._check_schema_validity("exercise"))
        errors.extend(self._check_schema_validity("muscle"))
        errors.extend(self._check_schema_validity("program"))
        errors.extend(self._check_orphan_muscle_references())
        errors.extend(self._check_orphan_exercise_references())
        errors.extend(self._check_contribution_totals())
        errors.extend(self._check_tag_format())
        errors.extend(self._check_reference_format())
        return errors

    def _get_ids(self, directory: Path) -> list[str]:
        ids = []
        for path in sorted(directory.glob("*.json")):
            if path.name == "_index.json":
                continue
            data = _load_json(path)
            ids.append(data.get("id", ""))
        return ids

    def _check_duplicate_ids(self, label: str, directory: Path) -> list[ValidationError]:
        ids = self._get_ids(directory)
        seen = {}
        errors = []
        for id_ in ids:
            if id_ in seen:
                errors.append(ValidationError(
                    f"Duplicate {label} ID '{id_}'",
                    category="duplicate_id",
                ))
            seen[id_] = True
        return errors

    def _check_duplicate_names(self) -> list[ValidationError]:
        names = []
        for path in sorted(self._exercises_dir.glob("*.json")):
            if path.name == "_index.json":
                continue
            data = _load_json(path)
            names.append(data.get("name", "").strip().lower())
        seen = {}
        errors = []
        for name in names:
            if name in seen:
                errors.append(ValidationError(
                    f"Duplicate exercise name '{name}'",
                    category="duplicate_name",
                ))
            seen[name] = True
        return errors

    def _check_file_names_match_ids(self, label: str, directory: Path) -> list[ValidationError]:
        errors = []
        for path in sorted(directory.glob("*.json")):
            if path.name == "_index.json":
                continue
            data = _load_json(path)
            expected = f"{data.get('id', '')}.json"
            if path.name != expected:
                errors.append(ValidationError(
                    f"{label.capitalize()} file '{path.name}' has id '{data.get('id', '')}', expected '{expected}'",
                    category="filename_mismatch",
                ))
        return errors

    def _check_alias_consistency(self) -> list[ValidationError]:
        errors = []
        known_ids = set(self._loader.get_all_exercises().keys())

        for ex_id, ex in self._loader.get_all_exercises().items():
            for alias in ex.get("aliases", []):
                if not isinstance(alias, str) or not alias.strip():
                    errors.append(ValidationError(
                        f"Exercise '{ex_id}' has empty alias",
                        category="alias_format",
                    ))

        alias_path = self._aliases_path
        if alias_path.exists():
            with open(alias_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if isinstance(data, dict):
                for alias_name, ex_id in data.items():
                    if ex_id not in known_ids:
                        errors.append(ValidationError(
                            f"Alias '{alias_name}' maps to unknown exercise '{ex_id}'",
                            category="alias_orphan",
                        ))
                    if not isinstance(ex_id, str):
                        names = ", ".join(ex_id) if isinstance(ex_id, list) else str(ex_id)
                        errors.append(ValidationError(
                            f"Alias '{alias_name}' maps to non-string value: {names}",
                            category="alias_format",
                        ))
        return errors

    def _check_schema_validity(self, schema_name: str) -> list[ValidationError]:
        errors = []
        schema_file = self._schemas_dir / f"{schema_name}.schema.json"
        if not schema_file.exists():
            return [ValidationError(f"Schema file not found: {schema_file}", category="schema_missing")]

        schema = _load_json(schema_file)

        if schema_name == "exercise":
            directory = self._exercises_dir
            skip = "_index.json"
        elif schema_name == "muscle":
            directory = self._muscles_dir
            skip = "_index.json"
        else:
            program_path = PROJECT_ROOT / "data" / "program.json"
            if not program_path.exists():
                return [ValidationError(f"Program file not found: {program_path}", category="schema_missing")]
            try:
                program = _load_json(program_path)
                jsonschema.validate(program, schema)
            except jsonschema.ValidationError as e:
                return [ValidationError(f"Program schema validation: {e.message}", category="schema_validation")]
            return []

        for path in sorted(directory.glob("*.json")):
            if path.name == skip:
                continue
            try:
                data = _load_json(path)
                jsonschema.validate(data, schema)
            except jsonschema.ValidationError as e:
                errors.append(ValidationError(
                    f"{schema_name.capitalize()} '{path.name}' schema error: {e.message}",
                    category="schema_validation",
                ))
        return errors

    def _check_orphan_muscle_references(self) -> list[ValidationError]:
        errors = []
        known_muscles = set(self._loader.get_all_muscles().keys())

        for ex_id, ex in self._loader.get_all_exercises().items():
            for m in ex.get("primary_muscles", []):
                if m not in known_muscles:
                    errors.append(ValidationError(
                        f"Exercise '{ex_id}' references unknown primary muscle '{m}'",
                        category="orphan_muscle",
                    ))
            for m in ex.get("secondary_muscles", []):
                if m and m not in known_muscles:
                    errors.append(ValidationError(
                        f"Exercise '{ex_id}' references unknown secondary muscle '{m}'",
                        category="orphan_muscle",
                    ))
            for mc in ex.get("muscle_contributions", []):
                mid = mc.get("muscle_id") if isinstance(mc, dict) else mc.muscle_id
                if mid not in known_muscles:
                    errors.append(ValidationError(
                        f"Exercise '{ex_id}' references unknown muscle '{mid}' in contributions",
                        category="orphan_muscle",
                    ))
        return errors

    def _check_orphan_exercise_references(self) -> list[ValidationError]:
        errors = []
        known_ids = set(self._loader.get_all_exercises().keys())
        program = self._loader.load_program()

        for day in program.get("days", []):
            day_name = day.get("name", "?")
            for ex in day.get("exercises", []):
                eid = ex.get("exercise_id", "")
                if eid and eid not in known_ids:
                    errors.append(ValidationError(
                        f"Program day '{day_name}' references unknown exercise '{eid}'",
                        category="orphan_exercise",
                    ))
        return errors

    def _check_contribution_totals(self) -> list[ValidationError]:
        errors = []
        for ex_id, ex in self._loader.get_all_exercises().items():
            mc_list = ex.get("muscle_contributions", [])
            if not mc_list:
                continue
            total = sum(mc.get("percentage", 0) if isinstance(mc, dict) else mc.percentage for mc in mc_list)
            if abs(total - 100.0) > 1.0:
                errors.append(ValidationError(
                    f"Exercise '{ex_id}' muscle_contributions sum to {total:.1f}%, expected ~100%",
                    category="contribution_total",
                ))
        return errors

    def _check_tag_format(self) -> list[ValidationError]:
        errors = []
        for ex_id, ex in self._loader.get_all_exercises().items():
            for tag in ex.get("tags", []):
                if not isinstance(tag, str) or not tag.strip():
                    errors.append(ValidationError(
                        f"Exercise '{ex_id}' has empty or invalid tag",
                        category="tag_format",
                    ))
                elif "  " in tag:
                    errors.append(ValidationError(
                        f"Exercise '{ex_id}' has tag with multiple spaces: '{tag}'",
                        category="tag_format",
                    ))
        return errors

    def _check_reference_format(self) -> list[ValidationError]:
        errors = []
        for ex_id, ex in self._loader.get_all_exercises().items():
            for i, ref in enumerate(ex.get("references", [])):
                if isinstance(ref, dict):
                    if "title" not in ref or not ref["title"]:
                        errors.append(ValidationError(
                            f"Exercise '{ex_id}' reference #{i} missing title",
                            category="reference_format",
                        ))
                else:
                    errors.append(ValidationError(
                        f"Exercise '{ex_id}' reference #{i} is not an object",
                        category="reference_format",
                    ))
        for m_id, m in self._loader.get_all_muscles().items():
            for i, ref in enumerate(m.get("references", [])):
                if isinstance(ref, dict):
                    if "title" not in ref or not ref["title"]:
                        errors.append(ValidationError(
                            f"Muscle '{m_id}' reference #{i} missing title",
                            category="reference_format",
                        ))
                else:
                    errors.append(ValidationError(
                        f"Muscle '{m_id}' reference #{i} is not an object",
                        category="reference_format",
                    ))
        return errors
