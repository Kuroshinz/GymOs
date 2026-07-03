from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Reference:
    title: str = ""
    url: str = ""
    authors: list[str] = field(default_factory=list)
    year: Optional[int] = None
    type: str = "other"


@dataclass
class MuscleContribution:
    muscle_id: str
    percentage: float


@dataclass
class RecommendedRir:
    min: int = 0
    max: int = 0
    description: str = ""


@dataclass
class JointStress:
    overall: str = "moderate"
    notes: str = ""


@dataclass
class VolumeLandmarks:
    mev: dict = field(default_factory=lambda: {"min_sets": 0, "max_sets": 0})
    mav: dict = field(default_factory=lambda: {"min_sets": 0, "max_sets": 0})
    mrv: dict = field(default_factory=lambda: {"min_sets": 0, "max_sets": 0})


@dataclass
class RecommendedFrequency:
    min_times_per_week: int = 1
    max_times_per_week: int = 1
    description: str = ""


@dataclass
class RecoveryCharacteristics:
    recovery_time_hours: Optional[dict] = None
    fatigue_factor: str = "moderate"
    description: str = ""


@dataclass
class ExerciseData:
    id: str
    name: str
    category: str
    primary_muscles: list[str] = field(default_factory=list)
    secondary_muscles: list[str] = field(default_factory=list)
    equipment: str = ""
    difficulty: str = "beginner"
    movement_pattern: str = ""
    mechanics: str = "compound"
    aliases: list[str] = field(default_factory=list)
    tempo: str = ""
    range_of_motion: str = ""
    setup: list[str] = field(default_factory=list)
    execution: list[str] = field(default_factory=list)
    cues: list[str] = field(default_factory=list)
    breathing: str = ""
    common_mistakes: list[str] = field(default_factory=list)
    alternatives: list[str] = field(default_factory=list)
    variations: list[str] = field(default_factory=list)
    progression: str = ""
    spotting: str = ""
    rep_ranges: Optional[dict] = None
    advantages: list[str] = field(default_factory=list)
    weight_progression: str = ""
    alterations: list[str] = field(default_factory=list)
    recommendation: str = ""
    alternative: Optional[list[str] | str] = None
    uses: Optional[list[str] | str] = None
    shoulder_safety_note: str = ""
    triceps_activation: str = ""
    purpose: str = ""
    hypertrophy_rep_range: Optional[dict] = None
    rest_time: Optional[dict] = None
    movement_plane: str = ""
    stability_requirement: str = "moderate"
    skill_requirement: str = "moderate"
    fatigue_score: Optional[float] = None
    systemic_fatigue: str = "moderate"
    joint_stress: Optional[JointStress] = None
    force_curve: str = ""
    resistance_profile: str = ""
    unilateral_bilateral: str = "bilateral"
    recommended_rir: Optional[RecommendedRir] = None
    muscle_contributions: list[MuscleContribution] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    knowledge_version: str = ""
    last_updated: str = ""
    references: list[Reference] = field(default_factory=list)
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "ExerciseData":
        mc_list = []
        for mc in data.get("muscle_contributions", []):
            mc_list.append(MuscleContribution(
                muscle_id=mc["muscle_id"],
                percentage=mc["percentage"],
            ))

        rir_raw = data.get("recommended_rir")
        rir = RecommendedRir(**rir_raw) if rir_raw else None

        js_raw = data.get("joint_stress")
        js = JointStress(**js_raw) if js_raw else None

        refs = []
        for r in data.get("references", []):
            refs.append(Reference(**r))

        return cls(
            id=data["id"],
            name=data["name"],
            category=data.get("category", ""),
            primary_muscles=data.get("primary_muscles", []),
            secondary_muscles=data.get("secondary_muscles", []),
            equipment=data.get("equipment", ""),
            difficulty=data.get("difficulty", "beginner"),
            movement_pattern=data.get("movement_pattern", ""),
            mechanics=data.get("mechanics", "compound"),
            aliases=data.get("aliases", []),
            tempo=data.get("tempo", ""),
            range_of_motion=data.get("range_of_motion", ""),
            setup=data.get("setup", []),
            execution=data.get("execution", []),
            cues=data.get("cues", []),
            breathing=data.get("breathing", ""),
            common_mistakes=data.get("common_mistakes", []),
            alternatives=data.get("alternatives", []),
            variations=data.get("variations", []),
            progression=data.get("progression", ""),
            spotting=data.get("spotting", ""),
            rep_ranges=data.get("rep_ranges"),
            advantages=data.get("advantages", []),
            weight_progression=data.get("weight_progression", ""),
            alterations=data.get("alterations", []),
            recommendation=data.get("recommendation", ""),
            alternative=data.get("alternative"),
            uses=data.get("uses"),
            shoulder_safety_note=data.get("shoulder_safety_note", ""),
            triceps_activation=data.get("triceps_activation", ""),
            purpose=data.get("purpose", ""),
            hypertrophy_rep_range=data.get("hypertrophy_rep_range"),
            rest_time=data.get("rest_time"),
            movement_plane=data.get("movement_plane", ""),
            stability_requirement=data.get("stability_requirement", "moderate"),
            skill_requirement=data.get("skill_requirement", "moderate"),
            fatigue_score=data.get("fatigue_score"),
            systemic_fatigue=data.get("systemic_fatigue", "moderate"),
            joint_stress=js,
            force_curve=data.get("force_curve", ""),
            resistance_profile=data.get("resistance_profile", ""),
            unilateral_bilateral=data.get("unilateral_bilateral", "bilateral"),
            recommended_rir=rir,
            muscle_contributions=mc_list,
            tags=data.get("tags", []),
            knowledge_version=data.get("knowledge_version", ""),
            last_updated=data.get("last_updated", ""),
            references=refs,
            raw=data,
        )


@dataclass
class MuscleData:
    id: str
    display_name: str
    group: str
    synergists: list[str] = field(default_factory=list)
    antagonists: list[str] = field(default_factory=list)
    weekly_volume_landmarks: Optional[VolumeLandmarks] = None
    recommended_frequency: Optional[RecommendedFrequency] = None
    recovery_characteristics: Optional[RecoveryCharacteristics] = None
    recommended_exercises: list[str] = field(default_factory=list)
    knowledge_version: str = ""
    created_at: str = ""
    last_updated: str = ""
    verified: Optional[bool] = None
    verified_by: str = ""
    evidence_level: str = ""
    references: list[Reference] = field(default_factory=list)
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "MuscleData":
        vl_raw = data.get("weekly_volume_landmarks")
        vl = VolumeLandmarks(**vl_raw) if vl_raw else None

        rf_raw = data.get("recommended_frequency")
        rf = RecommendedFrequency(**rf_raw) if rf_raw else None

        rc_raw = data.get("recovery_characteristics")
        rc = RecoveryCharacteristics(**rc_raw) if rc_raw else None

        refs = []
        for r in data.get("references", []):
            refs.append(Reference(**r))

        return cls(
            id=data["id"],
            display_name=data.get("display_name", ""),
            group=data.get("group", ""),
            synergists=data.get("synergists", []),
            antagonists=data.get("antagonists", []),
            weekly_volume_landmarks=vl,
            recommended_frequency=rf,
            recovery_characteristics=rc,
            recommended_exercises=data.get("recommended_exercises", []),
            knowledge_version=data.get("knowledge_version", ""),
            created_at=data.get("created_at", ""),
            last_updated=data.get("last_updated", ""),
            verified=data.get("verified"),
            verified_by=data.get("verified_by", ""),
            evidence_level=data.get("evidence_level", ""),
            references=refs,
            raw=data,
        )


@dataclass
class ProgramExerciseData:
    name: str
    exercise_id: str = ""
    target_sets: int = 3
    target_reps: str = "10"
    muscle_group: str = ""
    sort_order: int = 0
    notes: str = ""


@dataclass
class ProgramDayData:
    name: str
    sort_order: int = 0
    exercises: list[ProgramExerciseData] = field(default_factory=list)
    notes: str = ""


@dataclass
class ProgramData:
    name: str
    description: str = ""
    version: str = ""
    author: str = ""
    source: str = ""
    goal: str = "hypertrophy"
    experience_level: str = "intermediate"
    split: str = ""
    mesocycle_duration_weeks: int = 8
    deload_week: Optional[dict] = None
    progression_strategy: Optional[dict] = None
    priority_muscles: list[str] = field(default_factory=list)
    rules: list[str] = field(default_factory=list)
    days: list[ProgramDayData] = field(default_factory=list)
    knowledge_version: str = ""
    created_at: str = ""
    last_updated: str = ""
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> "ProgramData":
        days = []
        for d in data.get("days", []):
            exercises = []
            for e in d.get("exercises", []):
                exercises.append(ProgramExerciseData(
                    name=e.get("name", ""),
                    exercise_id=e.get("exercise_id", ""),
                    target_sets=e.get("target_sets", 3),
                    target_reps=e.get("target_reps", "10"),
                    muscle_group=e.get("muscle_group", ""),
                    sort_order=e.get("sort_order", 0),
                    notes=e.get("notes", ""),
                ))
            days.append(ProgramDayData(
                name=d.get("name", ""),
                sort_order=d.get("sort_order", 0),
                exercises=exercises,
                notes=d.get("notes", ""),
            ))

        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            version=data.get("version", ""),
            author=data.get("author", ""),
            source=data.get("source", ""),
            goal=data.get("goal", "hypertrophy"),
            experience_level=data.get("experience_level", "intermediate"),
            split=data.get("split", ""),
            mesocycle_duration_weeks=data.get("mesocycle_duration_weeks", 8),
            deload_week=data.get("deload_week"),
            progression_strategy=data.get("progression_strategy"),
            priority_muscles=data.get("priority_muscles", []),
            rules=data.get("rules", []),
            days=days,
            knowledge_version=data.get("knowledge_version", ""),
            created_at=data.get("created_at", ""),
            last_updated=data.get("last_updated", ""),
            raw=data,
        )
