"""Typed domain event models for the Predictive Intelligence Engine (RFC-020)."""

from dataclasses import dataclass, field

from shared.events.event import DomainEvent


@dataclass
class PredictionUpdated(DomainEvent):
    prediction_type: str = ""
    window: str = ""
    value: float = 0.0
    probability: float = 0.0
    confidence_score: float = 0.0
    summary: str = ""
    source: str = "prediction"


@dataclass
class PlateauPredicted(DomainEvent):
    probability: float = 0.0
    primary_factors: list[str] = field(default_factory=list)
    window: str = ""
    source: str = "prediction"


@dataclass
class GoalEtaChanged(DomainEvent):
    previous_eta_days: float = 0.0
    new_eta_days: float = 0.0
    change_days: float = 0.0
    source: str = "prediction"


@dataclass
class DeloadForecastUpdated(DomainEvent):
    deload_probability: float = 0.0
    recommended_window: str = ""
    primary_reason: str = ""
    source: str = "prediction"


@dataclass
class PredictionModelUpdated(DomainEvent):
    model_name: str = ""
    model_version: str = ""
    metrics: dict = field(default_factory=dict)
    source: str = "prediction"
