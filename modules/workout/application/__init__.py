from datetime import datetime
from typing import Optional

from core.event_bus import EventBus
from modules.workout.domain import Workout


class WorkoutService:
    def __init__(self, repository, event_bus: EventBus) -> None:
        self._repository = repository
        self._event_bus = event_bus

    async def create_workout(self, name: str) -> Workout:
        workout = Workout(name=name, started_at=datetime.now())
        saved = await self._repository.save(workout)
        await self._event_bus.emit("workout.created", {"workout_id": saved.id})
        return saved

    async def complete_workout(self, workout_id: str) -> Workout:
        workout = await self._repository.get(workout_id)
        if not workout:
            raise ValueError(f"Workout {workout_id} not found")
        workout.completed_at = datetime.now()
        await self._repository.update(workout)
        await self._event_bus.emit("workout.completed", {
            "workout_id": workout.id,
            "duration": workout.duration_minutes,
            "volume": workout.total_volume,
        })
        return workout

    async def get_workout(self, workout_id: str) -> Optional[Workout]:
        return await self._repository.get(workout_id)

    async def list_workouts(self, limit: int = 20, offset: int = 0) -> list[Workout]:
        return await self._repository.list(limit=limit, offset=offset)
