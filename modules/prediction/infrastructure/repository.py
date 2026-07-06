from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta

from sqlalchemy import create_engine, desc, func, select
from sqlalchemy.orm import Session

from modules.prediction.domain import (
    ConfidenceLevel,
    Forecast,
    ForecastPoint,
    Prediction,
    PredictionConfidence,
    PredictionExplanation,
    PredictionScenario,
    PredictionType,
    PredictionWindow,
    TrendModel,
)
from modules.prediction.infrastructure.models import (
    Base,
    ForecastModel,
    ForecastPointModel,
    PredictionModel,
    PredictionScenarioModel,
)
from modules.workout.infrastructure.models import init_db as ensure_tables


class PredictionRepository:
    def __init__(self, db_path: str = "data/gymos.db"):
        self._db_path = db_path
        self._engine = create_engine(f"sqlite:///{db_path}")
        ensure_tables(db_path)
        Base.metadata.create_all(self._engine)

    def _get_session(self) -> Session:
        return Session(self._engine)

    def save_prediction(self, prediction: Prediction) -> Prediction:
        pid = prediction.id or uuid.uuid4().hex[:36]
        with self._get_session() as session:
            existing = session.get(PredictionModel, pid)
            if existing:
                existing.value = prediction.value
                existing.probability = prediction.probability
                existing.confidence_score = prediction.confidence.score
                existing.confidence_level = prediction.confidence.level.name
                existing.summary = prediction.explanation.summary
                existing.reasoning = json.dumps(prediction.explanation.reasoning) if prediction.explanation.reasoning else None
                existing.assumptions = json.dumps(prediction.explanation.assumptions) if prediction.explanation.assumptions else None
                existing.risk_factors = json.dumps(prediction.explanation.risk_factors) if prediction.explanation.risk_factors else None
                existing.is_active = prediction.is_active
                existing.expires_at = prediction.expires_at
            else:
                model = PredictionModel(
                    id=pid,
                    prediction_type=prediction.prediction_type.value,
                    window=prediction.window.value,
                    value=prediction.value,
                    probability=prediction.probability,
                    confidence_score=prediction.confidence.score,
                    confidence_level=prediction.confidence.level.name,
                    summary=prediction.explanation.summary,
                    reasoning=json.dumps(prediction.explanation.reasoning) if prediction.explanation.reasoning else None,
                    assumptions=json.dumps(prediction.explanation.assumptions) if prediction.explanation.assumptions else None,
                    risk_factors=json.dumps(prediction.explanation.risk_factors) if prediction.explanation.risk_factors else None,
                    is_active=prediction.is_active,
                    expires_at=prediction.expires_at,
                    created_at=datetime.now(),
                )
                session.add(model)

            # Save scenarios
            for scenario in prediction.scenarios:
                sid = uuid.uuid4().hex[:36]
                scenario_model = PredictionScenarioModel(
                    id=sid, prediction_id=pid, name=scenario.name,
                    description=scenario.description, probability=scenario.probability,
                    created_at=datetime.now(),
                )
                session.add(scenario_model)

            # Save forecast
            if prediction.forecast:
                fid = uuid.uuid4().hex[:36]
                fcast = prediction.forecast
                forecast_model = ForecastModel(
                    id=fid, prediction_id=pid,
                    prediction_type=fcast.prediction_type.value,
                    window=fcast.window.value,
                    trend_model=fcast.trend_model.value,
                    confidence_score=fcast.confidence.score,
                    created_at=datetime.now(),
                )
                session.add(forecast_model)
                for point in fcast.points:
                    pt = ForecastPointModel(
                        id=uuid.uuid4().hex[:36], forecast_id=fid,
                        date=point.date, predicted_value=point.predicted_value,
                        lower_bound=point.lower_bound, upper_bound=point.upper_bound,
                        confidence_at_point=point.confidence_at_point,
                        created_at=datetime.now(),
                    )
                    session.add(pt)

            session.commit()
            prediction.id = pid
            return prediction

    def get_prediction(self, prediction_id: str) -> Prediction | None:
        with self._get_session() as session:
            model = session.get(PredictionModel, prediction_id)
            if model is None:
                return None
            return self._prediction_model_to_domain(session, model)

    def get_active_predictions(self) -> list[Prediction]:
        with self._get_session() as session:
            today = datetime.now().strftime("%Y-%m-%d")
            models = session.execute(
                select(PredictionModel)
                .where(PredictionModel.is_active == True)
                .where(
                    (PredictionModel.expires_at >= today) |
                    (PredictionModel.expires_at.is_(None)) |
                    (PredictionModel.expires_at == "")
                )
            ).scalars().all()
            return [self._prediction_model_to_domain(session, m) for m in models]

    def get_predictions_by_type(self, prediction_type: PredictionType, limit: int = 10) -> list[Prediction]:
        with self._get_session() as session:
            models = session.execute(
                select(PredictionModel)
                .where(PredictionModel.prediction_type == prediction_type.value)
                .order_by(desc(PredictionModel.created_at))
                .limit(limit)
            ).scalars().all()
            return [self._prediction_model_to_domain(session, m) for m in models]

    def list_predictions(self, days: int = 30) -> list[Prediction]:
        with self._get_session() as session:
            cutoff = datetime.now() - timedelta(days=days)
            models = session.execute(
                select(PredictionModel)
                .where(PredictionModel.created_at >= cutoff)
                .order_by(desc(PredictionModel.created_at))
            ).scalars().all()
            return [self._prediction_model_to_domain(session, m) for m in models]

    def delete_prediction(self, prediction_id: str) -> bool:
        with self._get_session() as session:
            model = session.get(PredictionModel, prediction_id)
            if model is None:
                return False
            session.delete(model)
            session.commit()
            return True

    def has_data(self) -> bool:
        with self._get_session() as session:
            count = session.execute(
                select(func.count(PredictionModel.id))
            ).scalar() or 0
            return count > 0

    def count_predictions(self) -> int:
        with self._get_session() as session:
            return session.execute(
                select(func.count(PredictionModel.id))
            ).scalar() or 0

    def _prediction_model_to_domain(self, session: Session, model: PredictionModel) -> Prediction:
        ptype = PredictionType(model.prediction_type)
        pwindow = PredictionWindow(model.window)

        # Scenarios
        scenario_models = session.execute(
            select(PredictionScenarioModel)
            .where(PredictionScenarioModel.prediction_id == model.id)
        ).scalars().all()
        scenarios = [
            PredictionScenario(name=s.name, description=s.description or "", probability=s.probability)
            for s in scenario_models
        ]

        # Forecast
        forecast = None
        forecast_model = session.execute(
            select(ForecastModel).where(ForecastModel.prediction_id == model.id)
        ).scalars().first()
        if forecast_model:
            point_models = session.execute(
                select(ForecastPointModel).where(ForecastPointModel.forecast_id == forecast_model.id)
                .order_by(ForecastPointModel.date)
            ).scalars().all()
            points = [
                ForecastPoint(
                    date=p.date, predicted_value=p.predicted_value,
                    lower_bound=p.lower_bound, upper_bound=p.upper_bound,
                    confidence_at_point=p.confidence_at_point,
                )
                for p in point_models
            ]
            forecast = Forecast(
                prediction_type=PredictionType(forecast_model.prediction_type),
                window=PredictionWindow(forecast_model.window),
                points=points,
                trend_model=TrendModel(forecast_model.trend_model),
                confidence=PredictionConfidence(score=forecast_model.confidence_score),
            )

        # Reasoning
        reasoning = []
        if model.reasoning:
            try:
                reasoning = json.loads(model.reasoning)
            except (json.JSONDecodeError, TypeError):
                reasoning = []

        assumptions = []
        if model.assumptions:
            try:
                assumptions = json.loads(model.assumptions)
            except (json.JSONDecodeError, TypeError):
                assumptions = []

        risk_factors = []
        if model.risk_factors:
            try:
                risk_factors = json.loads(model.risk_factors)
            except (json.JSONDecodeError, TypeError):
                risk_factors = []

        return Prediction(
            id=model.id,
            prediction_type=ptype,
            window=pwindow,
            value=model.value,
            probability=model.probability,
            confidence=PredictionConfidence(
                score=model.confidence_score,
                level=ConfidenceLevel[model.confidence_level.upper()] if model.confidence_level else ConfidenceLevel.MODERATE,
            ),
            explanation=PredictionExplanation(
                summary=model.summary or "",
                reasoning=reasoning,
                assumptions=assumptions,
                risk_factors=risk_factors,
            ),
            forecast=forecast,
            scenarios=scenarios,
            created_at=model.created_at.isoformat() if model.created_at else "",
            expires_at=model.expires_at or "",
            is_active=model.is_active,
        )

    def dispose(self) -> None:
        self._engine.dispose()
