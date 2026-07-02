from typing import Optional


class Coach:
    _instance: Optional["Coach"] = None

    def __new__(cls) -> "Coach":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def analyze_form(self, video_data: bytes) -> dict: ...
    async def give_feedback(self, workout_data: dict) -> str: ...
    async def suggest_exercise(self, muscle_group: str) -> str: ...
