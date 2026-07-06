"""GymOS Recovery Intelligence — first-class recovery domain for GymBrain.

GymBrain combines: Training + Body Weight + Nutrition + Recovery
to generate better recommendations for the user's lean bulk goal.

Usage:
    from modules.recovery import RecoveryService, IRecoveryProvider
    from modules.recovery.infrastructure.repository import RecoveryRepository

    repo = RecoveryRepository("data/gymos.db")
    service = RecoveryService(repo, db=db, event_bus=event_bus)
    snapshot = service.get_snapshot()
    print(snapshot.recovery_score)
"""

from modules.recovery.application import RecoveryService
from modules.recovery.domain import (
    DeloadPlan,
    DeloadStatus,
    FatigueFactors,
    FatigueLevel,
    ReadinessAssessment,
    ReadinessLevel,
    RecoveryFactors,
    RecoveryHistory,
    RecoveryMetrics,
    RecoveryProfile,
    RecoveryRecommendation,
    RecoveryScore,
    RecoverySession,
    RecoverySnapshot,
    RecoveryTrend,
    RecoveryTrendAnalysis,
    SleepLog,
    SleepQuality,
    SorenessLevel,
    StressLevel,
    StressLog,
)
from modules.recovery.engines import (
    DeloadEngine,
    FatigueAggregator,
    ReadinessEngine,
    RecoveryScoreEngine,
    RecoveryTrendAnalyzer,
    SleepAnalyzer,
    StressAnalyzer,
)
from modules.recovery.infrastructure.repository import RecoveryRepository
from modules.recovery.providers import IRecoveryProvider, ProductionRecoveryProvider

__all__ = [
    # Domain
    "DeloadPlan",
    "DeloadStatus",
    "FatigueFactors",
    "FatigueLevel",
    "ReadinessAssessment",
    "ReadinessLevel",
    "RecoveryFactors",
    "RecoveryHistory",
    "RecoveryMetrics",
    "RecoveryProfile",
    "RecoveryRecommendation",
    "RecoveryScore",
    "RecoverySession",
    "RecoverySnapshot",
    "RecoveryTrend",
    "RecoveryTrendAnalysis",
    "SleepLog",
    "SleepQuality",
    "SorenessLevel",
    "StressLevel",
    "StressLog",
    # Engines
    "DeloadEngine",
    "FatigueAggregator",
    "ReadinessEngine",
    "RecoveryScoreEngine",
    "RecoveryTrendAnalyzer",
    "SleepAnalyzer",
    "StressAnalyzer",
    # Infrastructure
    "RecoveryRepository",
    # Providers
    "IRecoveryProvider",
    "ProductionRecoveryProvider",
    # Service
    "RecoveryService",
]
