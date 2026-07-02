from __future__ import annotations

from typing import Optional


class Prediction:
    def __init__(self, value: float, confidence: float, label: str) -> None:
        self.value = value
        self.confidence = confidence
        self.label = label


class AIEngine:
    _instance: Optional["AIEngine"] = None

    def __new__(cls) -> "AIEngine":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._models: dict[str, Prediction] = {}
        return cls._instance

    async def predict(self, model: str, features: dict) -> Prediction:
        ...
        return Prediction(value=0.0, confidence=0.0, label="unknown")

    async def train(self, model: str, data: list[dict]) -> None: ...
