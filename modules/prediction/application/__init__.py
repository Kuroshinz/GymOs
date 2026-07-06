from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Optional

from modules.prediction.domain import (
    ExplainabilityDetail,
    Prediction,
    PredictionResult,
    PredictionType,
    PredictionWindow,
    RiskMetrics,
)
from modules.prediction.engines import (
    BodyweightPredictionEngine,
    ConsistencyPredictionEngine,
    CounterfactualEngine,
    DeloadPredictionEngine,
    ExplainabilityEngine,
    FatiguePredictionEngine,
    GoalEtaPredictionEngine,
    PlateauPredictionEngine,
    PredictionScenarioEngine,
    PRPredictionEngine,
    RecoveryPredictionEngine,
    RiskEngine,
    VolumePredictionEngine,
)
from modules.prediction.infrastructure.repository import PredictionRepository
from modules.prediction.providers import IPredictionProvider, ProductionPredictionProvider

logger = logging.getLogger(__name__)


class PredictionService:
    def __init__(
        self,
        repository: PredictionRepository,
        db: Any = None,
        event_bus: Any = None,
    ) -> None:
        self._repo = repository
        self._db = db
        self._event_bus = event_bus

        self._provider = ProductionPredictionProvider(self)
        self._plateau_engine = PlateauPredictionEngine()
        self._pr_engine = PRPredictionEngine()
        self._recovery_engine = RecoveryPredictionEngine()
        self._fatigue_engine = FatiguePredictionEngine()
        self._bodyweight_engine = BodyweightPredictionEngine()
        self._goal_eta_engine = GoalEtaPredictionEngine()
        self._volume_engine = VolumePredictionEngine()
        self._consistency_engine = ConsistencyPredictionEngine()
        self._deload_engine = DeloadPredictionEngine()
        self._scenario_engine = PredictionScenarioEngine()
        self._counterfactual_engine = CounterfactualEngine()
        self._explainability_engine = ExplainabilityEngine()
        self._risk_engine = RiskEngine()

    @property
    def provider(self) -> IPredictionProvider:
        return self._provider

    @property
    def repo(self) -> PredictionRepository:
        return self._repo

    def generate_all_predictions(self) -> PredictionResult:
        today = datetime.now().strftime("%Y-%m-%d")
        predictions: list[Prediction] = []

        for window in PredictionWindow:
            pred = self._generate_pr_prediction(window)
            if pred:
                predictions.append(pred)
            pred = self._generate_plateau_prediction(window)
            if pred:
                predictions.append(pred)
            pred = self._generate_recovery_prediction(window)
            if pred:
                predictions.append(pred)
            pred = self._generate_fatigue_prediction(window)
            if pred:
                predictions.append(pred)
            pred = self._generate_bodyweight_prediction(window)
            if pred:
                predictions.append(pred)
            pred = self._generate_volume_prediction(window)
            if pred:
                predictions.append(pred)
            pred = self._generate_consistency_prediction(window)
            if pred:
                predictions.append(pred)
            pred = self._generate_deload_prediction(window)
            if pred:
                predictions.append(pred)

        pred = self._generate_goal_eta()
        if pred:
            predictions.append(pred)

        for p in predictions:
            self._repo.save_prediction(p)
            self._publish_event("prediction.updated", {
                "type": p.prediction_type.value,
                "window": p.window.value,
                "value": p.value,
                "probability": p.probability,
            })

        scenario_results = self._scenario_engine.evaluate_all()
        scenario_rankings = self._scenario_engine.rank_scenarios(scenario_results)
        counterfactual_results = self._counterfactual_engine.evaluate_all()

        explainability: dict[str, ExplainabilityDetail] = {}
        risk_metrics: dict[str, RiskMetrics] = {}
        for p in predictions:
            key = f"{p.prediction_type.value}_{p.window.value}"
            explainability[key] = self._explainability_engine.explain(p)
            risk_metrics[key] = self._risk_engine.analyze_prediction(p)

        return PredictionResult(
            predictions=predictions,
            generated_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            total_predictions=len(predictions),
            scenario_results=scenario_results,
            counterfactual_results=counterfactual_results,
            explainability=explainability,
            risk_metrics=risk_metrics,
            scenario_rankings=scenario_rankings,
        )

    def get_latest_prediction(self, ptype: PredictionType, window: PredictionWindow) -> Prediction | None:
        preds = self._repo.get_predictions_by_type(ptype, limit=1)
        for p in preds:
            if p.window == window:
                return p
        return preds[0] if preds else None

    def get_prediction_result(self) -> PredictionResult:
        preds = self._repo.list_predictions(days=7)
        return PredictionResult(
            predictions=preds,
            generated_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            total_predictions=len(preds),
        )

    def _generate_pr_prediction(self, window: PredictionWindow) -> Prediction | None:
        consistency_streak = 0
        recent_prs = 0
        avg_rir = 2.0
        recovery_score = 70.0
        volume_trend = 0.0
        days_since_last_pr = 0
        is_deload = False

        if self._db:
            try:
                consistency_streak = self._db.get_streak() if hasattr(self._db, "get_streak") else 0
                sessions = self._db.list_sessions(limit=20) if hasattr(self._db, "list_sessions") else []
                recent_prs = sum(1 for s in sessions if hasattr(s, "is_pr") and s.is_pr) if sessions else 0
                bw = self._db.get_latest_body_weight() if hasattr(self._db, "get_latest_body_weight") else None
            except Exception:
                logger.warning("Failed to fetch PR prediction data", exc_info=True)

        if hasattr(self._db, "get_recent_volume"):
            try:
                v7 = self._db.get_recent_volume(days=7)
                v14 = self._db.get_recent_volume(days=14)
                volume_trend = (v7 / 7.0 - v14 / 14.0) * 7.0 if v14 else 0.0
            except Exception:
                logger.warning("Failed to fetch volume trend for PR prediction", exc_info=True)

        return self._pr_engine.predict(
            window=window,
            consistency_streak=consistency_streak,
            recent_prs=recent_prs,
            average_rir=avg_rir,
            recovery_score=recovery_score,
            recent_volume_trend=volume_trend,
            days_since_last_pr=days_since_last_pr,
            is_deload_week=is_deload,
        )

    def _generate_plateau_prediction(self, window: PredictionWindow) -> Prediction | None:
        recent_volume_7d = 0.0
        recent_volume_14d = 0.0
        session_count = 0
        avg_rir = 2.0

        if self._db:
            try:
                recent_volume_7d = self._db.get_recent_volume(days=7) if hasattr(self._db, "get_recent_volume") else 0
                recent_volume_14d = self._db.get_recent_volume(days=14) if hasattr(self._db, "get_recent_volume") else 0
                sessions = self._db.list_sessions(limit=20) if hasattr(self._db, "list_sessions") else []
                session_count = len(sessions)
            except Exception:
                logger.warning("Failed to fetch plateau prediction data", exc_info=True)

        volume_change = ((recent_volume_7d - recent_volume_14d / 2) / (recent_volume_14d / 2 + 1)) * 100
        return self._plateau_engine.predict(
            window=window,
            recent_volume_7d=recent_volume_7d,
            recent_volume_14d=recent_volume_14d,
            volume_change_percent=volume_change,
            reps_in_rir_avg=avg_rir,
            session_count_last_14d=session_count,
        )

    def _generate_recovery_prediction(self, window: PredictionWindow) -> Prediction | None:
        scores: list[float] = []
        sleep_trend = 0.0
        stress_trend = 0.0
        volume_trend = 0.0
        current_score = 70.0
        days_since_deload = 30

        if self._db:
            try:
                if hasattr(self._db, "get_recovery_scores"):
                    scores = self._db.get_recovery_scores(days=14) or []
                current_score = scores[-1] if scores else 70.0
                v7 = self._db.get_recent_volume(days=7) if hasattr(self._db, "get_recent_volume") else 0
                v14 = self._db.get_recent_volume(days=14) if hasattr(self._db, "get_recent_volume") else 0
                volume_trend = (v7 / 7.0 - v14 / 14.0) if v14 else 0.0
            except Exception:
                logger.warning("Failed to fetch recovery prediction data", exc_info=True)

        return self._recovery_engine.predict(
            window=window,
            recovery_scores=scores if scores else None,
            sleep_trend=sleep_trend,
            stress_trend=stress_trend,
            training_volume_trend=volume_trend,
            current_recovery_score=current_score,
            days_since_deload=days_since_deload,
        )

    def _generate_fatigue_prediction(self, window: PredictionWindow) -> Prediction | None:
        recent_volume_7d = 0.0
        recent_volume_14d = 0.0
        session_count = 4
        current_fatigue = 40.0
        days_since_deload = 30
        sleep_avg = 7.0
        stress_avg = 30.0

        if self._db:
            try:
                recent_volume_7d = self._db.get_recent_volume(days=7) if hasattr(self._db, "get_recent_volume") else 0
                recent_volume_14d = self._db.get_recent_volume(days=14) if hasattr(self._db, "get_recent_volume") else 0
                sessions = self._db.list_sessions(limit=20) if hasattr(self._db, "list_sessions") else []
                session_count = sum(1 for s in sessions if hasattr(s, "completed") and s.completed) if sessions else 4
            except Exception:
                logger.warning("Failed to fetch fatigue prediction data", exc_info=True)

        return self._fatigue_engine.predict(
            window=window,
            current_fatigue=current_fatigue,
            recent_volume_7d=recent_volume_7d,
            recent_volume_14d=recent_volume_14d,
            sleep_avg=sleep_avg,
            stress_avg=stress_avg,
            days_since_deload=days_since_deload,
            session_frequency=float(session_count),
        )

    def _generate_bodyweight_prediction(self, window: PredictionWindow) -> Prediction | None:
        bw_history: list[float] = []
        current_bw = 75.0
        calorie_surplus = 0.0
        adherence = 0.8

        if self._db:
            try:
                if hasattr(self._db, "get_body_weight_history"):
                    raw = self._db.get_body_weight_history(days=90)
                    if raw:
                        bw_history = [float(w.weight) if hasattr(w, "weight") else float(w) for w in raw]
                latest = self._db.get_latest_body_weight() if hasattr(self._db, "get_latest_body_weight") else None
                if latest:
                    current_bw = float(latest.weight) if hasattr(latest, "weight") else float(latest)
            except Exception:
                logger.warning("Failed to fetch bodyweight prediction data", exc_info=True)

        return self._bodyweight_engine.predict(
            window=window,
            bodyweight_history=bw_history if bw_history else None,
            current_bodyweight=current_bw,
            calorie_surplus_avg=calorie_surplus,
            calorie_adherence=adherence,
        )

    def _generate_goal_eta(self) -> Prediction | None:
        current_bw = 75.0
        goal_bw = 70.0
        bw_history: list[float] = []
        calorie_surplus = 0.0
        adherence = 0.8

        if self._db:
            try:
                if hasattr(self._db, "get_body_weight_history"):
                    raw = self._db.get_body_weight_history(days=90)
                    if raw:
                        bw_history = [float(w.weight) if hasattr(w, "weight") else float(w) for w in raw]
                latest = self._db.get_latest_body_weight() if hasattr(self._db, "get_latest_body_weight") else None
                if latest:
                    current_bw = float(latest.weight) if hasattr(latest, "weight") else float(latest)
                if hasattr(self._db, "get_goal_weight"):
                    goal = self._db.get_goal_weight()
                    if goal:
                        goal_bw = float(goal)
            except Exception:
                logger.warning("Failed to fetch goal ETA data", exc_info=True)

        return self._goal_eta_engine.predict(
            current_bodyweight=current_bw,
            goal_bodyweight=goal_bw,
            bodyweight_history=bw_history if bw_history else None,
            calorie_surplus_avg=calorie_surplus,
            calorie_adherence=adherence,
        )

    def _generate_volume_prediction(self, window: PredictionWindow) -> Prediction | None:
        weekly_volumes: list[float] = []
        current_weekly = 14000.0
        estimated_mrv = 20000.0
        session_count = 4

        if self._db:
            try:
                v7 = self._db.get_recent_volume(days=7) if hasattr(self._db, "get_recent_volume") else 0
                v14 = self._db.get_recent_volume(days=14) if hasattr(self._db, "get_recent_volume") else 0
                current_weekly = v7 if v7 > 0 else v14 / 2 if v14 > 0 else current_weekly
                weekly_volumes = [v14 / 2 if v14 > 0 else current_weekly, v7 if v7 > 0 else current_weekly]
                sessions = self._db.list_sessions(limit=10) if hasattr(self._db, "list_sessions") else []
                session_count = len(sessions)
            except Exception:
                logger.warning("Failed to fetch volume prediction data", exc_info=True)

        return self._volume_engine.predict(
            window=window,
            weekly_volumes=weekly_volumes if weekly_volumes else None,
            estimated_mrv=estimated_mrv,
            current_weekly_volume=current_weekly,
            session_count=session_count,
        )

    def _generate_consistency_prediction(self, window: PredictionWindow) -> Prediction | None:
        streak = 0
        missed = 0
        recovery_avg = 70.0

        if self._db:
            try:
                streak = self._db.get_streak() if hasattr(self._db, "get_streak") else 0
                sessions = self._db.list_sessions(limit=20) if hasattr(self._db, "list_sessions") else []
                missed = sum(1 for s in sessions if hasattr(s, "completed") and not s.completed) if sessions else 0
            except Exception:
                logger.warning("Failed to fetch consistency prediction data", exc_info=True)

        return self._consistency_engine.predict(
            window=window,
            current_streak=streak,
            missed_last_7d=missed,
            recovery_avg=recovery_avg,
            recent_completion_rate=0.8,
        )

    def _generate_deload_prediction(self, window: PredictionWindow) -> Prediction | None:
        scores: list[float] = []
        current_fatigue = 40.0
        weeks_since_deload = 6
        sleep_avg = 7.0
        session_count = 4

        if self._db:
            try:
                if hasattr(self._db, "get_recovery_scores"):
                    scores = self._db.get_recovery_scores(days=14) or []
                sessions = self._db.list_sessions(limit=20) if hasattr(self._db, "list_sessions") else []
                session_count = len(sessions)
            except Exception:
                logger.warning("Failed to fetch deload prediction data", exc_info=True)

        return self._deload_engine.predict(
            window=window,
            weeks_since_last_deload=weeks_since_deload,
            recovery_scores=scores if scores else None,
            current_fatigue=current_fatigue,
            sleep_avg=sleep_avg,
            session_count_7d=session_count,
        )

    def has_data(self) -> bool:
        return self._repo.has_data()

    def _publish_event(self, event_name: str, data: dict) -> None:
        if not self._event_bus:
            return
        try:
            import asyncio
            try:
                loop = asyncio.get_running_loop()
                if loop.is_running():
                    asyncio.ensure_future(self._event_bus.core.emit(event_name, data, source="prediction"))
                    return
            except RuntimeError:
                pass
            asyncio.run(self._event_bus.core.emit(event_name, data, source="prediction"))
        except Exception:
            logger.warning("Failed to publish %s event", event_name, exc_info=True)

    def dispose(self) -> None:
        self._repo.dispose()
