from typing import Optional


class Planner:
    _instance: Optional["Planner"] = None

    def __new__(cls) -> "Planner":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def create_workout_plan(self, goals: dict) -> dict: ...
    async def create_nutrition_plan(self, goals: dict) -> dict: ...
    async def adjust_plan(self, plan_id: str, feedback: dict) -> dict: ...
