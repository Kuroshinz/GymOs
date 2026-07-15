from pydantic import BaseModel
from typing import List, Optional

class WorkoutLogPayload(BaseModel):
    exercise_name: str
    weight_kg: float
    reps: int
    rir: int

class SetLogPayload(BaseModel):
    set_number: int
    weight: float
    reps: int
    rir: int
    is_completed: bool

class ExerciseLogPayload(BaseModel):
    exercise_id: str
    exercise_name: str
    sets: List[SetLogPayload]

class WorkoutSessionLogPayload(BaseModel):
    id: str
    program_id: str
    start_time: str
    end_time: Optional[str] = None
    exercises: List[ExerciseLogPayload]

class NutritionLogPayload(BaseModel):
    name: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
