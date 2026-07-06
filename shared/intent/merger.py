from __future__ import annotations

from datetime import datetime

from shared.intent.domain import (
    AdaptivePreference,
    ComplianceProfile,
    EquipmentProfile,
    IntentConflict,
    IntentConflictSeverity,
    LifestyleProfile,
    NutritionPreference,
    Priority,
    RecoveryPreference,
    RiskTolerance,
    Timeline,
    TrainingPreference,
    UserIntent,
)


class IntentMerger:
    @staticmethod
    def merge(base: UserIntent, override: UserIntent) -> UserIntent:
        return UserIntent(
            intent_id=base.intent_id or override.intent_id,
            version=override.version or base.version,
            status=override.status,
            created_at=base.created_at,
            updated_at=datetime.now().isoformat(),
            goals=override.goals if override.goals else base.goals,
            constraints=IntentMerger._merge_lists(base.constraints, override.constraints),
            timeline=override.timeline if override.timeline != Timeline() else base.timeline,
            equipment=override.equipment if override.equipment != EquipmentProfile() else base.equipment,
            lifestyle=override.lifestyle if override.lifestyle != LifestyleProfile() else base.lifestyle,
            compliance=override.compliance if override.compliance != ComplianceProfile() else base.compliance,
            risk_tolerance=override.risk_tolerance if override.risk_tolerance != RiskTolerance() else base.risk_tolerance,
            training=override.training if override.training != TrainingPreference() else base.training,
            nutrition=override.nutrition if override.nutrition != NutritionPreference() else base.nutrition,
            recovery=override.recovery if override.recovery != RecoveryPreference() else base.recovery,
            adaptive=override.adaptive if override.adaptive != AdaptivePreference() else base.adaptive,
            priorities=override.priorities if override.priorities != Priority() else base.priorities,
            conflicts=base.conflicts + override.conflicts,
        )

    @staticmethod
    def _merge_lists(base: list, override: list) -> list:
        return list(override) if override else list(base)


class ConflictResolver:
    @staticmethod
    def detect(intent: UserIntent) -> list[IntentConflict]:
        conflicts: list[IntentConflict] = []

        if intent.timeline.sessions_per_week > 6 and intent.lifestyle.occupation_hours_per_week >= 50:
            conflicts.append(IntentConflict(
                dimension_a="timeline.sessions_per_week",
                dimension_b="lifestyle.occupation_hours",
                description=f"Cannot sustain {intent.timeline.sessions_per_week} sessions with {intent.lifestyle.occupation_hours_per_week}h work weeks",
                severity=IntentConflictSeverity.HIGH,
            ))

        if intent.recovery.sleep_target > intent.lifestyle.sleep_avg_hours + 2:
            conflicts.append(IntentConflict(
                dimension_a="recovery.sleep_target",
                dimension_b="lifestyle.sleep_avg_hours",
                description=f"Sleep target {intent.recovery.sleep_target}h far exceeds current avg {intent.lifestyle.sleep_avg_hours}h",
                severity=IntentConflictSeverity.MEDIUM,
            ))

        if intent.nutrition.approach.value == "lean_bulk" and intent.nutrition.protein_g_per_kg < 1.6:
            conflicts.append(IntentConflict(
                dimension_a="nutrition.approach",
                dimension_b="nutrition.protein_g_per_kg",
                description="Lean bulk requires ≥1.6g/kg protein for optimal gains",
                severity=IntentConflictSeverity.MEDIUM,
            ))

        if intent.timeline.session_duration_minutes > 90 and intent.timeline.sessions_per_week >= 5:
            conflicts.append(IntentConflict(
                dimension_a="timeline.session_duration",
                dimension_b="timeline.sessions_per_week",
                description=f"{intent.timeline.sessions_per_week}x {intent.timeline.session_duration_minutes}min sessions exceed sustainable weekly volume",
                severity=IntentConflictSeverity.LOW,
            ))

        if intent.training.max_volume_per_muscle > 25 and intent.recovery.auto_deload:
            conflicts.append(IntentConflict(
                dimension_a="training.max_volume",
                dimension_b="recovery.auto_deload",
                description="High volume training contradicts auto-deload recovery preference",
                severity=IntentConflictSeverity.LOW,
            ))

        if intent.adaptive.require_approval and not intent.adaptive.enabled_scopes:
            conflicts.append(IntentConflict(
                dimension_a="adaptive.require_approval",
                dimension_b="adaptive.enabled_scopes",
                description="Approval required but no adaptive scopes enabled",
                severity=IntentConflictSeverity.MEDIUM,
            ))

        return conflicts

    @staticmethod
    def resolve(intent: UserIntent, auto_resolve: bool = True) -> UserIntent:
        detected = ConflictResolver.detect(intent)
        resolutions: list[IntentConflict] = []

        for conflict in detected:
            if not auto_resolve:
                resolutions.append(conflict)
                continue
            resolution = ConflictResolver._auto_resolve(conflict, intent)
            resolutions.append(resolution)

        return UserIntent(
            intent_id=intent.intent_id, version=intent.version, status=intent.status,
            created_at=intent.created_at, updated_at=datetime.now().isoformat(),
            goals=intent.goals, constraints=intent.constraints,
            timeline=intent.timeline, equipment=intent.equipment,
            lifestyle=intent.lifestyle, compliance=intent.compliance,
            risk_tolerance=intent.risk_tolerance,
            training=intent.training, nutrition=intent.nutrition,
            recovery=intent.recovery, adaptive=intent.adaptive,
            priorities=intent.priorities, conflicts=resolutions,
        )

    @staticmethod
    def _auto_resolve(conflict: IntentConflict, intent: UserIntent) -> IntentConflict:
        if "timeline.sessions_per_week" in conflict.dimension_a and "lifestyle" in conflict.dimension_b:
            return conflict.with_resolution("Reduce sessions to 4/week or adjust work hours expectation")
        if "recovery.sleep_target" in conflict.dimension_a:
            return conflict.with_resolution(f"Set sleep target to {intent.lifestyle.sleep_avg_hours + 0.5:.1f}h (incremental goal)")
        if "nutrition.approach" in conflict.dimension_a:
            return conflict.with_resolution("Increase protein target to 1.6g/kg minimum for lean bulk")
        if "session_duration" in conflict.dimension_a:
            return conflict.with_resolution("Reduce session duration to 75min or decrease frequency to 4/week")
        return conflict.with_resolution("Accepted — user preference override")
