from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from modules.prediction.domain import (
    Prediction,
    PredictionResult,
    PredictionType,
    PredictionWindow,
)


class IPredictionProvider(ABC):
    @abstractmethod
    def get_next_pr_probability(self, window: str = "7d") -> Prediction | None: ...
    @abstractmethod
    def get_plateau_probability(self, window: str = "7d") -> Prediction | None: ...
    @abstractmethod
    def get_recovery_forecast(self, window: str = "7d") -> Prediction | None: ...
    @abstractmethod
    def get_bodyweight_forecast(self, window: str = "14d") -> Prediction | None: ...
    @abstractmethod
    def get_goal_eta(self) -> Prediction | None: ...
    @abstractmethod
    def get_mrv_risk(self) -> Prediction | None: ...
    @abstractmethod
    def get_deload_probability(self) -> Prediction | None: ...
    @abstractmethod
    def get_consistency_forecast(self, window: str = "14d") -> Prediction | None: ...
    @abstractmethod
    def get_all_predictions(self) -> list[Prediction]: ...
    @abstractmethod
    def get_prediction_result(self) -> PredictionResult: ...


class ProductionPredictionProvider(IPredictionProvider):
    def __init__(self, service: Any) -> None:
        self._service = service

    def get_next_pr_probability(self, window: str = "7d") -> Prediction | None:
        return self._service.get_latest_prediction(PredictionType.NEXT_PR_PROBABILITY, PredictionWindow(window))

    def get_plateau_probability(self, window: str = "7d") -> Prediction | None:
        return self._service.get_latest_prediction(PredictionType.PLATEAU_PROBABILITY, PredictionWindow(window))

    def get_recovery_forecast(self, window: str = "7d") -> Prediction | None:
        return self._service.get_latest_prediction(PredictionType.RECOVERY_DECLINE, PredictionWindow(window))

    def get_bodyweight_forecast(self, window: str = "14d") -> Prediction | None:
        return self._service.get_latest_prediction(PredictionType.BODYWEIGHT_TREND, PredictionWindow(window))

    def get_goal_eta(self) -> Prediction | None:
        return self._service.get_latest_prediction(PredictionType.GOAL_ETA, PredictionWindow.NEXT_28_DAYS)

    def get_mrv_risk(self) -> Prediction | None:
        return self._service.get_latest_prediction(PredictionType.MRV_VIOLATION_RISK, PredictionWindow.NEXT_7_DAYS)

    def get_deload_probability(self) -> Prediction | None:
        return self._service.get_latest_prediction(PredictionType.DELOAD_PROBABILITY, PredictionWindow.NEXT_14_DAYS)

    def get_consistency_forecast(self, window: str = "14d") -> Prediction | None:
        return self._service.get_latest_prediction(PredictionType.CONSISTENCY_DECAY, PredictionWindow(window))

    def get_all_predictions(self) -> list[Prediction]:
        return self._service.repo.list_predictions(days=7)

    def get_prediction_result(self) -> PredictionResult:
        preds = self.get_all_predictions()
        return PredictionResult(
            predictions=preds,
            generated_at=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            total_predictions=len(preds),
        )
