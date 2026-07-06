# ADR-020: GymOS Explainability Platform

## Status

Accepted

## Context

GymOS makes intelligent decisions across 8+ engines (Decision, Prediction, Recovery, Planning, Intent, Knowledge, Adaptive, Optimization). Every recommendation, prediction, adaptation, optimization, or planning decision must become traceable, auditable, deterministic, and human understandable. Without a canonical explanation layer, each consuming subsystem (AI Coach, Digital Twin, Runtime, Command Center, Analytics) would build its own ad-hoc explanation logic, leading to duplication and inconsistency.

## Decision

Create `shared/explainability/` as a platform — not a feature — that provides:

| Component | Responsibility |
|---|---|
| `evidence.py` | Collect evidence from all 8 engine sources, structure as typed evidence items |
| `reason_tree.py` | Build complete reasoning chains (Intent → Knowledge → Recovery → Prediction → Decision → Recommendation) |
| `confidence.py` | Aggregate confidence from Prediction, Knowledge quality, Recovery quality, Planning certainty, Evidence strength |
| `counterfactual.py` | Generate deterministic alternatives with expected outcome, risk, and confidence |
| `impact_trace.py` | Trace RFC → Capability → Decision → Recommendation → UI for full auditing |
| `reports.py` | Generate Markdown, JSON, Timeline, Tree, Evidence, and Recommendation reports |
| `platform.py` | Composite root with `create_explainability_platform()` factory |

### Key Design Rules

- **No AI, no LLM** — all logic is deterministic
- **No duplicated logic** — consumes existing engine outputs via shared public types, never reimplements business logic
- **No module internals** — only imports from `shared.*` packages (`shared.events`, `shared.explainability`), never from `modules/`, `nexus/`, or `core/`
- **Pure deterministic platform** — identical inputs always produce identical outputs
- **Consumes canonical outputs** — evidence is collected from domain events and structured data, never from internal engine state

## Architecture

```
ExplainabilityPlatform
├── EvidenceGraph          — typed evidence items from 8 engine sources
├── ReasonTree             — immutable reasoning chains with confidence
├── ConfidenceEngine       — weighted aggregation (5 dimensions)
├── CounterfactualEngine   — 10 deterministic action alternatives
├── ImpactTraceStore       — RFC → Capability → Decision → Recommendation → UI
└── ReportGenerator        — 6 report formats (Markdown, JSON, Timeline, Tree, Evidence, Recommendation)
```

## File Impact

- 9 new source files in `shared/explainability/`
- 8 new test files in `tests/unit/explainability/` (474 tests)
- 0 modifications to existing business logic or engines
- 6 new documentation files

## Consequences

Positive:
- Canonical explanation layer consumed by all future subsystems
- Every recommendation has a complete reasoning chain
- Every confidence score is decomposable into 5 weighted dimensions
- Every adaptive action has deterministic counterfactual alternatives
- Full audit trail via impact traces
- Zero duplicated business logic

Negative:
- Additional abstraction layer
- Evidence collection depends on domain event coverage
