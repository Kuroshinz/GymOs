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
from schemas.api_models import WorkoutLogPayload, WorkoutSessionLogPayload, NutritionLogPayload
from modules.ai.workflows.routes import router as ai_router
from shared.knowledge_loader import get_loader
from shared.domain.repositories import MuscleRepository, ExerciseRepository

app = FastAPI(title="GymOS Headless API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai_router)

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

loader = get_loader()
muscle_repo = MuscleRepository(loader)
exercise_repo = ExerciseRepository(loader)

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


@app.get("/api/exercises")
def get_exercises():
    try:
        return [ex.raw for ex in exercise_repo.get_all().values()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/muscles")
def get_muscles():
    try:
        return [m.raw for m in muscle_repo.get_all().values()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/workout/sessions")
def get_workout_sessions():
    try:
        sessions = db.list_sessions(limit=100)
        serialized = []
        for s in sessions:
            serialized.append({
                "id": s.id,
                "day_name": s.day_name,
                "program_name": s.program_name,
                "started_at": s.started_at.isoformat() if s.started_at else None,
                "completed_at": s.completed_at.isoformat() if s.completed_at else None,
                "duration_minutes": s.duration_minutes,
                "total_volume": s.total_volume,
                "completed_sets_count": s.completed_sets_count,
            })
        return {
            "total_count": len(sessions),
            "sessions": serialized
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/workout/session")
def save_workout_session(payload: WorkoutSessionLogPayload):
    try:
        from datetime import datetime

        def parse_date(date_str: str) -> datetime | None:
            if not date_str:
                return None
            try:
                return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            except ValueError:
                # fallback parsing
                try:
                    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
                except ValueError:
                    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")

        exercises = []
        for ex_payload in payload.exercises:
            sets = []
            for s_payload in ex_payload.sets:
                sets.append(SessionSet(
                    set_number=s_payload.set_number,
                    weight_kg=s_payload.weight,
                    reps=s_payload.reps,
                    rir=s_payload.rir,
                    completed=s_payload.is_completed
                ))
            exercises.append(SessionExercise(
                name=ex_payload.exercise_name,
                sets=sets
            ))

        domain_session = WorkoutSession(
            id=payload.id,
            day_name="Completed Workout",
            program_name=payload.program_id,
            exercises=exercises,
            started_at=parse_date(payload.start_time),
            completed_at=parse_date(payload.end_time) if payload.end_time else None
        )

        saved = db.save_session(domain_session)
        return {
            "status": "success",
            "session_id": saved.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard/state")
def get_dashboard_state():
    try:
        from datetime import datetime, timedelta
        from modules.nutrition.infrastructure.repository import NutritionRepository
        from modules.nutrition.domain import MacroTarget, NutritionGoalType

        today_str = datetime.now().strftime("%Y-%m-%d")

        # 1. Recovery Readiness
        today_score_record = recovery_service.get_today_score()
        score = today_score_record.score if today_score_record else 85.0

        if score >= 85:
            recovery_color_hex = "#34D399"
        elif score >= 70:
            recovery_color_hex = "#38BDF8"
        elif score >= 55:
            recovery_color_hex = "#FBBF24"
        else:
            recovery_color_hex = "#FB7185"

        active_program_name = "PPL-UL Master v6"

        # 2. Muscle Fatigue (Inroad)
        recent_sessions = db.list_sessions(limit=50)
        seven_days_ago = datetime.now() - timedelta(days=7)
        past_week_sessions = [
            s for s in recent_sessions
            if s.completed_at and s.completed_at >= seven_days_ago
        ]

        from scripts.parse_excel_program import EXERCISE_MUSCLE_MAP
        muscle_sets_count = {}
        for s in past_week_sessions:
            for ex in s.exercises:
                muscle_group = EXERCISE_MUSCLE_MAP.get(ex.name, "")
                if muscle_group:
                    completed_sets = sum(1 for set_item in ex.sets if set_item.completed)
                    muscle_sets_count[muscle_group] = muscle_sets_count.get(muscle_group, 0) + completed_sets

        chest_sets = muscle_sets_count.get("chest", 0)
        triceps_sets = muscle_sets_count.get("triceps", 0)
        shoulders_sets = muscle_sets_count.get("shoulders", 0)

        chest_fatigue = min(100.0, (chest_sets / 16.0) * 100.0)
        triceps_fatigue = min(100.0, (triceps_sets / 12.0) * 100.0)
        front_delts_fatigue = min(100.0, (shoulders_sets / 12.0) * 100.0)

        def get_status_data(fatigue):
            if fatigue > 80:
                return {"fatigue": float(fatigue), "status_text": "Overloaded", "color": "#FB7185"}
            elif fatigue > 40:
                return {"fatigue": float(fatigue), "status_text": "Recovering", "color": "#FBBF24"}
            else:
                return {"fatigue": float(fatigue), "status_text": "Fresh", "color": "#34D399"}

        muscle_status = {
            "Chest": get_status_data(chest_fatigue),
            "Triceps": get_status_data(triceps_fatigue),
            "Front_Delts": get_status_data(front_delts_fatigue)
        }

        # 3. Nutrition Progress
        nutrition_repo = NutritionRepository(DB_PATH)
        day_nutrition = nutrition_repo.get_day(today_str)

        target = nutrition_repo.get_target(today_str)
        if not target:
            from modules.nutrition.domain import MacroTarget, NutritionGoalType
            target = MacroTarget(
                calories=2500,
                protein_g=160,
                carbs_g=280,
                fat_g=70,
                fiber_g=30,
                water_ml=2500,
                goal_type=NutritionGoalType.MAINTAIN
            )
            nutrition_repo.save_target(target, today_str)

        total_cal = 0.0
        total_prot = 0.0
        total_carb = 0.0
        total_fat = 0.0

        if day_nutrition:
            for m in day_nutrition.meals:
                for item in m.items:
                    total_cal += item.calories
                    total_prot += item.protein_g
                    total_carb += item.carbs_g
                    total_fat += item.fat_g

        calories_pct = min(100.0, (total_cal / target.calories * 100)) if target.calories > 0 else 0.0
        protein_pct = min(100.0, (total_prot / target.protein_g * 100)) if target.protein_g > 0 else 0.0
        carbs_pct = min(100.0, (total_carb / target.carbs_g * 100)) if target.carbs_g > 0 else 0.0
        fat_pct = min(100.0, (total_fat / target.fat_g * 100)) if target.fat_g > 0 else 0.0

        nutrition_summary = {
            "calories_pct": float(calories_pct),
            "calories_display": f"{int(total_cal)} / {int(target.calories)} kcal",
            "protein_pct": float(protein_pct),
            "protein_display": f"{int(total_prot)} / {int(target.protein_g)} g",
            "carbs_pct": float(carbs_pct),
            "carbs_display": f"{int(total_carb)} / {int(target.carbs_g)} g",
            "fat_pct": float(fat_pct),
            "fat_display": f"{int(total_fat)} / {int(target.fat_g)} g"
        }

        workout_recommender = {
            "suggested_exercise": "Lat Pulldown",
            "ai_coached_target": "3 sets x 10 reps @ RIR 2"
        }

        return {
            "recovery_score": int(score),
            "recovery_color_hex": recovery_color_hex,
            "active_program_name": active_program_name,
            "muscle_status": muscle_status,
            "nutrition_summary": nutrition_summary,
            "workout_recommender": workout_recommender
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/nutrition/log")
def log_nutrition(payload: NutritionLogPayload):
    try:
        from datetime import datetime
        from modules.nutrition.domain import DailyNutrition, Meal, MealItem
        from modules.nutrition.infrastructure.repository import NutritionRepository

        nutrition_repo = NutritionRepository(DB_PATH)
        today_str = datetime.now().strftime("%Y-%m-%d")

        day = nutrition_repo.get_day(today_str)
        if not day:
            day = DailyNutrition(date=today_str, meals=[], water_ml=0)

        item = MealItem(
            name=payload.name,
            calories=payload.calories,
            protein_g=payload.protein_g,
            carbs_g=payload.carbs_g,
            fat_g=payload.fat_g,
            fiber_g=0.0,
            quantity=1.0,
            unit="serving"
        )
        meal = Meal(
            name=payload.name,
            meal_type=None,
            items=[item],
            eaten_at=datetime.now()
        )

        day.meals.append(meal)
        nutrition_repo.save_day(day)

        return {
            "status": "success",
            "message": "Meal logged successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
