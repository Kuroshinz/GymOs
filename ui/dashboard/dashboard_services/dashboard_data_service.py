"""Centralized data fetching for the GymOS dashboard.

Every method is a self-contained fetch that never crashes.
If a source is unavailable, the method returns sensible defaults.

Design principle: The Dashboard never duplicates GymBrain logic.
All business intelligence flows through the DecisionEngine.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from ui.dashboard.dashboard_models import DashboardData
from ui.dashboard.dashboard_services.overview_metrics import enrich_overview

logger = logging.getLogger(__name__)


class DashboardDataService:
    """Fetches and aggregates all data needed by dashboard widgets.

    Each method is independent and returns defaults on failure.
    The service is stateless — every call fetches fresh data.
    """

    def __init__(
        self,
        db: Any = None,
        decision_engine: Any = None,
        pr_engine: Any = None,
        prog_mgr: Any = None,
        nutrition_service: Any = None,
    ) -> None:
        self._db = db
        self._engine = decision_engine
        self._pr_engine = pr_engine
        self._prog_mgr = prog_mgr
        self._nutrition_service = nutrition_service

    # ─── Main Entry Point ─────────────────────────────────────

    def fetch_all(self) -> DashboardData:
        """Fetch all dashboard data in a single call."""
        try:
            header = self._fetch_header()
            goal_progress = self._fetch_goal_progress()
            recommendations = self._fetch_recommendations()
            workout = self._fetch_today_workout()
            priority_muscles = self._fetch_priority_muscles()
            recovery = self._fetch_recovery()
            volume = self._fetch_weekly_volume()
            prs = self._fetch_recent_prs()

            # Build goal progress fields
            gp_weight = 0.0
            gp_target = 0.0
            gp_remaining = 0.0
            gp_weeks = 0
            gp_rate = 0.0
            gp_quality = ""
            gp_percent = 0.0
            gp_date = ""
            if goal_progress:
                gp_weight = getattr(goal_progress, "current_weight_kg", 0.0) or 0.0
                gp_target = getattr(goal_progress, "goal_weight_kg", 0.0) or 0.0
                gp_remaining = max(0.0, gp_target - gp_weight)
                gp_weeks = int(getattr(goal_progress, "estimated_completion_weeks", 0) or 0)
                gp_rate = getattr(goal_progress, "weekly_gain_rate", 0.0) or 0.0
                gp_quality = getattr(goal_progress, "lean_bulk_quality", "") or ""
                gp_date = getattr(goal_progress, "estimated_completion_date", "") or ""
                if gp_target > 0:
                    gp_percent = min(gp_weight / gp_target * 100, 100)

            # Build nutrition fields
            nutrition_summary = self._fetch_nutrition_summary()

            # Build recovery fields
            recovery_status_val = recovery.get("status")
            recovery_level_str = ""
            recovery_score_val = 0.0
            if recovery_status_val:
                recovery_level_str = getattr(recovery_status_val, "level", "")
                if hasattr(recovery_level_str, "value"):
                    recovery_level_str = recovery_level_str.value
                recovery_score_val = getattr(recovery_status_val, "score", 0.0) or 0.0
            recovery_suggested = ""
            if recovery_status_val:
                recs = getattr(recovery_status_val, "recommendations", [])
                if recs:
                    recovery_suggested = recs[0]

            result = DashboardData(
                user_name=header.get("user_name", "") or "",
                current_program=header.get("current_program") or "No Active Program",
                mesocycle_week=header.get("mesocycle_week", 0),
                current_split_day=header.get("current_split_day", ""),
                current_weight=header.get("current_weight", 0.0),
                goal_weight_kg=gp_target,
                remaining_weight=gp_remaining,
                current_streak=header.get("current_streak", 0),
                greeting=header.get("greeting", "Good Morning"),
                total_workouts=header.get("total_workouts", 0),
                weekly_volume_kg=header.get("weekly_volume_kg", 0.0),
                goal_progress_weight=gp_weight,
                goal_progress_target=gp_target,
                goal_progress_remaining=gp_remaining,
                goal_progress_weeks=gp_weeks,
                goal_progress_rate=gp_rate,
                goal_progress_quality=gp_quality,
                goal_progress_percent=gp_percent,
                goal_progress_estimated_date=gp_date,
                recommendations=recommendations,
                today_workout_name=workout.get("name", ""),
                today_workout_exercise_count=workout.get("exercise_count", 0),
                today_workout_estimated_duration=workout.get("estimated_duration", 0),
                today_workout_target_volume=workout.get("target_volume", 0.0),
                today_workout_primary_muscles=workout.get("primary_muscles", []),
                today_workout_warmup_status=workout.get("warmup_status", ""),
                priority_muscles=priority_muscles,
                recovery_status=recovery_status_val,
                recovery_level=recovery_level_str,
                recovery_score=recovery_score_val,
                recovery_flags=recovery.get("flags", []),
                recovery_suggested_action=recovery_suggested,
                weekly_volume_data=volume,
                recent_prs=prs,
                nutrition_configured=nutrition_summary.get("configured", False),
                nutrition_data=nutrition_summary.get("data", {}),
            )
            enrich_overview(
                result,
                db=self._db,
                prog_mgr=self._prog_mgr,
                nutrition_service=self._nutrition_service,
            )
            return result
        except Exception:
            logger.warning("Dashboard fetch_all failed", exc_info=True)
            return DashboardData()

    # ─── Header ───────────────────────────────────────────────

    def _fetch_header(self) -> dict[str, Any]:
        try:
            prog_name = ""
            if self._prog_mgr:
                try:
                    prog_name = self._prog_mgr.get_active_name()
                except Exception:
                    logger.warning("Failed to get active program name", exc_info=True)

            total = 0
            streak = 0
            volume = 0.0
            current_weight = 0.0
            if self._db:
                try:
                    total = self._db.get_total_workouts()
                except Exception:
                    logger.warning("Failed to get total workouts", exc_info=True)
                try:
                    streak = self._db.get_streak()
                except Exception:
                    logger.warning("Failed to get streak", exc_info=True)
                try:
                    volume = self._db.get_recent_volume(7)
                except Exception:
                    logger.warning("Failed to get recent volume", exc_info=True)
                try:
                    latest_bw = self._db.get_latest_body_weight()
                    if latest_bw:
                        current_weight = float(getattr(latest_bw, "weight_kg", 0))
                except Exception:
                    logger.warning("Failed to get latest body weight", exc_info=True)

            hour = datetime.now().hour
            if hour < 12:
                greeting = "Good Morning"
            elif hour < 18:
                greeting = "Good Afternoon"
            else:
                greeting = "Good Evening"

            meso_week = 1
            split_day = ""
            try:
                if self._prog_mgr:
                    days_count = self._prog_mgr.get_active_day_count()
                    if days_count > 0 and total > 0:
                        meso_week = (total // days_count) + 1
                        days = self._prog_mgr.get_active_program_days()
                        if days:
                            idx = total % len(days)
                            split_day = days[idx].get("name", "") if idx < len(days) else ""
            except Exception:
                logger.warning("Failed to compute mesocycle week", exc_info=True)

            return {
                "user_name": "",
                "current_program": prog_name,
                "mesocycle_week": meso_week,
                "current_split_day": split_day,
                "current_weight": current_weight,
                "current_streak": streak,
                "greeting": greeting,
                "total_workouts": total,
                "weekly_volume_kg": volume,
            }
        except Exception:
            logger.warning("Dashboard _fetch_header failed", exc_info=True)
            return {}

    # ─── Goal Progress ────────────────────────────────────────

    def _fetch_goal_progress(self) -> Any:
        if not self._engine:
            return None
        try:
            return self._engine.get_goal_progress()
        except Exception:
            logger.warning("Failed to fetch goal progress", exc_info=True)
            return None

    # ─── Recommendations ──────────────────────────────────────

    def _fetch_recommendations(self) -> list[Any]:
        if not self._engine:
            return []
        try:
            return self._engine.get_today_recommendations(max_recs=10)
        except Exception:
            logger.warning("Failed to fetch recommendations", exc_info=True)
            return []

    # ─── Today's Workout ──────────────────────────────────────

    def _fetch_today_workout(self) -> dict[str, Any]:
        try:
            days: list[dict] = []
            if self._prog_mgr:
                try:
                    days = self._prog_mgr.get_active_program_days()
                except Exception:
                    logger.warning("Failed to get active program days", exc_info=True)
            if not days:
                return {}

            total = 0
            if self._db:
                try:
                    total = self._db.get_total_workouts()
                except Exception:
                    logger.warning("Failed to get total workouts", exc_info=True)

            idx = total % len(days) if total > 0 else 0
            day = days[idx] if idx < len(days) else days[0]

            exercises = day.get("exercises", [])
            primary_muscles = sorted(set(
                e.get("muscle_group", "") for e in exercises if e.get("muscle_group")
            ))

            duration = len(exercises) * 8 + 10
            target_vol = sum(
                e.get("target_sets", 3) * 10 * 40 for e in exercises
            )

            warmup_status = "Remember to warm up properly before starting."
            if self._engine:
                try:
                    recovery = self._engine.get_recovery_status()
                    if recovery:
                        level = recovery.level
                        if hasattr(level, "value"):
                            level = level.value
                        if level in ("high", "very_high"):
                            warmup_status = "Extended warm-up recommended due to high fatigue."
                except Exception:
                    logger.warning("Failed to get recovery status for warmup", exc_info=True)

            return {
                "name": day.get("name", "Rest Day"),
                "exercise_count": len(exercises),
                "estimated_duration": duration,
                "target_volume": target_vol,
                "primary_muscles": primary_muscles,
                "warmup_status": warmup_status,
            }
        except Exception:
            logger.warning("Dashboard _fetch_today_workout failed", exc_info=True)
            return {}

    # ─── Priority Muscles ─────────────────────────────────────

    def _fetch_priority_muscles(self) -> list[Any]:
        if not self._engine:
            return []
        try:
            return self._engine.get_priority_muscles()
        except Exception:
            logger.warning("Failed to fetch priority muscles", exc_info=True)
            return []

    # ─── Recovery ─────────────────────────────────────────────

    def _fetch_recovery(self) -> dict[str, Any]:
        status = None
        flags = []
        if self._engine:
            try:
                status = self._engine.get_recovery_status()
            except Exception:
                logger.warning("Failed to get recovery status from engine", exc_info=True)

        if self._db:
            try:
                from modules.workout.application.recovery_engine import RecoveryEngine

                re = RecoveryEngine(self._db)
                report = re.get_dashboard_flags()
                if report:
                    flags = report.flags
            except Exception:
                logger.warning("Failed to get dashboard flags from RecoveryEngine", exc_info=True)

        return {"status": status, "flags": flags}

    # ─── Weekly Volume ────────────────────────────────────────

    def _fetch_weekly_volume(self) -> list[dict[str, Any]]:
        if not self._db:
            return []
        try:
            return self._db.get_volume_by_day(days=28)
        except Exception:
            logger.warning("Failed to fetch weekly volume", exc_info=True)
            return []

    # ─── Nutrition ────────────────────────────────────────────

    def _fetch_nutrition_summary(self) -> dict:
        """Fetch nutrition summary for the dashboard."""
        if not self._nutrition_service:
            return {"configured": False, "data": {}}
        try:
            summary = self._nutrition_service.get_summary()
            return {
                "configured": summary.configured,
                "data": summary.to_dict(),
            }
        except Exception:
            logger.warning("Failed to fetch nutrition summary", exc_info=True)
            return {"configured": False, "data": {}}

    # ─── Recent PRs ───────────────────────────────────────────

    def _fetch_recent_prs(self) -> list[Any]:
        if not self._pr_engine:
            return []
        try:
            return self._pr_engine.get_latest_prs(limit=5)
        except Exception:
            logger.warning("Failed to fetch recent PRs", exc_info=True)
            return []

    # ─── Section Refresh ──────────────────────────────────────

    def refresh_section(self, data: DashboardData, section: str) -> None:
        """Refresh a single dashboard section in-place."""
        try:
            if section == "recommendations":
                data.recommendations = self._fetch_recommendations()
            elif section == "recovery":
                rec = self._fetch_recovery()
                data.recovery_status = rec.get("status")
                data.recovery_flags = rec.get("flags", [])
                if data.recovery_status:
                    level = getattr(data.recovery_status, "level", "")
                    if hasattr(level, "value"):
                        level = level.value
                    data.recovery_level = level
                    data.recovery_score = getattr(data.recovery_status, "score", 0.0) or 0.0
                    recs_list = getattr(data.recovery_status, "recommendations", [])
                    data.recovery_suggested_action = recs_list[0] if recs_list else ""
            elif section == "weight":
                header = self._fetch_header()
                data.current_weight = header.get("current_weight", data.current_weight)
                data.current_streak = header.get("current_streak", data.current_streak)
            elif section == "workout":
                workout = self._fetch_today_workout()
                data.today_workout_name = workout.get("name", data.today_workout_name)
                data.today_workout_exercise_count = workout.get("exercise_count", data.today_workout_exercise_count)
                data.today_workout_estimated_duration = workout.get("estimated_duration", data.today_workout_estimated_duration)
                data.today_workout_primary_muscles = workout.get("primary_muscles", data.today_workout_primary_muscles)
            elif section == "prs":
                data.recent_prs = self._fetch_recent_prs()
            elif section == "goal_progress":
                gp = self._fetch_goal_progress()
                if gp:
                    data.goal_progress_weight = getattr(gp, "current_weight_kg", 0.0) or 0.0
                    data.goal_progress_target = getattr(gp, "goal_weight_kg", 0.0) or 0.0
                    data.goal_progress_remaining = max(0.0, data.goal_progress_target - data.goal_progress_weight)
                    data.goal_progress_weeks = int(getattr(gp, "estimated_completion_weeks", 0) or 0)
                    data.goal_progress_rate = getattr(gp, "weekly_gain_rate", 0.0) or 0.0
                    data.goal_progress_quality = getattr(gp, "lean_bulk_quality", "") or ""
                    if data.goal_progress_target > 0:
                        data.goal_progress_percent = min(data.goal_progress_weight / data.goal_progress_target * 100, 100)
                    data.goal_progress_estimated_date = getattr(gp, "estimated_completion_date", "") or ""
            elif section == "volume":
                data.weekly_volume_data = self._fetch_weekly_volume()
            elif section == "priority_muscles":
                data.priority_muscles = self._fetch_priority_muscles()
            elif section == "nutrition":
                nutrition_summary = self._fetch_nutrition_summary()
                data.nutrition_configured = nutrition_summary.get("configured", False)
                data.nutrition_data = nutrition_summary.get("data", {})
        except Exception:
            logger.warning("Dashboard refresh_section(%s) failed", section, exc_info=True)
