# GMP-001 — GymOS Master Plan

**Status:** Ratified  
**Version:** 1.0  
**Date:** July 2026  
**Supersedes:** All prior ad-hoc planning documents

---

## Mission

Build the definitive Personal Hypertrophy Operating System — a single-user intelligence platform that answers **"What should I do today to build my best physique?"** with deterministic, explainable, data-driven precision.

---

## Vision

| Horizon | State |
|---------|-------|
| **v1.0 (12 months)** | Full Autopilot — the user trains, GymOS optimizes every variable. 1200+ tests, all 7 pillars operational, 8 engines mature. |
| **v2.0 (24 months)** | Digital Twin — longitudinal athlete model with adaptation tracking, injury risk prediction, form decay detection, and automated program evolution. Self-evolving platform. |
| **v5.0 (5 years)** | Autonomous Coach — GymOS operates as an independent intelligence that understands the user's physiology, psychology, and lifestyle well enough to program, motivate, and adapt in real time without manual input. |

---

## Core Philosophy

**GymOS is not a fitness app. GymOS is an operating system for hypertrophy.**

### Foundational Beliefs

1. **One user, perfectly served.** Every feature evaluated against: "Does this help the user build muscle?"
2. **Deterministic > Probabilistic.** Rules and engines always produce the same output from the same input. Never use LLMs for business logic.
3. **Offline-first by mandate.** Zero internet required. Sync is convenience, not architecture.
4. **Knowledge-powered.** All fitness science in `knowledge/`. No module bypasses it.
5. **Event-driven.** All cross-module communication through EventBus. No cross-module imports.
6. **Clean Architecture.** Every module: Domain → Application → Infrastructure → Presentation.
7. **Explainable by design.** Every prediction, recommendation, and decision must be traceable to its inputs.

### What GymOS Is NOT

- NOT a social fitness app
- NOT a powerlifting tracker
- NOT a generic calorie counter
- NOT a multi-user platform
- NOT a cloud service
- NOT a marketplace or plugin ecosystem

---

## Product Principles

| # | Principle | Rationale |
|---|-----------|-----------|
| 1 | **One product, one user** | Every design decision optimized for a single athlete profile |
| 2 | **Data-driven, not hype-driven** | Training decisions from user history, not generic programs |
| 3 | **Minimalist** | Features that don't directly improve a pillar are rejected |
| 4 | **Calm, premium, fast** | No noise, polished interactions, instant startup |
| 5 | **Offline-first** | Zero internet required |
| 6 | **Knowledge-powered** | All science in `knowledge/`, consumed through typed interfaces |
| 7 | **Deterministic explainability** | Same inputs → same outputs; every output explainable |

---

## Engineering Principles

| # | Principle | Enforced By |
|---|-----------|-------------|
| 1 | **Clean Architecture** per module | Dependency rules verified at code review |
| 2 | **No cross-module imports** | EventBus for all inter-module communication |
| 3 | **Typed Provider interfaces** | Protocol/ABC classes; mocks required for tests |
| 4 | **Deterministic engines** | No random seeds, no external API calls in business logic |
| 5 | **Test-first for engines** | All engines require ≥80% branch coverage |
| 6 | **Documentation as code** | ADRs for architectural decisions; README per module; docs/ for product |
| 7 | **RFC-driven changes** | Every significant change requires an RFC, review, and ADR |
| 8 | **Capability registration** | Every module registers maturity, health, deps in Capability Platform |
| 9 | **Backward compatibility** | No breaking changes without deprecation cycle (1 minor version) |
| 10 | **Offline-first infrastructure** | No external service required for core functionality |

---

## Roadmap

| Version | Identity | Theme | Key Deliverables | Test Target |
|---------|----------|-------|------------------|-------------|
| **v0.5** | Platform | Architecture hardening, Nutrition Intelligence | Engineering Constitution, ADRs, Providers, DI, Capability Platform, Knowledge Platform, GymBrain (18 rules) | 688 |
| **v0.6** | Coach | Recovery Intelligence | Sleep/HRV/fatigue tracking, deload scheduling, nutrition UI, weekly review rendering, recovery provider | 800 |
| **v0.7** | Analyst | Prediction Engine | 9 prediction types, scenario simulation (10 interventions), counterfactual analysis (5 queries), explainability, risk metrics, 5 UI widgets | 900 |
| **v0.8** | Coach | AI Coach | NLG recommendations, multi-rule synthesis, adaptive rule prioritization, progress narrative | 1000 |
| **v0.9** | Autopilot | Adaptive Programming | Auto-adjustment engine, dynamic exercise selection, volume auto-regulation, auto-deload | 1100 |
| **v1.0** | OS | Full Autopilot | All 7 pillars operational, 13 prediction engines live, AI Coach integrated, adaptive programming, digital twin foundation | 1200+ |
| **v2.0** | Twin | Digital Athlete | Longitudinal models, adaptation tracking, injury risk, form decay, automated evolution | 2000+ |

---

## Milestones

| Milestone | Version | Criteria | Dependencies |
|-----------|---------|----------|--------------|
| Platform Maturity | v0.5 | 688 tests, 6 capabilities COMPLETE, Engineering Constitution, 5 ADRs | None |
| Recovery Intelligence | v0.6 | Recovery module end-to-end, deload scheduler, nutrition dashboard, 800 tests | Platform Maturity |
| Prediction Intelligence | v0.7 | 272 prediction tests, 13 engines, scenario/counterfactual/explainability/risk, 900 tests | Platform Maturity |
| AI Coach | v0.8 | NLG engine, multi-rule synthesis, 1000 tests | Prediction Intelligence |
| Adaptive Programming | v0.9 | Auto-adjustment engine, dynamic exercises, volume auto-regulation, 1100 tests | AI Coach |
| Full Autopilot | v1.0 | All capabilities IMPLEMENTED+, 1200+ tests, performance targets met | All prior |
| Digital Twin | v2.0 | Athlete models, adaptation tracking, 2000+ tests | v1.0 |

---

## Version Strategy

```
Semantic versions with product identity:

v<major>.<minor>.<patch>
  │       │       └─ Hotfixes, small improvements
  │       └─ Capability milestones (new pillar delivered)
  └─ Platform rewrites, architecture overhauls

Release cadence: milestone-driven, not time-driven.
Each version ships when all its criteria are met.
```

### Version Identity Map

| Version | Identity | Phase | Stage |
|---------|----------|-------|-------|
| v0.1–0.4 | Prototype | Pre-product | Not tracked |
| v0.5 | Platform | Alpha | Foundation |
| v0.6 | Coach | Alpha | Foundation |
| v0.7 | Analyst | Alpha | Foundation |
| v0.8 | Coach | Alpha | Growth |
| v0.9 | Autopilot | Beta | Growth |
| v1.0 | Operating System | Stable | Optimization |
| v1.x | Iterations | Stable | Optimization |
| v2.0 | Digital Twin | Mature | Expansion |
| v3.0+ | Autonomous | Mature | Expansion |

---

## Capability Growth Strategy

### Growth Model

```
CONCEPT → DESIGN → FOUNDATION → IMPLEMENTED → STABLE → ADVANCED → OPTIMIZED → SELF-EVOLVING
```

Each capability progresses through these stages. A capability is not "done" until it reaches at least **IMPLEMENTED**.

### Current State (v0.5)

| Capability | Current | Target | Status |
|---|---|---|---|
| Training Intelligence | IMPLEMENTED | STABLE | COMPLETE |
| Nutrition Intelligence | IMPLEMENTED | STABLE | COMPLETE |
| Knowledge Platform | IMPLEMENTED | STABLE | COMPLETE |
| Event Platform | IMPLEMENTED | STABLE | COMPLETE |
| Capability Platform | IMPLEMENTED | STABLE | COMPLETE |
| Product Intelligence | IMPLEMENTED | STABLE | COMPLETE |
| Decision Intelligence | FOUNDATION | IMPLEMENTED | IN_PROGRESS |
| Prediction Engine | IMPLEMENTED | STABLE | COMPLETE |
| Recovery Intelligence | DESIGN | IMPLEMENTED | NOT_STARTED |
| Experience Platform | CONCEPT | DESIGN | NOT_STARTED |
| AI Coach | CONCEPT | DESIGN | NOT_STARTED |
| Digital Twin | CONCEPT | DESIGN | NOT_STARTED |

### Target (v1.0)

All capabilities at IMPLEMENTED+, 5 at STABLE+, 2 at ADVANCED.

### Target (v2.0)

3 capabilities at OPTIMIZED, Digital Twin at IMPLEMENTED, remaining at STABLE+.

---

## AI Roadmap

### Phase 1 — Deterministic Intelligence (v0.5–v0.7) ✅
- 18 GymBrain rules (training + nutrition)
- 13 Prediction engines (forecast + scenario + counterfactual + explainability + risk)
- All purely deterministic — same inputs, same outputs

### Phase 2 — Rule-to-Text NLG (v0.8)
- Convert structured RuleResult into natural language explanations
- Template-based, no LLM dependency
- Adaptive tone and depth based on context

### Phase 3 — Multi-Rule Synthesis (v0.8)
- Combine recommendations from training, nutrition, recovery, prediction
- Rank and prioritize across domains
- Produce unified weekly narrative

### Phase 4 — Adaptive Prioritization (v0.9)
- Rules reorder based on user's current phase/goals
- Prediction-aware recommendation weighting
- Context-sensitive coaching

### Phase 5 — Digital Twin (v2.0+)
- Longitudinal athlete adaptation model
- Injury risk prediction from form/volume patterns
- Automated program evolution from historical response data

---

## Automation Roadmap

### Level 0 — Manual (v0.1–v0.4)
- All decisions manual
- App is a structured logger

### Level 1 — Inform (v0.5) ✅
- GymBrain detects plateaus, fatigue, imbalances
- Recommendations presented to user
- User decides what to act on

### Level 2 — Suggest (v0.6–v0.7)
- Deload scheduling suggested from fatigue data
- Nutrition adjustments suggested from macro tracking
- Scenario simulations show "what if" outcomes
- Prediction risk levels guide user attention

### Level 3 — Act with Approval (v0.8–v0.9)
- Deload weeks auto-inserted, user approves
- Volume auto-regulated from recovery trend, user reviews
- Exercise swaps suggested with rationale

### Level 4 — Auto-pilot (v1.0)
- Program auto-adjusts weekly
- User intervention only for exceptions
- All recommendations have NL explanations

### Level 5 — Autonomous (v2.0+)
- Program evolves from athlete's historical response
- Injury risk auto-mitigated
- Nutrition adjusts from training load automatically
- User only trains and logs — everything else automated
