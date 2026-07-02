from typing import Any, Optional


class Reasoner:
    _instance: Optional["Reasoner"] = None

    def __new__(cls) -> "Reasoner":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def analyze_progress(self, history: list[dict]) -> dict: ...
    async def detect_plateau(self, metrics: list[dict]) -> bool: ...
    async def suggest_adjustments(self, current_plan: dict, results: dict) -> dict: ...
