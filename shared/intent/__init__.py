"""Intent Platform — canonical source of truth for user intent.

Every future decision in GymOS must be derived from the Intent Platform,
not directly from raw data. The Intent Platform captures what the user
WANTS, not what they HAVE — goals, preferences, constraints, priorities,
and tolerance levels.

Usage:
    from shared.intent import (
        IntentEngine, IntentRepository, IntentSerializer,
        IntentValidator, IntentScorer, IntentReport, IntentMetrics,
        IntentState, UserIntent, IntentBuilder, IntentMerger,
        ConflictResolver, IntentVersioner,
    )

    engine = IntentEngine()
    config = {"goals": [{"goal_type": "hypertrophy", "target_value": 75}], ...}
    intent, score, validation = engine.build_and_score(config)
"""

from __future__ import annotations

from shared.intent.builder import IntentBuilder
from shared.intent.domain import (
    AdaptivePreference,
    ComplianceProfile,
    Constraint,
    EquipmentLevel,
    EquipmentProfile,
    GoalIntent,
    GoalType,
    IntentConflict,
    IntentConflictSeverity,
    IntentDimension,
    IntentSnapshot,
    IntentStatus,
    LifestyleProfile,
    NutritionApproach,
    NutritionPreference,
    Priority,
    RecoveryPreference,
    RecoveryPriority,
    RiskLevel,
    RiskTolerance,
    Timeline,
    TrainingPreference,
    TrainingStyle,
    UserIntent,
)
from shared.intent.engine import IntentEngine
from shared.intent.merger import ConflictResolver, IntentMerger
from shared.intent.metrics import IntentHealthScore, IntentMetrics
from shared.intent.report import IntentReport
from shared.intent.repository import IntentRepository
from shared.intent.scorer import IntentScorer
from shared.intent.serializer import IntentSerializer
from shared.intent.state import IntentState
from shared.intent.validator import IntentValidator, ValidationError, ValidationResult
from shared.intent.versioner import IntentVersioner

__all__ = (
    "AdaptivePreference",
    "ComplianceProfile",
    "ConflictResolver",
    "Constraint",
    "EquipmentLevel",
    "EquipmentProfile",
    "GoalIntent",
    "GoalType",
    "IntentConflict",
    "IntentConflictSeverity",
    "IntentDimension",
    "IntentEngine",
    "IntentHealthScore",
    "IntentMetrics",
    "IntentMerger",
    "IntentReport",
    "IntentRepository",
    "IntentScorer",
    "IntentSerializer",
    "IntentSnapshot",
    "IntentState",
    "IntentStatus",
    "IntentValidator",
    "IntentVersioner",
    "IntentBuilder",
    "LifestyleProfile",
    "NutritionApproach",
    "NutritionPreference",
    "Priority",
    "RecoveryPreference",
    "RecoveryPriority",
    "RiskLevel",
    "RiskTolerance",
    "Timeline",
    "TrainingPreference",
    "TrainingStyle",
    "UserIntent",
    "ValidationError",
    "ValidationResult",
)
