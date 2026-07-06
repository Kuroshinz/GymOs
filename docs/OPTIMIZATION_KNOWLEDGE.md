# Optimization Knowledge Engine

## Overview

The Optimization Knowledge Engine is a deterministic, statistical, versioned knowledge accumulation system that mines patterns from optimization plan runs. It collects experiences from the Planning Optimizer, extracts actionable patterns through pure statistical aggregation, computes descriptive statistics with confidence intervals, derives rules, and generates insights and recommendations — all without any AI or LLM dependencies.

## Core Philosophy

- **No AI/LLM** — All pattern extraction, statistics, and reasoning is deterministic, explainable, and reproducible
- **Versioned & Append-Only** — Knowledge is immutable once written; new versions are created by extracting fresh knowledge from accumulated experiences
- **Statistical Confidence** — Every pattern includes sample size, success rate, and confidence level for informed decision-making
- **Explainable** — Every insight, rule, and recommendation traces back to specific patterns and supporting data

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 OptimizationKnowledgeOrchestrator             │
│  ┌──────────┐  ┌───────────┐  ┌───────────┐  ┌──────────┐  │
│  │Experience │  │ Pattern   │  │Statistics │  │Knowledge │  │
│  │ Engine    │  │ Mining    │  │ Engine    │  │ Extractor│  │
│  │           │  │ Engine    │  │           │  │          │  │
│  └──────────┘  └───────────┘  └───────────┘  └──────────┘  │
│  ┌──────────┐  ┌───────────┐  ┌───────────┐  ┌──────────┐  │
│  │Knowledge │  │ Knowledge │  │ Knowledge │  │ Report   │  │
│  │ Query    │  │ Metrics   │  │ History   │  │ Generator│  │
│  └──────────┘  └───────────┘  └───────────┘  └──────────┘  │
│  ┌──────────┐  ┌───────────┐                               │
│  │Repository│  │Serializer │                               │
│  └──────────┘  └───────────┘                               │
└─────────────────────────────────────────────────────────────┘
```

## Key Components

### ExperienceEngine
Collects and classifies optimization plan results into experiences. Each experience captures plan parameters (volume, frequency, split, weeks, sets, mesocycles, deload) and is classified as SUCCESS or FAILURE based on a configurable score threshold.

### PatternMiningEngine
Mines patterns across 7 dimensions:
- **Volume** — Average weekly sets (binned ranges)
- **Frequency** — Sessions per week (discrete values)
- **Split** — Training split style (categorical)
- **Recovery** — Total program weeks (binned ranges)
- **Adherence** — Mesocycle count (binned ranges)
- **Deload** — Presence of deload weeks (binary)
- **Fatigue** — Total program sets (binned ranges)

### StatisticsEngine
Computes descriptive statistics from experiences:
- Mean, median, std dev, variance, min/max scores
- Success rate
- 95% confidence interval (normal approximation via CLT)
- Trend direction and slope (linear regression)
- Moving average (configurable window)

### KnowledgeExtractor
Derives higher-level knowledge from patterns and statistics:
- **Rules** — INCREASE (success_rate >= 0.7), DECREASE (success_rate <= 0.3), MAINTAIN (otherwise)
- **Insights** — Summaries of reliable patterns with category classification
- **Recommendations** — Actionable suggestions from high-confidence INCREASE rules

### KnowledgeQueryEngine
Queries accumulated knowledge for optimal parameters:
- Best split, volume, frequency, mesocycle, progression
- Best profile by goal
- Top recommendations by confidence

### KnowledgeMetrics
Computes knowledge quality metrics:
- Total/reliable/high-confidence/low-sample pattern counts
- Pattern type coverage
- Average confidence and success rate

### KnowledgeReportGenerator
Generates human-readable reports:
- Summary report (version, stats, top patterns, rules, recommendations)
- Detailed report (all patterns by type, profiles, insights, rules, recommendations)
- State report (current version, counts, rates)

### OptimizationKnowledgeRepository
Versioned, append-only repository for experiences and knowledge snapshots. Knowledge versions are immutable once saved.

### KnowledgeHistory
Maintains a versioned history of knowledge extraction events with snapshot capabilities.

### OptimizationKnowledgeSerializer
Full dict/JSON round-trip serialization for all domain models.

## Usage

```python
from shared.optimization_knowledge import OptimizationKnowledgeOrchestrator

orchestrator = OptimizationKnowledgeOrchestrator()

# Record experiences
orchestrator.record_experience(
    plan_id="plan_1",
    overall_score=0.85,
    avg_weekly_sets=16,
    sessions_per_week=4,
    total_weeks=12,
    total_sets=192,
    mesocycle_count=3,
    has_deload=True,
    split_style="PPL",
    goal="hypertrophy",
)

# Extract knowledge
knowledge = orchestrator.extract_knowledge()

# Query
best_split = orchestrator.query_best_split()
best_volume = orchestrator.query_best_volume()

# Reports
summary = orchestrator.generate_summary_report()
detailed = orchestrator.generate_detailed_report()

# Metrics
metrics = orchestrator.get_metrics()

# State
state = orchestrator.get_state()
```

## Determinism Guarantee

Same inputs always produce identical outputs:
- Same experiences → Same patterns (same bins, same success rates)
- Same patterns → Same rules, insights, recommendations
- Same experiences → Same statistics (mean, median, std dev, CI, trend)

## Data Flow

1. User records optimization experiences via the orchestrator
2. Experiences are stored in the append-only repository
3. On `extract_knowledge()`:
   a. PatternMiningEngine mines patterns from all experiences
   b. StatisticsEngine computes descriptive statistics
   c. KnowledgeExtractor derives rules, insights, and recommendations
   d. A new versioned OptimizationKnowledge snapshot is created
   e. The knowledge is stored and the version history is updated
4. Queries, reports, and metrics are computed from the current knowledge

## Versioning

Knowledge versions follow semantic versioning (vX.Y.Z):
- First extraction: v1.0.0
- Subsequent extractions: v1.1.0, v1.2.0, etc.
- Each version tracks its parent_version for full audit trail

## File Structure

```
shared/optimization_knowledge/
├── __init__.py          # OptimizationKnowledgeOrchestrator
├── domain.py            # Domain models (10 models + 5 enums)
├── engine.py            # ExperienceEngine + KnowledgeExtractor
├── patterns.py          # PatternMiningEngine (7 pattern types)
├── statistics.py        # StatisticsEngine
├── query.py             # KnowledgeQueryEngine
├── metrics.py           # KnowledgeMetrics
├── reports.py           # KnowledgeReportGenerator
├── repository.py        # OptimizationKnowledgeRepository
├── history.py           # KnowledgeHistory
├── serializer.py        # OptimizationKnowledgeSerializer
├── events.py            # Domain events (6 event types)
└── tests/
    ├── __init__.py
    ├── test_domain.py
    ├── test_engine.py
    ├── test_patterns.py
    ├── test_statistics.py
    ├── test_query.py
    ├── test_metrics.py
    ├── test_reports.py
    ├── test_repository.py
    ├── test_history.py
    ├── test_serializer.py
    ├── test_events.py
    ├── test_orchestrator.py
    ├── test_integration.py
    └── test_full_pipeline.py
```
