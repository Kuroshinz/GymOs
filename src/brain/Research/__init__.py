from typing import Optional


class Research:
    _instance: Optional["Research"] = None

    def __new__(cls) -> "Research":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def search_exercises(self, query: str) -> list[dict]: ...
    async def get_scientific_papers(self, topic: str) -> list[dict]: ...
    async def get_training_tips(self, muscle_group: str) -> list[str]: ...
