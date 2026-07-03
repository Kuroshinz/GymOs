"""Knowledge module publisher — publishes knowledge update events."""

from shared.events.domain_events import ExerciseKnowledgeUpdated
from shared.events.publisher import Publisher


class KnowledgePublisher(Publisher):
    """Publishes events from the knowledge platform."""

    def publish_exercise_updated(
        self,
        exercise_id: str,
        exercise_name: str = "",
        version: str = "",
        changed_fields: list[str] | None = None,
    ) -> ExerciseKnowledgeUpdated:
        return self.publish(ExerciseKnowledgeUpdated(
            exercise_id=exercise_id,
            exercise_name=exercise_name,
            version=version,
            changed_fields=changed_fields or [],
        ))
