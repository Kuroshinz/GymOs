# ADR-015: Knowledge Evolution Engine

## Status

Accepted

## Context

The NexusOS ecosystem produces substantial optimization knowledge via the Optimization Knowledge Engine (ADR-014) and other modules (prediction, recovery, nutrition, decision-making). However, this knowledge is currently static — once extracted, it does not evolve as new evidence arrives. To build a truly self-improving system, we need a mechanism that:

1. **Collects evidence** from multiple modules (optimizer, predictor, recovery, nutrition, decision engine)
2. **Computes confidence** statistically based on the volume, consistency, and freshness of evidence
3. **Detects conflicts** when evidence contradicts existing knowledge
4. **Resolves conflicts** automatically by promoting higher-confidence knowledge
5. **Versions knowledge** with full audit trail and rollback support
6. **Evolves autonomously** as new evidence accumulates
7. **Generates reports** on knowledge quality, conflicts, and lifecycle
8. **Operates deterministically** — no AI/LLM, all pure statistics

The existing optimization knowledge system (ADR-014) collects experiences and mines patterns, but it does not support continuous evidence-driven evolution, Bayesian confidence updates, freshness decay, or conflict resolution across domains.

## Decision

Create a new `knowledge_evolution` module that provides evidence-driven, self-evolving knowledge capabilities. The module is a standalone system with its own domain models, engines, repository, and query layer, connected to other modules via integration bridges.

### Architecture

```
KnowledgeEvolutionOrchestrator
├── EvolutionEngine          — Pipeline orchestrator
│   ├── ConfidenceEngine     — Bayesian + freshness + reliability scoring
│   ├── ConflictEngine       — Conflict detection & resolution
│   └── VersionManager       — Semantic versioning & snapshots
├── KnowledgeEvolutionRepository  — Append-only immutable store
├── KnowledgeEvolutionQuery       — Query helpers
├── KnowledgeEvolutionMetrics     — Aggregate metrics
├── EvolutionReportGenerator      — Human-readable reports
├── Serializers                   — Full round-trip dict/JSON
└── Integration Bridges           — Module → evidence conversion
    ├── OptimizationKnowledgeBridge
    ├── PlanningOptimizerBridge
    ├── PredictionBridge
    ├── RecoveryBridge
    ├── NutritionBridge
    └── DecisionBridge
```

### Domain Models

All models are frozen dataclasses for immutability:

| Model | Purpose |
|-------|---------|
| `KnowledgeRecord` | A knowledge statement with evidence trail and lifecycle |
| `KnowledgeEvidence` | A single supporting or contradicting observation |
| `KnowledgeConfidence` | Bayesian-style confidence with 3 sub-scores |
| `KnowledgeVersion` | Semantic version (vX.Y.Z) with parent chain |
| `KnowledgeRevision` | Immutable confidence change record |
| `KnowledgeConflict` | Detected conflict between two records |
| `KnowledgeSnapshot` | Point-in-time state capture |
| `KnowledgeDeprecation` | Deprecation record |
| `KnowledgeLifecycle` | Lifecycle stage transition |
| `KnowledgeEvolutionReport` | Aggregate report data |

### Enums

- `EvidenceType`: 7 types (optimization_result, prediction_outcome, recovery_observation, nutrition_observation, decision_outcome, user_feedback, external_research)
- `ConfidenceLevel`: 5 levels (very_low → very_high)
- `ConflictSeverity`: 4 levels (minor → critical)
- `LifecycleStage`: 5 stages (draft → active → superseded → deprecated → archived)
- `RevisionReason`: 5 reasons (new_evidence, confidence_update, conflict_resolution, deprecation, manual_revision)

### Confidence Model

Three sub-scores weighted into overall confidence:

```
Overall = Bayesian × 0.4 + Freshness × 0.3 + Reliability × 0.3
```

- **Bayesian** — Beta distribution posterior mean with uniform prior Beta(1, 1): `(support + 1) / (support + contradiction + 2)`
- **Freshness** — Exponential decay: `exp(-age_days × ln(2) / half_life)` with configurable half-life (default: 30 days)
- **Reliability** — Source consistency: `support / (support + contradiction)`, defaults to 0.5 below minimum evidence threshold (default: 3)

### Conflict Detection & Resolution

- Two records conflict when their confidence scores are on opposite sides of 0.5 and both have sufficient evidence
- Conflicts are resolved by superseding the lower-confidence record
- Severity levels: CRITICAL (diff >= 0.6), MAJOR (diff >= 0.4), MODERATE (diff >= 0.2), MINOR (diff < 0.2)
- Configurable: `enable_conflict_detection`, `max_conflict_resolution_attempts`

### Versioning

- Semantic versioning vX.Y.Z (minor auto-incremented on each evolution)
- Parent version chain for full audit trail
- Timestamped point-in-time snapshots
- Rollback support via version history query

### Repository

- Append-only for versions, conflicts, revisions, and snapshots
- Records are overwritable by knowledge_id (latest state)
- Full serialization/deserialization to dict/JSON

### Domain Events

Eight event types published during the evolution lifecycle: `EvidenceCollected`, `ConfidenceUpdated`, `ConflictDetected`, `ConflictResolved`, `KnowledgeRevised`, `KnowledgeDeprecated`, `KnowledgeVersionPublished`, `SnapshotCreated`. Events use the shared `DomainEvent` base class from `shared.events.event`.

### Integration Bridges

Six bridge classes convert external module data into `KnowledgeEvidence` without direct cross-module imports. Each bridge accepts dict-like data or prototype objects:

- `OptimizationKnowledgeBridge` — GymOS optimizer experiences and patterns
- `PlanningOptimizerBridge` — Planning optimizer results and candidates
- `PredictionBridge` — Prediction outcomes with error-based weighting
- `RecoveryBridge` — Recovery observations with success/failure classification
- `NutritionBridge` — Nutrition observations with impact scoring
- `DecisionBridge` — Decision outcomes with result classification

### No AI/LLM

All computations are pure statistics:
- Bayesian confidence = closed-form Beta distribution formula
- Freshness = deterministic exponential decay
- Reliability = simple proportion
- Conflict detection = threshold comparison
- Conflict resolution = score comparison
- All deterministic, explainable, and reproducible

## Consequences

### Positive

1. **Self-evolving knowledge** — Knowledge improves autonomously as new evidence accumulates
2. **Full audit trail** — Every confidence change, version, and conflict is immutably recorded
3. **Explainable scores** — Every confidence score decomposes into interpretable sub-scores
4. **Conflict resolution** — Contradictions are automatically detected and resolved
5. **Deterministic** — Same evidence always produces same confidence scores
6. **No AI dependencies** — Zero external model calls, fully reproducible
7. **450+ tests** — Comprehensive test coverage across all components (domain, engine, confidence, conflict, versioning, orchestrator, integration, events, serialization, infrastructure)
8. **Integration bridges** — Clean separation from source modules via bridge pattern
9. **Configurable** — Half-life, thresholds, toggles all configurable via `EvolutionConfig`
10. **Serializable** — Full round-trip serialization for persistence and state transfer

### Negative

1. **In-memory repository** — Current implementation stores everything in memory; no persistent database backend
2. **Simple conflict resolution** — Resolution is always "lower confidence is superseded"; no merging or manual override support
3. **Minor-only version bumps** — Major and patch versions are reserved but not auto-incremented
4. **No cross-domain conflict detection** — Conflicts are only detected within the same domain
5. **Freshness based on newest evidence only** — Does not consider evidence distribution over time
6. **No persistence** — Repository is in-memory; serialization to dict/JSON must be managed by the caller

## Technical Notes

- All domain models are frozen dataclasses with `from __future__ import annotations`
- Confidence engine supports both `compute_confidence` (from scratch) and `update_confidence` (incremental)
- All engines accept optional `EvolutionConfig` parameter for customization
- Freshness decay can be disabled via `enable_freshness_decay`
- Conflict detection can be disabled via `enable_conflict_detection`
- Evidence weight is clamped to >= 0.1 across all bridges
- Events registered in `KNOWLEDGE_EVOLUTION_EVENT_REGISTRY`
- 450+ tests across 8 test files:
  - `test_domain.py` — Model creation, immutability, property access, comparison
  - `test_engine.py` — ConfidenceEngine, ConflictEngine, VersionManager (563+ lines)
  - `test_evolution.py` — EvolutionEngine pipeline
  - `test_events.py` — Event creation and registry
  - `test_orchestrator.py` — Orchestrator facade (578+ lines)
  - `test_integration.py` — Integration bridges
  - `test_infrastructure.py` — Repository, serializers, metrics, reports, queries
  - `test_full_pipeline.py` — End-to-end evolution pipeline

### Related Documents

- [KNOWLEDGE_EVOLUTION.md](../KNOWLEDGE_EVOLUTION.md) — Comprehensive system overview
- [KNOWLEDGE_VERSIONING.md](../KNOWLEDGE_VERSIONING.md) — Versioning and snapshot details
- [EVIDENCE_ENGINE.md](../EVIDENCE_ENGINE.md) — Evidence/confidence system details
- [ADR-014: Optimization Knowledge Engine](ADR-014-optimization-knowledge.md) — Precursor static knowledge system
- [ADR-002: Knowledge System](../adr/ADR-002-knowledge-system.md) — Original knowledge system architecture

### Module Location

```
shared/knowledge_evolution/
├── __init__.py              # KnowledgeEvolutionOrchestrator
├── domain.py                # Domain models + enums + config
├── evolution_engine.py      # EvolutionEngine + EvolutionResult
├── confidence.py            # ConfidenceEngine
├── conflict.py              # ConflictEngine
├── version_manager.py       # VersionManager
├── repository.py            # KnowledgeEvolutionRepository
├── query.py                 # KnowledgeEvolutionQuery
├── metrics.py               # KnowledgeEvolutionMetrics
├── reports.py               # EvolutionReportGenerator
├── events.py                # Domain events
├── serializer.py            # Serializers
├── integration.py           # Integration bridges
└── tests/                   # 450+ tests across 8 files
```
