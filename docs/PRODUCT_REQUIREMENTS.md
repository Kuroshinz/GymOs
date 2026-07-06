# GymOS — Product Requirements

**Version:** v0.5 — Platform Maturity  
**Previous:** See `docs/archive/PRODUCT_REQUIREMENTS.md` for the original v0.1 MVP specification.

---

## 1. Product Overview

### 1.1 Vision
GymOS is a Personal Hypertrophy Operating System for ONE user. It exists to help the owner build the best aesthetic physique possible using data-driven training, nutrition, and recovery intelligence.

### 1.2 Mission
Replace guesswork with deterministic intelligence. Every workout, meal, and rest day is informed by the user's own data, interpreted by evidence-based rules, and presented as explainable recommendations.

### 1.3 Primary User

| Attribute | Value |
|-----------|-------|
| Description | Male, 178 cm, 63.4 kg, lean bulking to 72-75 kg |
| Training | PPL-UL split, 5-6 days/week |
| Goal | Hypertrophy — build muscle, not strength |
| Focus | Shoulders, Upper Chest, Back Width, Arms |

### 1.4 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Body weight | 63.4 → 72-75 kg | Weekly weigh-in trend |
| Strength progression | Linear 6+ months | Volume/1RM charts |
| Workout consistency | ≥85% sessions completed | Streak tracking |
| Nutrition compliance | Protein ≥140g, calories ≥2800 | Macro tracking |
| Test coverage | 688+ passing | `pytest` |
| Architecture quality | ADR, Constitution, Protocols | Platform audit |

---

## 2. Functional Domains

### 2.1 Training Intelligence

| Requirement | Status | Module |
|-------------|--------|--------|
| Workout plan management (PPL-UL templates) | ✅ v0.1 | workout_program |
| Exercise library from knowledge/ | ✅ v0.1 | workout + shared/knowledge |
| Set logging (weight, reps, RPE, RIR) | ✅ v0.1 | workout |
| Previous session comparison | ✅ v0.1 | workout |
| Personal Record detection (weight, volume, e1RM) | ✅ v0.1 | workout/application/pr_engine |
| Workout completion flow with summary | ✅ v0.1 | workout |
| Volume analysis (weekly, per muscle group) | ✅ v0.2 | gymbrain/analysis |
| Fatigue analysis (5-factor model) | ✅ v0.2 | gymbrain/analysis |
| Plateau detection (6 plateau types) | ✅ v0.2 | gymbrain/analysis |
| Progression recommendations | ✅ v0.2 | gymbrain/analysis |
| Deload detection and scheduling | ⏳ v0.6 | gymbrain/rules (detection done, UI planned) |

### 2.2 Nutrition Intelligence

| Requirement | Status | Module |
|-------------|--------|--------|
| Cronometer CSV import | ✅ v0.1 | nutrition/infrastructure |
| Daily macro display (dashboard) | ✅ v0.1 | ui/dashboard |
| Target vs actual visualization | ✅ v0.1 | ui/dashboard |
| Macro analysis engine | ✅ v3.2 | nutrition/analysis |
| Lean bulk quality analysis | ✅ v3.2 | nutrition/analysis |
| Meal logging (manual) | ✅ v3.2 | nutrition/services |
| Water/hydration tracking | ✅ v3.2 | nutrition/services |
| Nutrition summary with overall score | ✅ v3.2 | nutrition/providers |
| GymBrain nutrition integration (5 rules) | ✅ v3.2 | gymbrain/rules/nutrition_rules |
| Nutrition dashboard widgets | ⏳ v0.6 | ui/dashboard (planned) |
| Live Cronometer API sync | 📋 v0.7 | nutrition/providers (planned) |

### 2.3 Recovery Intelligence

| Requirement | Status | Module |
|-------------|--------|--------|
| Recovery domain entities (scaffolding) | ✅ v3.2.5 | recovery/domain |
| RecoveryScoreUpdated event | ✅ v3.2 | shared/events |
| DataProvider recovery_engine parameter | ✅ v0.2 | gymbrain/providers |
| Recovery rule (RecoveryRule, ConsistencyRule) | ✅ v0.2 | gymbrain/rules |
| Sleep tracking | ⏳ v0.6 | recovery (planned) |
| HRV integration | ⏳ v0.6 | recovery (planned) |
| Readiness score | ⏳ v0.6 | recovery (planned) |

### 2.4 GymBrain (Decision Intelligence)

| Requirement | Status | Module |
|-------------|--------|--------|
| Rule engine with priority × confidence ranking | ✅ v0.2 | gymbrain/rules/engine |
| 18 registered rules (training + nutrition) | ✅ v3.2 | gymbrain/services |
| DataProvider facade (typed, injectable) | ✅ v3.2 | gymbrain/providers |
| AnalysisCache with invalidation | ✅ v0.2 | gymbrain/cache |
| WeeklyReviewGenerator | ✅ v0.2 | gymbrain/services |
| Goal tracking (bodyweight, bulk quality) | ✅ v0.2 | gymbrain/analysis |
| Event-driven cache invalidation | ✅ v3.2 | shared/events/subscribers |
| Nutrition provider integration | ✅ v3.2 | gymbrain/providers |

### 2.5 Event Platform

| Requirement | Status | Module |
|-------------|--------|--------|
| Typed DomainEvent hierarchy | ✅ v0.2 | shared/events |
| Single event registry (14 events) | ✅ v3.2 | shared/events/domain_events |
| Serialization round-trips | ✅ v3.2 | shared/events/domain_events |
| EventBus with middleware | ✅ v0.2 | shared/events |
| Wildcard subscriptions | ✅ v0.2 | shared/events |
| Error isolation per subscriber | ✅ v3.2 | shared/events |
| Event replay (EventStore) | ✅ v0.2 | shared/events/store |

### 2.6 Knowledge Platform

| Requirement | Status | Module |
|-------------|--------|--------|
| KnowledgeLoader (single source of truth) | ✅ v0.2 | shared/knowledge_loader |
| KnowledgeValidator (schema, orphan, format checks) | ✅ v0.2 | shared/domain/validator |
| KnowledgeService (typed accessor) | ✅ v0.2 | shared/domain/service |
| Exercise definitions (95+ JSON) | ✅ v0.2 | knowledge/exercises |
| Muscle definitions (52 JSON) | ✅ v0.2 | knowledge/muscles |
| Progression knowledge (volume, deload, RIR, RPE) | ✅ v0.2 | knowledge/progression |
| Nutrition knowledge (macros, protein, hydration) | ✅ v0.2 | knowledge/nutrition |
| Recovery knowledge (sleep, HRV, fatigue) | ✅ v0.2 | knowledge/recovery |
| Research evidence summaries | ✅ v0.2 | knowledge/research |
| Versioned knowledge files | ✅ v3.2.5 | knowledge/* (semver in files) |

### 2.7 Dashboard

| Requirement | Status | Module |
|-------------|--------|--------|
| Today's scheduled workout / rest day | ✅ v0.1 | ui/dashboard |
| Daily calories vs target | ✅ v0.1 | ui/dashboard |
| Daily protein vs target | ✅ v0.1 | ui/dashboard |
| Current body weight with trend | ✅ v0.1 | ui/dashboard |
| Last PR highlight | ✅ v0.1 | ui/dashboard |
| Workout streak (fire icon) | ✅ v0.1 | ui/dashboard |
| GymBrain recommendations | ✅ v0.2 | ui/dashboard |
| Nutrition summary widget | ⏳ v0.6 | ui/dashboard (planned) |
| Weekly review rendering | ⏳ v0.6 | ui/dashboard (planned) |

### 2.8 Progress Charts

| Requirement | Status | Module |
|-------------|--------|--------|
| Weight trend (30/90 day) | ✅ v0.1 | ui/dashboard |
| Volume trend (weekly, by muscle group) | ✅ v0.1 | ui/dashboard |
| Strength trend (e1RM per major lift) | ✅ v0.1 | ui/dashboard |
| Workout frequency (sessions/week) | ✅ v0.1 | ui/dashboard |

---

## 3. Platform Requirements

### 3.1 Architecture

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Clean Architecture per module | ✅ | 6/7 modules use layered structure |
| Engineering Constitution | ✅ | .ai/ENGINEERING_CONSTITUTION.md |
| Architecture Decision Records | ✅ | 5 ADRs in docs/architecture/ADR/ |
| Protocol interfaces for module boundaries | ✅ | shared/interfaces/ |
| Dependency Injection Standard | ✅ | docs/architecture/DI_STANDARD.md |
| Module Responsibility Audit | ✅ | docs/architecture/MODULE_AUDIT.md |

### 3.2 Quality

| Requirement | Status | Value |
|-------------|--------|-------|
| Unit tests | ✅ | 688+ passing |
| Event serialization tests | ✅ | Round-trip verified for all 14 events |
| Rule evaluation tests | ✅ | All 18 rules tested |
| Nutrition model tests | ✅ | 49 nutrition tests |
| Provider contract tests | ✅ | Production provider tested |
| Offline-first | ✅ | Zero internet required |

### 3.3 Performance

| Requirement | Target | Status |
|-------------|--------|--------|
| App launch | <3 seconds | ✅ |
| Workout logging | <100ms | ✅ |
| Charts render | <500ms | ✅ |
| CSV import (1 year) | <5 seconds | ✅ |

---

## 4. Out of Scope

| Feature | Reason | Version |
|---------|--------|---------|
| Mobile app | Desktop-first | Not planned |
| Cloud sync | Offline-first | Not planned |
| Social features | Single user | Never |
| Multi-user / coach | Single user | Never |
| Plugin marketplace | Not needed | Never |
| Vision AI / form analysis | High complexity, low value | v1.0+ |
| Voice assistant | Low priority | v1.0+ |
| Meal planning / recipes | Cronometer handles logging | Never |
| Powerlifting focus | Hypertrophy-first | Never |
