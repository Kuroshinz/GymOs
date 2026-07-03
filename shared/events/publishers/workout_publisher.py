"""Workout module publisher — publishes workout lifecycle events."""

from datetime import datetime

from shared.events.domain_events import (
    BodyWeightUpdated,
    ExerciseCompleted,
    SetCompleted,
    WorkoutCompleted,
    WorkoutStarted,
)
from shared.events.publisher import Publisher


class WorkoutPublisher(Publisher):
    """Publishes events from the workout module."""

    def publish_workout_started(
        self,
        workout_id: str,
        program_name: str = "",
        day_name: str = "",
    ) -> WorkoutStarted:
        return self.publish(WorkoutStarted(
            workout_id=workout_id,
            program_name=program_name,
            day_name=day_name,
            started_at=datetime.utcnow(),
        ))

    def publish_workout_completed(
        self,
        workout_id: str,
        program_name: str = "",
        day_name: str = "",
        duration_minutes: float = 0.0,
        total_volume_kg: float = 0.0,
        exercise_count: int = 0,
        total_sets: int = 0,
    ) -> WorkoutCompleted:
        return self.publish(WorkoutCompleted(
            workout_id=workout_id,
            program_name=program_name,
            day_name=day_name,
            duration_minutes=duration_minutes,
            total_volume_kg=total_volume_kg,
            exercise_count=exercise_count,
            total_sets=total_sets,
        ))

    def publish_exercise_completed(
        self,
        workout_id: str,
        exercise_id: str,
        exercise_name: str = "",
        sets_completed: int = 0,
        total_reps: int = 0,
        total_volume_kg: float = 0.0,
    ) -> ExerciseCompleted:
        return self.publish(ExerciseCompleted(
            workout_id=workout_id,
            exercise_id=exercise_id,
            exercise_name=exercise_name,
            sets_completed=sets_completed,
            total_reps=total_reps,
            total_volume_kg=total_volume_kg,
        ))

    def publish_set_completed(
        self,
        workout_id: str,
        exercise_id: str,
        set_number: int = 0,
        reps: int = 0,
        weight_kg: float = 0.0,
        rir: float | None = None,
        rpe: float | None = None,
    ) -> SetCompleted:
        return self.publish(SetCompleted(
            workout_id=workout_id,
            exercise_id=exercise_id,
            set_number=set_number,
            reps=reps,
            weight_kg=weight_kg,
            rir=rir,
            rpe=rpe,
        ))

    def publish_body_weight_updated(
        self,
        weight_kg: float,
        date: str = "",
        change_from_last: float | None = None,
    ) -> BodyWeightUpdated:
        return self.publish(BodyWeightUpdated(
            weight_kg=weight_kg,
            date=date,
            change_from_last=change_from_last,
        ))
