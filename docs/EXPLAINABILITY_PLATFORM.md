# GymOS Explainability Platform

## Overview

The Explainability Platform (`shared/explainability/`) transforms GymOS from an intelligent decision system into an explainable intelligence platform. Every recommendation, prediction, adaptation, optimization, or planning decision becomes traceable, auditable, deterministic, and human understandable.

This is a **platform**, not a feature. It consumes canonical outputs only, never creates business logic, never changes decisions — it only explains them.

## Quick Start

```python
from shared.explainability import create_explainability_platform
from shared.events.event import DomainEvent

platform = create_explainability_platform()

# Collect evidence from a domain event
event = DomainEvent(event_name="prediction.updated")
platform.collect_event(event)

# Add evidence directly
from shared.explainability.domain import EvidenceSource, EvidenceType
from shared.explainability.evidence import EvidenceItem
item = EvidenceItem(
    evidence_id="evt-001",
    source=EvidenceSource.RECOVERY,
    evidence_type=EvidenceType.SCORE,
    label="Recovery Score: 78",
    confidence=0.85,
)
platform.add_evidence(item)

# Build a reasoning chain
from shared.explainability.domain import ReasonNodeType
from shared.explainability.reason_tree import ReasonNode
platform.reason_tree.add_node(ReasonNode(
    node_id="rec-001", node_type=ReasonNodeType.RECOMMENDATION, label="Increase Volume",
    confidence=0.8, parent_id="dec-001",
))

# Explain a recommendation
explanation = platform.explain_recommendation("rec-001")

# Generate reports
report = platform.generate_full_report()  # Markdown
json_report = platform.generate_evidence_report(fmt=ReportFormat.JSON)
```

## Architecture

```
ExplainabilityPlatform
├── evidence              — EvidenceGraph (typed evidence items, 8 sources)
├── reason_tree           — ReasonTree (reasoning chains, 6 node types)
├── confidence            — ConfidenceEngine (5-dimension weighted aggregation)
├── counterfactual        — CounterfactualEngine (10 deterministic actions)
├── impact_traces         — ImpactTraceStore (RFC→UI audit traces)
└── reports               — ReportGenerator (6 report formats)
```

## Core Concepts

### Evidence Sources
- Decision Engine — recommendations, rules, analyses
- Prediction — forecasts, ETAs, plateau predictions
- Recovery — scores, readiness, deload recommendations
- Planning — macrocycles, mesocycles, session plans
- Intent — goals, preferences, constraints
- Knowledge — evidence, confidence, conflicts
- Adaptive Programming — recommendations, decisions, scenarios
- Optimization — candidates, patterns, insights

### Reasoning Chain
Every recommendation traces back through: Intent → Knowledge → Recovery → Prediction → Decision → Recommendation

### Confidence Model
5 weighted dimensions: Prediction (25%), Knowledge Quality (20%), Recovery Quality (15%), Planning Certainty (15%), Evidence Strength (25%)

### Counterfactuals
10 deterministic action alternatives with risk assessment, expected outcome, and confidence scoring.

### Impact Trace
Full audit path: RFC → Capability → Decision → Recommendation → UI
