from datetime import date, timedelta
from typing import Optional
from src.services import (
    UserService, WeightService, WorkoutService, NutritionService,
    RecoveryService, PRService, OverloadService, MuscleHeatmapService,
    SleepService
)


class AICoach:
    @staticmethod
    def get_daily_recommendation(user_id: int) -> str:
        user = UserService.get_or_create_user()
        recovery = RecoveryService.calculate_recovery_score(user_id)
        today_workout = WorkoutService.get_today_workout(user_id)
        workout_count = WorkoutService.get_weekly_workouts_count(user_id)
        streak = WorkoutService.get_workout_streak(user_id)
        latest_weight = WeightService.get_latest(user_id)
        nutrition = NutritionService.get_daily_totals(user_id)

        parts = []

        if streak > 0:
            parts.append(f"🔥 {streak}-day streak! ")

        if latest_weight:
            diff = round(latest_weight.weight_kg - 63.4, 1)
            if diff > 0:
                parts.append(f"📈 +{diff}kg from start. ")
            else:
                parts.append(f"📉 {diff}kg from start. ")

        if recovery.recovery_score < 40:
            parts.append("⚠️ Recovery is low. ")
            if today_workout and not today_workout.is_completed:
                parts.append("Consider taking a rest day or doing a light session. ")
        elif recovery.recovery_score > 80:
            parts.append("⚡ Great recovery! Push hard today. ")
        else:
            parts.append("✅ Good to train. ")

        if nutrition["protein"] < user.target_protein_g * 0.5 and nutrition["calories"] > 0:
            parts.append(f"🥩 Only {nutrition['protein']}g protein so far. Need {user.target_protein_g}g. ")
        elif nutrition["protein"] >= user.target_protein_g:
            parts.append(f"🥩 Protein goal: {nutrition['protein']}g ✓ ")

        if workout_count < user.workout_days_per_week:
            remaining = user.workout_days_per_week - workout_count
            parts.append(f"📅 {remaining} workout(s) remaining this week. ")

        if today_workout and not today_workout.is_completed:
            parts.append(f"💪 Today: {today_workout.name or today_workout.split_type} ")

        return "".join(parts) if parts else "Keep showing up. Consistency is everything. 💪"

    @staticmethod
    def get_workout_recommendation(user_id: int, exercise_id: int) -> str:
        decision = OverloadService.decide(user_id, exercise_id)
        prev = WorkoutService.get_previous_session_exercise(user_id, exercise_id)

        if decision.decision == "deload":
            return f"⚠️ Deload advised: Volume is dropping. Use {decision.suggested_weight_kg}kg × {decision.suggested_reps} reps. Focus on perfect form."
        elif decision.decision == "increase" or decision.decision == "increase_big":
            return f"📈 Increase to {decision.suggested_weight_kg}kg × {decision.suggested_reps} reps. Previous session: {prev['total_volume']}kg volume." if prev else f"Start with {decision.suggested_weight_kg}kg."
        elif decision.decision == "decrease":
            return f"⬇️ Lower to {decision.suggested_weight_kg}kg × {decision.suggested_reps} reps. Focus on controlled reps."
        else:
            if prev:
                top_set = max(prev["sets"], key=lambda s: s["weight"] * s["reps"])
                return f"✅ Keep {top_set['weight']}kg. Aim for {top_set['reps'] + 1} reps on your top set. Last: {prev['total_volume']}kg volume."
            return "Start with a moderate weight and focus on form."

    @staticmethod
    def get_nutrition_recommendation(user_id: int) -> str:
        user = UserService.get_or_create_user()
        nutrition = NutritionService.get_daily_totals(user_id)
        remaining_protein = max(0, user.target_protein_g - nutrition["protein"])
        remaining_calories = max(0, user.target_calories - nutrition["calories"])
        remaining_water = max(0, (user.target_water_ml or 3500) - nutrition["water_ml"])

        if nutrition["calories"] == 0:
            return "📝 No meals logged today. Remember: 2700 kcal with 130g protein for lean bulk."

        parts = []
        if remaining_calories > 0:
            parts.append(f"{remaining_calories} kcal remaining. ")
        if remaining_protein > 0:
            parts.append(f"{remaining_protein}g protein remaining. ")
        if remaining_water > 0:
            parts.append(f"Drink {int(remaining_water)}ml more water. ")

        if nutrition["protein"] >= user.target_protein_g * 0.9:
            parts.append("Protein goal met! ✓")

        return "".join(parts) if parts else "All goals met for today! Great work. ✓"

    @staticmethod
    def get_weekly_summary(user_id: int) -> str:
        user = UserService.get_or_create_user()
        workouts = WorkoutService.get_weekly_workouts_count(user_id)
        volume = WorkoutService.get_weekly_volume(user_id)
        streak = WorkoutService.get_workout_streak(user_id)
        weight = WeightService.get_latest(user_id)
        nutrition_avg = NutritionService.get_weekly_average(user_id)

        lines = [f"📊 Weekly Summary (last 7 days)", ""]
        lines.append(f"🏋️ Workouts: {workouts}/{user.workout_days_per_week}")
        lines.append(f"📦 Volume: {int(volume):,} kg")
        lines.append(f"🔥 Streak: {streak} days")

        if weight:
            lines.append(f"⚖️ Weight: {weight.weight_kg} kg")

        lines.append(f"🥩 Avg Protein: {nutrition_avg['protein']}g / {user.target_protein_g}g")
        lines.append(f"🔥 Avg Calories: {nutrition_avg['calories']} / {user.target_calories}")

        calories_pct = int((nutrition_avg["calories"] / user.target_calories) * 100) if user.target_calories else 0
        protein_pct = int((nutrition_avg["protein"] / user.target_protein_g) * 100) if user.target_protein_g else 0

        lines.append(f"📈 Calorie adherence: {calories_pct}%")
        lines.append(f"📈 Protein adherence: {protein_pct}%")

        recovery = RecoveryService.calculate_recovery_score(user_id)
        lines.append(f"🔄 Recovery: {int(recovery.recovery_score)}%")

        if protein_pct < 70:
            lines.append("💡 Focus on hitting protein targets next week.")
        if workouts < user.workout_days_per_week:
            lines.append("💡 Try to get all scheduled workouts in next week.")

        return "\n".join(lines)

    @staticmethod
    def get_monthly_summary(user_id: int) -> str:
        user = UserService.get_or_create_user()
        total_workouts = WorkoutService.get_total_workouts(user_id)
        monthly_workouts = WorkoutService.get_weekly_workouts_count(user_id) * 4
        monthly_volume = WorkoutService.get_monthly_volume(user_id)
        latest_weight = WeightService.get_latest(user_id)
        start_weight = 63.4
        prs = PRService.get_all_prs(user_id)

        lines = [f"📊 Monthly Summary", ""]
        lines.append(f"🏋️ Total Workouts: {total_workouts}")
        lines.append(f"📦 Monthly Volume: {int(monthly_volume):,} kg")

        if latest_weight:
            change = round(latest_weight.weight_kg - start_weight, 1)
            lines.append(f"⚖️ Weight: {latest_weight.weight_kg} kg ({'+' if change > 0 else ''}{change} kg from start)")
            eta_days, eta_date = WeightService.get_eta_to_goal(user_id, latest_weight.weight_kg)
            if eta_days > 0:
                lines.append(f"🎯 ETA to {user.target_weight_kg}kg: {eta_date}")

        lines.append(f"🏆 Personal Records: {len(prs)}")

        heatmap = MuscleHeatmapService.get_heatmap_data(user_id)
        undertrained = [m for m, d in heatmap.items() if d["status"] == "undertrained"]
        if undertrained:
            lines.append(f"💡 Focus on: {', '.join(undertrained[:3])}")

        return "\n".join(lines)

    @staticmethod
    def get_plateau_detection(user_id: int, exercise_id: int) -> Optional[str]:
        history = WorkoutService.get_exercise_history(user_id, exercise_id, limit=5)
        if len(history) < 3:
            return None

        volumes = [h["volume"] for h in history]
        if all(volumes[i] <= volumes[i + 1] * 1.05 and volumes[i] >= volumes[i + 1] * 0.95 for i in range(len(volumes) - 1)):
            return "Plateau detected! Try: (1) Deload week (2) Change rep scheme (3) Add volume"
        return None

    @staticmethod
    def get_motivation() -> str:
        import random
        quotes = [
            "The only bad workout is the one that didn't happen.",
            "Strength does not come from the body. It comes from the will.",
            "Your body can stand almost anything. It's your mind you have to convince.",
            "The pain you feel today will be the strength you feel tomorrow.",
            "Don't stop when you're tired. Stop when you're done.",
            "It never gets easier. You just get stronger.",
            "Success starts with self-discipline.",
            "Be stronger than your excuses.",
            "The best project you'll ever work on is you.",
            "Small progress is still progress.",
        ]
        return random.choice(quotes)

    @staticmethod
    def get_weak_muscle_detection(user_id: int) -> list:
        heatmap = MuscleHeatmapService.get_heatmap_data(user_id)
        weak = []
        for muscle, data in sorted(heatmap.items(), key=lambda x: x[1]["percentage"]):
            if data["status"] in ("untrained", "undertrained") and data["target"] > 3000:
                weak.append({"muscle": muscle, "volume": data["volume"], "target": data["target"], "pct": data["percentage"]})
        return weak[:5]
