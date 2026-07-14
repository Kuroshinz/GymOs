"""Capability Platform — self-describing introspection layer for GymOS.

Every module's maturity, health, dependencies, and roadmap are registered here.
The platform introspection answers: "where are we, what's weak, what's next for v1.0?"

Usage:
    from shared.capabilities import registry, compute_platform_state, generate_markdown_report
    state = compute_platform_state(registry)
    print(generate_markdown_report(registry))
"""

from __future__ import annotations

from shared.capabilities.capability import Capability
from shared.capabilities.dependency_graph import (
    DependencyEdge,
    DependencyGraphResult,
    build_dependency_graph,
)
from shared.capabilities.enums import (
    CapabilityMaturity,
    CapabilityPriority,
    CapabilityStatus,
    DebtSeverity,
    MilestoneType,
    RiskLevel,
)
from shared.capabilities.health import calculate_health
from shared.capabilities.metrics import (
    CompletionMetrics,
    HealthScore,
    MetricResult,
)
from shared.capabilities.milestone import (
    CapabilityRoadmap,
    Milestone,
    RoadmapPhase,
)
from shared.capabilities.platform_state import (
    PlatformState,
    compute_platform_state,
)
from shared.capabilities.registry import CapabilityRegistry
from shared.capabilities.report_generator import (
    generate_json_report,
    generate_markdown_report,
    generate_terminal_summary,
)
from shared.capabilities.roadmap import (
    GapAnalysis,
    RoadmapSummary,
    analyze_gaps,
    summarize_roadmap,
)
from shared.capabilities.technical_debt import TechnicalDebtItem, TechnicalDebtSummary

# ---------------------------------------------------------------------------
# Build the capability registry
# ---------------------------------------------------------------------------

registry = CapabilityRegistry()

# ---- Training Intelligence ----
registry.register(Capability(
    capability_id="training-intelligence",
    name="Training Intelligence",
    description="Exercise logging, set/rep tracking, RPE, volume, progression schemes, auto-regulation logic.",
    category="core",
    owner="GymOS Team",
    status=CapabilityStatus.COMPLETE,
    version_introduced="0.1",
    target_version="0.5",
    current_maturity=CapabilityMaturity.IMPLEMENTED,
    target_maturity=CapabilityMaturity.STABLE,
    health=HealthScore(overall=78, architecture=85, test_coverage=82, documentation=70, platform=75),
    completion=CompletionMetrics(current_percent=100, target_percent=100, remaining_tasks=0, total_tasks=42),
    technical_debt=TechnicalDebtSummary(total_items=8, critical=0, high=2, medium=4, low=2),
    dependencies=(),
    blocked_by=(),
    used_by=("workout-program",),
    risk_level=RiskLevel.LOW,
    priority=CapabilityPriority.HIGH,
    documentation_links=("modules/workout/README.md",),
))

# ---- Nutrition Intelligence ----
registry.register(Capability(
    capability_id="nutrition-intelligence",
    name="Nutrition Intelligence",
    description="Meal logging, meal planning, macro tracking, micronutrient goals, Cronometer sync, meal templates.",
    category="core",
    owner="GymOS Team",
    status=CapabilityStatus.COMPLETE,
    version_introduced="0.2",
    target_version="0.5",
    current_maturity=CapabilityMaturity.IMPLEMENTED,
    target_maturity=CapabilityMaturity.STABLE,
    health=HealthScore(overall=74, architecture=80, test_coverage=70, documentation=72, platform=74),
    completion=CompletionMetrics(current_percent=100, target_percent=100, remaining_tasks=0, total_tasks=38),
    technical_debt=TechnicalDebtSummary(total_items=6, critical=0, high=1, medium=3, low=2),
    dependencies=("training-intelligence",),
    blocked_by=(),
    used_by=("ai-coach", "prediction-engine",),
    risk_level=RiskLevel.LOW,
    priority=CapabilityPriority.HIGH,
    documentation_links=("modules/nutrition/README.md",),
))

# ---- Recovery Intelligence ----
registry.register(Capability(
    capability_id="recovery-intelligence",
    name="Recovery Intelligence",
    description="Sleep logging, HRV readiness, soreness tracking, recovery score, deload scheduling, wellness trends.",
    category="core",
    owner="GymOS Team",
    status=CapabilityStatus.IN_PROGRESS,
    version_introduced="0.5",
    target_version="1.0",
    current_maturity=CapabilityMaturity.DESIGN,
    target_maturity=CapabilityMaturity.IMPLEMENTED,
    health=HealthScore(overall=15, architecture=70, test_coverage=0, documentation=5, platform=0),
    completion=CompletionMetrics(current_percent=10, target_percent=100, remaining_tasks=27, total_tasks=30),
    technical_debt=TechnicalDebtSummary(total_items=0, critical=0, high=0, medium=0, low=0),
    dependencies=("training-intelligence",),
    blocked_by=("recovery-settings",),
    used_by=("ai-coach", "decision-intelligence",),
    risk_level=RiskLevel.HIGH,
    priority=CapabilityPriority.HIGH,
    documentation_links=(),
))

# ---- Decision Intelligence ----
registry.register(Capability(
    capability_id="decision-intelligence",
    name="Decision Intelligence",
    description="Weekly review engine, next-week recommendation, plateau detection, exercise selection, program adjustment logic.",
    category="intelligence",
    owner="GymOS Team",
    status=CapabilityStatus.IN_PROGRESS,
    version_introduced="0.4",
    target_version="0.5",
    current_maturity=CapabilityMaturity.FOUNDATION,
    target_maturity=CapabilityMaturity.IMPLEMENTED,
    health=HealthScore(overall=40, architecture=80, test_coverage=45, documentation=35, platform=0),
    completion=CompletionMetrics(current_percent=40, target_percent=100, remaining_tasks=18, total_tasks=30),
    technical_debt=TechnicalDebtSummary(total_items=2, critical=0, high=0, medium=1, low=1),
    dependencies=("training-intelligence", "nutrition-intelligence", "recovery-intelligence",),
    blocked_by=("recovery-intelligence",),
    used_by=("ai-coach", "workout-program",),
    risk_level=RiskLevel.MEDIUM,
    priority=CapabilityPriority.MEDIUM,
    documentation_links=("modules/gymbrain/README.md",),
))

# ---- Knowledge Platform ----
registry.register(Capability(
    capability_id="knowledge-platform",
    name="Knowledge Platform",
    description="Hypertrophy knowledge graph, exercise database, muscle group taxonomy, progression principles, evidence-backed recommendations.",
    category="platform",
    owner="GymOS Team",
    status=CapabilityStatus.COMPLETE,
    version_introduced="0.3",
    target_version="0.5",
    current_maturity=CapabilityMaturity.IMPLEMENTED,
    target_maturity=CapabilityMaturity.STABLE,
    health=HealthScore(overall=65, architecture=88, test_coverage=55, documentation=52, platform=65),
    completion=CompletionMetrics(current_percent=100, target_percent=100, remaining_tasks=0, total_tasks=25),
    technical_debt=TechnicalDebtSummary(total_items=3, critical=0, high=1, medium=1, low=1),
    dependencies=(),
    blocked_by=(),
    used_by=("decision-intelligence", "ai-coach", "prediction-engine",),
    risk_level=RiskLevel.LOW,
    priority=CapabilityPriority.HIGH,
    documentation_links=("knowledge/README.md",),
))

# ---- Event Platform ----
registry.register(Capability(
    capability_id="event-platform",
    name="Event Platform",
    description="Domain event bus, typed event definitions, event schema validation, event-driven module communication.",
    category="platform",
    owner="GymOS Team",
    status=CapabilityStatus.COMPLETE,
    version_introduced="0.3",
    target_version="0.5",
    current_maturity=CapabilityMaturity.IMPLEMENTED,
    target_maturity=CapabilityMaturity.STABLE,
    health=HealthScore(overall=82, architecture=90, test_coverage=85, documentation=75, platform=78),
    completion=CompletionMetrics(current_percent=100, target_percent=100, remaining_tasks=0, total_tasks=18),
    technical_debt=TechnicalDebtSummary(total_items=2, critical=0, high=0, medium=1, low=1),
    dependencies=(),
    blocked_by=(),
    used_by=("knowledge-platform", "training-intelligence", "nutrition-intelligence",),
    risk_level=RiskLevel.LOW,
    priority=CapabilityPriority.HIGH,
    documentation_links=("shared/events/README.md",),
))

# ---- Experience Platform ----
registry.register(Capability(
    capability_id="experience-platform",
    name="Experience Platform",
    description="UI widgets, dashboard, shared component library, notification system, onboarding flows.",
    category="platform",
    owner="GymOS Team",
    status=CapabilityStatus.NOT_STARTED,
    version_introduced="0.4",
    target_version="0.5",
    current_maturity=CapabilityMaturity.CONCEPT,
    target_maturity=CapabilityMaturity.DESIGN,
    health=HealthScore(overall=2, architecture=10, test_coverage=0, documentation=0, platform=0),
    completion=CompletionMetrics(current_percent=0, target_percent=100, remaining_tasks=15, total_tasks=15),
    technical_debt=TechnicalDebtSummary(total_items=0, critical=0, high=0, medium=0, low=0),
    dependencies=("training-intelligence", "nutrition-intelligence", "recovery-intelligence", "decision-intelligence",),
    blocked_by=("recovery-intelligence",),
    used_by=(),
    risk_level=RiskLevel.MEDIUM,
    priority=CapabilityPriority.MEDIUM,
    documentation_links=(),
))

# ---- AI Coach ----
registry.register(Capability(
    capability_id="ai-coach",
    name="AI Coach",
    description="Personalized coaching engine: workout recommendations, nutrition adjustments, recovery advice, form tips, motivational nudges.",
    category="intelligence",
    owner="GymOS Team",
    status=CapabilityStatus.NOT_STARTED,
    version_introduced="0.5",
    target_version="1.0",
    current_maturity=CapabilityMaturity.CONCEPT,
    target_maturity=CapabilityMaturity.DESIGN,
    health=HealthScore(overall=1, architecture=5, test_coverage=0, documentation=0, platform=0),
    completion=CompletionMetrics(current_percent=0, target_percent=100, remaining_tasks=25, total_tasks=25),
    technical_debt=TechnicalDebtSummary(total_items=0, critical=0, high=0, medium=0, low=0),
    dependencies=("decision-intelligence", "knowledge-platform", "training-intelligence", "nutrition-intelligence", "recovery-intelligence",),
    blocked_by=("decision-intelligence", "recovery-intelligence",),
    used_by=("prediction-engine", "digital-twin",),
    risk_level=RiskLevel.HIGH,
    priority=CapabilityPriority.LOW,
    documentation_links=(),
))

# ---- Prediction Engine ----
registry.register(Capability(
    capability_id="prediction-engine",
    name="Prediction Engine",
    description="Progress forecasting, plateau prediction, goal achievement timelines, what-if simulation, trend analysis, scenario comparison, counterfactual analysis, explainability, risk assessment.",
    category="intelligence",
    owner="GymOS Team",
    status=CapabilityStatus.COMPLETE,
    version_introduced="0.5",
    target_version="0.5",
    current_maturity=CapabilityMaturity.IMPLEMENTED,
    target_maturity=CapabilityMaturity.STABLE,
    health=HealthScore(overall=82, architecture=88, test_coverage=85, documentation=75, platform=80),
    completion=CompletionMetrics(current_percent=100, target_percent=100, remaining_tasks=0, total_tasks=38),
    technical_debt=TechnicalDebtSummary(total_items=3, critical=0, high=0, medium=2, low=1),
    dependencies=("training-intelligence", "nutrition-intelligence", "recovery-intelligence", "knowledge-platform",),
    blocked_by=(),
    used_by=("digital-twin", "decision-intelligence", "ai-coach",),
    risk_level=RiskLevel.LOW,
    priority=CapabilityPriority.HIGH,
    documentation_links=(
        "docs/prediction/PREDICTION_EXPLAINABILITY.md",
        "docs/prediction/SCENARIO_ENGINE.md",
        "docs/prediction/COUNTERFACTUALS.md",
        "docs/architecture/ADR-010.5-prediction-upgrade.md",
    ),
))

# ---- Digital Twin ----
registry.register(Capability(
    capability_id="digital-twin",
    name="Digital Twin",
    description="Longitudinal athlete profile: full history, adaptation tracking, injury risk, form decay, biological age modeling.",
    category="future",
    owner="GymOS Team",
    status=CapabilityStatus.NOT_STARTED,
    version_introduced="1.0",
    target_version="2.0",
    current_maturity=CapabilityMaturity.CONCEPT,
    target_maturity=CapabilityMaturity.DESIGN,
    health=HealthScore(overall=0, architecture=0, test_coverage=0, documentation=0, platform=0),
    completion=CompletionMetrics(current_percent=0, target_percent=100, remaining_tasks=30, total_tasks=30),
    technical_debt=TechnicalDebtSummary(total_items=0, critical=0, high=0, medium=0, low=0),
    dependencies=("prediction-engine", "ai-coach", "knowledge-platform", "training-intelligence", "nutrition-intelligence", "recovery-intelligence",),
    blocked_by=("prediction-engine", "ai-coach",),
    used_by=(),
    risk_level=RiskLevel.HIGH,
    priority=CapabilityPriority.LOW,
    documentation_links=(),
))

# ---- Product Intelligence ----
registry.register(Capability(
    capability_id="product-intelligence",
    name="Product Intelligence",
    description="Self-describing product metadata: current milestone, version, maturity table, roadmap, capability health, architecture decisions.",
    category="meta",
    owner="GymOS Team",
    status=CapabilityStatus.COMPLETE,
    version_introduced="0.5",
    target_version="0.5",
    current_maturity=CapabilityMaturity.IMPLEMENTED,
    target_maturity=CapabilityMaturity.STABLE,
    health=HealthScore(overall=82, architecture=90, test_coverage=80, documentation=80, platform=80),
    completion=CompletionMetrics(current_percent=100, target_percent=100, remaining_tasks=0, total_tasks=12),
    technical_debt=TechnicalDebtSummary(total_items=1, critical=0, high=0, medium=1, low=0),
    dependencies=(),
    blocked_by=(),
    used_by=(),
    risk_level=RiskLevel.LOW,
    priority=CapabilityPriority.HIGH,
    documentation_links=(
        "docs/PRODUCT_STRATEGY.md",
        "docs/VERSION_STRATEGY.md",
        "docs/PRODUCT_PILLARS.md",
    ),
))

# ---- Capability Platform (self-reference) ----
registry.register(Capability(
    capability_id="capability-platform",
    name="Capability Platform",
    description="Introspection layer for capability registry, health scoring, dependency management, roadmap gap analysis, reporting.",
    category="meta",
    owner="GymOS Team",
    status=CapabilityStatus.COMPLETE,
    version_introduced="0.5",
    target_version="0.5",
    current_maturity=CapabilityMaturity.IMPLEMENTED,
    target_maturity=CapabilityMaturity.STABLE,
    health=HealthScore(overall=85, architecture=92, test_coverage=85, documentation=80, platform=83),
    completion=CompletionMetrics(current_percent=100, target_percent=100, remaining_tasks=0, total_tasks=14),
    technical_debt=TechnicalDebtSummary(total_items=1, critical=0, high=0, medium=1, low=0),
    dependencies=(),
    blocked_by=(),
    used_by=("product-intelligence",),
    risk_level=RiskLevel.LOW,
    priority=CapabilityPriority.HIGH,
    documentation_links=(
        "docs/architecture/CAPABILITY_PLATFORM.md",
        "docs/architecture/ADR-006.md",
    ),
))

# ---- Intent Platform ----
registry.register(Capability(
    capability_id="intent-platform",
    name="Intent Platform",
    description="Canonical user intent model: declarative intent specification, conflict detection, scoring, validation, versioning, serialization, metrics, reporting.",
    category="platform",
    owner="GymOS Team",
    status=CapabilityStatus.COMPLETE,
    version_introduced="0.5",
    target_version="0.5",
    current_maturity=CapabilityMaturity.IMPLEMENTED,
    target_maturity=CapabilityMaturity.STABLE,
    health=HealthScore(overall=80, architecture=88, test_coverage=85, documentation=72, platform=75),
    completion=CompletionMetrics(current_percent=100, target_percent=100, remaining_tasks=0, total_tasks=20),
    technical_debt=TechnicalDebtSummary(total_items=2, critical=0, high=0, medium=1, low=1),
    dependencies=("capability-platform",),
    blocked_by=(),
    used_by=("prediction-engine", "decision-intelligence", "ai-coach", "planning-engine",),
    risk_level=RiskLevel.LOW,
    priority=CapabilityPriority.HIGH,
    documentation_links=(
        "docs/INTENT_PLATFORM.md",
        "docs/INTENT_ENGINE.md",
        "docs/INTENT_MODEL.md",
        "docs/architecture/ADR-011-intent-platform.md",
    ),
))

# ---- Planning Engine ----
registry.register(Capability(
    capability_id="planning-engine",
    name="Planning Engine",
    description="Deterministic periodization pipeline: macrocycle, mesocycle, microcycle, week, session generation. Volume/intensity/frequency/RIR allocation. Scientific validation, quality scoring, adherence prediction, history tracking.",
    category="platform",
    owner="GymOS Team",
    status=CapabilityStatus.COMPLETE,
    version_introduced="0.5",
    target_version="0.5",
    current_maturity=CapabilityMaturity.IMPLEMENTED,
    target_maturity=CapabilityMaturity.STABLE,
    health=HealthScore(overall=82, architecture=90, test_coverage=80, documentation=75, platform=82),
    completion=CompletionMetrics(current_percent=100, target_percent=100, remaining_tasks=0, total_tasks=24),
    technical_debt=TechnicalDebtSummary(total_items=2, critical=0, high=0, medium=1, low=1),
    dependencies=("capability-platform", "intent-platform",),
    blocked_by=(),
    used_by=("prediction-engine", "decision-intelligence", "ai-coach", "workout-program",),
    risk_level=RiskLevel.LOW,
    priority=CapabilityPriority.HIGH,
    documentation_links=(
        "docs/PLANNING_ENGINE.md",
        "docs/PLANNING_MODEL.md",
        "docs/PERIODIZATION.md",
        "docs/architecture/ADR-012-planning-engine.md",
    ),
))

# ---- Planning Optimizer ----
registry.register(Capability(
    capability_id="planning-optimizer",
    name="Planning Optimizer",
    description="Multi-objective evolutionary optimization for training plans. Generates, mutates, evaluates, ranks, and selects optimal plan variants against configurable objectives and constraints.",
    category="platform",
    owner="GymOS Team",
    status=CapabilityStatus.COMPLETE,
    version_introduced="0.5",
    target_version="0.5",
    current_maturity=CapabilityMaturity.IMPLEMENTED,
    target_maturity=CapabilityMaturity.STABLE,
    health=HealthScore(overall=82, architecture=90, test_coverage=80, documentation=75, platform=82),
    completion=CompletionMetrics(current_percent=100, target_percent=100, remaining_tasks=0, total_tasks=24),
    technical_debt=TechnicalDebtSummary(total_items=1, critical=0, high=0, medium=1, low=0),
    dependencies=("capability-platform", "planning-engine", "intent-platform",),
    blocked_by=(),
    used_by=("prediction-engine", "decision-intelligence", "ai-coach",),
    risk_level=RiskLevel.LOW,
    priority=CapabilityPriority.HIGH,
    documentation_links=(
        "docs/PLANNING_OPTIMIZER.md",
        "docs/OPTIMIZATION_MODEL.md",
        "docs/MULTI_OBJECTIVE_OPTIMIZATION.md",
        "docs/architecture/ADR-013-planning-optimizer.md",
    ),
))

# ---- Adaptive Programming ----
registry.register(Capability(
    capability_id="adaptive-programming",
    name="Adaptive Programming",
    description="Continuously adapts the user's long-term training strategy using canonical platform outputs. Deterministic, rule-based adaptation across volume, frequency, exercise substitution, mesocycle, progression, deload, nutrition, and goals. No AI/LLM dependencies.",
    category="platform",
    owner="GymOS Team",
    status=CapabilityStatus.COMPLETE,
    version_introduced="0.5",
    target_version="0.5",
    current_maturity=CapabilityMaturity.IMPLEMENTED,
    target_maturity=CapabilityMaturity.STABLE,
    health=HealthScore(overall=85, architecture=90, test_coverage=90, documentation=78, platform=82),
    completion=CompletionMetrics(current_percent=100, target_percent=100, remaining_tasks=0, total_tasks=30),
    technical_debt=TechnicalDebtSummary(total_items=0, critical=0, high=0, medium=0, low=0),
    dependencies=("capability-platform", "knowledge-evolution", "optimization-knowledge", "planning-optimizer", "planning-engine", "intent-platform",),
    blocked_by=(),
    used_by=("prediction-engine", "decision-intelligence", "ai-coach",),
    risk_level=RiskLevel.LOW,
    priority=CapabilityPriority.HIGH,
    documentation_links=(
        "docs/ADAPTIVE_PROGRAMMING.md",
        "docs/STRATEGY_ENGINE.md",
        "docs/ADAPTATION_POLICY.md",
        "docs/architecture/ADR-016-adaptive-programming.md",
    ),
))

# ---- Knowledge Evolution ----
registry.register(Capability(
    capability_id="knowledge-evolution",
    name="Knowledge Evolution",
    description="Evidence-driven, versioned, self-evolving knowledge system. Bayesian-style confidence updates, conflict detection and resolution, semantic versioning with immutable history, freshness decay, lifecycle management, rollback support. No AI/LLM dependencies.",
    category="platform",
    owner="GymOS Team",
    status=CapabilityStatus.COMPLETE,
    version_introduced="0.5",
    target_version="0.5",
    current_maturity=CapabilityMaturity.IMPLEMENTED,
    target_maturity=CapabilityMaturity.STABLE,
    health=HealthScore(overall=84, architecture=90, test_coverage=88, documentation=78, platform=80),
    completion=CompletionMetrics(current_percent=100, target_percent=100, remaining_tasks=0, total_tasks=28),
    technical_debt=TechnicalDebtSummary(total_items=0, critical=0, high=0, medium=0, low=0),
    dependencies=("capability-platform", "optimization-knowledge", "planning-optimizer", "planning-engine",),
    blocked_by=(),
    used_by=("prediction-engine", "decision-intelligence", "ai-coach",),
    risk_level=RiskLevel.LOW,
    priority=CapabilityPriority.HIGH,
    documentation_links=(
        "docs/KNOWLEDGE_EVOLUTION.md",
        "docs/KNOWLEDGE_VERSIONING.md",
        "docs/EVIDENCE_ENGINE.md",
        "docs/architecture/ADR-015-knowledge-evolution.md",
    ),
))

# ---- Optimization Knowledge ----
registry.register(Capability(
    capability_id="optimization-knowledge",
    name="Optimization Knowledge",
    description="Deterministic, statistical, versioned knowledge accumulation system. Mines patterns from optimization runs, computes descriptive statistics with confidence intervals, derives rules, generates insights and recommendations. No AI/LLM dependencies.",
    category="platform",
    owner="GymOS Team",
    status=CapabilityStatus.COMPLETE,
    version_introduced="0.5",
    target_version="0.5",
    current_maturity=CapabilityMaturity.IMPLEMENTED,
    target_maturity=CapabilityMaturity.STABLE,
    health=HealthScore(overall=82, architecture=90, test_coverage=85, documentation=75, platform=78),
    completion=CompletionMetrics(current_percent=100, target_percent=100, remaining_tasks=0, total_tasks=24),
    technical_debt=TechnicalDebtSummary(total_items=0, critical=0, high=0, medium=0, low=0),
    dependencies=("capability-platform", "planning-optimizer", "planning-engine",),
    blocked_by=(),
    used_by=("prediction-engine", "decision-intelligence", "ai-coach",),
    risk_level=RiskLevel.LOW,
    priority=CapabilityPriority.HIGH,
    documentation_links=(
        "docs/OPTIMIZATION_KNOWLEDGE.md",
        "docs/PATTERN_MINING.md",
        "docs/STATISTICAL_LEARNING.md",
        "docs/architecture/ADR-014-optimization-knowledge.md",
    ),
))

# ---- Cognitive Layer ----
registry.register(Capability(
    capability_id="cognitive-layer",
    name="Cognitive Layer & Attention Engine",
    description="Deterministic attention, priority, context, focus, and notification platform above all existing engines. No AI. Consumes canonical outputs only.",
    category="platform",
    owner="GymOS Team",
    status=CapabilityStatus.COMPLETE,
    version_introduced="0.7",
    target_version="0.7",
    current_maturity=CapabilityMaturity.IMPLEMENTED,
    target_maturity=CapabilityMaturity.STABLE,
    health=HealthScore(overall=88, architecture=90, test_coverage=95, documentation=85, platform=80),
    completion=CompletionMetrics(current_percent=100, target_percent=100, remaining_tasks=0, total_tasks=28),
    technical_debt=TechnicalDebtSummary(total_items=0, critical=0, high=0, medium=0, low=0),
    dependencies=("product-intelligence", "capability-platform", "experience-platform", "prediction-engine", "recovery-intelligence", "planning-engine",),
    blocked_by=(),
    used_by=("experience-platform", "ai-coach",),
    risk_level=RiskLevel.LOW,
    priority=CapabilityPriority.HIGH,
    documentation_links=(
        "docs/cognitive_layer.md",
        "docs/adr/ADR-029-cognitive-layer.md",
    ),
))

# Freeze the registry — no more capabilities can be registered
registry.freeze()

__all__ = (
    "registry",
    "calculate_health",
    "compute_platform_state",
    "generate_markdown_report",
    "generate_json_report",
    "generate_terminal_summary",
    "build_dependency_graph",
    "summarize_roadmap",
    "analyze_gaps",
    "Capability",
    "CapabilityRegistry",
    "CapabilityMaturity",
    "CapabilityPriority",
    "CapabilityStatus",
    "DebtSeverity",
    "MilestoneType",
    "RiskLevel",
    "HealthScore",
    "CompletionMetrics",
    "MetricResult",
    "TechnicalDebtItem",
    "TechnicalDebtSummary",
    "Milestone",
    "RoadmapPhase",
    "CapabilityRoadmap",
    "PlatformState",
    "RoadmapSummary",
    "GapAnalysis",
    "DependencyEdge",
    "DependencyGraphResult",
)
