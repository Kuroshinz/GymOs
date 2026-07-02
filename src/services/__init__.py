from datetime import date, timedelta, datetime
from typing import Optional, List, Tuple
from sqlalchemy import func, and_
from src.database import get_session
from src.models import (
    User, WeightEntry, WorkoutSession, WorkoutExercise, ExerciseSet,
    Exercise, PersonalRecord, NutritionLog, WaterLog, SleepLog,
    Measurement, DailyRecovery, OverloadDecision, Achievement, UserAchievement,
    MuscleGroup
)
import json


class UserService:
    @staticmethod
    def get_or_create_user() -> User:
        session = get_session()
        try:
            user = session.query(User).first()
            if not user:
                user = User(
                    name="Athlete", age=16, height_cm=178.0,
                    target_weight_kg=72.5, goal="Lean Bulk",
                    workout_split="PPL-UL", workout_days_per_week=5,
                    target_calories=2700, target_protein_g=130,
                    target_fat_g=75, target_carbs_g=340,
                    target_fiber_g=30, target_water_ml=3500
                )
                session.add(user)
                session.commit()
                session.refresh(user)
            return user
        finally:
            session.close()

    @staticmethod
    def update_user(user_id: int, **kwargs) -> User:
        session = get_session()
        try:
            user = session.query(User).get(user_id)
            for k, v in kwargs.items():
                if hasattr(user, k):
                    setattr(user, k, v)
            session.commit()
            session.refresh(user)
            return user
        finally:
            session.close()


class WeightService:
    @staticmethod
    def log_weight(user_id: int, weight_kg: float, log_date: date = None) -> WeightEntry:
        session = get_session()
        try:
            entry = WeightEntry(user_id=user_id, weight_kg=weight_kg, date=log_date or date.today())
            session.add(entry)
            session.commit()
            session.refresh(entry)
            return entry
        finally:
            session.close()

    @staticmethod
    def get_recent(user_id: int, days: int = 30) -> List[WeightEntry]:
        session = get_session()
        try:
            cutoff = date.today() - timedelta(days=days)
            return session.query(WeightEntry).filter(
                WeightEntry.user_id == user_id,
                WeightEntry.date >= cutoff
            ).order_by(WeightEntry.date).all()
        finally:
            session.close()

    @staticmethod
    def get_latest(user_id: int) -> Optional[WeightEntry]:
        session = get_session()
        try:
            return session.query(WeightEntry).filter(
                WeightEntry.user_id == user_id
            ).order_by(WeightEntry.date.desc()).first()
        finally:
            session.close()

    @staticmethod
    def get_weekly_average(user_id: int) -> float:
        session = get_session()
        try:
            cutoff = date.today() - timedelta(days=7)
            result = session.query(func.avg(WeightEntry.weight_kg)).filter(
                WeightEntry.user_id == user_id,
                WeightEntry.date >= cutoff
            ).scalar()
            return round(result, 1) if result else 0
        finally:
            session.close()

    @staticmethod
    def get_monthly_average(user_id: int) -> float:
        session = get_session()
        try:
            cutoff = date.today() - timedelta(days=30)
            result = session.query(func.avg(WeightEntry.weight_kg)).filter(
                WeightEntry.user_id == user_id,
                WeightEntry.date >= cutoff
            ).scalar()
            return round(result, 1) if result else 0
        finally:
            session.close()

    @staticmethod
    def get_eta_to_goal(user_id: int, current_weight: float) -> Tuple[int, str]:
        session = get_session()
        try:
            user = session.query(User).get(user_id)
            if not user:
                return 0, ""
            entries = session.query(WeightEntry).filter(
                WeightEntry.user_id == user_id
            ).order_by(WeightEntry.date).all()
            if len(entries) < 2:
                return 0, "Need more data"
            recent = entries[-14:] if len(entries) >= 14 else entries
            if len(recent) < 2:
                return 0, "Need more data"
            weights = [e.weight_kg for e in recent]
            dates = [(e.date - recent[0].date).days for e in recent]
            if dates[-1] == 0:
                return 0, "Need more data"
            slope = (weights[-1] - weights[0]) / dates[-1] if dates[-1] > 0 else 0
            if slope <= 0:
                remaining = user.target_weight_kg - current_weight
                if remaining <= 0:
                    return 0, "Goal reached!"
                return 0, "Gaining - adjust nutrition"
            days_needed = int((user.target_weight_kg - current_weight) / slope)
            eta = date.today() + timedelta(days=abs(days_needed))
            return abs(days_needed), eta.strftime("%B %d, %Y")
        finally:
            session.close()


class WorkoutService:
    @staticmethod
    def get_today_workout(user_id: int) -> Optional[WorkoutSession]:
        session = get_session()
        try:
            return session.query(WorkoutSession).filter(
                WorkoutSession.user_id == user_id,
                WorkoutSession.date == date.today()
            ).first()
        finally:
            session.close()

    @staticmethod
    def get_workout_streak(user_id: int) -> int:
        session = get_session()
        try:
            streak = 0
            check_date = date.today()
            while True:
                found = session.query(WorkoutSession).filter(
                    WorkoutSession.user_id == user_id,
                    WorkoutSession.date == check_date,
                    WorkoutSession.is_completed == True
                ).first()
                if found:
                    streak += 1
                    check_date -= timedelta(days=1)
                else:
                    break
            return streak
        finally:
            session.close()

    @staticmethod
    def get_weekly_volume(user_id: int) -> float:
        session = get_session()
        try:
            cutoff = date.today() - timedelta(days=7)
            return session.query(func.sum(ExerciseSet.weight_kg * ExerciseSet.reps)).select_from(
                WorkoutSession
            ).join(WorkoutExercise).join(ExerciseSet).filter(
                WorkoutSession.user_id == user_id,
                WorkoutSession.date >= cutoff,
                WorkoutSession.is_completed == True,
                ExerciseSet.is_warmup == False
            ).scalar() or 0
        finally:
            session.close()

    @staticmethod
    def get_monthly_volume(user_id: int) -> float:
        session = get_session()
        try:
            cutoff = date.today() - timedelta(days=30)
            return session.query(func.sum(ExerciseSet.weight_kg * ExerciseSet.reps)).select_from(
                WorkoutSession
            ).join(WorkoutExercise).join(ExerciseSet).filter(
                WorkoutSession.user_id == user_id,
                WorkoutSession.date >= cutoff,
                WorkoutSession.is_completed == True,
                ExerciseSet.is_warmup == False
            ).scalar() or 0
        finally:
            session.close()

    @staticmethod
    def get_weekly_workouts_count(user_id: int) -> int:
        session = get_session()
        try:
            cutoff = date.today() - timedelta(days=7)
            return session.query(WorkoutSession).filter(
                WorkoutSession.user_id == user_id,
                WorkoutSession.date >= cutoff,
                WorkoutSession.is_completed == True
            ).count()
        finally:
            session.close()

    @staticmethod
    def get_total_workouts(user_id: int) -> int:
        session = get_session()
        try:
            return session.query(WorkoutSession).filter(
                WorkoutSession.user_id == user_id,
                WorkoutSession.is_completed == True
            ).count()
        finally:
            session.close()

    @staticmethod
    def get_exercise_history(user_id: int, exercise_id: int, limit: int = 10) -> List[dict]:
        session = get_session()
        try:
            results = session.query(
                WorkoutSession.date,
                func.sum(ExerciseSet.weight_kg * ExerciseSet.reps).label("volume"),
                func.max(ExerciseSet.weight_kg).label("max_weight"),
                func.max(ExerciseSet.reps).label("max_reps"),
                func.count(ExerciseSet.id).label("sets")
            ).select_from(WorkoutSession).join(
                WorkoutExercise, WorkoutExercise.session_id == WorkoutSession.id
            ).join(
                ExerciseSet, ExerciseSet.workout_exercise_id == WorkoutExercise.id
            ).filter(
                WorkoutSession.user_id == user_id,
                WorkoutExercise.exercise_id == exercise_id,
                WorkoutSession.is_completed == True,
                ExerciseSet.is_warmup == False
            ).group_by(WorkoutSession.date).order_by(
                WorkoutSession.date.desc()
            ).limit(limit).all()

            return [
                {
                    "date": r.date,
                    "volume": round(r.volume, 1) if r.volume else 0,
                    "max_weight": round(r.max_weight, 1) if r.max_weight else 0,
                    "max_reps": r.max_reps or 0,
                    "sets": r.sets or 0
                }
                for r in results
            ]
        finally:
            session.close()

    @staticmethod
    def get_best_set(exercise_id: int, user_id: int) -> Optional[dict]:
        session = get_session()
        try:
            result = session.query(
                ExerciseSet, WorkoutSession.date
            ).join(
                WorkoutExercise, WorkoutExercise.id == ExerciseSet.workout_exercise_id
            ).join(
                WorkoutSession, WorkoutSession.id == WorkoutExercise.session_id
            ).filter(
                WorkoutExercise.exercise_id == exercise_id,
                WorkoutSession.user_id == user_id,
                ExerciseSet.is_warmup == False
            ).order_by(
                (ExerciseSet.weight_kg * ExerciseSet.reps).desc()
            ).first()
            if result:
                es, d = result
                return {"weight": es.weight_kg, "reps": es.reps, "date": d, "volume": es.weight_kg * es.reps}
            return None
        finally:
            session.close()

    @staticmethod
    def get_previous_session_exercise(user_id: int, exercise_id: int) -> Optional[dict]:
        session = get_session()
        try:
            prev_session = session.query(WorkoutSession).join(
                WorkoutExercise, WorkoutExercise.session_id == WorkoutSession.id
            ).filter(
                WorkoutSession.user_id == user_id,
                WorkoutExercise.exercise_id == exercise_id,
                WorkoutSession.is_completed == True,
                WorkoutSession.date < date.today()
            ).order_by(WorkoutSession.date.desc()).first()
            if not prev_session:
                return None
            we = session.query(WorkoutExercise).filter(
                WorkoutExercise.session_id == prev_session.id,
                WorkoutExercise.exercise_id == exercise_id
            ).first()
            if not we:
                return None
            sets = session.query(ExerciseSet).filter(
                ExerciseSet.workout_exercise_id == we.id,
                ExerciseSet.is_warmup == False
            ).order_by(ExerciseSet.set_number).all()
            return {
                "date": prev_session.date,
                "sets": [{"weight": s.weight_kg, "reps": s.reps, "rpe": s.rpe} for s in sets],
                "total_volume": sum(s.weight_kg * s.reps for s in sets)
            }
        finally:
            session.close()

    @staticmethod
    def get_muscle_volume(user_id: int, days: int = 30):
        session = get_session()
        try:
            cutoff = date.today() - timedelta(days=days)
            results = session.query(
                Exercise.primary_muscle,
                func.sum(ExerciseSet.weight_kg * ExerciseSet.reps).label("volume")
            ).select_from(WorkoutSession).join(
                WorkoutExercise, WorkoutExercise.session_id == WorkoutSession.id
            ).join(
                Exercise, Exercise.id == WorkoutExercise.exercise_id
            ).join(
                ExerciseSet, ExerciseSet.workout_exercise_id == WorkoutExercise.id
            ).filter(
                WorkoutSession.user_id == user_id,
                WorkoutSession.date >= cutoff,
                ExerciseSet.is_warmup == False
            ).group_by(Exercise.primary_muscle).all()
            return {r.primary_muscle: round(r.volume, 1) for r in results}
        finally:
            session.close()


class NutritionService:
    @staticmethod
    def get_daily_totals(user_id: int, log_date: date = None) -> dict:
        session = get_session()
        try:
            d = log_date or date.today()
            result = session.query(
                func.sum(NutritionLog.calories).label("calories"),
                func.sum(NutritionLog.protein_g).label("protein"),
                func.sum(NutritionLog.fat_g).label("fat"),
                func.sum(NutritionLog.carbs_g).label("carbs"),
                func.sum(NutritionLog.fiber_g).label("fiber"),
            ).filter(
                NutritionLog.user_id == user_id,
                NutritionLog.date == d
            ).first()

            water = session.query(func.sum(WaterLog.amount_ml)).filter(
                WaterLog.user_id == user_id,
                WaterLog.date == d
            ).scalar() or 0

            return {
                "calories": result.calories or 0,
                "protein": round(result.protein or 0, 1),
                "fat": round(result.fat or 0, 1),
                "carbs": round(result.carbs or 0, 1),
                "fiber": round(result.fiber or 0, 1),
                "water_ml": water or 0,
            }
        finally:
            session.close()

    @staticmethod
    def get_weekly_average(user_id: int) -> dict:
        session = get_session()
        try:
            cutoff = date.today() - timedelta(days=7)
            result = session.query(
                func.avg(NutritionLog.calories).label("calories"),
                func.avg(NutritionLog.protein_g).label("protein"),
                func.avg(NutritionLog.fat_g).label("fat"),
                func.avg(NutritionLog.carbs_g).label("carbs"),
            ).filter(
                NutritionLog.user_id == user_id,
                NutritionLog.date >= cutoff
            ).first()
            return {
                "calories": round(result.calories or 0),
                "protein": round(result.protein or 0, 1),
                "fat": round(result.fat or 0, 1),
                "carbs": round(result.carbs or 0, 1),
            }
        finally:
            session.close()

    @staticmethod
    def log_meal(user_id: int, meal: str, calories: int, protein: float, fat: float, carbs: float,
                 fiber: float = 0, food_name: str = "", log_date: date = None) -> NutritionLog:
        session = get_session()
        try:
            nl = NutritionLog(
                user_id=user_id, date=log_date or date.today(),
                meal=meal, calories=calories, protein_g=protein,
                fat_g=fat, carbs_g=carbs, fiber_g=fiber,
                food_name=food_name
            )
            session.add(nl)
            session.commit()
            session.refresh(nl)
            return nl
        finally:
            session.close()

    @staticmethod
    def log_water(user_id: int, amount_ml: int, log_date: date = None) -> WaterLog:
        session = get_session()
        try:
            wl = WaterLog(user_id=user_id, date=log_date or date.today(), amount_ml=amount_ml)
            session.add(wl)
            session.commit()
            session.refresh(wl)
            return wl
        finally:
            session.close()

    @staticmethod
    def get_daily_protein_streak(user_id: int) -> int:
        session = get_session()
        try:
            user = session.query(User).get(user_id)
            if not user:
                return 0
            streak = 0
            check_date = date.today()
            while True:
                total = session.query(func.sum(NutritionLog.protein_g)).filter(
                    NutritionLog.user_id == user_id,
                    NutritionLog.date == check_date
                ).scalar() or 0
                if total >= user.target_protein_g:
                    streak += 1
                    check_date -= timedelta(days=1)
                else:
                    break
            return streak
        finally:
            session.close()

    @staticmethod
    def get_weekly_calories(user_id: int) -> List[dict]:
        session = get_session()
        try:
            results = []
            for i in range(7):
                d = date.today() - timedelta(days=6 - i)
                totals = NutritionService.get_daily_totals(user_id, d)
                results.append({"date": d, "calories": totals["calories"], "protein": totals["protein"]})
            return results
        finally:
            session.close()


class RecoveryService:
    @staticmethod
    def calculate_recovery_score(user_id: int) -> DailyRecovery:
        session = get_session()
        try:
            user = session.query(User).get(user_id)
            today = date.today()

            sleep = session.query(SleepLog).filter(
                SleepLog.user_id == user_id, SleepLog.date == today
            ).first()

            water = session.query(func.sum(WaterLog.amount_ml)).filter(
                WaterLog.user_id == user_id, WaterLog.date == today
            ).scalar() or 0

            nutrition = NutritionService.get_daily_totals(user_id, today)

            last_7_volume = WorkoutService.get_weekly_volume(user_id)
            last_7_workouts = WorkoutService.get_weekly_workouts_count(user_id)

            sleep_score = min(100, ((sleep.hours or 0) / 8) * 100) if sleep else 50
            water_score = min(100, (water / (user.target_water_ml or 3500)) * 100)
            protein_score = min(100, (nutrition["protein"] / (user.target_protein_g or 130)) * 100)
            calories_score = min(100, (nutrition["calories"] / (user.target_calories or 2700)) * 100)
            nutrition_score = (protein_score * 0.6 + calories_score * 0.4)

            fatigue = min(10, (last_7_workouts * 2) + (last_7_volume / 50000 * 3))
            recovery = (sleep_score * 0.35 + nutrition_score * 0.35 + water_score * 0.3)
            recovery = max(0, min(100, recovery - (fatigue * 5)))

            rec = DailyRecovery(
                user_id=user_id, date=today,
                fatigue_score=round(fatigue, 1),
                recovery_score=round(recovery, 1),
                sleep_score=round(sleep_score, 1),
                nutrition_score=round(nutrition_score, 1),
                volume_score=round(min(100, last_7_volume / 100000 * 100), 1)
            )

            if recovery >= 80:
                rec.recommendation = "You're fully recovered. Ready to push hard!"
            elif recovery >= 60:
                rec.recommendation = "Good recovery. Train as planned but listen to your body."
            elif recovery >= 40:
                rec.recommendation = "Moderate recovery. Consider lighter weights or extra rest."
            else:
                rec.recommendation = "Low recovery. Consider rest day or deload."

            existing = session.query(DailyRecovery).filter(
                DailyRecovery.user_id == user_id,
                DailyRecovery.date == today
            ).first()

            if existing:
                for k, v in rec.__dict__.items():
                    if k != "_sa_instance_state" and not k.startswith("_"):
                        setattr(existing, k, v)
                session.commit()
                session.refresh(existing)
                return existing
            else:
                session.add(rec)
                session.commit()
                session.refresh(rec)
                return rec
        finally:
            session.close()


class PRService:
    @staticmethod
    def check_and_update_prs(user_id: int, session_id: int):
        session = get_session()
        try:
            ws = session.query(WorkoutSession).get(session_id)
            if not ws:
                return []

            new_prs = []
            for we in ws.exercises:
                for es in we.sets:
                    if es.is_warmup:
                        continue

                    estimated_1rm = es.weight_kg * (1 + es.reps / 30) if es.reps > 0 else 0
                    volume = es.weight_kg * es.reps

                    existing_1rm = session.query(PersonalRecord).filter(
                        PersonalRecord.user_id == user_id,
                        PersonalRecord.exercise_id == we.exercise_id,
                        PersonalRecord.record_type == "weight_1rm"
                    ).order_by(PersonalRecord.value.desc()).first()

                    if estimated_1rm > (existing_1rm.value if existing_1rm else 0) and estimated_1rm > 0:
                        pr = PersonalRecord(
                            user_id=user_id, exercise_id=we.exercise_id,
                            record_type="weight_1rm", value=round(estimated_1rm, 1),
                            date=ws.date, set_id=es.id
                        )
                        session.add(pr)
                        new_prs.append(("Estimated 1RM", we.exercise.name, round(estimated_1rm, 1)))

                    existing_volume = session.query(PersonalRecord).filter(
                        PersonalRecord.user_id == user_id,
                        PersonalRecord.exercise_id == we.exercise_id,
                        PersonalRecord.record_type == "best_set"
                    ).order_by(PersonalRecord.value.desc()).first()

                    if volume > (existing_volume.value if existing_volume else 0) and volume > 0:
                        pr = PersonalRecord(
                            user_id=user_id, exercise_id=we.exercise_id,
                            record_type="best_set", value=round(volume, 1),
                            date=ws.date, set_id=es.id
                        )
                        session.add(pr)
                        new_prs.append(("Best Set", we.exercise.name, round(volume, 1)))

            session.commit()
            return new_prs
        finally:
            session.close()

    @staticmethod
    def get_all_prs(user_id: int) -> List[dict]:
        session = get_session()
        try:
            results = session.query(PersonalRecord, Exercise.name).join(
                Exercise, Exercise.id == PersonalRecord.exercise_id
            ).filter(
                PersonalRecord.user_id == user_id
            ).order_by(PersonalRecord.record_type, PersonalRecord.value.desc()).all()

            return [
                {
                    "exercise_name": name,
                    "record_type": pr.record_type,
                    "value": pr.value,
                    "date": pr.date,
                }
                for pr, name in results
            ]
        finally:
            session.close()

    @staticmethod
    def get_latest_pr(user_id: int) -> Optional[dict]:
        session = get_session()
        try:
            pr = session.query(PersonalRecord, Exercise.name).join(
                Exercise, Exercise.id == PersonalRecord.exercise_id
            ).filter(
                PersonalRecord.user_id == user_id
            ).order_by(PersonalRecord.date.desc()).first()
            if pr:
                return {
                    "exercise_name": pr[1],
                    "record_type": pr[0].record_type,
                    "value": pr[0].value,
                    "date": pr[0].date,
                }
            return None
        finally:
            session.close()


class AchievementService:
    @staticmethod
    def check_achievements(user_id: int) -> List[str]:
        session = get_session()
        try:
            new_achievements = []
            all_achievements = session.query(Achievement).all()
            earned_ids = {ua.achievement_id for ua in session.query(UserAchievement).filter(
                UserAchievement.user_id == user_id
            ).all()}

            total_workouts = WorkoutService.get_total_workouts(user_id)
            streak = WorkoutService.get_workout_streak(user_id)
            protein_streak = NutritionService.get_daily_protein_streak(user_id)
            user = session.query(User).get(user_id)

            for ach in all_achievements:
                if ach.id in earned_ids:
                    continue
                earned = False
                if ach.condition_type == "workouts" and total_workouts >= ach.condition_value:
                    earned = True
                elif ach.condition_type == "streak" and streak >= ach.condition_value:
                    earned = True
                elif ach.condition_type == "protein_streak" and protein_streak >= ach.condition_value:
                    earned = True
                elif ach.condition_type == "weight_100":
                    has_100 = session.query(PersonalRecord).filter(
                        PersonalRecord.user_id == user_id,
                        PersonalRecord.value >= 100
                    ).first()
                    if has_100:
                        earned = True
                elif ach.condition_type == "pr":
                    pr_count = session.query(PersonalRecord).filter(
                        PersonalRecord.user_id == user_id
                    ).count()
                    if pr_count >= ach.condition_value:
                        earned = True
                elif ach.condition_type == "weight_goal":
                    latest = WeightService.get_latest(user_id)
                    if latest and latest.weight_kg >= user.target_weight_kg:
                        earned = True

                if earned:
                    ua = UserAchievement(user_id=user_id, achievement_id=ach.id)
                    session.add(ua)
                    new_achievements.append(ach.name)

            session.commit()
            return new_achievements
        finally:
            session.close()

    @staticmethod
    def get_all_earned(user_id: int) -> List[dict]:
        session = get_session()
        try:
            results = session.query(Achievement, UserAchievement.unlocked_at).join(
                UserAchievement, UserAchievement.achievement_id == Achievement.id
            ).filter(
                UserAchievement.user_id == user_id
            ).all()
            return [
                {"name": a.name, "description": a.description, "icon": a.icon, "unlocked_at": ua}
                for a, ua in results
            ]
        finally:
            session.close()


class OverloadService:
    @staticmethod
    def decide(user_id: int, exercise_id: int) -> OverloadDecision:
        session = get_session()
        try:
            decision = OverloadDecision(user_id=user_id, exercise_id=exercise_id, date=date.today())

            history = WorkoutService.get_exercise_history(user_id, exercise_id, limit=3)
            prev = WorkoutService.get_previous_session_exercise(user_id, exercise_id)

            if not prev or not prev["sets"]:
                decision.decision = "start"
                decision.reason = "No history yet. Start with moderate weight."
                decision.suggested_weight_kg = 20
                decision.suggested_reps = 10
                decision.suggested_sets = 3
            else:
                all_reps = [s["reps"] for s in prev["sets"]]
                all_weights = [s["weight"] for s in prev["sets"]]
                avg_reps = sum(all_reps) / len(all_reps) if all_reps else 0
                avg_weight = sum(all_weights) / len(all_weights) if all_weights else 0
                top_set = max(prev["sets"], key=lambda s: s["weight"] * s["reps"])

                if len(history) >= 3:
                    recent_volumes = [h["volume"] for h in history[:3]]
                    if len(recent_volumes) >= 2:
                        if recent_volumes[0] < recent_volumes[1] * 0.9 and recent_volumes[1] < recent_volumes[2] * 0.9:
                            decision.decision = "deload"
                            decision.reason = "Volume declining. Consider deload."
                            decision.suggested_weight_kg = round(avg_weight * 0.7, 1)
                            decision.suggested_reps = int(avg_reps)
                            decision.suggested_sets = 3
                            session.add(decision)
                            session.commit()
                            session.refresh(decision)
                            return decision

                if avg_reps >= 12 and avg_reps <= 15:
                    decision.decision = "increase"
                    decision.reason = "Hit rep range. Increase weight."
                    decision.suggested_weight_kg = round(avg_weight + 2.5, 1)
                    decision.suggested_reps = max(6, int(avg_reps - 2))
                    decision.suggested_sets = len(prev["sets"])
                elif avg_reps >= 8 and avg_reps < 12:
                    decision.decision = "keep"
                    decision.reason = "Good rep range. Keep weight and push for more reps."
                    decision.suggested_weight_kg = round(avg_weight, 1)
                    decision.suggested_reps = int(avg_reps + 1)
                    decision.suggested_sets = len(prev["sets"])
                elif avg_reps >= 15:
                    decision.decision = "increase_big"
                    decision.reason = "Too many reps. Increase weight significantly."
                    decision.suggested_weight_kg = round(avg_weight + 5, 1)
                    decision.suggested_reps = max(6, int(avg_reps - 4))
                    decision.suggested_sets = len(prev["sets"])
                elif avg_reps < 6:
                    decision.decision = "decrease"
                    decision.reason = "Too heavy. Decrease weight."
                    decision.suggested_weight_kg = round(avg_weight - 2.5, 1)
                    decision.suggested_reps = int(avg_reps + 2)
                    decision.suggested_sets = len(prev["sets"])
                else:
                    decision.decision = "keep"
                    decision.reason = "Keep progressing."
                    decision.suggested_weight_kg = round(avg_weight, 1)
                    decision.suggested_reps = int(min(avg_reps + 1, 12))
                    decision.suggested_sets = len(prev["sets"])

            session.add(decision)
            session.commit()
            session.refresh(decision)
            return decision
        finally:
            session.close()


class MuscleHeatmapService:
    VOLUME_TARGETS = {
        "Chest": 12000, "Back": 14000, "Shoulders": 10000,
        "Biceps": 6000, "Triceps": 7000, "Forearms": 3000,
        "Abs": 4000, "Quads": 12000, "Hamstrings": 8000,
        "Glutes": 6000, "Calves": 4000, "Traps": 4000,
        "Lats": 8000, "Rear Delts": 3000, "Side Delts": 3000,
    }

    @staticmethod
    def get_heatmap_data(user_id: int, days: int = 30) -> dict:
        volumes = WorkoutService.get_muscle_volume(user_id, days)
        result = {}
        for muscle in MuscleGroup:
            name = muscle.value
            vol = volumes.get(name, 0)
            target = MuscleHeatmapService.VOLUME_TARGETS.get(name, 5000)
            if vol == 0:
                status = "untrained"
                pct = 0
            elif vol < target * 0.5:
                status = "undertrained"
                pct = int((vol / target) * 100)
            elif vol <= target * 1.3:
                status = "optimal"
                pct = int((vol / target) * 100)
            else:
                status = "overtrained"
                pct = int((vol / target) * 100)
            result[name] = {"volume": round(vol, 1), "target": target, "status": status, "percentage": pct}
        return result


class SleepService:
    @staticmethod
    def log_sleep(user_id: int, hours: float, quality: int = 3, log_date: date = None) -> SleepLog:
        session = get_session()
        try:
            sl = SleepLog(user_id=user_id, date=log_date or date.today(), hours=hours, quality=quality)
            session.add(sl)
            session.commit()
            session.refresh(sl)
            return sl
        finally:
            session.close()

    @staticmethod
    def get_recent(user_id: int, days: int = 7) -> List[SleepLog]:
        session = get_session()
        try:
            cutoff = date.today() - timedelta(days=days)
            return session.query(SleepLog).filter(
                SleepLog.user_id == user_id,
                SleepLog.date >= cutoff
            ).order_by(SleepLog.date).all()
        finally:
            session.close()


class MeasurementService:
    @staticmethod
    def log_measurements(user_id: int, **kwargs) -> Measurement:
        session = get_session()
        try:
            m = Measurement(user_id=user_id, date=kwargs.pop("log_date", date.today()), **kwargs)
            session.add(m)
            session.commit()
            session.refresh(m)
            return m
        finally:
            session.close()

    @staticmethod
    def get_latest(user_id: int) -> Optional[Measurement]:
        session = get_session()
        try:
            return session.query(Measurement).filter(
                Measurement.user_id == user_id
            ).order_by(Measurement.date.desc()).first()
        finally:
            session.close()

    @staticmethod
    def get_history(user_id: int, limit: int = 10) -> List[Measurement]:
        session = get_session()
        try:
            return session.query(Measurement).filter(
                Measurement.user_id == user_id
            ).order_by(Measurement.date.desc()).limit(limit).all()
        finally:
            session.close()
