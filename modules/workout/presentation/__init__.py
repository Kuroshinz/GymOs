from modules.workout.application import WorkoutService


class WorkoutController:
    def __init__(self, workout_service: WorkoutService) -> None:
        self._workout_service = workout_service

    async def start_workout(self, name: str):
        return await self._workout_service.create_workout(name)

    async def finish_workout(self, workout_id: str):
        return await self._workout_service.complete_workout(workout_id)

    async def get_workout(self, workout_id: str):
        return await self._workout_service.get_workout(workout_id)

    async def list_workouts(self):
        return await self._workout_service.list_workouts()
