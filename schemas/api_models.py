from pydantic import BaseModel

class WorkoutLogPayload(BaseModel):
    exercise_name: str
    weight_kg: float
    reps: int
    rir: int
