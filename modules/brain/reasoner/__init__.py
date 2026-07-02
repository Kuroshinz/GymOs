from typing import Optional


class Reasoner:
    _instance: Optional["Reasoner"] = None

    def __new__(cls) -> "Reasoner":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def analyze_progress(self, user_data: dict) -> dict: ...
    async def detect_plateau(self, history: list[dict]) -> bool: ...
    async def suggest_adjustments(self, analysis: dict) -> list[str]: ...
