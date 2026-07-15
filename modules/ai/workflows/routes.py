from fastapi import APIRouter, HTTPException
from modules.ai.workflows.models import (
    ProgressiveOverloadRequest, ProgressiveOverloadResponse,
    VolumeLandmarksRequest, VolumeLandmarksResponse,
    RecoveryForecastRequest, RecoveryForecastResponse,
    CounterfactualRequest, CounterfactualResponse
)
from modules.ai.rules.progressive_overload import evaluate_progressive_overload
from modules.ai.rules.volume_landmarks import calculate_volume_landmarks
from modules.ai.skills.recovery_forecasting import forecast_recovery
from modules.ai.skills.counterfactual_generation import generate_counterfactual

router = APIRouter(prefix="/api/ai", tags=["AI Analytics"])

@router.post("/progressive-overload", response_model=ProgressiveOverloadResponse)
def evaluate_progression(payload: ProgressiveOverloadRequest):
    try:
        result = evaluate_progressive_overload(
            reps=payload.reps,
            rir=payload.rir,
            current_weight=payload.current_weight,
            target_reps=payload.target_reps,
            target_rir=payload.target_rir
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/volume-landmarks", response_model=VolumeLandmarksResponse)
def evaluate_landmarks(payload: VolumeLandmarksRequest):
    try:
        result = calculate_volume_landmarks(
            muscle_group=payload.muscle_group,
            weekly_sets=payload.weekly_sets
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/forecast-recovery", response_model=RecoveryForecastResponse)
def evaluate_forecast(payload: RecoveryForecastRequest):
    try:
        result = forecast_recovery(
            sleep_hours=payload.sleep_hours,
            stress_level=payload.stress_level,
            soreness_level=payload.soreness_level,
            previous_scores=payload.previous_scores
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulate-counterfactual", response_model=CounterfactualResponse)
def evaluate_simulation(payload: CounterfactualRequest):
    try:
        result = generate_counterfactual(
            baseline_sleep=payload.baseline_sleep,
            baseline_stress=payload.baseline_stress,
            baseline_soreness=payload.baseline_soreness,
            previous_scores=payload.previous_scores,
            modified_parameters=payload.modified_parameters
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("")
def get_ai_data():
    try:
        return {
            "status": "success",
            "hypertrophy_insights": (
                "AI analysis predicts high stimulus responsiveness in target muscle groups (Latissimus Dorsi, Biceps Brachii). "
                "Current weekly volume is at 18 sets, which is near the optimal maximum recoverable volume (MRV) threshold. "
                "To optimize hypertrophy without overreaching, keep target RIR at 1-2 for pulling movements and "
                "ensure at least 48 hours of recovery between sessions."
            ),
            "readiness_summary": "Based on 7-day HRV and sleep quality, your CNS recovery status is optimal for high-intensity training today."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
