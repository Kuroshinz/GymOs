"""Migration script: Upgrade all exercise, muscle, and program files with v2 fields.

Idempotent — safe to run multiple times.
"""

import json
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXERCISES_DIR = PROJECT_ROOT / "knowledge" / "exercises"
MUSCLES_DIR = PROJECT_ROOT / "knowledge" / "muscles"
PROGRAM_PATH = PROJECT_ROOT / "data" / "program.json"


def _load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _save_json(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _infer_movement_plane(ex: dict) -> str:
    mp = ex.get("movement_pattern", "")
    plane_map = {
        "horizontal_push": "sagittal",
        "vertical_push": "sagittal",
        "horizontal_pull": "sagittal",
        "vertical_pull": "sagittal",
        "squat": "sagittal",
        "hip_hinge": "sagittal",
        "lunge": "sagittal",
        "lateral_lunge": "frontal",
        "side_raise": "frontal",
        "lateral_raise": "frontal",
        "rotational": "transverse",
        "twist": "transverse",
        "carry": "frontal",
        "cable_rotation": "transverse",
        "cable_rotational": "transverse",
        "anti_rotation": "transverse",
    }
    return plane_map.get(mp, "multi_planar")


def _infer_stability(ex: dict) -> str:
    equip = ex.get("equipment", "").lower()
    if equip in ("machine", "smith_machine"):
        return "low"
    if equip in ("bodyweight",):
        return "high"
    if equip in ("cable",):
        return "moderate"
    if ex.get("mechanics") == "isolation":
        return "low"
    if ex.get("movement_pattern") in ("squat", "hip_hinge", "lunge"):
        return "high"
    return "moderate"


def _infer_skill(ex: dict) -> str:
    diff = ex.get("difficulty", "")
    skill_map = {"beginner": "low", "intermediate": "moderate", "advanced": "high"}
    return skill_map.get(diff, "moderate")


def _infer_fatigue_score(ex: dict) -> float:
    mech = ex.get("mechanics", "")
    if mech == "compound":
        return 6.0
    elif mech == "isolation":
        return 3.0
    return 5.0


def _infer_systemic_fatigue(ex: dict) -> str:
    mech = ex.get("mechanics", "")
    if mech == "compound":
        return "high"
    elif mech == "isometric":
        return "moderate"
    return "low"


def _infer_force_curve(ex: dict) -> str:
    equip = ex.get("equipment", "").lower()
    curve_map = {
        "band": "ascending",
        "cable": "ascending",
        "dumbbell": "flat",
        "barbell": "flat",
        "machine": "flat",
        "smith_machine": "flat",
        "bodyweight": "flat",
    }
    return curve_map.get(equip, "flat")


def _infer_resistance_profile(ex: dict) -> str:
    equip = ex.get("equipment", "").lower()
    profile_map = {
        "band": "ascending",
        "cable": "ascending",
        "dumbbell": "constant",
        "barbell": "constant",
        "machine": "linear_variable",
        "smith_machine": "constant",
    }
    return profile_map.get(equip, "constant")


def _infer_unilateral(ex: dict) -> str:
    name = ex.get("name", "").lower()
    if any(kw in name for kw in ("single", "one-arm", "one_arm", "unilateral", "single-leg", "single_leg", "bulgarian")):
        return "unilateral"
    return "bilateral"


def _infer_joint_stress(ex: dict) -> dict:
    equip = ex.get("equipment", "").lower()
    mp = ex.get("movement_pattern", "")
    stress = "moderate"
    notes = ""
    if equip == "machine" or equip == "bodyweight":
        stress = "low"
    if mp in ("squat", "hip_hinge", "lunge"):
        stress = "high"
    return {"overall": stress, "notes": notes}


def _infer_muscle_contributions(ex: dict) -> list[dict]:
    if ex.get("muscle_contributions"):
        return ex["muscle_contributions"]
    primary = ex.get("primary_muscles", [])
    secondary = ex.get("secondary_muscles", [])
    if not primary:
        return []
    contributions = []
    total = len(primary) + len(secondary) * 0.3
    primary_pct = 100.0 / total if total else 0
    secondary_pct = (30.0 / total) if total and secondary else 0
    for pm in primary:
        contributions.append({"muscle_id": pm, "percentage": round(primary_pct, 1)})
    for sm in secondary:
        contributions.append({"muscle_id": sm, "percentage": round(secondary_pct, 1)})
    return contributions


def _infer_rir(ex: dict) -> dict | None:
    if ex.get("recommended_rir"):
        return ex["recommended_rir"]
    diff = ex.get("difficulty", "")
    rir_map = {
        "beginner": {"min": 2, "max": 3, "description": "Leave 2-3 reps in reserve for safety"},
        "intermediate": {"min": 1, "max": 2, "description": "Leave 1-2 reps in reserve"},
        "advanced": {"min": 0, "max": 1, "description": "Take close to failure, 0-1 RIR"},
    }
    return rir_map.get(diff, {"min": 1, "max": 2, "description": "Leave 1-2 reps in reserve"})


def _today() -> str:
    return date.today().isoformat()


def migrate_exercises() -> int:
    count = 0
    for path in sorted(EXERCISES_DIR.glob("*.json")):
        if path.name == "_index.json":
            continue
        ex = _load_json(path)
        changed = False
        new_v2 = {
            "movement_plane": _infer_movement_plane(ex),
            "stability_requirement": _infer_stability(ex),
            "skill_requirement": _infer_skill(ex),
            "fatigue_score": _infer_fatigue_score(ex),
            "systemic_fatigue": _infer_systemic_fatigue(ex),
            "joint_stress": _infer_joint_stress(ex),
            "force_curve": _infer_force_curve(ex),
            "resistance_profile": _infer_resistance_profile(ex),
            "unilateral_bilateral": _infer_unilateral(ex),
            "recommended_rir": _infer_rir(ex),
            "muscle_contributions": _infer_muscle_contributions(ex),
            "tags": ex.get("tags", []),
            "knowledge_version": ex.get("knowledge_version", "1.0.0"),
            "last_updated": ex.get("last_updated", _today()),
            "references": ex.get("references", []),
        }
        for key, value in new_v2.items():
            existing = ex.get(key)
            if key not in ex or (isinstance(existing, str) and existing == "" and isinstance(value, str) and value != ""):
                ex[key] = value
                changed = True
        if changed:
            _save_json(path, ex)
            count += 1
    return count


def migrate_muscles() -> int:
    count = 0
    for path in sorted(MUSCLES_DIR.glob("*.json")):
        if path.name == "_index.json":
            continue
        m = _load_json(path)
        changed = False
        new_versioning = {
            "knowledge_version": m.get("knowledge_version", "1.0.0"),
            "created_at": m.get("created_at", ""),
            "last_updated": m.get("last_updated", _today()),
            "verified_by": m.get("verified_by", ""),
            "references": m.get("references", []),
        }
        for key, value in new_versioning.items():
            if key not in m:
                m[key] = value
                changed = True

        vertype = type(m.get("verified"))
        if vertype is not bool and "verified" in m and m.get("verified") is None:
            del m["verified"]
            changed = True

        evidence = m.get("evidence_level")
        if evidence == "" and "evidence_level" in m:
            del m["evidence_level"]
            changed = True
        if changed:
            _save_json(path, m)
            count += 1
    return count


def migrate_program() -> bool:
    if not PROGRAM_PATH.exists():
        print(f"Program file not found: {PROGRAM_PATH}")
        return False
    prog = _load_json(PROGRAM_PATH)
    changed = False
    new_fields = {
        "knowledge_version": prog.get("knowledge_version", "1.0.0"),
        "created_at": prog.get("created_at", ""),
        "last_updated": prog.get("last_updated", _today()),
    }
    for key, value in new_fields.items():
        if key not in prog:
            prog[key] = value
            changed = True
    if changed:
        _save_json(PROGRAM_PATH, prog)
    return changed


def main():
    print("Migrating exercise files...")
    ex_count = migrate_exercises()
    print(f"  Updated {ex_count} exercise files")

    print("Migrating muscle files...")
    m_count = migrate_muscles()
    print(f"  Updated {m_count} muscle files")

    print("Migrating program file...")
    prog_changed = migrate_program()
    print(f"  Program {'updated' if prog_changed else 'already up to date'}")

    print("\nMigration complete.")


if __name__ == "__main__":
    main()
