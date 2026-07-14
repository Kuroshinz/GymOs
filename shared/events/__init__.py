from typing import TypeVar

from shared.events.dispatcher import discover_subscribers, register_subscribers
from shared.events.domain_events import (
    DOMAIN_EVENT_REGISTRY,
    BodyWeightUpdated,
    ExerciseCompleted,
    ExerciseKnowledgeUpdated,
    MealLogged,
    PersonalRecordUnlocked,
    ProgramActivated,
    ProgramImported,
    RecoveryScoreUpdated,
    SetCompleted,
    WorkoutCompleted,
    WorkoutStarted,
    event_from_dict,
)
from shared.events.event import DomainEvent
from shared.events.event_bus import EventBus, get_event_bus
from shared.events.publisher import Publisher
from shared.events.store import EventStore
from shared.events.subscriber import Subscriber

_E = TypeVar("_E", bound=DomainEvent)


def emit(event: _E) -> _E:
    """Emit a domain event through the global event bus."""
    get_event_bus().publish(event)
    return event


__all__ = [
    "DomainEvent",
    "WorkoutStarted",
    "WorkoutCompleted",
    "ExerciseCompleted",
    "SetCompleted",
    "ProgramImported",
    "ProgramActivated",
    "BodyWeightUpdated",
    "PersonalRecordUnlocked",
    "RecoveryScoreUpdated",
    "MealLogged",
    "ExerciseKnowledgeUpdated",
    "DOMAIN_EVENT_REGISTRY",
    "event_from_dict",
    "EventBus",
    "get_event_bus",
    "Publisher",
    "Subscriber",
    "discover_subscribers",
    "register_subscribers",
    "EventStore",
]
