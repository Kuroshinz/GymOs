"""Optimization Knowledge Repository — Versioned, append-only, immutable knowledge store."""

from __future__ import annotations

from shared.optimization_knowledge.domain import (
    KnowledgeState,
    OptimizationExperience,
    OptimizationKnowledge,
)


class OptimizationKnowledgeRepository:
    """Versioned, append-only repository for optimization knowledge.

    Knowledge versions are immutable once written. New versions are created
    by extracting fresh knowledge from the accumulated experience base.
    """

    def __init__(self) -> None:
        self._experiences: dict[str, OptimizationExperience] = {}
        self._knowledge_versions: dict[str, OptimizationKnowledge] = {}
        self._current_version: str = ""

    def record_experience(self, experience: OptimizationExperience) -> None:
        self._experiences[experience.experience_id] = experience

    def get_experience(self, experience_id: str) -> OptimizationExperience | None:
        return self._experiences.get(experience_id)

    def list_experiences(self) -> list[OptimizationExperience]:
        return list(self._experiences.values())

    def delete_experience(self, experience_id: str) -> bool:
        if experience_id in self._experiences:
            del self._experiences[experience_id]
            return True
        return False

    def clear_experiences(self) -> None:
        self._experiences.clear()

    def save_knowledge(self, knowledge: OptimizationKnowledge) -> None:
        self._knowledge_versions[knowledge.version] = knowledge
        self._current_version = knowledge.version

    def get_knowledge(self, version: str) -> OptimizationKnowledge | None:
        return self._knowledge_versions.get(version)

    def get_current_knowledge(self) -> OptimizationKnowledge | None:
        if self._current_version:
            return self._knowledge_versions.get(self._current_version)
        return None

    def list_versions(self) -> list[str]:
        return sorted(self._knowledge_versions.keys())

    def get_version_count(self) -> int:
        return len(self._knowledge_versions)

    def get_current_version(self) -> str:
        return self._current_version

    def get_state(self) -> KnowledgeState:
        current = self.get_current_knowledge()
        versions = self.list_versions()
        experiences = self.list_experiences()

        successes = sum(1 for e in experiences if e.is_successful)
        mean_score = sum(e.overall_score for e in experiences) / max(len(experiences), 1)

        return KnowledgeState(
            current_version=self._current_version,
            total_experiences=len(experiences),
            total_patterns=len(current.patterns) if current else 0,
            total_insights=len(current.insights) if current else 0,
            total_rules=len(current.rules) if current else 0,
            total_versions=len(versions),
            global_success_rate=successes / max(len(experiences), 1),
            global_mean_score=round(mean_score, 4),
        )

    def clear_all(self) -> None:
        self._experiences.clear()
        self._knowledge_versions.clear()
        self._current_version = ""

    def experience_count(self) -> int:
        return len(self._experiences)
