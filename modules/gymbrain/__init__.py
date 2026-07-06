"""GymBrain Core — evidence-based training intelligence engine.

GymBrain answers: "What should the user do next to maximize hypertrophy?"
Every recommendation is deterministic, reproducible, and explainable.
"""

from modules.gymbrain.analysis.fatigue import FatigueAnalyzer
from modules.gymbrain.analysis.goals import GoalTracker
from modules.gymbrain.analysis.muscle import MuscleAnalyzer
from modules.gymbrain.analysis.plateau import PlateauDetector
from modules.gymbrain.models.analysis import (
    FatigueLevel,
    FatigueResult,
    GoalProgress,
    MuscleAnalysisResult,
    MuscleStatus,
    PlateauResult,
    PlateauType,
    WeeklyReview,
)
from modules.gymbrain.models.recommendations import (
    Recommendation,
    RecommendationAction,
    RecommendationCategory,
    RecommendationEvidence,
    RecommendationPriority,
)
from modules.gymbrain.providers.data_provider import DataProvider
from modules.gymbrain.rules.base import BaseRule, RuleResult
from modules.gymbrain.rules.engine import RuleEngine
from modules.gymbrain.services.decision_engine import DecisionEngine
from modules.gymbrain.services.weekly_review import WeeklyReviewGenerator

__all__ = [
    "Recommendation",
    "RecommendationCategory",
    "RecommendationPriority",
    "RecommendationAction",
    "RecommendationEvidence",
    "FatigueLevel",
    "FatigueResult",
    "PlateauResult",
    "PlateauType",
    "MuscleStatus",
    "MuscleAnalysisResult",
    "GoalProgress",
    "WeeklyReview",
    "BaseRule",
    "RuleResult",
    "RuleEngine",
    "PlateauDetector",
    "FatigueAnalyzer",
    "MuscleAnalyzer",
    "GoalTracker",
    "DecisionEngine",
    "WeeklyReviewGenerator",
    "DataProvider",
]
