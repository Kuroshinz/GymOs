# Knowledge Evolution Engine

## Overview

The Knowledge Evolution Engine is a deterministic, statistical, versioned system that transforms static optimization knowledge into self-evolving, evidence-driven knowledge. It collects evidence from across the NexusOS ecosystem, computes Bayesian-style confidence scores, detects and resolves knowledge conflicts, manages semantic versioning with immutable history, and generates comprehensive evolution reports — all without any AI or LLM dependencies.

## Core Philosophy

- **No AI/LLM** — All confidence computation, conflict detection, and evolution logic is purely statistical, deterministic, explainable, and reproducible
- **Evidence-Driven** — Every knowledge record is backed by a trail of evidence that directly determines its confidence score
- **Versioned & Immutable** — Knowledge is versioned with semantic versioning (vX.Y.Z); once published, versions are never mutated
- **Self-Evolving** — As new evidence arrives, the engine automatically recalculates confidence, detects conflicts, and evolves the knowledge graph
- **Append-Only Repository** — All records, versions, revisions, conflicts, and snapshots are append-only; nothing is ever deleted

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    KnowledgeEvolutionOrchestrator                        │
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │  Evolution   │  │  Confidence  │  │   Conflict   │  │   Version   │  │
│  │    Engine    │  │    Engine    │  │    Engine    │  │   Manager   │  │
│  │              │  │              │  │              │  │             │  │
│  │ • collect    │  │ • compute    │  │ • detect     │  │ • create    │  │
│  │   evidence   │  │   confidence │  │   conflicts  │  │   version   │  │
│  │ • aggregate  │  │ • update     │  │ • resolve    │  │ • snapshot  │  │
│  │ • evolve_all │  │   confidence │  │   conflicts  │  │ • rollback  │  │
│  │ • deprecate  │  │ • bayesian   │  │ • rank       │  │ • history   │  │
│  │ • publish    │  │ • freshness  │  │   evidence   │  │             │  │
│  │   version    │  │ • reliability│  │              │  │             │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘  │
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │ Repository   │  │   Query     │  │   Metrics    │  │   Reports   │  │
│  │ (Append-Only)│  │              │  │              │  │  Generator  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘  │
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐                                     │
│  │ Serializer   │  │  Integration │                                     │
│  │ (Dict/JSON)  │  │   Bridges    │                                     │
│  └──────────────┘  └──────────────┘                                     │
└──────────────────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
  │  Optimizer   │   │  Predictor   │   │   Recovery   │
  │    Bridge    │   │    Bridge    │   │    Bridge    │
  └──────────────┘   └──────────────┘   └──────────────┘
  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
  │  Nutrition   │   │  Decision    │   │   Other      │
  │    Bridge    │   │    Bridge    │   │   Modules    │
  └──────────────┘   └──────────────┘   └──────────────┘
```

## Components

### EvolutionEngine

The central orchestrator that runs the full evolution pipeline. It coordinates all sub-engines to transform raw evidence into evolved knowledge.

**Responsibilities:**
- `collect_evidence()` — Assigns IDs and timestamps to incoming evidence
- `aggregate_evidence()` — Prepares evidence for confidence recalculation
- `recalculate_confidence()` — Delegates to ConfidenceEngine for score computation
- `detect_conflicts()` — Delegates to ConflictEngine for conflict detection
- `resolve_conflicts()` — Automatically resolves conflicts by superseding the lower-confidence record
- `deprecate_obsolete()` — Marks specified records as DEPRECATED
- `publish_version()` — Creates a new semantic version via VersionManager
- `evolve_all()` — Full pipeline: aggregate → recalculate → detect/resolve conflicts → deprecate → create versions → snapshot

### ConfidenceEngine

Computes multi-dimensional confidence scores using Bayesian statistics, freshness decay, and source reliability. See [EVIDENCE_ENGINE.md](EVIDENCE_ENGINE.md) for full details.

**Scoring formula:**
```
Overall = Bayesian × 0.4 + Freshness × 0.3 + Reliability × 0.3
```

### ConflictEngine

Detects and resolves knowledge conflicts within the same domain.

- **Detection:** Two records conflict when their confidence scores are on opposite sides of 0.5 (one >= 0.5, the other < 0.5) and both have sufficient evidence
- **Severity:** CRITICAL (diff >= 0.6), MAJOR (diff >= 0.4), MODERATE (diff >= 0.2), MINOR (diff < 0.2)
- **Resolution:** The lower-confidence record is superseded; the conflict is marked resolved with a timestamp and superseded knowledge ID
- **Ranking:** `rank_competing_evidence()` orders records by total evidence weight

### VersionManager

Manages semantic versioning (vX.Y.Z) and point-in-time snapshots. See [KNOWLEDGE_VERSIONING.md](KNOWLEDGE_VERSIONING.md) for full details.

- First version: v1.0.0
- Subsequent versions: v1.1.0, v1.2.0 (minor increment on each evolution)
- Snapshots: Timestamped global snapshots of all records and conflicts
- Rollback: Retrieve any historical version by version string
- History: Sorted version history per knowledge record

### KnowledgeEvolutionOrchestrator

Unified facade that wraps all components behind a single entry point. Provides high-level methods for evidence ingestion, record management, evolution execution, querying, reporting, metrics, serialization, and state inspection.

### KnowledgeEvolutionRepository

Append-only, immutable, versioned in-memory store. Records are keyed by `knowledge_id` (latest version overwrites). Versions, conflicts, revisions, and snapshots are all append-only — once written, they are never mutated.

### KnowledgeEvolutionQuery

Stateless query methods for retrieving latest/historical versions, confidence timelines, evidence history, conflict history, and filtered record lists by domain, confidence score, or lifecycle stage.

### KnowledgeEvolutionMetrics

Computes aggregate metrics across all knowledge records: total/active/superseded/deprecated counts, average confidence/freshness/reliability, stability/volatility ratios, revision frequency, and conflict rate.

### EvolutionReportGenerator

Generates four human-readable report types:
- **Evolution Report** — Comprehensive overview with metrics, confidence summaries, conflict status, revision breakdown, stability analysis, and snapshot listing
- **Confidence Report** — Distribution by confidence level with per-record breakdown
- **Conflict Report** — Severity distribution with unresolved and resolved conflict details
- **Lifecycle Report** — Stage distribution with per-stage record listings

### Integration Bridges

Six bridge classes convert external module data into knowledge evidence:

| Bridge | Source Module | Evidence Type |
|--------|-------------|---------------|
| `OptimizationKnowledgeBridge` | GymOS Optimizer | `OPTIMIZATION_RESULT` |
| `PlanningOptimizerBridge` | Planning Optimizer | `OPTIMIZATION_RESULT` |
| `PredictionBridge` | Prediction Engine | `PREDICTION_OUTCOME` |
| `RecoveryBridge` | Recovery Monitor | `RECOVERY_OBSERVATION` |
| `NutritionBridge` | Nutrition Analyzer | `NUTRITION_OBSERVATION` |
| `DecisionBridge` | Decision Engine | `DECISION_OUTCOME` |

### Domain Events

Eight event types are published during the evolution lifecycle:

| Event | Trigger |
|-------|---------|
| `EvidenceCollected` | New evidence added to a record |
| `ConfidenceUpdated` | Confidence score changes |
| `ConflictDetected` | New conflict identified |
| `ConflictResolved` | Conflict is resolved |
| `KnowledgeRevised` | Record is revised |
| `KnowledgeDeprecated` | Record is deprecated |
| `KnowledgeVersionPublished` | New version is created |
| `SnapshotCreated` | Global snapshot is taken |

### Serializers

Full dict/JSON round-trip serialization for all domain models: `KnowledgeEvidenceSerializer`, `KnowledgeConfidenceSerializer`, `KnowledgeConflictSerializer`, `KnowledgeDeprecationSerializer`, `KnowledgeRecordSerializer`, `KnowledgeRevisionSerializer`, `KnowledgeVersionSerializer`, `KnowledgeSnapshotSerializer`, `KnowledgeLifecycleSerializer`, `KnowledgeEvolutionReportSerializer`, `EvolutionConfigSerializer`.

## Domain Models

| Model | Description |
|-------|-------------|
| `KnowledgeRecord` | A single piece of knowledge with its evidence trail, confidence, and lifecycle stage |
| `KnowledgeEvidence` | A single piece of evidence supporting or contradicting a record |
| `KnowledgeConfidence` | Bayesian-style confidence metrics (score, support/contradiction counts, freshness, reliability) |
| `KnowledgeVersion` | A versioned snapshot of a knowledge record (semver + parent chain) |
| `KnowledgeRevision` | Immutable record of a confidence score change with reason |
| `KnowledgeConflict` | A detected conflict between two knowledge records |
| `KnowledgeSnapshot` | A point-in-time snapshot of all knowledge and conflicts |
| `KnowledgeDeprecation` | Records the deprecation of a knowledge record |
| `KnowledgeLifecycle` | Tracks stage transitions for a knowledge record |
| `KnowledgeEvolutionReport` | Comprehensive evolution report data |

## Enums

| Enum | Values |
|------|--------|
| `EvidenceType` | `OPTIMIZATION_RESULT`, `PREDICTION_OUTCOME`, `RECOVERY_OBSERVATION`, `NUTRITION_OBSERVATION`, `DECISION_OUTCOME`, `USER_FEEDBACK`, `EXTERNAL_RESEARCH` |
| `ConfidenceLevel` | `VERY_LOW` (0.0–0.2), `LOW` (0.2–0.4), `MEDIUM` (0.4–0.6), `HIGH` (0.6–0.8), `VERY_HIGH` (0.8–1.0) |
| `ConflictSeverity` | `MINOR`, `MODERATE`, `MAJOR`, `CRITICAL` |
| `LifecycleStage` | `DRAFT`, `ACTIVE`, `SUPERSEDED`, `DEPRECATED`, `ARCHIVED` |
| `RevisionReason` | `NEW_EVIDENCE`, `CONFIDENCE_UPDATE`, `CONFLICT_RESOLUTION`, `DEPRECATION`, `MANUAL_REVISION` |

## Configuration

`EvolutionConfig` provides the following tunable parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `base_weight` | 1.0 | Base weight for evidence |
| `freshness_half_life_days` | 30.0 | Half-life for exponential freshness decay |
| `min_evidence_for_confidence` | 3 | Minimum evidence items for meaningful confidence |
| `conflict_threshold` | 0.3 | Threshold for conflict detection sensitivity |
| `deprecation_grace_period_days` | 14 | Grace period before auto-deprecation |
| `max_conflict_resolution_attempts` | 3 | Max attempts for auto-resolving conflicts |
| `enable_auto_evolution` | True | Master toggle for auto-evolution |
| `enable_freshness_decay` | True | Enable exponential freshness decay |
| `enable_conflict_detection` | True | Enable automatic conflict detection |
| `enable_deprecation` | True | Enable automatic deprecation |

## Usage

### Basic Usage

```python
from shared.knowledge_evolution import KnowledgeEvolutionOrchestrator
from shared.knowledge_evolution.domain import KnowledgeEvidence

orch = KnowledgeEvolutionOrchestrator()

# Add a knowledge record
record = KnowledgeRecord(
    knowledge_id="rec_1",
    domain="training",
    statement="High volume training improves hypertrophy",
)
orch.add_record(record)

# Add evidence
evidence = KnowledgeEvidence(
    knowledge_id="rec_1",
    source="optimizer",
    supports=True,
    weight=2.0,
    evidence_type=EvidenceType.OPTIMIZATION_RESULT,
)
orch.add_evidence(evidence)

# Run evolution pipeline
result = orch.evolve()

# Query results
latest = orch.get_latest_version("rec_1")
confidence = orch.get_confidence_timeline("rec_1")
print(f"Confidence score: {latest.record.confidence.score}")

# Generate reports
print(orch.generate_evolution_report())
print(orch.generate_confidence_report())
```

### Custom Configuration

```python
from shared.knowledge_evolution import KnowledgeEvolutionOrchestrator
from shared.knowledge_evolution.domain import EvolutionConfig

config = EvolutionConfig(
    freshness_half_life_days=60.0,
    min_evidence_for_confidence=5,
    enable_freshness_decay=True,
    enable_conflict_detection=True,
)
orch = KnowledgeEvolutionOrchestrator(config=config)
```

### Using Integration Bridges

```python
from shared.knowledge_evolution.integration import OptimizationKnowledgeBridge

bridge = OptimizationKnowledgeBridge()
experience = {"experience_id": "exp_1", "knowledge_id": "rec_1", "reward": 0.85}
evidence = bridge.from_optimization_experience(experience)
orch.add_evidence(evidence)
```

### Serialization

```python
# Export all state to dict
data = orch.to_dict()

# Restore from dict
restored = KnowledgeEvolutionOrchestrator.from_dict(data)
```

### State Inspection

```python
state = orch.get_state()
# {
#     "total_records": 42,
#     "total_versions": 87,
#     "total_conflicts": 3,
#     "unresolved_conflicts": 1,
#     "total_snapshots": 12,
#     "pending_evidence_count": 5,
#     "domains": ["training", "nutrition", "recovery"],
#     "active_records": 35,
#     "deprecated_records": 4,
# }
```

### Query Methods

```python
# Latest version of a record
version = orch.get_latest_version("rec_1")

# Historical version
version = orch.get_historical_version("rec_1", "v1.2.0")

# Confidence timeline
timeline = orch.get_confidence_timeline("rec_1")
# [("v1.0.0", 0.5000), ("v1.1.0", 0.6854), ("v1.2.0", 0.7219)]

# Filter records
active = orch.query_active_records()
domain_records = orch.query_by_domain("training")
high_confidence = orch.query_by_confidence(0.7)
drafts = orch.query_by_lifecycle(LifecycleStage.DRAFT)
```

## Integration Points

| Module | Integration | Bridge |
|--------|-------------|--------|
| GymOS Optimizer | Optimization experiences → evidence | `OptimizationKnowledgeBridge` |
| Planning Optimizer | Plan results → evidence | `PlanningOptimizerBridge` |
| Prediction Engine | Prediction outcomes → evidence | `PredictionBridge` |
| Recovery Monitor | Recovery observations → evidence | `RecoveryBridge` |
| Nutrition Analyzer | Nutrition observations → evidence | `NutritionBridge` |
| Decision Engine | Decision outcomes → evidence | `DecisionBridge` |
| Event Bus | Domain events published on evolution lifecycle | `events.py` |
| Knowledge Platform | Consumes evolution reports and metrics | N/A |

## Data Flow

1. External modules generate evidence via integration bridges
2. Evidence is added to the orchestrator (`add_evidence()`)
3. Evidence is stored in the repository (appended to the record's evidence list)
4. On `evolve()`:
   a. All pending evidence is aggregated into their respective records
   b. ConfidenceEngine recomputes scores for all records
   c. ConflictEngine detects and resolves conflicts
   d. Obsolete records are deprecated
   e. VersionManager creates new semantic versions
   f. A global snapshot is taken
   g. All changes are stored in the append-only repository
5. Queries, reports, and metrics are computed from the current state
6. Full state can be serialized/deserialized for persistence

## Determinism Guarantee

Same inputs always produce identical outputs:
- Same evidence → Same Bayesian confidence scores (same Beta posterior)
- Same records + evidence → Same conflict detection results
- Same version chain → Same version strings
- Same state → Same serialized output

## File Structure

```
shared/knowledge_evolution/
├── __init__.py              # KnowledgeEvolutionOrchestrator
├── domain.py                # Domain models (10 models + 5 enums)
├── evolution_engine.py      # EvolutionEngine + EvolutionResult
├── confidence.py            # ConfidenceEngine (Bayesian + freshness + reliability)
├── conflict.py              # ConflictEngine (detection, resolution, ranking)
├── version_manager.py       # VersionManager (semver, snapshots, rollback)
├── repository.py            # KnowledgeEvolutionRepository (append-only)
├── query.py                 # KnowledgeEvolutionQuery
├── metrics.py               # KnowledgeEvolutionMetrics
├── reports.py               # EvolutionReportGenerator
├── events.py                # Domain events (8 event types)
├── serializer.py            # Serializers (11 serializers)
├── integration.py           # Integration bridges (6 bridges)
└── tests/
    ├── __init__.py
    ├── test_domain.py
    ├── test_engine.py
    ├── test_evolution.py
    ├── test_events.py
    ├── test_orchestrator.py
    ├── test_integration.py
    ├── test_infrastructure.py
    └── test_full_pipeline.py  (450+ tests across all test files)
```
