"""Planning Engine domain events — published when planning actions occur."""

from __future__ import annotations

from dataclasses import dataclass

from shared.events.event import DomainEvent


@dataclass
class MacrocycleGenerated(DomainEvent):
    macrocycle_id: str = ""
    duration_weeks: int = 0
    mesocycle_count: int = 0
    total_sessions: int = 0
    source: str = "planning"


@dataclass
class MesocycleGenerated(DomainEvent):
    mesocycle_id: str = ""
    macrocycle_id: str = ""
    goal: str = ""
    focus: str = ""
    week_count: int = 0
    source: str = "planning"


@dataclass
class WeekPlanGenerated(DomainEvent):
    week_number: int = 0
    macrocycle_id: str = ""
    session_count: int = 0
    total_sets: int = 0
    is_deload: bool = False
    source: str = "planning"


@dataclass
class SessionPlanGenerated(DomainEvent):
    session_id: str = ""
    week_number: int = 0
    day_type: str = ""
    exercise_count: int = 0
    total_sets: int = 0
    estimated_duration: int = 0
    source: str = "planning"


@dataclass
class PlanActivated(DomainEvent):
    macrocycle_id: str = ""
    name: str = ""
    duration_weeks: int = 0
    source: str = "planning"


@dataclass
class PlanProgressed(DomainEvent):
    macrocycle_id: str = ""
    week_completed: int = 0
    sessions_completed: int = 0
    adherence_rate: float = 0.0
    completion_percent: float = 0.0
    source: str = "planning"


@dataclass
class PlanModified(DomainEvent):
    macrocycle_id: str = ""
    modification_type: str = ""
    description: str = ""
    source: str = "planning"


@dataclass
class PlanCompleted(DomainEvent):
    macrocycle_id: str = ""
    name: str = ""
    total_sessions_completed: int = 0
    adherence_rate: float = 0.0
    source: str = "planning"


@dataclass
class DeloadWeekGenerated(DomainEvent):
    macrocycle_id: str = ""
    week_number: int = 0
    reason: str = ""
    weeks_since_last_deload: int = 0
    source: str = "planning"


@dataclass
class VolumeAllocationAdjusted(DomainEvent):
    session_id: str = ""
    previous_sets: int = 0
    new_sets: int = 0
    reason: str = ""
    source: str = "planning"


PLANNING_EVENT_REGISTRY: dict[str, type[DomainEvent]] = {
    "MacrocycleGenerated": MacrocycleGenerated,
    "MesocycleGenerated": MesocycleGenerated,
    "WeekPlanGenerated": WeekPlanGenerated,
    "SessionPlanGenerated": SessionPlanGenerated,
    "PlanActivated": PlanActivated,
    "PlanProgressed": PlanProgressed,
    "PlanModified": PlanModified,
    "PlanCompleted": PlanCompleted,
    "DeloadWeekGenerated": DeloadWeekGenerated,
    "VolumeAllocationAdjusted": VolumeAllocationAdjusted,
}
