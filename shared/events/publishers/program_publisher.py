"""Program module publisher — publishes program lifecycle events."""

from shared.events.domain_events import ProgramActivated, ProgramImported
from shared.events.publisher import Publisher


class ProgramPublisher(Publisher):
    """Publishes events from the workout_program module."""

    def publish_program_imported(
        self,
        program_name: str,
        version: str = "",
        source_file: str = "",
        day_count: int = 0,
        exercise_count: int = 0,
    ) -> ProgramImported:
        return self.publish(ProgramImported(
            program_name=program_name,
            version=version,
            source_file=source_file,
            day_count=day_count,
            exercise_count=exercise_count,
        ))

    def publish_program_activated(
        self,
        program_name: str,
        version: str = "",
        previous_program: str = "",
    ) -> ProgramActivated:
        return self.publish(ProgramActivated(
            program_name=program_name,
            version=version,
            previous_program=previous_program,
        ))
