"""Optimization Knowledge Events — Domain events for the knowledge accumulation pipeline."""

from __future__ import annotations

from dataclasses import dataclass

from shared.events.event import DomainEvent


@dataclass
class ExperienceRecorded(DomainEvent):
    source: str = "optimization_knowledge"
    experience_id: str = ""
    plan_id: str = ""
    is_successful: bool = False
    overall_score: float = 0.0


@dataclass
class PatternMined(DomainEvent):
    source: str = "optimization_knowledge"
    pattern_id: str = ""
    pattern_type: str = ""
    pattern_label: str = ""
    success_rate: float = 0.0
    sample_size: int = 0


@dataclass
class StatisticsUpdated(DomainEvent):
    source: str = "optimization_knowledge"
    statistics_id: str = ""
    scope: str = ""
    total_experiences: int = 0
    success_rate: float = 0.0
    mean_score: float = 0.0


@dataclass
class InsightGenerated(DomainEvent):
    source: str = "optimization_knowledge"
    insight_id: str = ""
    category: str = ""
    title: str = ""
    confidence: float = 0.0


@dataclass
class RuleDerived(DomainEvent):
    source: str = "optimization_knowledge"
    rule_id: str = ""
    pattern_type: str = ""
    effect: str = ""
    confidence: float = 0.0
    sample_size: int = 0


@dataclass
class KnowledgeVersioned(DomainEvent):
    source: str = "optimization_knowledge"
    knowledge_id: str = ""
    version: str = ""
    parent_version: str = ""
    pattern_count: int = 0
    insight_count: int = 0
    rule_count: int = 0


OPTIMIZATION_KNOWLEDGE_EVENT_REGISTRY: dict[str, type[DomainEvent]] = {
    "ExperienceRecorded": ExperienceRecorded,
    "PatternMined": PatternMined,
    "StatisticsUpdated": StatisticsUpdated,
    "InsightGenerated": InsightGenerated,
    "RuleDerived": RuleDerived,
    "KnowledgeVersioned": KnowledgeVersioned,
}
