from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from src.models import Base, User, Achievement
from pathlib import Path
import json

DB_PATH = Path(__file__).parent.parent.parent / "database" / "gymos.db"

_engine = None
_SessionFactory = None


def get_engine():
    global _engine
    if _engine is None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        _engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
    return _engine


def get_session() -> Session:
    global _SessionFactory
    if _SessionFactory is None:
        _SessionFactory = scoped_session(sessionmaker(bind=get_engine()))
    return _SessionFactory()


def init_db():
    engine = get_engine()
    Base.metadata.create_all(engine)
    _seed_achievements()
    _seed_exercises()


def _seed_achievements():
    session = get_session()
    try:
        if session.query(Achievement).count() > 0:
            return
        achievements = [
            Achievement(name="First Workout", description="Complete your first workout", icon="🏋️", condition_type="workouts", condition_value=1),
            Achievement(name="10 Workouts", description="Complete 10 workouts", icon="💪", condition_type="workouts", condition_value=10),
            Achievement(name="50 Workouts", description="Complete 50 workouts", icon="🔥", condition_type="workouts", condition_value=50),
            Achievement(name="100 Workouts", description="Complete 100 workouts", icon="🏆", condition_type="workouts", condition_value=100),
            Achievement(name="7 Day Streak", description="Train 7 days in a row", icon="📅", condition_type="streak", condition_value=7),
            Achievement(name="30 Day Streak", description="Train 30 days in a row", icon="🌟", condition_type="streak", condition_value=30),
            Achievement(name="Protein Goal 7 Days", description="Hit protein goal for 7 days straight", icon="🥩", condition_type="protein_streak", condition_value=7),
            Achievement(name="Protein Goal 30 Days", description="Hit protein goal for 30 days straight", icon="🥇", condition_type="protein_streak", condition_value=30),
            Achievement(name="100kg Lift", description="Lift 100kg on any exercise", icon="💯", condition_type="weight_100", condition_value=100),
            Achievement(name="New PR", description="Set a new personal record", icon="📈", condition_type="pr", condition_value=1),
            Achievement(name="Weight Goal", description="Reach your target weight", icon="🎯", condition_type="weight_goal", condition_value=1),
            Achievement(name="Perfect Week", description="Complete all scheduled workouts in a week", icon="✨", condition_type="perfect_week", condition_value=1),
            Achievement(name="Dedicated Month", description="Train consistently for a month", icon="⭐", condition_type="month_consistent", condition_value=1),
            Achievement(name="Volume Master", description="Accumulate 100,000kg total volume", icon="📊", condition_type="total_volume", condition_value=100000),
            Achievement(name="Hydrated", description="Hit water goal for 30 days", icon="💧", condition_type="water_streak", condition_value=30),
        ]
        session.add_all(achievements)
        session.commit()
    finally:
        session.close()


def _seed_exercises():
    from src.models import Exercise
    session = get_session()
    try:
        if session.query(Exercise).count() > 0:
            return
        exercises = [
            Exercise(name="Bench Press", primary_muscle="Chest", secondary_muscles=["Shoulders", "Triceps"], equipment="Barbell", grip="Overhand", difficulty="Intermediate",
                     execution="Lie on flat bench, grip bar slightly wider than shoulder-width. Lower bar to mid-chest, press up explosively.",
                     common_mistakes="Bouncing bar off chest, flaring elbows too wide", recommended_tempo="2-1-2", recommended_rest_seconds=120,
                     alternative_exercises=["Dumbbell Bench Press", "Incline Bench Press", "Machine Chest Press"]),
            Exercise(name="Incline Bench Press", primary_muscle="Chest", secondary_muscles=["Shoulders", "Triceps"], equipment="Barbell", grip="Overhand", difficulty="Intermediate",
                     execution="Lie on incline bench at 30-45 degrees. Press bar from upper chest.", common_mistakes="Too steep incline, using too much weight",
                     recommended_tempo="2-1-2", recommended_rest_seconds=120, alternative_exercises=["Flat Bench Press", "Dumbbell Incline Press"]),
            Exercise(name="Dumbbell Bench Press", primary_muscle="Chest", secondary_muscles=["Shoulders", "Triceps"], equipment="Dumbbell", grip="Neutral", difficulty="Beginner",
                     execution="Lie on flat bench with dumbbells at chest height. Press up and squeeze at top.",
                     recommended_tempo="2-1-2", recommended_rest_seconds=90, alternative_exercises=["Barbell Bench Press", "Machine Chest Press"]),
            Exercise(name="Overhead Press", primary_muscle="Shoulders", secondary_muscles=["Triceps", "Chest"], equipment="Barbell", grip="Overhand", difficulty="Intermediate",
                     execution="Stand with bar at front shoulders. Press overhead. Keep core tight.", common_mistakes="Arching back too much",
                     recommended_tempo="2-1-2", recommended_rest_seconds=120, alternative_exercises=["Dumbbell Shoulder Press", "Machine Shoulder Press"]),
            Exercise(name="Dumbbell Shoulder Press", primary_muscle="Shoulders", secondary_muscles=["Triceps"], equipment="Dumbbell", grip="Neutral", difficulty="Beginner",
                     execution="Sit on bench with dumbbells at shoulder height. Press overhead.", recommended_tempo="2-1-2", recommended_rest_seconds=90,
                     alternative_exercises=["Barbell Overhead Press", "Arnold Press"]),
            Exercise(name="Barbell Row", primary_muscle="Back", secondary_muscles=["Biceps", "Rear Delts"], equipment="Barbell", grip="Overhand", difficulty="Intermediate",
                     execution="Hinge at hips, keep back flat. Row bar to lower chest.", common_mistakes="Rounding lower back, using momentum",
                     recommended_tempo="2-1-2", recommended_rest_seconds=120, alternative_exercises=["Dumbbell Row", "T-Bar Row", "Cable Row"]),
            Exercise(name="Pull Up", primary_muscle="Back", secondary_muscles=["Biceps", "Forearms"], equipment="Bodyweight", grip="Overhand", difficulty="Advanced",
                     execution="Hang from bar with wide grip. Pull chin over bar.", common_mistakes="Kipping too much, not full ROM",
                     recommended_tempo="2-1-2", recommended_rest_seconds=90, alternative_exercises=["Lat Pulldown", "Assisted Pull Up"]),
            Exercise(name="Lat Pulldown", primary_muscle="Back", secondary_muscles=["Biceps"], equipment="Cable", grip="Overhand", difficulty="Beginner",
                     execution="Sit at lat pulldown machine, grip wide. Pull bar to upper chest.", recommended_tempo="2-1-2", recommended_rest_seconds=90,
                     alternative_exercises=["Pull Up", "Dumbbell Row"]),
            Exercise(name="Squat", primary_muscle="Quads", secondary_muscles=["Glutes", "Hamstrings", "Core"], equipment="Barbell", grip="Overhand", difficulty="Advanced",
                     execution="Bar on upper back, squat to parallel or below. Keep chest up.", common_mistakes="Heels coming up, knees caving in",
                     recommended_tempo="3-1-2", recommended_rest_seconds=180, alternative_exercises=["Leg Press", "Goblet Squat", "Hack Squat"]),
            Exercise(name="Leg Press", primary_muscle="Quads", secondary_muscles=["Glutes", "Hamstrings"], equipment="Machine", grip="Neutral", difficulty="Beginner",
                     execution="Sit on leg press, place feet shoulder-width. Press weight.", recommended_tempo="2-1-2", recommended_rest_seconds=120,
                     alternative_exercises=["Squat", "Hack Squat", "Bulgarian Split Squat"]),
            Exercise(name="Romanian Deadlift", primary_muscle="Hamstrings", secondary_muscles=["Glutes", "Lower Back"], equipment="Barbell", grip="Overhand", difficulty="Intermediate",
                     execution="Hinge at hips, slide bar down legs. Feel hamstring stretch.", common_mistakes="Rounding back, not hinging enough",
                     recommended_tempo="3-1-2", recommended_rest_seconds=120, alternative_exercises=["Deadlift", "Leg Curl", "Good Morning"]),
            Exercise(name="Deadlift", primary_muscle="Back", secondary_muscles=["Glutes", "Hamstrings", "Traps"], equipment="Barbell", grip="Mixed", difficulty="Advanced",
                     execution="Bar over mid-foot, flat back, drive through heels.", common_mistakes="Rounding lower back, bar too far from shins",
                     recommended_tempo="1-1-2", recommended_rest_seconds=180, alternative_exercises=["Romanian Deadlift", "Trap Bar Deadlift", "Rack Pull"]),
            Exercise(name="Barbell Curl", primary_muscle="Biceps", secondary_muscles=["Forearms"], equipment="EZ Bar", grip="Underhand", difficulty="Beginner",
                     execution="Curl bar to shoulders, squeeze at top. Control descent.", recommended_tempo="2-0-2", recommended_rest_seconds=60,
                     alternative_exercises=["Dumbbell Curl", "Hammer Curl", "Cable Curl"]),
            Exercise(name="Dumbbell Curl", primary_muscle="Biceps", secondary_muscles=["Forearms"], equipment="Dumbbell", grip="Underhand", difficulty="Beginner",
                     execution="Curl dumbbells, palms facing up. Squeeze at top.", recommended_tempo="2-0-2", recommended_rest_seconds=60,
                     alternative_exercises=["Barbell Curl", "Hammer Curl", "Concentration Curl"]),
            Exercise(name="Tricep Pushdown", primary_muscle="Triceps", secondary_muscles=[], equipment="Cable", grip="Overhand", difficulty="Beginner",
                     execution="Push cable down, lock elbows at sides.", recommended_tempo="2-0-2", recommended_rest_seconds=60,
                     alternative_exercises=["Skull Crusher", "Close Grip Bench", "Overhead Tricep Extension"]),
            Exercise(name="Lateral Raise", primary_muscle="Shoulders", secondary_muscles=["Traps"], equipment="Dumbbell", grip="Neutral", difficulty="Beginner",
                     execution="Raise dumbbells to sides, slight bend in elbows. Don't go too heavy.", recommended_tempo="2-1-2", recommended_rest_seconds=60,
                     alternative_exercises=["Cable Lateral Raise", "Machine Lateral Raise"]),
            Exercise(name="Face Pull", primary_muscle="Shoulders", secondary_muscles=["Rear Delts", "Traps"], equipment="Cable", grip="Overhand", difficulty="Beginner",
                     execution="Pull cable rope to face, elbows high. Squeeze rear delts.", recommended_tempo="2-1-2", recommended_rest_seconds=60,
                     alternative_exercises=["Rear Delt Fly", "Reverse Pec Deck"]),
            Exercise(name="Leg Curl", primary_muscle="Hamstrings", secondary_muscles=["Calves"], equipment="Machine", grip="Neutral", difficulty="Beginner",
                     execution="Sit on leg curl machine, curl weight towards glutes.", recommended_tempo="2-1-2", recommended_rest_seconds=90,
                     alternative_exercises=["Romanian Deadlift", "Nordic Curl"]),
            Exercise(name="Leg Extension", primary_muscle="Quads", secondary_muscles=[], equipment="Machine", grip="Neutral", difficulty="Beginner",
                     execution="Extend legs on machine, squeeze quads at top.", recommended_tempo="2-1-2", recommended_rest_seconds=90,
                     alternative_exercises=["Squat", "Leg Press"]),
            Exercise(name="Calf Raise", primary_muscle="Calves", secondary_muscles=[], equipment="Machine", grip="Neutral", difficulty="Beginner",
                     execution="Stand on calf raise machine, push through balls of feet.", recommended_tempo="2-1-2", recommended_rest_seconds=60,
                     alternative_exercises=["Seated Calf Raise", "Donkey Calf Raise"]),
            Exercise(name="Cable Fly", primary_muscle="Chest", secondary_muscles=["Shoulders"], equipment="Cable", grip="Neutral", difficulty="Intermediate",
                     execution="Stand between cables, bring hands together in front of chest.", recommended_tempo="2-1-2", recommended_rest_seconds=60,
                     alternative_exercises=["Dumbbell Fly", "Pec Deck Fly"]),
            Exercise(name="Dumbbell Row", primary_muscle="Back", secondary_muscles=["Biceps"], equipment="Dumbbell", grip="Neutral", difficulty="Beginner",
                     execution="One knee on bench, row dumbbell to hip.", recommended_tempo="2-1-2", recommended_rest_seconds=90,
                     alternative_exercises=["Barbell Row", "Cable Row", "T-Bar Row"]),
            Exercise(name="Hack Squat", primary_muscle="Quads", secondary_muscles=["Glutes"], equipment="Machine", grip="Neutral", difficulty="Intermediate",
                     execution="Shoulders on pads, squat down to 90 degrees.", recommended_tempo="2-1-2", recommended_rest_seconds=120,
                     alternative_exercises=["Squat", "Leg Press"]),
            Exercise(name="Seated Cable Row", primary_muscle="Back", secondary_muscles=["Biceps"], equipment="Cable", grip="Neutral", difficulty="Beginner",
                     execution="Sit at cable row, pull handle to stomach. Squeeze back.", recommended_tempo="2-1-2", recommended_rest_seconds=90,
                     alternative_exercises=["Barbell Row", "Dumbbell Row"]),
            Exercise(name="Incline Dumbbell Curl", primary_muscle="Biceps", secondary_muscles=[], equipment="Dumbbell", grip="Underhand", difficulty="Intermediate",
                     execution="Sit on incline bench, curl dumbbells. Stretch biceps at bottom.", recommended_tempo="2-1-2", recommended_rest_seconds=60,
                     alternative_exercises=["Barbell Curl", "Concentration Curl"]),
            Exercise(name="Skull Crusher", primary_muscle="Triceps", secondary_muscles=[], equipment="EZ Bar", grip="Overhand", difficulty="Intermediate",
                     execution="Lie on flat bench, lower bar to forehead. Extend elbows.", recommended_tempo="2-1-2", recommended_rest_seconds=60,
                     alternative_exercises=["Tricep Pushdown", "Overhead Tricep Extension"]),
            Exercise(name="Dumbbell Fly", primary_muscle="Chest", secondary_muscles=["Shoulders"], equipment="Dumbbell", grip="Neutral", difficulty="Intermediate",
                     execution="Lie on flat bench, arms extended. Lower dumbbells to sides. Squeeze up.", recommended_tempo="3-1-2", recommended_rest_seconds=60,
                     alternative_exercises=["Cable Fly", "Pec Deck"]),
            Exercise(name="Arnold Press", primary_muscle="Shoulders", secondary_muscles=["Triceps", "Chest"], equipment="Dumbbell", grip="Neutral", difficulty="Intermediate",
                     execution="Start palms facing you, rotate as you press overhead.", recommended_tempo="2-1-2", recommended_rest_seconds=90,
                     alternative_exercises=["Dumbbell Shoulder Press", "Overhead Press"]),
            Exercise(name="T-Bar Row", primary_muscle="Back", secondary_muscles=["Biceps", "Rear Delts"], equipment="Machine", grip="Neutral", difficulty="Intermediate",
                     execution="Straddle T-bar, row weight to chest. Squeeze back.", recommended_tempo="2-1-2", recommended_rest_seconds=90,
                     alternative_exercises=["Barbell Row", "Seated Cable Row"]),
            Exercise(name="Bulgarian Split Squat", primary_muscle="Quads", secondary_muscles=["Glutes", "Hamstrings"], equipment="Dumbbell", grip="Neutral", difficulty="Intermediate",
                     execution="Back foot on bench, front foot forward. Squeeze down, press through front heel.", recommended_tempo="2-1-2", recommended_rest_seconds=90,
                     alternative_exercises=["Squat", "Leg Press", "Lunges"]),
        ]
        session.add_all(exercises)
        session.commit()
    finally:
        session.close()
