from pydantic import BaseModel, Field
from typing import list, dict

class ProgressiveOverloadRequest(BaseModel):
    reps: list[int] = Field(..., description="Reps completed per set")
    rir: list[int] = Field(..., description="RIR recorded per set")
    current_weight: float = Field(..., description="Current weight lifted in kg")
    target_reps: int = Field(10, description="Target reps to trigger weight progression")
    target_rir: int = Field(2, description="Target reps in reserve to trigger weight progression")

class ProgressiveOverloadResponse(BaseModel):
    should_increase: bool
    suggested_weight: float
    reason: str

class VolumeLandmarksRequest(BaseModel):
    muscle_group: str
    weekly_sets: int

class VolumeLandmarksResponse(BaseModel):
    muscle_group: str
    weekly_sets: int
    MEV: int
    MAV_range: str
    MRV: int
    status: str

class RecoveryForecastRequest(BaseModel):
    sleep_hours: float
    stress_level: int
    soreness_level: int
    previous_scores: list[float] = Field(default_factory=list)

class RecoveryForecastResponse(BaseModel):
    forecasted_score: float
    level: str
    description: str

class CounterfactualRequest(BaseModel):
    baseline_sleep: float
    baseline_stress: int
    baseline_soreness: int
    previous_scores: list[float] = Field(default_factory=list)
    modified_parameters: dict = Field(..., description="Modified sleep_hours, stress_level, soreness_level")

class CounterfactualResponse(BaseModel):
    baseline_score: float
    simulated_score: float
    delta: float
    impact_level: str
    baseline_level: str
    simulated_level: str
