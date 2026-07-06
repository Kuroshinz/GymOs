from ui.design_system.visualization.trend_indicator import TrendIndicator
from ui.visualization.charts.area_chart import AreaChart
from ui.visualization.charts.bar_chart import BarChart
from ui.visualization.charts.comparison_chart import ComparisonChart
from ui.visualization.charts.delta_chart import DeltaChart
from ui.visualization.charts.radar_chart import RadarChart
from ui.visualization.charts.trend_chart import TrendChart
from ui.visualization.curves.bodyweight_curve import BodyweightCurve
from ui.visualization.curves.macro_curve import MacroCurve
from ui.visualization.curves.pr_curve import PRCurve
from ui.visualization.curves.recovery_curve import RecoveryCurve
from ui.visualization.curves.training_load_curve import TrainingLoadCurve
from ui.visualization.graphs.dependency_graph_view import DependencyGraphView
from ui.visualization.graphs.evidence_graph_view import EvidenceGraphView
from ui.visualization.graphs.knowledge_graph_view import KnowledgeGraphView
from ui.visualization.graphs.reason_tree_view import ReasonTreeView
from ui.visualization.heatmaps.compliance_heatmap import ComplianceHeatmap
from ui.visualization.heatmaps.fatigue_heatmap import FatigueHeatmap
from ui.visualization.heatmaps.muscle_heatmap import MuscleHeatmap
from ui.visualization.heatmaps.volume_heatmap import VolumeHeatmap
from ui.visualization.indicators.confidence_gauge import ConfidenceGauge
from ui.visualization.indicators.momentum_gauge import MomentumGauge
from ui.visualization.indicators.risk_gauge import RiskGauge
from ui.visualization.indicators.stability_gauge import StabilityGauge
from ui.visualization.rings.confidence_ring import ConfidenceRing
from ui.visualization.rings.goal_ring import GoalRing
from ui.visualization.rings.progress_ring_v2 import ProgressRingV2
from ui.visualization.rings.readiness_ring import ReadinessRing
from ui.visualization.rings.recovery_ring import RecoveryRing
from ui.visualization.timelines.adaptation_timeline import AdaptationTimeline
from ui.visualization.timelines.mesocycle_timeline import MesocycleTimeline
from ui.visualization.timelines.prediction_timeline import PredictionTimeline
from ui.visualization.timelines.recovery_timeline import RecoveryTimeline
from ui.visualization.timelines.weekly_timeline import WeeklyTimeline
from ui.visualization.timelines.workout_timeline import WorkoutTimeline

# Legacy aliases for backward compatibility
RiskMeter = RiskGauge

__all__ = [
    "TrendIndicator",
    "RecoveryRing",
    "GoalRing",
    "ProgressRingV2",
    "ConfidenceRing",
    "ReadinessRing",
    "WeeklyTimeline",
    "PredictionTimeline",
    "RecoveryTimeline",
    "WorkoutTimeline",
    "MesocycleTimeline",
    "AdaptationTimeline",
    "MuscleHeatmap",
    "VolumeHeatmap",
    "FatigueHeatmap",
    "ComplianceHeatmap",
    "TrendChart",
    "AreaChart",
    "DeltaChart",
    "ComparisonChart",
    "RadarChart",
    "BarChart",
    "KnowledgeGraphView",
    "EvidenceGraphView",
    "ReasonTreeView",
    "DependencyGraphView",
    "ConfidenceGauge",
    "RiskGauge",
    "StabilityGauge",
    "MomentumGauge",
    "TrainingLoadCurve",
    "RecoveryCurve",
    "MacroCurve",
    "BodyweightCurve",
    "PRCurve",
    "RiskMeter",
]
