"""Recovery Service — application-layer orchestration for all recovery features.

Coordinates repository, engines, providers, and event publishing.
This is the primary API consumed by the Dashboard and GymBrain.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from modules.recovery.domain import (
    DeloadPlan,
    DeloadStatus,
    FatigueFactors,
    ReadinessAssessment,
    RecoveryProfile,
    RecoveryRecommendation,
    RecoveryScore,
    RecoverySession,
    RecoverySnapshot,
    RecoveryTrend,
    SleepLog,
    SleepQuality,
    SorenessLevel,
    StressLevel,
    StressLog,
)
from modules.recovery.engines import (
    DeloadEngine,
    FatigueAggregator,
    ReadinessEngine,
    RecoveryScoreEngine,
    RecoveryTrendAnalyzer,
    SleepAnalyzer,
    StressAnalyzer,
)
from modules.recovery.infrastructure.repository import RecoveryRepository
from modules.recovery.providers import IRecoveryProvider, ProductionRecoveryProvider

logger = logging.getLogger("gymos.recovery.service")


class RecoveryService:
    """Application service for all recovery operations.

    This is the primary entry point for:
      - Dashboard (via get_snapshot(), get_scores())
      - GymBrain rules (via provider)
      - Recovery data logging
      - Score computation
      - Readiness assessment
      - Deload management
    """

    def __init__(
        self,
        repository: RecoveryRepository,
        db: Any = None,
        event_bus: Any = None,
    ) -> None:
        self._repo = repository
        self._db = db
        self._event_bus = event_bus

        # Create provider
        self._provider = ProductionRecoveryProvider(repository, db)

        # Create engines
        self._score_engine = RecoveryScoreEngine()
        self._readiness_engine = ReadinessEngine()
        self._deload_engine = DeloadEngine()
        self._sleep_analyzer = SleepAnalyzer()
        self._stress_analyzer = StressAnalyzer()
        self._fatigue_aggregator = FatigueAggregator()
        self._trend_analyzer = RecoveryTrendAnalyzer()

    @property
    def provider(self) -> IRecoveryProvider:
        return self._provider

    @property
    def score_engine(self) -> RecoveryScoreEngine:
        return self._score_engine

    @property
    def readiness_engine(self) -> ReadinessEngine:
        return self._readiness_engine

    # ─── Data Access ─────────────────────────────────────────

    def get_today_score(self) -> RecoveryScore | None:
        return self._repo.get_score_by_date(datetime.now().strftime("%Y-%m-%d"))

    def get_score_by_date(self, date: str) -> RecoveryScore | None:
        return self._repo.get_score_by_date(date)

    def get_recent_scores(self, days: int = 30) -> list[RecoveryScore]:
        return self._repo.list_scores(days=days)

    def get_sleep_by_date(self, date: str) -> SleepLog | None:
        return self._repo.get_sleep_by_date(date)

    def get_recent_sleep(self, days: int = 7) -> list[SleepLog]:
        return self._repo.list_sleep_logs(days=days)

    def get_stress_by_date(self, date: str) -> StressLog | None:
        return self._repo.get_stress_by_date(date)

    def get_recent_stress(self, days: int = 7) -> list[StressLog]:
        return self._repo.list_stress_logs(days=days)

    def get_profile(self) -> RecoveryProfile:
        profile = self._repo.get_profile()
        if profile is None:
            profile = RecoveryProfile()
            self._repo.save_profile(profile)
        return profile

    def save_profile(self, profile: RecoveryProfile) -> RecoveryProfile:
        return self._repo.save_profile(profile)

    # ─── Sleep Logging ───────────────────────────────────────

    def log_sleep(self, date: str, hours: float,
                  quality: SleepQuality | None = None,
                  bedtime: str | None = None,
                  wake_time: str | None = None,
                  interruptions: int = 0,
                  note: str = "") -> SleepLog:
        """Log a sleep entry and auto-update recovery score."""
        log = SleepLog(
            date=date,
            hours=hours,
            quality=quality,
            bedtime=bedtime,
            wake_time=wake_time,
            interruptions=interruptions,
            note=note,
        )
        saved = self._repo.save_sleep_log(log)
        self._recompute_score_for_date(date)
        self._publish_event("recovery.sleep_logged", {
            "date": date, "hours": hours, "quality": quality.value if quality else None,
        })
        return saved

    # ─── Stress Logging ──────────────────────────────────────

    def log_stress(self, date: str, level: StressLevel = StressLevel.MODERATE,
                   source: str = "", note: str = "") -> StressLog:
        """Log a stress entry and auto-update recovery score."""
        log = StressLog(date=date, level=level, source=source, note=note)
        saved = self._repo.save_stress_log(log)
        self._recompute_score_for_date(date)
        self._publish_event("recovery.stress_logged", {
            "date": date, "level": level.value,
        })
        return saved

    # ─── Recovery Session ────────────────────────────────────

    def log_recovery_session(self, session: RecoverySession) -> RecoveryScore:
        """Log a complete recovery session and compute score."""
        # Save individual components
        if session.sleep_hours > 0:
            self._repo.save_sleep_log(SleepLog(
                date=session.date,
                hours=session.sleep_hours,
                quality=session.sleep_quality,
            ))
        if session.stress_level:
            self._repo.save_stress_log(StressLog(
                date=session.date,
                level=session.stress_level,
            ))

        # Compute and save score
        score = self._compute_score(
            date=session.date,
            sleep_hours=session.sleep_hours,
            sleep_quality=session.sleep_quality,
            stress_level=session.stress_level,
            soreness_level=session.soreness_level,
            subjective_fatigue=session.subjective_fatigue,
            hrv_value=session.hrv_value,
            resting_hr=session.resting_hr,
        )
        self._repo.save_score(score)
        self._publish_event("recovery.session_logged", {"date": session.date, "score": score.overall_score})
        return score

    # ─── Score Computation ──────────────────────────────────

    def compute_and_save_score(self, date: str | None = None) -> RecoveryScore:
        """Compute a recovery score for a date (or today) from available data."""
        target_date = date or datetime.now().strftime("%Y-%m-%d")
        return self._recompute_score_for_date(target_date)

    def _recompute_score_for_date(self, date: str) -> RecoveryScore:
        """Recompute recovery score from sleep, stress, and training data."""
        sleep_log = self._repo.get_sleep_by_date(date)
        stress_log = self._repo.get_stress_by_date(date)
        profile = self._repo.get_profile()

        # Training fatigue from DB
        training_fatigue = 30.0
        consistency = 80.0
        if self._db:
            try:
                recent_volume = self._db.get_recent_volume(days=7)
                training_fatigue = min(recent_volume / 50000.0 * 100.0, 100.0)
                # Consistency: streak-based
                streak = self._db.get_streak()
                consistency = min(streak / 14.0 * 100.0, 100.0)
            except Exception:
                logger.warning("Failed to fetch recovery score training data", exc_info=True)

        # Bodyweight trend
        bw_trend = 80.0
        if self._db:
            try:
                bw = self._db.get_latest_body_weight()
                if bw:
                    bw_trend = 80.0  # Will be refined as more data comes in
            except Exception:
                logger.warning("Failed to fetch body weight for recovery score", exc_info=True)

        score = self._score_engine.compute(
            sleep_hours=sleep_log.hours if sleep_log else 7.5,
            sleep_quality=sleep_log.quality if sleep_log else None,
            stress_level=stress_log.level if stress_log else None,
            training_fatigue_score=training_fatigue,
            bodyweight_trend_score=bw_trend,
            consistency_score=consistency,
            profile=profile,
        )
        score.date = date
        saved = self._repo.save_score(score)

        # Publish event
        self._publish_event("recovery.score_updated", {
            "date": date, "score": score.overall_score,
            "readiness": score.readiness_level.value,
        })

        return saved

    def _compute_score(
        self, date: str = "",
        sleep_hours: float = 7.5,
        sleep_quality: SleepQuality | None = None,
        stress_level: StressLevel | None = None,
        soreness_level: SorenessLevel | None = None,
        subjective_fatigue: int | None = None,
        hrv_value: float | None = None,
        resting_hr: float | None = None,
    ) -> RecoveryScore:
        """Internal score computation helper."""
        profile = self._repo.get_profile()
        training_fatigue = 30.0
        consistency = 80.0

        if self._db:
            try:
                recent_volume = self._db.get_recent_volume(days=7)
                training_fatigue = min(recent_volume / 50000.0 * 100.0, 100.0)
                streak = self._db.get_streak()
                consistency = min(streak / 14.0 * 100.0, 100.0)
            except Exception:
                logger.warning("Failed to fetch _compute_score training data", exc_info=True)

        score = self._score_engine.compute(
            sleep_hours=sleep_hours,
            sleep_quality=sleep_quality,
            stress_level=stress_level or StressLevel.MODERATE,
            soreness_level=soreness_level,
            subjective_fatigue=subjective_fatigue,
            hrv_value=hrv_value,
            resting_hr=resting_hr,
            training_fatigue_score=training_fatigue,
            consistency_score=consistency,
            profile=profile,
        )
        score.date = date
        return score

    # ─── Readiness Assessment ────────────────────────────────

    def assess_readiness(self, date: str | None = None) -> ReadinessAssessment:
        """Assess training readiness for a date (or today)."""
        target_date = date or datetime.now().strftime("%Y-%m-%d")
        score = self._repo.get_score_by_date(target_date)

        if score is None:
            # Need to compute first
            score = self._recompute_score_for_date(target_date)

        # Get recent trend
        recent_scores = self._repo.list_scores(days=14)
        trend = self._trend_analyzer.analyze(recent_scores)
        profile = self._repo.get_profile()

        assessment = self._readiness_engine.assess(score, trend, profile)
        assessment.date = target_date
        saved = self._repo.save_readiness(assessment)

        self._publish_event("recovery.readiness_updated", {
            "date": target_date,
            "score": assessment.readiness_score,
            "level": assessment.readiness_level.value,
        })

        return saved

    # ─── Fatigue Analysis ────────────────────────────────────

    def analyze_fatigue(self, days: int = 7) -> FatigueFactors:
        """Analyze fatigue factors from recent training and recovery data."""
        recent_volume_7d = 0.0
        recent_volume_14d = 0.0
        session_count_7d = 0
        avg_rpe = 7.0
        days_since_deload = 999
        recent_sleep_avg = 7.0
        recent_stress_avg = 30.0

        if self._db:
            try:
                recent_volume_7d = self._db.get_recent_volume(days=7)
                recent_volume_14d = self._db.get_recent_volume(days=14)
                sessions = self._db.list_sessions(limit=10)
                session_count_7d = sum(1 for s in sessions if s.completed_at)
            except Exception:
                logger.warning("Failed to fetch get_snapshot training data", exc_info=True)

        recent_deload = self._repo.get_most_recent_deload()
        if recent_deload and recent_deload.end_date:
            try:
                end = datetime.strptime(recent_deload.end_date, "%Y-%m-%d")
                days_since_deload = (datetime.now() - end).days
            except (ValueError, TypeError):
                pass

        sleep_logs = self._repo.list_sleep_logs(days=7)
        if sleep_logs:
            recent_sleep_avg = sum(s.hours for s in sleep_logs) / len(sleep_logs)

        stress_logs = self._repo.list_stress_logs(days=7)
        if stress_logs:
            stress_scores = {"very_low": 5, "low": 15, "moderate": 35, "high": 60, "very_high": 85}
            recent_stress_avg = sum(stress_scores.get(s.level.value, 35) for s in stress_logs) / len(stress_logs)

        return self._fatigue_aggregator.compute_fatigue_factors(
            recent_volume_7d=recent_volume_7d,
            recent_volume_14d=recent_volume_14d,
            session_count_7d=session_count_7d,
            average_rpe=avg_rpe,
            days_since_deload=days_since_deload,
            recent_sleep_avg=recent_sleep_avg,
            recent_stress_avg=recent_stress_avg,
        )

    # ─── Deload Management ───────────────────────────────────

    def check_deload(self) -> tuple[bool, str, DeloadPlan | None]:
        """Check if a deload is needed. Returns (should_deload, reason, plan)."""
        profile = self._repo.get_profile()
        weeks_since_deload = self._get_weeks_since_last_deload()

        recent_scores_raw = self._repo.list_scores(days=14)
        recent_scores = [s.overall_score for s in recent_scores_raw]

        fatigue = self.analyze_fatigue()

        should_deload, reason = self._deload_engine.should_deload(
            weeks_since_last_deload=weeks_since_deload,
            recent_scores=recent_scores,
            fatigue_factors=fatigue,
            profile=profile,
        )

        plan = None
        if should_deload:
            plan = self._deload_engine.create_deload_plan(
                reason=reason,
                weeks_since_last_deload=weeks_since_deload,
                profile=profile,
            )
            self._repo.save_deload_plan(plan)
            self._publish_event("recovery.deload_recommended", {
                "reason": reason,
                "start_date": plan.start_date,
                "end_date": plan.end_date,
            })

        return should_deload, reason, plan

    def complete_deload(self, plan_id: str) -> DeloadPlan | None:
        """Mark a deload plan as completed."""
        plan = DeloadPlan(id=plan_id, status=DeloadStatus.COMPLETED)
        return self._repo.save_deload_plan(plan)

    def get_active_deload(self) -> DeloadPlan | None:
        return self._repo.get_active_deload_plan()

    def get_deload_history(self, limit: int = 10) -> list[DeloadPlan]:
        return self._repo.list_deload_plans(limit=limit)

    def _get_weeks_since_last_deload(self) -> int:
        recent = self._repo.get_most_recent_deload()
        if recent and recent.end_date:
            try:
                end = datetime.strptime(recent.end_date, "%Y-%m-%d")
                return max((datetime.now() - end).days // 7, 0)
            except (ValueError, TypeError):
                pass
        # Check deload count
        count = self._repo.count_completed_deloads()
        if count == 0:
            return 999  # Never deloaded
        return 12  # Estimate based on history

    # ─── Trends ──────────────────────────────────────────────

    def get_trend(self, days: int = 14) -> RecoveryTrend:
        scores = self._repo.list_scores(days=days)
        return self._trend_analyzer.analyze(scores)

    def get_weekly_averages(self, weeks: int = 4) -> list[dict]:
        return self._repo.get_weekly_averages(weeks=weeks)

    # ─── Snapshot ────────────────────────────────────────────

    def get_snapshot(self) -> RecoverySnapshot:
        """Get complete recovery snapshot for the Dashboard."""
        return self._provider.get_snapshot()

    # ─── Recommendations ────────────────────────────────────

    def generate_recommendations(self) -> list[RecoveryRecommendation]:
        """Generate recovery recommendations based on current state."""
        recs: list[RecoveryRecommendation] = []
        today = datetime.now().strftime("%Y-%m-%d")
        score = self.get_today_score()
        stress_log = self._repo.get_stress_by_date(today)

        if score and score.overall_score < 40:
            recs.append(RecoveryRecommendation(
                date=today, category="training", priority=5,
                message="Recovery score critically low — take a rest day today",
                reason=f"Score: {score.overall_score:.0f}/100",
                action="Take a complete rest day with active recovery (walking, stretching)",
            ))

        if score and score.sleep_score < 40:
            recs.append(RecoveryRecommendation(
                date=today, category="sleep", priority=4,
                message="Sleep quality needs improvement — aim for 8+ hours tonight",
                reason=f"Sleep score: {score.sleep_score:.0f}/100",
                action="Go to bed 1 hour earlier, no screens 30min before bed",
            ))

        if stress_log and stress_log.level in (StressLevel.HIGH, StressLevel.VERY_HIGH):
            recs.append(RecoveryRecommendation(
                date=today, category="stress", priority=3,
                message="Elevated stress detected — incorporate stress management",
                reason=f"Stress level: {stress_log.level.value}",
                action="Deep breathing (5 min), light walk, or meditation",
            ))

        should_deload, reason, plan = self.check_deload()
        if should_deload:
            recs.append(RecoveryRecommendation(
                date=today, category="deload", priority=5,
                message=f"Deload recommended: {reason}",
                reason=reason,
                action="Reduce volume by 50%, keep intensity, maintain frequency",
            ))

        # Save all recommendations
        for rec in recs:
            self._repo.save_recommendation(rec)

        return recs

    def get_recommendations(self, days: int = 7, include_dismissed: bool = False) -> list[RecoveryRecommendation]:
        return self._repo.list_recommendations(days=days, include_dismissed=include_dismissed)

    def dismiss_recommendation(self, rec_id: str) -> bool:
        return self._repo.dismiss_recommendation(rec_id)

    # ─── Events ──────────────────────────────────────────────

    def _publish_event(self, event_name: str, data: dict) -> None:
        if not self._event_bus:
            return
        try:
            # Use the event bus directly
            import asyncio
            try:
                loop = asyncio.get_running_loop()
                if loop.is_running():
                    asyncio.ensure_future(self._event_bus.core.emit(event_name, data, source="recovery"))
                    return
            except RuntimeError:
                pass
            asyncio.run(self._event_bus.core.emit(event_name, data, source="recovery"))
        except Exception:
            logger.warning("Failed to publish %s event", event_name, exc_info=True)

    # ─── Has Data ────────────────────────────────────────────

    def has_data(self) -> bool:
        return self._repo.has_data()

    # ─── Cleanup ─────────────────────────────────────────────

    def dispose(self) -> None:
        self._repo.dispose()
