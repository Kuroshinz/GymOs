from abc import ABC, abstractmethod
from typing import Optional

from src.Workout.domain import Workout


class WorkoutRepository(ABC):
    @abstractmethod
    async def save(self, workout: Workout) -> Workout: ...

    @abstractmethod
    async def get(self, workout_id: str) -> Optional[Workout]: ...

    @abstractmethod
    async def update(self, workout: Workout) -> Workout: ...

    @abstractmethod
    async def delete(self, workout_id: str) -> None: ...

    @abstractmethod
    async def list(self, limit: int = 20, offset: int = 0) -> list[Workout]: ...
