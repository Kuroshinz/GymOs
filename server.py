import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from modules.workout.infrastructure.repository import GymDatabase
from modules.workout.domain import SessionSet, SessionExercise, WorkoutSession
from modules.workout.application.volume_analytics import VolumeAnalytics
from modules.recovery.infrastructure.repository import RecoveryRepository
from modules.recovery.application import RecoveryService
from modules.prediction.infrastructure.repository import PredictionRepository
from modules.prediction.application import PredictionService
from modules.gymbrain.services.decision_engine import DecisionEngine
from shared.events.event_bus import get_event_bus
from schemas.api_models import WorkoutLogPayload

app = FastAPI(title="GymOS Headless API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resolve DB Path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "gymos.db")

# Initialize infrastructure
db = GymDatabase(DB_PATH)
event_bus = get_event_bus()

recovery_repo = RecoveryRepository(DB_PATH)
recovery_service = RecoveryService(
    repository=recovery_repo,
    db=db,
    event_bus=event_bus,
)

prediction_repo = PredictionRepository(DB_PATH)
prediction_service = PredictionService(
    repository=prediction_repo,
    db=db,
    event_bus=event_bus,
)

engine = DecisionEngine.from_production(
    db=db,
    recovery_provider=recovery_service.provider,
)

@app.post("/api/workout/log")
def log_workout(payload: WorkoutLogPayload):
    try:
        # Create completed SessionSet
        set_item = SessionSet(
            set_number=1,
            weight_kg=payload.weight_kg,
            reps=payload.reps,
            rir=payload.rir,
            completed=True,
        )
        exercise = SessionExercise(
            name=payload.exercise_name,
            sets=[set_item],
        )
        session = WorkoutSession(
            day_name="API Session",
            exercises=[exercise],
            started_at=datetime.now(),
            completed_at=datetime.now(),
        )
        
        # Save workout session to DB
        saved_session = db.save_session(session)

        # Trigger weekly/current volume analytics
        analytics = VolumeAnalytics(db)
        volume_report = analytics.get_current_week_volume()

        # Trigger GymBrain decision engine recommendations evaluation
        recs = engine.get_today_recommendations()
        
        return {
            "status": "success",
            "message": "Workout set logged successfully",
            "logged_set": {
                "exercise_name": payload.exercise_name,
                "weight_kg": payload.weight_kg,
                "reps": payload.reps,
                "rir": payload.rir,
            },
            "volume_analytics": {
                "week_label": volume_report.week_label,
                "total_sets": volume_report.total_sets,
                "total_volume_kg": volume_report.total_volume_kg,
                "muscles": [
                    {
                        "muscle_group": m.muscle_group,
                        "total_sets": m.total_sets,
                        "total_volume_kg": m.total_volume_kg,
                        "status": m.status,
                    }
                    for m in volume_report.muscles
                ]
            },
            "recommendations": [
                {
                    "title": r.title,
                    "description": r.description,
                    "category": r.category.value if hasattr(r.category, "value") else str(r.category),
                    "priority": r.priority.value if hasattr(r.priority, "value") else str(r.priority),
                }
                for r in recs
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/recovery")
def get_recovery_analytics():
    try:
        scores = recovery_service.get_recent_scores(days=7)
        today_score = recovery_service.get_today_score()
        
        # Compute a default readiness assessment
        readiness = recovery_service.readiness_engine.assess_readiness(
            sleep_quality=3,
            soreness=2,
            stress=2,
            prev_recovery_score=float(today_score.score) if today_score else 70.0
        )

        return {
            "today_score": today_score.score if today_score else None,
            "recent_scores": [
                {
                    "date": s.date,
                    "score": s.score,
                }
                for s in scores
            ],
            "readiness": {
                "level": readiness.level.value if hasattr(readiness.level, "value") else str(readiness.level),
                "score": readiness.score,
                "description": readiness.description,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/predictions")
def get_prediction_analytics():
    try:
        # Generate new prediction result
        prediction_result = prediction_service.generate_all_predictions()
        
        return {
            "generated_at": prediction_result.generated_at,
            "total_predictions": prediction_result.total_predictions,
            "scenarios": [
                {
                    "intervention": s.intervention.value if hasattr(s.intervention, "value") else str(s.intervention),
                    "overall_assessment": s.overall_assessment,
                    "recommended": s.recommended,
                    "risk_level": s.risk_level,
                }
                for s in getattr(prediction_result, "scenario_results", [])
            ],
            "counterfactuals": [
                {
                    "parameter": c.query.parameter if hasattr(c.query, "parameter") else "",
                    "baseline_prediction": c.baseline_prediction,
                    "counterfactual_prediction": c.counterfactual_prediction,
                    "absolute_delta": c.absolute_delta,
                    "percent_delta": c.percent_delta,
                    "impact_level": c.impact_level,
                }
                for c in getattr(prediction_result, "counterfactual_results", [])
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
