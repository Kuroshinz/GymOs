# GymOS Roadmap

## v0.5 — Platform Maturity ✅

*Current version*

**Identity:** Platform  
**Theme:** Architecture hardening, standardization, Nutrition Intelligence

| Area | Status |
|------|--------|
| Engineering Constitution | ✅ |
| 5 ADRs (Event, Knowledge, GymBrain, Providers, Communication) | ✅ |
| Protocol interfaces (7 total) | ✅ |
| DI Standard + dependency graph | ✅ |
| Module Responsibility Audit | ✅ |
| Knowledge Platform (validated pipeline) | ✅ |
| 4 Engineering Standards | ✅ |
| Nutrition Intelligence (49 tests) | ✅ |
| Test infrastructure + conftest | ✅ |
| All module READMEs | ✅ |

**688 tests passing**

---

## v0.6 — Recovery Intelligence ⏳

*Next sprint*

**Identity:** Coach  
**Theme:** Recovery tracking, deload scheduling, nutrition UI, weekly review

| Epic | Description |
|------|-------------|
| Recovery Module | Sleep tracking, HRV, fatigue, readiness score — domain entities through infrastructure |
| Deload Scheduling | Scheduler that detects accumulated fatigue and suggests deload weeks |
| Nutrition Dashboard | Daily nutrition widget, macro target editing, meal log UI |
| Weekly Review UI | Render WeeklyReview from GymBrain as a rich dashboard section |
| Goal Configuration | Macro target configuration, weight goal management |

**Target: 800+ tests**

---

## v0.7 — Prediction Engine

**Identity:** Analyst  
**Theme:** Trend prediction, forecasting, smart recommendations

| Epic | Description |
|------|-------------|
| Prediction Engine | Plateau timing prediction, goal completion forecasting |
| Performance Trends | Automated trend analysis on all tracked metrics |
| Cronometer API Sync | Live nutrition import (replaces CSV workflow) |
| Recovery Provider | Wire IRecoveryProvider into DataProvider |

**Target: 900+ tests**

---

## v0.8 — AI Coach

**Identity:** Coach  
**Theme:** Natural language explanations, adaptive guidance

| Epic | Description |
|------|-------------|
| Recommendation NLG | Convert RuleResult into natural language explanations |
| Context-Aware Coaching | Recommendations consider training history, nutrition, recovery simultaneously |
| Adaptive Rule Prioritization | Rules reorder based on user's current phase/goals |
| Progress Narrative | Monthly summary in natural language |

**Target: 1000+ tests**

---

## v0.9 — Adaptive Programming

**Identity:** Autopilot  
**Theme:** Self-tuning programs, automated adjustments

| Epic | Description |
|------|-------------|
| Auto-Adjustment Engine | Modify program parameters based on recovery/nutrition data |
| Dynamic Exercise Selection | Swap exercises based on plateau detection and variety needs |
| Volume Auto-Regulation | Adjust weekly volume based on recovery trend |
| Deload Auto-Scheduling | Automatic deload insertion based on fatigue model |

**Target: 1100+ tests**

---

## v1.0 — Full Autopilot

**Identity:** Operating System  
**Theme:** Complete, polished, production-ready

| Criteria | Definition |
|----------|------------|
| All 7 pillars implemented | Training, Nutrition, Recovery, Consistency, Intelligence, Automation, Knowledge |
| Recovery module complete | Sleep, HRV, readiness, deload |
| Prediction engine live | Forecasting plateaus, goal timing, performance trends |
| AI Coach integrated | Natural language explanations for all recommendations |
| Adaptive programming | Program auto-adjusts weekly |
| 1200+ tests | All passing |
| Performance targets met | Launch <1s, logging <100ms, charts <500ms |
| Documentation complete | Product, architecture, ADR, user guide |

---

## Legend

- ✅ Complete
- ⏳ In progress
- 📋 Planned
