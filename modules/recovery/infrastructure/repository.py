"""RecoveryRepository — CRUD operations for all recovery data in the SQLite database."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta

from sqlalchemy import create_engine, desc, func, select
from sqlalchemy.orm import Session

from modules.recovery.domain import (
    DeloadPlan,
    DeloadStatus,
    ReadinessAssessment,
    ReadinessLevel,
    RecoveryProfile,
    RecoveryRecommendation,
    RecoveryScore,
    SleepLog,
    SleepQuality,
    SorenessLevel,
    StressLevel,
    StressLog,
)
from modules.recovery.infrastructure.models import (
    DeloadPlanModel,
    ReadinessAssessmentModel,
    RecoveryProfileModel,
    RecoveryRecommendationModel,
    RecoveryScoreModel,
    SleepLogModel,
    StressLogModel,
)
from modules.workout.infrastructure.models import init_db as ensure_tables


class RecoveryRepository:
    """Persistent repository for recovery data backed by SQLite."""

    def __init__(self, db_path: str = "data/gymos.db"):
        self._db_path = db_path
        self._engine = create_engine(f"sqlite:///{db_path}")
        ensure_tables(db_path)

    def _get_session(self) -> Session:
        return Session(self._engine)

    # ─── Profile ─────────────────────────────────────────────

    def get_profile(self) -> RecoveryProfile | None:
        with self._get_session() as session:
            model = session.execute(
                select(RecoveryProfileModel)
            ).scalars().first()
            if model is None:
                return None
            return self._profile_to_domain(model)

    def save_profile(self, profile: RecoveryProfile) -> RecoveryProfile:
        profile_id = profile.id or uuid.uuid4().hex[:36]
        with self._get_session() as session:
            existing = session.get(RecoveryProfileModel, profile_id)
            if existing:
                existing.hrv_baseline = profile.hrv_baseline
                existing.resting_hr_baseline = profile.resting_hr_baseline
                existing.sleep_need_hours = profile.sleep_need_hours
                existing.sleep_sensitivity = profile.sleep_sensitivity
                existing.stress_sensitivity = profile.stress_sensitivity
                existing.fatigue_sensitivity = profile.fatigue_sensitivity
                existing.deload_frequency_weeks = profile.deload_frequency_weeks
                existing.updated_at = datetime.now()
            else:
                now = datetime.now().isoformat()
                model = RecoveryProfileModel(
                    id=profile_id,
                    hrv_baseline=profile.hrv_baseline,
                    resting_hr_baseline=profile.resting_hr_baseline,
                    sleep_need_hours=profile.sleep_need_hours,
                    sleep_sensitivity=profile.sleep_sensitivity,
                    stress_sensitivity=profile.stress_sensitivity,
                    fatigue_sensitivity=profile.fatigue_sensitivity,
                    deload_frequency_weeks=profile.deload_frequency_weeks,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )
                session.add(model)
            session.commit()
            profile.id = profile_id
            return profile

    # ─── Scores ──────────────────────────────────────────────

    def save_score(self, score: RecoveryScore) -> RecoveryScore:
        score_id = score.id or uuid.uuid4().hex[:36]
        with self._get_session() as session:
            existing = session.get(RecoveryScoreModel, score_id)
            if existing:
                existing.overall_score = score.overall_score
                existing.readiness_score = score.readiness_score
                existing.readiness_level = score.readiness_level.value
                existing.fatigue_score = score.fatigue_score
                existing.sleep_score = score.sleep_score
                existing.sleep_hours = score.sleep_hours
                existing.sleep_quality = score.sleep_quality.name if score.sleep_quality else None
                existing.stress_score = score.stress_score
                existing.stress_level = score.stress_level.name if score.stress_level else None
                existing.soreness_level = score.soreness_level.name if score.soreness_level else None
                existing.muscle_recovery_score = score.muscle_recovery_score
                existing.training_fatigue_score = score.training_fatigue_score
                existing.nutrition_adherence_score = score.nutrition_adherence_score
                existing.bodyweight_trend_score = score.bodyweight_trend_score
                existing.consistency_score = score.consistency_score
                existing.hrv_value = score.hrv_value
                existing.resting_hr = score.resting_hr
                existing.subjective_fatigue = score.subjective_fatigue
                existing.note = score.note
            else:
                model = RecoveryScoreModel(
                    id=score_id,
                    date=score.date,
                    overall_score=score.overall_score,
                    readiness_score=score.readiness_score,
                    readiness_level=score.readiness_level.value if score.readiness_level else "good",
                    fatigue_score=score.fatigue_score,
                    sleep_score=score.sleep_score,
                    sleep_hours=score.sleep_hours,
                    sleep_quality=score.sleep_quality.name if score.sleep_quality else None,
                    stress_score=score.stress_score,
                    stress_level=score.stress_level.name if score.stress_level else None,
                    soreness_level=score.soreness_level.name if score.soreness_level else None,
                    muscle_recovery_score=score.muscle_recovery_score,
                    training_fatigue_score=score.training_fatigue_score,
                    nutrition_adherence_score=score.nutrition_adherence_score,
                    bodyweight_trend_score=score.bodyweight_trend_score,
                    consistency_score=score.consistency_score,
                    hrv_value=score.hrv_value,
                    resting_hr=score.resting_hr,
                    subjective_fatigue=score.subjective_fatigue,
                    note=score.note,
                    created_at=datetime.now(),
                )
                session.add(model)
            session.commit()
            score.id = score_id
            return score

    def get_score(self, score_id: str) -> RecoveryScore | None:
        with self._get_session() as session:
            model = session.get(RecoveryScoreModel, score_id)
            if model is None:
                return None
            return self._score_model_to_domain(model)

    def get_score_by_date(self, date: str) -> RecoveryScore | None:
        with self._get_session() as session:
            model = session.execute(
                select(RecoveryScoreModel).where(RecoveryScoreModel.date == date)
            ).scalars().first()
            if model is None:
                return None
            return self._score_model_to_domain(model)

    def list_scores(self, days: int = 30, offset: int = 0) -> list[RecoveryScore]:
        with self._get_session() as session:
            cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            models = session.execute(
                select(RecoveryScoreModel)
                .where(RecoveryScoreModel.date >= cutoff)
                .order_by(desc(RecoveryScoreModel.date))
                .offset(offset)
            ).scalars().all()
            return [self._score_model_to_domain(m) for m in models]

    def delete_score(self, score_id: str) -> bool:
        with self._get_session() as session:
            model = session.get(RecoveryScoreModel, score_id)
            if model is None:
                return False
            session.delete(model)
            session.commit()
            return True

    # ─── Sleep Logs ──────────────────────────────────────────

    def save_sleep_log(self, log: SleepLog) -> SleepLog:
        log_id = log.id or uuid.uuid4().hex[:36]
        with self._get_session() as session:
            existing = session.get(SleepLogModel, log_id)
            if existing:
                existing.date = log.date
                existing.hours = log.hours
                existing.quality = log.quality.name if log.quality else None
                existing.bedtime = log.bedtime
                existing.wake_time = log.wake_time
                existing.interruptions = log.interruptions
                existing.note = log.note
            else:
                model = SleepLogModel(
                    id=log_id,
                    date=log.date,
                    hours=log.hours,
                    quality=log.quality.name if log.quality else None,
                    bedtime=log.bedtime,
                    wake_time=log.wake_time,
                    interruptions=log.interruptions,
                    note=log.note,
                    created_at=datetime.now(),
                )
                session.add(model)
            session.commit()
            log.id = log_id
            return log

    def get_sleep_log(self, log_id: str) -> SleepLog | None:
        with self._get_session() as session:
            model = session.get(SleepLogModel, log_id)
            if model is None:
                return None
            return self._sleep_model_to_domain(model)

    def get_sleep_by_date(self, date: str) -> SleepLog | None:
        with self._get_session() as session:
            model = session.execute(
                select(SleepLogModel).where(SleepLogModel.date == date)
            ).scalars().first()
            if model is None:
                return None
            return self._sleep_model_to_domain(model)

    def list_sleep_logs(self, days: int = 30) -> list[SleepLog]:
        with self._get_session() as session:
            cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            models = session.execute(
                select(SleepLogModel)
                .where(SleepLogModel.date >= cutoff)
                .order_by(desc(SleepLogModel.date))
            ).scalars().all()
            return [self._sleep_model_to_domain(m) for m in models]

    # ─── Stress Logs ─────────────────────────────────────────

    def save_stress_log(self, log: StressLog) -> StressLog:
        log_id = log.id or uuid.uuid4().hex[:36]
        with self._get_session() as session:
            existing = session.get(StressLogModel, log_id)
            if existing:
                existing.date = log.date
                existing.level = log.level.name
                existing.source = log.source
                existing.note = log.note
            else:
                model = StressLogModel(
                    id=log_id,
                    date=log.date,
                    level=log.level.name,
                    source=log.source,
                    note=log.note,
                    created_at=datetime.now(),
                )
                session.add(model)
            session.commit()
            log.id = log_id
            return log

    def get_stress_log(self, log_id: str) -> StressLog | None:
        with self._get_session() as session:
            model = session.get(StressLogModel, log_id)
            if model is None:
                return None
            return self._stress_model_to_domain(model)

    def get_stress_by_date(self, date: str) -> StressLog | None:
        with self._get_session() as session:
            model = session.execute(
                select(StressLogModel).where(StressLogModel.date == date)
            ).scalars().first()
            if model is None:
                return None
            return self._stress_model_to_domain(model)

    def list_stress_logs(self, days: int = 30) -> list[StressLog]:
        with self._get_session() as session:
            cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            models = session.execute(
                select(StressLogModel)
                .where(StressLogModel.date >= cutoff)
                .order_by(desc(StressLogModel.date))
            ).scalars().all()
            return [self._stress_model_to_domain(m) for m in models]

    # ─── Readiness Assessments ───────────────────────────────

    def save_readiness(self, assessment: ReadinessAssessment) -> ReadinessAssessment:
        aid = assessment.id or uuid.uuid4().hex[:36]
        with self._get_session() as session:
            existing = session.get(ReadinessAssessmentModel, aid)
            if existing:
                existing.readiness_score = assessment.readiness_score
                existing.readiness_level = assessment.readiness_level.value
                existing.recovery_score = assessment.recovery_score
                existing.fatigue_score = assessment.fatigue_score
                existing.suggested_intensity_modifier = assessment.suggested_intensity_modifier
                existing.suggested_volume_modifier = assessment.suggested_volume_modifier
                existing.recommended_action = assessment.recommended_action
                existing.flags = json.dumps(assessment.flags) if assessment.flags else None
            else:
                model = ReadinessAssessmentModel(
                    id=aid,
                    date=assessment.date,
                    readiness_score=assessment.readiness_score,
                    readiness_level=assessment.readiness_level.value,
                    recovery_score=assessment.recovery_score,
                    fatigue_score=assessment.fatigue_score,
                    suggested_intensity_modifier=assessment.suggested_intensity_modifier,
                    suggested_volume_modifier=assessment.suggested_volume_modifier,
                    recommended_action=assessment.recommended_action,
                    flags=json.dumps(assessment.flags) if assessment.flags else None,
                    created_at=datetime.now(),
                )
                session.add(model)
            session.commit()
            assessment.id = aid
            return assessment

    def get_readiness_by_date(self, date: str) -> ReadinessAssessment | None:
        with self._get_session() as session:
            model = session.execute(
                select(ReadinessAssessmentModel).where(ReadinessAssessmentModel.date == date)
            ).scalars().first()
            if model is None:
                return None
            return self._readiness_model_to_domain(model)

    def list_readiness(self, days: int = 30) -> list[ReadinessAssessment]:
        with self._get_session() as session:
            cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            models = session.execute(
                select(ReadinessAssessmentModel)
                .where(ReadinessAssessmentModel.date >= cutoff)
                .order_by(desc(ReadinessAssessmentModel.date))
            ).scalars().all()
            return [self._readiness_model_to_domain(m) for m in models]

    # ─── Deload Plans ────────────────────────────────────────

    def save_deload_plan(self, plan: DeloadPlan) -> DeloadPlan:
        pid = plan.id or uuid.uuid4().hex[:36]
        with self._get_session() as session:
            existing = session.get(DeloadPlanModel, pid)
            if existing:
                existing.start_date = plan.start_date
                existing.end_date = plan.end_date
                existing.reason = plan.reason
                existing.volume_reduction_percent = plan.volume_reduction_percent
                existing.intensity_reduction_percent = plan.intensity_reduction_percent
                existing.instructions = plan.instructions
                existing.status = plan.status.value
                existing.weeks_since_last_deload = plan.weeks_since_last_deload
            else:
                model = DeloadPlanModel(
                    id=pid,
                    start_date=plan.start_date,
                    end_date=plan.end_date,
                    reason=plan.reason,
                    volume_reduction_percent=plan.volume_reduction_percent,
                    intensity_reduction_percent=plan.intensity_reduction_percent,
                    instructions=plan.instructions,
                    status=plan.status.value,
                    weeks_since_last_deload=plan.weeks_since_last_deload,
                    created_at=datetime.now(),
                )
                session.add(model)
            session.commit()
            plan.id = pid
            return plan

    def get_active_deload_plan(self) -> DeloadPlan | None:
        with self._get_session() as session:
            today = datetime.now().strftime("%Y-%m-%d")
            model = session.execute(
                select(DeloadPlanModel)
                .where(DeloadPlanModel.start_date <= today)
                .where(DeloadPlanModel.end_date >= today)
                .where(DeloadPlanModel.status.in_(["planned", "in_progress"]))
            ).scalars().first()
            if model is None:
                return None
            return self._deload_model_to_domain(model)

    def list_deload_plans(self, limit: int = 10) -> list[DeloadPlan]:
        with self._get_session() as session:
            models = session.execute(
                select(DeloadPlanModel)
                .order_by(desc(DeloadPlanModel.created_at))
                .limit(limit)
            ).scalars().all()
            return [self._deload_model_to_domain(m) for m in models]

    def get_most_recent_deload(self) -> DeloadPlan | None:
        with self._get_session() as session:
            model = session.execute(
                select(DeloadPlanModel)
                .where(DeloadPlanModel.status.in_(["completed", "in_progress"]))
                .order_by(desc(DeloadPlanModel.end_date))
                .limit(1)
            ).scalars().first()
            if model is None:
                return None
            return self._deload_model_to_domain(model)

    def count_completed_deloads(self) -> int:
        with self._get_session() as session:
            return session.execute(
                select(func.count(DeloadPlanModel.id))
                .where(DeloadPlanModel.status == "completed")
            ).scalar() or 0

    # ─── Recommendations ─────────────────────────────────────

    def save_recommendation(self, rec: RecoveryRecommendation) -> RecoveryRecommendation:
        rid = rec.id or uuid.uuid4().hex[:36]
        with self._get_session() as session:
            model = RecoveryRecommendationModel(
                id=rid,
                date=rec.date,
                category=rec.category,
                priority=rec.priority,
                message=rec.message,
                reason=rec.reason,
                action=rec.action,
                dismissed=rec.dismissed,
                created_at=datetime.now(),
            )
            session.add(model)
            session.commit()
            rec.id = rid
            return rec

    def list_recommendations(self, days: int = 7, include_dismissed: bool = False) -> list[RecoveryRecommendation]:
        with self._get_session() as session:
            cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            stmt = (
                select(RecoveryRecommendationModel)
                .where(RecoveryRecommendationModel.date >= cutoff)
                .order_by(desc(RecoveryRecommendationModel.priority))
            )
            if not include_dismissed:
                stmt = stmt.where(RecoveryRecommendationModel.dismissed == False)
            models = session.execute(stmt).scalars().all()
            return [self._rec_model_to_domain(m) for m in models]

    def dismiss_recommendation(self, rec_id: str) -> bool:
        with self._get_session() as session:
            model = session.get(RecoveryRecommendationModel, rec_id)
            if model is None:
                return False
            model.dismissed = True
            session.commit()
            return True

    # ─── Stats ───────────────────────────────────────────────

    def get_average_score(self, days: int = 7) -> float:
        with self._get_session() as session:
            cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            result = session.execute(
                select(func.avg(RecoveryScoreModel.overall_score))
                .where(RecoveryScoreModel.date >= cutoff)
            ).scalar()
            return round(result, 1) if result else 0.0

    def get_weekly_averages(self, weeks: int = 4) -> list[dict]:
        scores = self.list_scores(days=weeks * 7)
        weekly: dict[str, list[float]] = {}
        for s in scores:
            try:
                d = datetime.strptime(s.date, "%Y-%m-%d")
                week_key = d.strftime("%Y-W%V")
                weekly.setdefault(week_key, []).append(s.overall_score)
            except (ValueError, TypeError):
                continue
        return sorted(
            [{"week": k, "average": round(sum(v) / len(v), 1)} for k, v in weekly.items()],
            key=lambda x: x["week"],
        )

    def has_data(self) -> bool:
        with self._get_session() as session:
            count = session.execute(
                select(func.count(RecoveryScoreModel.id))
            ).scalar() or 0
            return count > 0

    def count_scores(self) -> int:
        with self._get_session() as session:
            return session.execute(
                select(func.count(RecoveryScoreModel.id))
            ).scalar() or 0

    def count_sleep_logs(self) -> int:
        with self._get_session() as session:
            return session.execute(
                select(func.count(SleepLogModel.id))
            ).scalar() or 0

    def count_stress_logs(self) -> int:
        with self._get_session() as session:
            return session.execute(
                select(func.count(StressLogModel.id))
            ).scalar() or 0

    # ─── Model → Domain mappers ──────────────────────────────

    @staticmethod
    def _score_model_to_domain(m: RecoveryScoreModel) -> RecoveryScore:
        sleep_q = None
        if m.sleep_quality:
            try:
                sleep_q = SleepQuality[m.sleep_quality]
            except (KeyError, ValueError):
                pass
        stress_l = None
        if m.stress_level:
            try:
                stress_l = StressLevel[m.stress_level]
            except (KeyError, ValueError):
                pass
        soreness = None
        if m.soreness_level:
            try:
                soreness = SorenessLevel[m.soreness_level]
            except (KeyError, ValueError):
                pass
        return RecoveryScore(
            id=m.id,
            date=m.date,
            overall_score=m.overall_score,
            readiness_score=m.readiness_score,
            readiness_level=ReadinessLevel(m.readiness_level) if m.readiness_level else ReadinessLevel.GOOD,
            fatigue_score=m.fatigue_score,
            sleep_score=m.sleep_score,
            sleep_hours=m.sleep_hours,
            sleep_quality=sleep_q,
            stress_score=m.stress_score,
            stress_level=stress_l,
            soreness_level=soreness,
            muscle_recovery_score=m.muscle_recovery_score,
            training_fatigue_score=m.training_fatigue_score,
            nutrition_adherence_score=m.nutrition_adherence_score,
            bodyweight_trend_score=m.bodyweight_trend_score,
            consistency_score=m.consistency_score,
            hrv_value=m.hrv_value,
            resting_hr=m.resting_hr,
            subjective_fatigue=m.subjective_fatigue,
            note=m.note or "",
            created_at=m.created_at.isoformat() if m.created_at else "",
        )

    @staticmethod
    def _sleep_model_to_domain(m: SleepLogModel) -> SleepLog:
        quality = None
        if m.quality:
            try:
                quality = SleepQuality[m.quality]
            except (KeyError, ValueError):
                pass
        return SleepLog(
            id=m.id,
            date=m.date,
            hours=m.hours,
            quality=quality,
            bedtime=m.bedtime,
            wake_time=m.wake_time,
            interruptions=m.interruptions,
            note=m.note or "",
            created_at=m.created_at.isoformat() if m.created_at else "",
        )

    @staticmethod
    def _stress_model_to_domain(m: StressLogModel) -> StressLog:
        level = StressLevel.MODERATE
        try:
            level = StressLevel[m.level]
        except (KeyError, ValueError):
            pass
        return StressLog(
            id=m.id,
            date=m.date,
            level=level,
            source=m.source or "",
            note=m.note or "",
            created_at=m.created_at.isoformat() if m.created_at else "",
        )

    @staticmethod
    def _readiness_model_to_domain(m: ReadinessAssessmentModel) -> ReadinessAssessment:
        flags = []
        if m.flags:
            try:
                flags = json.loads(m.flags)
            except (json.JSONDecodeError, TypeError):
                pass
        return ReadinessAssessment(
            id=m.id,
            date=m.date,
            readiness_score=m.readiness_score,
            readiness_level=ReadinessLevel(m.readiness_level),
            recovery_score=m.recovery_score,
            fatigue_score=m.fatigue_score,
            suggested_intensity_modifier=m.suggested_intensity_modifier,
            suggested_volume_modifier=m.suggested_volume_modifier,
            recommended_action=m.recommended_action or "",
            flags=flags,
            created_at=m.created_at.isoformat() if m.created_at else "",
        )

    @staticmethod
    def _deload_model_to_domain(m: DeloadPlanModel) -> DeloadPlan:
        return DeloadPlan(
            id=m.id,
            start_date=m.start_date,
            end_date=m.end_date,
            reason=m.reason or "",
            volume_reduction_percent=m.volume_reduction_percent,
            intensity_reduction_percent=m.intensity_reduction_percent,
            instructions=m.instructions or "",
            status=DeloadStatus(m.status),
            weeks_since_last_deload=m.weeks_since_last_deload,
            created_at=m.created_at.isoformat() if m.created_at else "",
        )

    @staticmethod
    def _profile_to_domain(m: RecoveryProfileModel) -> RecoveryProfile:
        return RecoveryProfile(
            id=m.id,
            hrv_baseline=m.hrv_baseline,
            resting_hr_baseline=m.resting_hr_baseline,
            sleep_need_hours=m.sleep_need_hours,
            sleep_sensitivity=m.sleep_sensitivity,
            stress_sensitivity=m.stress_sensitivity,
            fatigue_sensitivity=m.fatigue_sensitivity,
            deload_frequency_weeks=m.deload_frequency_weeks,
            created_at=m.created_at.isoformat() if m.created_at else "",
            updated_at=m.updated_at.isoformat() if m.updated_at else "",
        )

    @staticmethod
    def _rec_model_to_domain(m: RecoveryRecommendationModel) -> RecoveryRecommendation:
        return RecoveryRecommendation(
            id=m.id,
            date=m.date,
            category=m.category,
            priority=m.priority,
            message=m.message,
            reason=m.reason or "",
            action=m.action or "",
            dismissed=m.dismissed,
            created_at=m.created_at.isoformat() if m.created_at else "",
        )

    def dispose(self) -> None:
        self._engine.dispose()
