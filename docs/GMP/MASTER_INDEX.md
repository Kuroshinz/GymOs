# GymOS Document Index

Single navigation page linking every architecture document, ADR, RFC, roadmap, and product document.

---

## Governing Document

| Document | Description | Link |
|---|---|---|
| **GMP-001 Master Plan** | Mission, Vision, Philosophy, Principles, Roadmap, Milestones, Version Strategy | `docs/GMP/MASTER_PLAN.md` |

---

## GMP Documents

| Document | Description | Link |
|---|---|---|
| Product Lifecycle | Concept → Prototype → Alpha → Beta → RC → Production → LTS | `docs/GMP/PRODUCT_LIFECYCLE.md` |
| Master Roadmap | Full roadmap v0.5 → v2.0 with epics, tests, metrics | `docs/GMP/MASTER_ROADMAP.md` |
| Engine Matrix | Every engine: purpose, inputs, outputs, deps, health, evolution | `docs/GMP/ENGINE_MATRIX.md` |
| Product Maturity Model | Maturity levels for every product area | `docs/GMP/PRODUCT_MATURITY_MODEL.md` |
| Engineering Governance | RFC, milestone, capability, release, deprecation, compatibility, documentation policies | `docs/GMP/ENGINEERING_GOVERNANCE.md` |

---

## Product Documents

| Document | Description | Link |
|---|---|---|
| Product Pillars | 8 pillars, cross-pillar dependencies, feature classification template | `docs/PRODUCT_PILLARS.md` |
| Engine Roadmap | Every engine's current maturity and planned evolution | `docs/ENGINE_ROADMAP.md` |
| Project Context | Identity, current phase, user profile, architecture principles | `.ai/PROJECT_CONTEXT.md` |
| Project Vision | North star, long-term vision, design philosophy, success metrics | `.ai/PROJECT_VISION.md` |
| Current Milestone | v0.5 Platform Standardization, achievements, remaining work | `.ai/CURRENT_MILESTONE.md` |
| Capability History | Capability evolution tracking, snapshots, trends, timelines | `docs/CAPABILITY_HISTORY.md` |
| Evolution Engine | Product evolution analysis, RFC impact scoring, growth rates | `docs/EVOLUTION_ENGINE.md` |
| Kernel | Product OS — product identity, RFC lifecycle, release readiness | `docs/KERNEL.md` |

---

## Architecture Documents

| Document | Description | Link |
|---|---|---|
| Architecture Overview | System design, core principles, layer boundaries, data flow | `docs/architecture/overview.md` |
| Module Boundaries | Module responsibility audit | `docs/architecture/MODULE_AUDIT.md` |
| DI Standard | Dependency injection standard | `docs/architecture/DI_STANDARD.md` |
| Event Bus | Event-driven communication architecture | `docs/architecture/event-bus.md` |
| Capability Platform | Self-describing introspection layer | `docs/architecture/CAPABILITY_PLATFORM.md` |
| Knowledge Platform | Knowledge pipeline, validation, versioning | `docs/architecture/KNOWLEDGE_PLATFORM.md` |
| Plugin SDK | Plugin development contract | `docs/architecture/plugin-sdk.md` |

---

## Architecture Decision Records

| ADR | Title | Status | Link |
|---|---|---|---|
| ADR-001 | Event Architecture | Accepted | `docs/architecture/ADR/ADR-001-event-architecture.md` |
| ADR-002 | Knowledge System | Accepted | `docs/architecture/ADR/ADR-002-knowledge-system.md` |
| ADR-003 | GymBrain Architecture | Accepted | `docs/architecture/ADR/ADR-003-gymbrain-architecture.md` |
| ADR-004 | Provider Interfaces | Accepted | `docs/architecture/ADR/ADR-004-provider-interfaces.md` |
| ADR-005 | Event-Driven Communication | Accepted | `docs/architecture/ADR/ADR-005-event-driven-communication.md` |
| ADR-006 | Capability Platform | Accepted | `docs/architecture/ADR/ADR-006-capability-platform.md` |
| ADR-007 | Product Knowledge Graph | Accepted | `docs/adr/ADR-007-product-knowledge-graph.md` |
| ADR-008 | Product State Engine | Accepted | `docs/adr/ADR-008-product-state-engine.md` |
| ADR-009 | Recovery Intelligence | Accepted | `docs/adr/ADR-009-recovery-intelligence.md` |
| ADR-010 | Predictive Intelligence (RFC-020) | Accepted | `docs/architecture/ADR-010-predictive-intelligence.md` |
| ADR-010.5 | Prediction Intelligence Upgrade (RFC-020.5) | Accepted | `docs/architecture/ADR-010.5-prediction-upgrade.md` |
| ADR-011 | Core Architecture Decisions | Accepted | `docs/adr/001-core-architecture-decisions.md` |

---

## RFC Registry

| RFC | Title | Status | ADR |
|---|---|---|---|
| RFC-018 | Capability Platform | COMPLETE | ADR-006 |
| RFC-018.5 | GymOS Kernel | IN_PROGRESS | — |
| RFC-019 | Recovery Intelligence | DRAFT | ADR-009 |
| RFC-020 | Prediction Intelligence | COMPLETE | ADR-010 |
| RFC-020.5 | Prediction Intelligence Upgrade | COMPLETE | ADR-010.5 |

---

## Engine Documentation

| Engine | Primary Doc | Tests |
|---|---|---|
| Workout Engine | `docs/ENGINE_ROADMAP.md` | 163 (via GymBrain) |
| Nutrition Engine | `docs/ENGINE_ROADMAP.md` | 49 |
| Recovery Engine | `docs/ENGINE_ROADMAP.md` | 0 |
| Decision Engine (GymBrain) | `docs/ENGINE_ROADMAP.md` | 163 |
| Prediction Engine | `docs/prediction/PREDICTION_EXPLAINABILITY.md` | 272 |
| Scenario Engine | `docs/prediction/SCENARIO_ENGINE.md` | 53 |
| Counterfactual Engine | `docs/prediction/COUNTERFACTUALS.md` | 36 |
| Explainability Engine | `docs/prediction/PREDICTION_EXPLAINABILITY.md` | 44 |
| Risk Engine | `docs/prediction/PREDICTION_EXPLAINABILITY.md` | 26 |
| AI Coach Engine | — (not started) | 0 |
| Automation Engine | — (not started) | 0 |
| Knowledge Engine | `docs/architecture/KNOWLEDGE_PLATFORM.md` | 0 |
| Physique Engine | — (not started) | 0 |

---

## Prediction Documentation

| Document | Description | Link |
|---|---|---|
| Prediction Explainability | Architecture, evidence pipeline, factor ranking, NL/MR generation | `docs/prediction/PREDICTION_EXPLAINABILITY.md` |
| Scenario Engine | Scenario lifecycle, builder, comparison, ranking, examples | `docs/prediction/SCENARIO_ENGINE.md` |
| Counterfactuals | What-if philosophy, generation pipeline, examples | `docs/prediction/COUNTERFACTUALS.md` |
| Capability Report | Architecture, documentation, testing, UX maturity; remaining gaps | `docs/prediction/CAPABILITY_REPORT.md` |

---

## Recovery Documentation

| Document | Description | Link |
|---|---|---|
| Recovery Dashboard | Widget architecture, data flow | `docs/recovery/RECOVERY_DASHBOARD.md` |
| ADR-009 Recovery Intelligence | Architecture decision record | `docs/adr/ADR-009-recovery-intelligence.md` |

---

## Roadmap Documents

| Document | Description | Link |
|---|---|---|
| Master Roadmap | Full platform roadmap v0.5 → v2.0 | `docs/GMP/MASTER_ROADMAP.md` |
| Version Roadmap | v0.5–v1.0 with epics, targets, status | `docs/roadmap/index.md` |
| Capability Growth Strategy | How capabilities progress through maturity stages | `docs/GMP/MASTER_PLAN.md` (Capability Growth Strategy section) |

---

## Platform Documents

| Document | Description | Link |
|---|---|---|
| Capability Platform | Introspection layer, registry, health, deps | `shared/capabilities/` |
| Kernel | Product OS, product identity, RFC lifecycle, release readiness | `shared/kernel/` |
| Evolution Engine | Product evolution, RFC impact, growth rates, forecasting | `shared/evolution/` |
| State Engine | Deterministic state evaluation, drift detection, transitions | `shared/state/` |
| Knowledge Graph | Typed property graph, 10 node types, impact analysis | `shared/graph/` |

---

## Agent Files

| Document | Description | Link |
|---|---|---|
| Project Vision | North star, pillars, long-term vision, design philosophy | `.ai/PROJECT_VISION.md` |
| Project Context | Identity, current phase, user profile, what NOT to build | `.ai/PROJECT_CONTEXT.md` |
| Current Milestone | v0.5 Platform Standardization, achievements, blockers | `.ai/CURRENT_MILESTONE.md` |

---

## Quick Reference

### File Tree

```
docs/
├── GMP/
│   ├── MASTER_PLAN.md
│   ├── PRODUCT_LIFECYCLE.md
│   ├── MASTER_ROADMAP.md
│   ├── ENGINE_MATRIX.md
│   ├── PRODUCT_MATURITY_MODEL.md
│   ├── ENGINEERING_GOVERNANCE.md
│   └── MASTER_INDEX.md            ← YOU ARE HERE
├── architecture/
│   ├── overview.md
│   ├── CAPABILITY_PLATFORM.md
│   ├── DI_STANDARD.md
│   ├── KNOWLEDGE_PLATFORM.md
│   ├── MODULE_AUDIT.md
│   ├── event-bus.md
│   ├── plugin-sdk.md
│   ├── ADR-010.5-prediction-upgrade.md
│   └── ADR/
│       ├── ADR-001-event-architecture.md
│       ├── ADR-002-knowledge-system.md
│       ├── ADR-003-gymbrain-architecture.md
│       ├── ADR-004-provider-interfaces.md
│       ├── ADR-005-event-driven-communication.md
│       └── ADR-006-capability-platform.md
├── adr/
│   ├── 001-core-architecture-decisions.md
│   ├── ADR-007-product-knowledge-graph.md
│   ├── ADR-008-product-state-engine.md
│   ├── ADR-009-recovery-intelligence.md
│   └── ADR-010-predictive-intelligence.md
├── prediction/
│   ├── PREDICTION_EXPLAINABILITY.md
│   ├── SCENARIO_ENGINE.md
│   ├── COUNTERFACTUALS.md
│   └── CAPABILITY_REPORT.md
├── recovery/
│   └── RECOVERY_DASHBOARD.md
├── roadmap/
│   └── index.md
├── ENGINE_ROADMAP.md
├── PRODUCT_PILLARS.md
├── CAPABILITY_HISTORY.md
├── EVOLUTION_ENGINE.md
├── KERNEL.md
├── PREDICTION.md
├── PREDICTION_ENGINE.md
├── FORECAST_MODEL.md
└── ...
```

### Search Tips

- **Architecture decisions** → `docs/architecture/ADR/` or `docs/adr/`
- **Engine specs** → `docs/ENGINE_ROADMAP.md` or `docs/GMP/ENGINE_MATRIX.md`
- **Product direction** → `docs/GMP/MASTER_PLAN.md` or `.ai/PROJECT_VISION.md`
- **Capability status** → `shared/capabilities/__init__.py`
- **RFC tracking** → `shared/kernel/kernel_state.py` or `docs/GMP/ENGINEERING_GOVERNANCE.md`
- **Prediction deep-dive** → `docs/prediction/`
- **Release readiness** → `shared/kernel/kernel_runtime.py`
