"""Planning Optimizer Constraints — Constraint checking and penalty computation for optimization candidates."""

from __future__ import annotations

from typing import Any

from shared.planning_optimizer.domain import ConstraintType, OptimizationConstraint


class ConstraintChecker:
    """Pure functions that check constraints against candidate plan data.

    Each method returns (is_satisfied, violations) where violations is a list of messages.
    """

    @staticmethod
    def check_equipment(
        plan_data: dict[str, Any],
        constraint: OptimizationConstraint,
    ) -> tuple[bool, list[str]]:
        """Check if plan only uses available equipment."""
        violations: list[str] = []
        available = constraint.value
        if available is None:
            return True, violations
        if isinstance(available, (list, set)):
            available_set = set(available)
            exercises = ConstraintChecker._extract_exercises(plan_data)
            for ex in exercises:
                equipment = ex.get("equipment", "")
                if equipment and equipment not in available_set:
                    violations.append(
                        f"Exercise requires '{equipment}' which is not in available equipment"
                    )
        return len(violations) == 0, violations

    @staticmethod
    def check_frequency(
        plan_data: dict[str, Any],
        constraint: OptimizationConstraint,
    ) -> tuple[bool, list[str]]:
        """Check if session frequency is within limits."""
        violations: list[str] = []
        sessions_per_week = plan_data.get("sessions_per_week", 0)

        if constraint.max_value is not None and sessions_per_week > constraint.max_value:
            violations.append(
                f"Session frequency {sessions_per_week} exceeds max {constraint.max_value}"
            )
        if constraint.min_value is not None and sessions_per_week < constraint.min_value:
            violations.append(
                f"Session frequency {sessions_per_week} below min {constraint.min_value}"
            )
        return len(violations) == 0, violations

    @staticmethod
    def check_time(
        plan_data: dict[str, Any],
        constraint: OptimizationConstraint,
    ) -> tuple[bool, list[str]]:
        """Check if session duration is within time limits."""
        violations: list[str] = []
        weeks = plan_data.get("weeks", [])

        for week_idx, week in enumerate(weeks):
            for session_idx, session in enumerate(week.get("sessions", [])):
                duration = session.get("estimated_duration_minutes", 0)
                if constraint.max_value is not None and duration > constraint.max_value:
                    violations.append(
                        f"Session {session_idx} in week {week_idx}: duration {duration}m exceeds max {constraint.max_value}m"
                    )
                if constraint.min_value is not None and duration < constraint.min_value:
                    violations.append(
                        f"Session {session_idx} in week {week_idx}: duration {duration}m below min {constraint.min_value}m"
                    )
        return len(violations) == 0, violations

    @staticmethod
    def check_recovery(
        plan_data: dict[str, Any],
        constraint: OptimizationConstraint,
    ) -> tuple[bool, list[str]]:
        """Check if recovery constraints are satisfied."""
        violations: list[str] = []
        weeks = plan_data.get("weeks", [])

        total_sessions = sum(len(w.get("sessions", [])) for w in weeks)
        rest_sessions = sum(
            1 for w in weeks for s in w.get("sessions", [])
            if s.get("day_type") == "rest"
        )
        rest_ratio = rest_sessions / max(total_sessions, 1)

        if constraint.min_value is not None and rest_ratio < constraint.min_value:
            violations.append(
                f"Rest ratio {rest_ratio:.2f} below min {constraint.min_value:.2f}"
            )

        max_consecutive = 0
        current = 0
        for w in weeks:
            for s in w.get("sessions", []):
                if s.get("day_type") != "rest":
                    current += 1
                    max_consecutive = max(max_consecutive, current)
                else:
                    current = 0

        if constraint.max_value is not None and max_consecutive > constraint.max_value:
            violations.append(
                f"Max consecutive training days {max_consecutive} exceeds limit {constraint.max_value}"
            )
        return len(violations) == 0, violations

    @staticmethod
    def check_intent(
        plan_data: dict[str, Any],
        constraint: OptimizationConstraint,
    ) -> tuple[bool, list[str]]:
        """Check if plan aligns with user intent."""
        violations: list[str] = []
        target_goal = constraint.value
        if target_goal is None:
            return True, violations

        mesocycles = plan_data.get("mesocycles", [])
        has_matching = any(
            m.get("goal", "").lower() == target_goal.lower()
            for m in mesocycles
        )
        if not has_matching and constraint.is_hard:
            violations.append(f"No mesocycle matches target goal '{target_goal}'")
        return len(violations) == 0, violations

    @staticmethod
    def check_nutrition(
        plan_data: dict[str, Any],
        constraint: OptimizationConstraint,
    ) -> tuple[bool, list[str]]:
        """Check if nutritional constraints are satisfied."""
        violations: list[str] = []
        nutrition = plan_data.get("nutrition", {})
        if constraint.min_value is not None:
            actual = nutrition.get("calories", 0)
            if actual < constraint.min_value:
                violations.append(
                    f"Calories {actual} below min {constraint.min_value}"
                )
        if constraint.max_value is not None:
            actual = nutrition.get("protein", 0)
            if actual > constraint.max_value:
                violations.append(
                    f"Protein {actual}g exceeds max {constraint.max_value}g"
                )
        return len(violations) == 0, violations

    @staticmethod
    def check_safety(
        plan_data: dict[str, Any],
        constraint: OptimizationConstraint,
    ) -> tuple[bool, list[str]]:
        """Check safety constraints (volume, intensity ceilings)."""
        violations: list[str] = []
        total_sets = plan_data.get("total_sets", 0)
        total_weeks = plan_data.get("total_weeks", 1)

        if total_weeks > 0:
            avg_weekly_sets = total_sets / total_weeks
            if constraint.max_value is not None and avg_weekly_sets > constraint.max_value:
                violations.append(
                    f"Average weekly sets {avg_weekly_sets:.0f} exceeds safety limit {constraint.max_value}"
                )

        weeks = plan_data.get("weeks", [])
        high_volume_sessions = 0
        total_sessions = 0
        for w in weeks:
            for s in w.get("sessions", []):
                total_sessions += 1
                session_sets = sum(e.get("sets", 0) for e in s.get("exercises", []))
                if session_sets > 20:
                    high_volume_sessions += 1

        if total_sessions > 0 and high_volume_sessions / total_sessions > 0.3:
            violations.append(
                f"High-volume sessions ({high_volume_sessions}/{total_sessions}) exceed safe threshold"
            )
        return len(violations) == 0, violations

    @staticmethod
    def check_experience(
        plan_data: dict[str, Any],
        constraint: OptimizationConstraint,
    ) -> tuple[bool, list[str]]:
        """Check if plan is appropriate for user experience level."""
        violations: list[str] = []
        weeks = plan_data.get("weeks", [])

        max_sets_per_session = 0
        for w in weeks:
            for s in w.get("sessions", []):
                session_sets = sum(e.get("sets", 0) for e in s.get("exercises", []))
                max_sets_per_session = max(max_sets_per_session, session_sets)

        if constraint.max_value is not None and max_sets_per_session > constraint.max_value:
            violations.append(
                f"Max sets per session {max_sets_per_session} exceeds experience limit {constraint.max_value}"
            )
        return len(violations) == 0, violations

    @staticmethod
    def check_injury(
        plan_data: dict[str, Any],
        constraint: OptimizationConstraint,
    ) -> tuple[bool, list[str]]:
        """Check if plan avoids injured muscle groups."""
        violations: list[str] = []
        injured_groups = constraint.value
        if injured_groups is None:
            return True, violations
        if isinstance(injured_groups, (list, set)):
            injured_set = set(injured_groups)
            exercises = ConstraintChecker._extract_exercises(plan_data)
            for ex in exercises:
                mg = ex.get("target_muscle_group", "")
                if mg in injured_set:
                    violations.append(
                        f"Exercise targets injured muscle group '{mg}'"
                    )
        return len(violations) == 0, violations

    @staticmethod
    def check_schedule(
        plan_data: dict[str, Any],
        constraint: OptimizationConstraint,
    ) -> tuple[bool, list[str]]:
        """Check if plan fits schedule constraints."""
        violations: list[str] = []
        weeks = plan_data.get("weeks", [])
        total_weeks = len(weeks)

        if constraint.max_value is not None and total_weeks > constraint.max_value:
            violations.append(
                f"Plan duration {total_weeks} weeks exceeds max {constraint.max_value}"
            )
        if constraint.min_value is not None and total_weeks < constraint.min_value:
            violations.append(
                f"Plan duration {total_weeks} weeks below min {constraint.min_value}"
            )
        return len(violations) == 0, violations

    @staticmethod
    def check(
        plan_data: dict[str, Any],
        constraint: OptimizationConstraint,
    ) -> tuple[bool, list[str]]:
        """Dispatch to the correct checker based on constraint type."""
        dispatcher = {
            ConstraintType.EQUIPMENT: ConstraintChecker.check_equipment,
            ConstraintType.FREQUENCY: ConstraintChecker.check_frequency,
            ConstraintType.TIME: ConstraintChecker.check_time,
            ConstraintType.RECOVERY: ConstraintChecker.check_recovery,
            ConstraintType.INTENT: ConstraintChecker.check_intent,
            ConstraintType.NUTRITION: ConstraintChecker.check_nutrition,
            ConstraintType.SAFETY: ConstraintChecker.check_safety,
            ConstraintType.EXPERIENCE: ConstraintChecker.check_experience,
            ConstraintType.INJURY: ConstraintChecker.check_injury,
            ConstraintType.SCHEDULE: ConstraintChecker.check_schedule,
        }
        checker = dispatcher.get(constraint.constraint_type)
        if checker is None:
            return True, []
        return checker(plan_data, constraint)

    @staticmethod
    def check_all(
        plan_data: dict[str, Any],
        constraints: list[OptimizationConstraint],
    ) -> tuple[bool, list[str], int]:
        """Check all constraints against plan data.

        Returns (all_satisfied, violations_list, violation_count).
        """
        all_violations: list[str] = []
        hard_violations = 0

        for constraint in constraints:
            satisfied, violations = ConstraintChecker.check(plan_data, constraint)
            all_violations.extend(violations)
            if not satisfied and constraint.is_hard:
                hard_violations += 1

        return hard_violations == 0, all_violations, hard_violations

    @staticmethod
    def compute_penalty(
        plan_data: dict[str, Any],
        constraints: list[OptimizationConstraint],
        penalty_factor: float = 0.3,
    ) -> float:
        """Compute a score penalty based on constraint violations."""
        if not constraints:
            return 0.0
        _, violations, hard_violations = ConstraintChecker.check_all(plan_data, constraints)
        if hard_violations == 0 and not violations:
            return 0.0
        return min(1.0, (hard_violations * 0.5 + len(violations) * 0.1) * penalty_factor)

    @staticmethod
    def _extract_exercises(plan_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract all exercises from plan data."""
        exercises: list[dict[str, Any]] = []
        weeks = plan_data.get("weeks", [])
        if not weeks:
            mesocycles = plan_data.get("mesocycles", [])
            for m in mesocycles:
                for w in m.get("weeks", []):
                    weeks.append(w)
        for w in weeks:
            for s in w.get("sessions", []):
                for e in s.get("exercises", []):
                    exercises.append(e)
        return exercises
