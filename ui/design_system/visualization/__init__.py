"""
Design System Visualization re-exports.

This package provides a unified import surface for visualization components.
Most components are imported lazily from ``ui/visualization/*`` to avoid
circular imports and maintain backward compatibility.

NOTE: Several files in this directory are DUPLICATE implementations that exist
only behind lazy re-exports. The canonical implementations live in
``ui/visualization/`` (rings, timelines, charts, indicators, heatmaps).

DEPRECATED files (will be removed in next major):
- goal_ring.py → uses ui/visualization/rings/GoalRing instead
- recovery_ring.py → uses ui/visualization/rings/RecoveryRing instead
- weekly_timeline.py → uses ui/visualization/timelines/WeeklyTimeline instead
- prediction_timeline.py → uses ui/visualization/timelines/PredictionTimeline instead
- confidence_gauge.py → uses ui/visualization/indicators/ConfidenceGauge instead
- muscle_heatmap.py → uses ui/visualization/heatmaps/MuscleHeatmap instead
- risk_meter.py → uses ui/visualization/indicators/RiskGauge instead

Components defined locally (CANONICAL):
- TrendIndicator → defined in trend_indicator.py (KEEP)
"""

from __future__ import annotations

import importlib
from typing import Any

from ui.design_system.visualization.trend_indicator import TrendIndicator

_MODULE_CACHE: dict[str, Any] = {}


def __getattr__(name: str) -> Any:
    # Mapping: design_system name → (canonical module, canonical class)
    mapping: dict[str, tuple[str, str]] = {
        "AreaChart": ("ui.visualization.charts.area_chart", "AreaChart"),
        "BarChart": ("ui.visualization.charts.bar_chart", "BarChart"),
        "ComparisonChart": ("ui.visualization.charts.comparison_chart", "ComparisonChart"),
        "DeltaChart": ("ui.visualization.charts.delta_chart", "DeltaChart"),
        "RadarChart": ("ui.visualization.charts.radar_chart", "RadarChart"),
        "TrendChart": ("ui.visualization.charts.trend_chart", "TrendChart"),
        "BodyweightCurve": ("ui.visualization.curves.bodyweight_curve", "BodyweightCurve"),
        "MacroCurve": ("ui.visualization.curves.macro_curve", "MacroCurve"),
        "PRCurve": ("ui.visualization.curves.pr_curve", "PRCurve"),
        "RecoveryCurve": ("ui.visualization.curves.recovery_curve", "RecoveryCurve"),
        "TrainingLoadCurve": ("ui.visualization.curves.training_load_curve", "TrainingLoadCurve"),
        "DependencyGraphView": ("ui.visualization.graphs.dependency_graph_view", "DependencyGraphView"),
        "EvidenceGraphView": ("ui.visualization.graphs.evidence_graph_view", "EvidenceGraphView"),
        "KnowledgeGraphView": ("ui.visualization.graphs.knowledge_graph_view", "KnowledgeGraphView"),
        "ReasonTreeView": ("ui.visualization.graphs.reason_tree_view", "ReasonTreeView"),
        "ComplianceHeatmap": ("ui.visualization.heatmaps.compliance_heatmap", "ComplianceHeatmap"),
        "FatigueHeatmap": ("ui.visualization.heatmaps.fatigue_heatmap", "FatigueHeatmap"),
        "MuscleHeatmap": ("ui.visualization.heatmaps.muscle_heatmap", "MuscleHeatmap"),
        "VolumeHeatmap": ("ui.visualization.heatmaps.volume_heatmap", "VolumeHeatmap"),
        "ConfidenceGauge": ("ui.visualization.indicators.confidence_gauge", "ConfidenceGauge"),
        "MomentumGauge": ("ui.visualization.indicators.momentum_gauge", "MomentumGauge"),
        "RiskGauge": ("ui.visualization.indicators.risk_gauge", "RiskGauge"),
        "StabilityGauge": ("ui.visualization.indicators.stability_gauge", "StabilityGauge"),
        "ConfidenceRing": ("ui.visualization.rings.confidence_ring", "ConfidenceRing"),
        "GoalRing": ("ui.visualization.rings.goal_ring", "GoalRing"),
        "ProgressRingV2": ("ui.visualization.rings.progress_ring_v2", "ProgressRingV2"),
        "ReadinessRing": ("ui.visualization.rings.readiness_ring", "ReadinessRing"),
        "RecoveryRing": ("ui.visualization.rings.recovery_ring", "RecoveryRing"),
        "AdaptationTimeline": ("ui.visualization.timelines.adaptation_timeline", "AdaptationTimeline"),
        "MesocycleTimeline": ("ui.visualization.timelines.mesocycle_timeline", "MesocycleTimeline"),
        "PredictionTimeline": ("ui.visualization.timelines.prediction_timeline", "PredictionTimeline"),
        "RecoveryTimeline": ("ui.visualization.timelines.recovery_timeline", "RecoveryTimeline"),
        "WeeklyTimeline": ("ui.visualization.timelines.weekly_timeline", "WeeklyTimeline"),
        "WorkoutTimeline": ("ui.visualization.timelines.workout_timeline", "WorkoutTimeline"),
        "RiskMeter": ("ui.visualization.indicators.risk_gauge", "RiskGauge"),
    }
    if name in mapping:
        mod_path, attr = mapping[name]
        if name not in _MODULE_CACHE:
            mod = importlib.import_module(mod_path)
            _MODULE_CACHE[name] = getattr(mod, attr)
        return _MODULE_CACHE[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Local canonical
    "TrendIndicator",
    # Charts
    "AreaChart", "BarChart", "ComparisonChart", "DeltaChart", "RadarChart", "TrendChart",
    # Curves
    "BodyweightCurve", "MacroCurve", "PRCurve", "RecoveryCurve", "TrainingLoadCurve",
    # Graphs
    "DependencyGraphView", "EvidenceGraphView", "KnowledgeGraphView", "ReasonTreeView",
    # Heatmaps
    "ComplianceHeatmap", "FatigueHeatmap", "MuscleHeatmap", "VolumeHeatmap",
    # Indicators / Gauges
    "ConfidenceGauge", "MomentumGauge", "RiskGauge", "StabilityGauge",
    # Rings
    "ConfidenceRing", "GoalRing", "ProgressRingV2", "ReadinessRing", "RecoveryRing",
    # Timelines
    "AdaptationTimeline", "MesocycleTimeline", "PredictionTimeline",
    "RecoveryTimeline", "WeeklyTimeline", "WorkoutTimeline",
    # Aliases
    "RiskMeter",
]
