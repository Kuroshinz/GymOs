"""GymOS Shared Library — cross-cutting types, events, interfaces, and domain models.

All modules may import from shared. Shared must not import from any module.
"""

from shared.events.domain_events import (
    DOMAIN_EVENT_REGISTRY,
    BodyWeightUpdated,
    DomainEvent,
    ExerciseCompleted,
    ExerciseKnowledgeUpdated,
    MacroTargetChanged,
    MealLogged,
    NutritionUpdated,
    PersonalRecordUnlocked,
    ProgramActivated,
    ProgramImported,
    RecommendationsUpdated,
    RecoveryScoreUpdated,
    SetCompleted,
    WorkoutCompleted,
    WorkoutStarted,
    event_from_dict,
)
from shared.events.event_bus import EventBus, get_event_bus
from shared.interfaces import (
    IDataProvider,
    IGoalProvider,
    IKnowledgeRepository,
    INutritionProvider,
    IRecommendationEngine,
    IRecoveryProvider,
    ITrainingProvider,
)
from shared.knowledge_loader import KnowledgeLoader

__all__ = [
    # Domain Events
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
    "NutritionUpdated",
    "MacroTargetChanged",
    "ExerciseKnowledgeUpdated",
    "RecommendationsUpdated",
    "DOMAIN_EVENT_REGISTRY",
    "event_from_dict",
    # Event Bus
    "EventBus",
    "get_event_bus",
    # Interfaces
    "IDataProvider",
    "ITrainingProvider",
    "INutritionProvider",
    "IRecoveryProvider",
    "IGoalProvider",
    "IKnowledgeRepository",
    "IRecommendationEngine",
    # Knowledge
    "KnowledgeLoader",
]
