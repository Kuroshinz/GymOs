from sqlalchemy import Column, Integer, Float, String, Text, DateTime, Date, Boolean, ForeignKey, JSON, Time
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, date
import enum

Base = declarative_base()


class WorkoutSplit(enum.Enum):
    PPL_UL = "PPL-UL"
    PUSH_PULL_LEGS = "Push-Pull-Legs"
    UPPER_LOWER = "Upper-Lower"
    FULL_BODY = "Full Body"
    BRO_SPLIT = "Bro Split"
    CUSTOM = "Custom"


class Difficulty(enum.Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class MuscleGroup(enum.Enum):
    CHEST = "Chest"
    BACK = "Back"
    SHOULDERS = "Shoulders"
    BICEPS = "Biceps"
    TRICEPS = "Triceps"
    FOREARMS = "Forearms"
    ABS = "Abs"
    QUADS = "Quads"
    HAMSTRINGS = "Hamstrings"
    GLUTES = "Glutes"
    CALVES = "Calves"
    TRAPS = "Traps"
    LATS = "Lats"
    REAR_DELTS = "Rear Delts"
    SIDE_DELTS = "Side Delts"


class Equipment(enum.Enum):
    BARBELL = "Barbell"
    DUMBBELL = "Dumbbell"
    CABLE = "Cable"
    MACHINE = "Machine"
    BODYWEIGHT = "Bodyweight"
    KETTLEBELL = "Kettlebell"
    BAND = "Band"
    SMITH_MACHINE = "Smith Machine"
    EZ_BAR = "EZ Bar"
    TRX = "TRX"


class Grip(enum.Enum):
    OVERHAND = "Overhand"
    UNDERHAND = "Underhand"
    NEUTRAL = "Neutral"
    MIXED = "Mixed"
    HOOK = "Hook"
    FALSE = "False"
    WIDE = "Wide"
    CLOSE = "Close"
    REVERSE = "Reverse"


class Goal(enum.Enum):
    LEAN_BULK = "Lean Bulk"
    BULK = "Bulk"
    CUT = "Cut"
    MAINTENANCE = "Maintenance"
    RECOMP = "Recomp"


# ---------- USER ----------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), default="Athlete")
    age = Column(Integer, default=16)
    height_cm = Column(Float, default=178.0)
    target_weight_kg = Column(Float, default=72.5)
    goal = Column(String(50), default=Goal.LEAN_BULK.value)
    workout_split = Column(String(50), default=WorkoutSplit.PPL_UL.value)
    workout_days_per_week = Column(Integer, default=5)
    target_calories = Column(Integer, default=2700)
    target_protein_g = Column(Integer, default=130)
    target_fat_g = Column(Integer, default=75)
    target_carbs_g = Column(Integer, default=340)
    target_fiber_g = Column(Integer, default=30)
    target_water_ml = Column(Integer, default=3500)
    theme = Column(String(50), default="dark")
    language = Column(String(10), default="en")
    units = Column(String(10), default="metric")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    weights = relationship("WeightEntry", back_populates="user", cascade="all, delete-orphan")
    workouts = relationship("WorkoutSession", back_populates="user", cascade="all, delete-orphan")
    nutrition_logs = relationship("NutritionLog", back_populates="user", cascade="all, delete-orphan")
    measurements = relationship("Measurement", back_populates="user", cascade="all, delete-orphan")
    physique_photos = relationship("PhysiquePhoto", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    water_logs = relationship("WaterLog", back_populates="user", cascade="all, delete-orphan")
    sleep_logs = relationship("SleepLog", back_populates="user", cascade="all, delete-orphan")


# ---------- WEIGHT ----------
class WeightEntry(Base):
    __tablename__ = "weight_entries"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, default=date.today, nullable=False)
    weight_kg = Column(Float, nullable=False)
    notes = Column(Text, default="")

    user = relationship("User", back_populates="weights")


# ---------- WORKOUT ----------
class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True, nullable=False)
    primary_muscle = Column(String(50), nullable=False)
    secondary_muscles = Column(JSON, default=list)
    equipment = Column(String(50), default=Equipment.BARBELL.value)
    grip = Column(String(50), default=Grip.OVERHAND.value)
    difficulty = Column(String(20), default=Difficulty.INTERMEDIATE.value)
    execution = Column(Text, default="")
    common_mistakes = Column(Text, default="")
    recommended_tempo = Column(String(20), default="2-1-2")
    recommended_rest_seconds = Column(Integer, default=90)
    video_link = Column(String(500), default="")
    gif_path = Column(String(500), default="")
    alternative_exercises = Column(JSON, default=list)
    is_custom = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

    workout_exercises = relationship("WorkoutExercise", back_populates="exercise")
    personal_records = relationship("PersonalRecord", back_populates="exercise", cascade="all, delete-orphan")


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, default=date.today, nullable=False)
    split_type = Column(String(50), nullable=False)
    name = Column(String(200), default="")  # e.g., "Push A", "Pull B"
    duration_minutes = Column(Integer, default=0)
    notes = Column(Text, default="")
    is_completed = Column(Boolean, default=False)
    is_deload = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="workouts")
    exercises = relationship("WorkoutExercise", back_populates="session", cascade="all, delete-orphan")


class WorkoutExercise(Base):
    __tablename__ = "workout_exercises"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("workout_sessions.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    order = Column(Integer, default=0)
    notes = Column(Text, default="")

    session = relationship("WorkoutSession", back_populates="exercises")
    exercise = relationship("Exercise", back_populates="workout_exercises")
    sets = relationship("ExerciseSet", back_populates="workout_exercise", cascade="all, delete-orphan")


class ExerciseSet(Base):
    __tablename__ = "exercise_sets"

    id = Column(Integer, primary_key=True)
    workout_exercise_id = Column(Integer, ForeignKey("workout_exercises.id"), nullable=False)
    set_number = Column(Integer, nullable=False)
    weight_kg = Column(Float, default=0)
    reps = Column(Integer, default=0)
    rpe = Column(Float, default=0)
    tempo = Column(String(20), default="")
    is_warmup = Column(Boolean, default=False)
    is_completed = Column(Boolean, default=True)

    workout_exercise = relationship("WorkoutExercise", back_populates="sets")


class PersonalRecord(Base):
    __tablename__ = "personal_records"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    record_type = Column(String(20), nullable=False)  # weight_1rm, weight_volume, best_reps, best_set
    value = Column(Float, nullable=False)
    date = Column(Date, default=date.today)
    set_id = Column(Integer, ForeignKey("exercise_sets.id"), nullable=True)

    user = relationship("User")
    exercise = relationship("Exercise", back_populates="personal_records")


# ---------- NUTRITION ----------
class NutritionLog(Base):
    __tablename__ = "nutrition_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, default=date.today, nullable=False)
    meal = Column(String(50), default="")  # breakfast, lunch, dinner, snack
    calories = Column(Integer, default=0)
    protein_g = Column(Float, default=0)
    fat_g = Column(Float, default=0)
    carbs_g = Column(Float, default=0)
    fiber_g = Column(Float, default=0)
    food_name = Column(String(200), default="")
    source = Column(String(50), default="manual")  # manual, cronometer_csv
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="nutrition_logs")


class WaterLog(Base):
    __tablename__ = "water_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, default=date.today, nullable=False)
    amount_ml = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="water_logs")


class SleepLog(Base):
    __tablename__ = "sleep_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, default=date.today, nullable=False)
    hours = Column(Float, default=0)
    quality = Column(Integer, default=3)  # 1-5
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="sleep_logs")


# ---------- PHYSIQUE ----------
class Measurement(Base):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, default=date.today, nullable=False)
    chest_cm = Column(Float, default=0)
    waist_cm = Column(Float, default=0)
    shoulders_cm = Column(Float, default=0)
    left_arm_cm = Column(Float, default=0)
    right_arm_cm = Column(Float, default=0)
    left_thigh_cm = Column(Float, default=0)
    right_thigh_cm = Column(Float, default=0)
    left_calf_cm = Column(Float, default=0)
    right_calf_cm = Column(Float, default=0)
    body_fat_pct = Column(Float, default=0)

    user = relationship("User", back_populates="measurements")


class PhysiquePhoto(Base):
    __tablename__ = "physique_photos"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, default=date.today, nullable=False)
    angle = Column(String(20), nullable=False)  # front, side, back
    file_path = Column(String(500), nullable=False)

    user = relationship("User", back_populates="physique_photos")


# ---------- ACHIEVEMENTS ----------
class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True, nullable=False)
    description = Column(Text, default="")
    icon = Column(String(50), default="")
    condition_type = Column(String(50), nullable=False)
    condition_value = Column(Integer, default=0)


class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("achievements.id"), nullable=False)
    unlocked_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement")


# ---------- RECOVERY ----------
class DailyRecovery(Base):
    __tablename__ = "daily_recovery"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, default=date.today, nullable=False)
    fatigue_score = Column(Float, default=0)  # 0-10
    recovery_score = Column(Float, default=0)  # 0-100
    sleep_score = Column(Float, default=0)
    nutrition_score = Column(Float, default=0)
    volume_score = Column(Float, default=0)
    recommendation = Column(String(500), default="")

    user = relationship("User")


# ---------- PROGRESSIVE OVERLOAD ----------
class OverloadDecision(Base):
    __tablename__ = "overload_decisions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    date = Column(Date, default=date.today)
    decision = Column(String(50), nullable=False)  # increase, keep, decrease, deload, extra_volume, less_volume
    reason = Column(Text, default="")
    suggested_weight_kg = Column(Float, default=0)
    suggested_reps = Column(Integer, default=0)
    suggested_sets = Column(Integer, default=0)

    user = relationship("User")
    exercise = relationship("Exercise")


class WeekPlan(Base):
    __tablename__ = "week_plans"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    week_start = Column(Date, nullable=False)
    split_type = Column(String(50), nullable=False)
    days = Column(JSON, default=list)  # list of day plans
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User")
