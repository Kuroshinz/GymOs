from typing import Optional


class Prediction:
    _instance: Optional["Prediction"] = None

    def __new__(cls) -> "Prediction":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def predict_one_rm(self, exercise_history: list[dict]) -> float: ...
    async def predict_progress(self, user_profile: dict) -> dict: ...
    async def predict_recovery(self, workload: dict) -> dict: ...
