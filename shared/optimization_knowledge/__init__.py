"""Optimization Knowledge Engine — Statistical knowledge accumulation system.

Mines patterns, computes statistics, derives rules, and generates recommendations
from optimization plan experiences. Fully deterministic with no AI/LLM dependencies.
"""

from __future__ import annotations

import uuid
from datetime import datetime

import shared.events as events_module
from shared.optimization_knowledge.domain import (
    KnowledgeConfig,
    KnowledgeScope,
    KnowledgeState,
    OptimizationExperience,
    OptimizationInsight,
    OptimizationKnowledge,
    OptimizationPattern,
    OptimizationRule,
    OptimizationStatistics,
)
from shared.optimization_knowledge.engine import ExperienceEngine, KnowledgeExtractor
from shared.optimization_knowledge.events import (
    ExperienceRecorded,
    InsightGenerated,
    KnowledgeVersioned,
    PatternMined,
    RuleDerived,
    StatisticsUpdated,
)
from shared.optimization_knowledge.history import KnowledgeHistory
from shared.optimization_knowledge.metrics import KnowledgeMetrics, KnowledgeMetricsResult
from shared.optimization_knowledge.patterns import PatternMiningEngine
from shared.optimization_knowledge.query import KnowledgeQueryEngine
from shared.optimization_knowledge.reports import KnowledgeReportGenerator
from shared.optimization_knowledge.repository import OptimizationKnowledgeRepository
from shared.optimization_knowledge.serializer import OptimizationKnowledgeSerializer
from shared.optimization_knowledge.statistics import StatisticsEngine


class OptimizationKnowledgeOrchestrator:
    """Main orchestrator for the optimization knowledge system.

    Coordinates experience recording, pattern mining, statistics computation,
    insight generation, rule derivation, recommendation generation, and
    versioned knowledge storage.
    """

    def __init__(
        self,
        config: KnowledgeConfig | None = None,
    ) -> None:
        self.config = config or KnowledgeConfig()
        self.experience_engine = ExperienceEngine(config)
        self.pattern_miner = PatternMiningEngine(config)
        self.statistics_engine = StatisticsEngine(config)
        self.extractor = KnowledgeExtractor(config)
        self.repository = OptimizationKnowledgeRepository()
        self.history = KnowledgeHistory(config)
        self.query = KnowledgeQueryEngine()
        self.metrics_calc = KnowledgeMetrics(config)
        self.reports = KnowledgeReportGenerator(config)
        self.serializer = OptimizationKnowledgeSerializer()

    def record_experience(
        self,
        plan_id: str,
        overall_score: float,
        avg_weekly_sets: int,
        sessions_per_week: int,
        total_weeks: int,
        total_sets: int,
        mesocycle_count: int,
        has_deload: bool,
        split_style: str | None = None,
        goal: str | None = None,
    ) -> OptimizationExperience:
        experience = self.experience_engine.record_experience(
            plan_id=plan_id,
            overall_score=overall_score,
            avg_weekly_sets=avg_weekly_sets,
            sessions_per_week=sessions_per_week,
            total_weeks=total_weeks,
            total_sets=total_sets,
            mesocycle_count=mesocycle_count,
            has_deload=has_deload,
            split_style=split_style,
            goal=goal,
        )
        self.repository.record_experience(experience)
        event = ExperienceRecorded(
            experience_id=experience.experience_id,
            plan_id=plan_id,
            is_successful=experience.is_successful,
            overall_score=overall_score,
        )
        events_module.emit(event)
        return experience

    def extract_knowledge(
        self,
        scope: KnowledgeScope = KnowledgeScope.GLOBAL,
    ) -> OptimizationKnowledge:
        experiences = self.repository.list_experiences()
        patterns = self.pattern_miner.mine_all(experiences, scope)
        for p in patterns:
            self._emit_pattern_mined(p)
        statistics = self.statistics_engine.compute_all(experiences, scope)
        for s in statistics:
            self._emit_statistics_updated(s)
        profiles = self.statistics_engine.build_profiles(experiences, scope)
        insights = self.extractor.generate_insights(patterns, statistics)
        for i in insights:
            self._emit_insight_generated(i)
        rules = self.extractor.derive_rules(patterns)
        for r in rules:
            self._emit_rule_derived(r)
        recommendations = self.extractor.generate_recommendations(rules, profiles)
        current = self.repository.get_current_knowledge()
        parent_version = current.version if current else ""
        version = self._next_version(parent_version)

        knowledge = OptimizationKnowledge(
            knowledge_id=f"know_{uuid.uuid4().hex[:12]}",
            version=version,
            parent_version=parent_version,
            experiences=experiences,
            patterns=patterns,
            statistics=statistics,
            profiles=profiles,
            insights=insights,
            rules=rules,
            recommendations=recommendations,
            created_at=current.created_at if current else datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )

        self.repository.save_knowledge(knowledge)
        self.history.record_version(knowledge, "knowledge extraction")
        event = KnowledgeVersioned(
            knowledge_id=knowledge.knowledge_id,
            version=version,
            parent_version=parent_version,
            pattern_count=len(patterns),
            insight_count=len(insights),
            rule_count=len(rules),
        )
        events_module.emit(event)
        return knowledge

    def _next_version(self, parent_version: str) -> str:
        if not parent_version:
            return "v1.0.0"
        parts = parent_version.split(".")
        if len(parts) == 3:
            major = int(parts[0][1:])
            minor = int(parts[1]) + 1
            return f"v{major}.{minor}.0"
        return "v1.0.0"

    def _emit_pattern_mined(self, pattern: OptimizationPattern) -> None:
        event = PatternMined(
            pattern_id=pattern.pattern_id,
            pattern_type=pattern.pattern_type.value,
            pattern_label=pattern.label,
            success_rate=pattern.success_rate,
            sample_size=pattern.sample_size,
        )
        events_module.emit(event)

    def _emit_statistics_updated(self, stats: OptimizationStatistics) -> None:
        event = StatisticsUpdated(
            statistics_id=stats.statistics_id,
            scope=stats.scope.value,
            total_experiences=stats.total_experiences,
            success_rate=stats.success_rate,
            mean_score=stats.mean_score,
        )
        events_module.emit(event)

    def _emit_insight_generated(self, insight: OptimizationInsight) -> None:
        event = InsightGenerated(
            insight_id=insight.insight_id,
            category=insight.category.value,
            title=insight.title,
            confidence=insight.confidence,
        )
        events_module.emit(event)

    def _emit_rule_derived(self, rule: OptimizationRule) -> None:
        event = RuleDerived(
            rule_id=rule.rule_id,
            pattern_type=rule.pattern_type.value,
            effect=rule.effect.value,
            confidence=rule.confidence,
            sample_size=rule.sample_size,
        )
        events_module.emit(event)

    def query_best_split(self, min_samples: int = 5) -> OptimizationPattern | None:
        knowledge = self.repository.get_current_knowledge()
        if not knowledge:
            return None
        return self.query.best_split(knowledge, min_samples)

    def query_best_volume(self, min_samples: int = 5) -> OptimizationPattern | None:
        knowledge = self.repository.get_current_knowledge()
        if not knowledge:
            return None
        return self.query.best_volume(knowledge, min_samples)

    def query_best_frequency(self, min_samples: int = 5) -> OptimizationPattern | None:
        knowledge = self.repository.get_current_knowledge()
        if not knowledge:
            return None
        return self.query.best_frequency(knowledge, min_samples)

    def get_current_knowledge(self) -> OptimizationKnowledge | None:
        return self.repository.get_current_knowledge()

    def get_state(self) -> KnowledgeState:
        return self.repository.get_state()

    def get_metrics(self) -> KnowledgeMetricsResult | None:
        knowledge = self.repository.get_current_knowledge()
        if not knowledge:
            return None
        return self.metrics_calc.compute_metrics(knowledge)

    def generate_summary_report(self) -> str:
        knowledge = self.repository.get_current_knowledge()
        if not knowledge:
            return "No knowledge available."
        return self.reports.generate_summary_report(knowledge)

    def generate_detailed_report(self) -> str:
        knowledge = self.repository.get_current_knowledge()
        if not knowledge:
            return "No knowledge available."
        return self.reports.generate_detailed_report(knowledge)

    def list_experiences(self) -> list[OptimizationExperience]:
        return self.repository.list_experiences()

    def get_experience_count(self) -> int:
        return self.repository.experience_count()

    def clear_all(self) -> None:
        self.repository.clear_all()
        self.history.clear()

    def to_dict(self) -> dict:
        knowledge = self.repository.get_current_knowledge()
        state = self.get_state()
        result = {
            "state": self.serializer.serialize_state(state),
            "history": [e.to_dict() for e in self.history.get_history()],
        }
        if knowledge:
            result["knowledge"] = self.serializer.serialize_knowledge(knowledge)
        return result

    def from_dict(self, data: dict) -> None:
        if "knowledge" in data:
            knowledge = self.serializer.deserialize_knowledge(data["knowledge"])
            self.repository.save_knowledge(knowledge)
        if "history" in data:
            from shared.optimization_knowledge.history import KnowledgeHistoryEntry
            for entry_data in data["history"]:
                entry = KnowledgeHistoryEntry.from_dict(entry_data)
                self.history._entries.append(entry)
