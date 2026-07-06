# Master Roadmap

## v0.5 — Platform Maturity ✅

**Version:** 0.5.0  
**Identity:** Platform  
**Phase:** Alpha (Foundation)  
**RFCs:** RFC-018 (Capability Platform), RFC-018.5 (GymOS Kernel), RFC-020 (Prediction Intelligence), RFC-020.5 (Prediction Intelligence Upgrade)

### Capabilities COMPLETE (7)
- [x] Training Intelligence — 163 tests, IMPLEMENTED
- [x] Nutrition Intelligence — 49 tests, IMPLEMENTED
- [x] Knowledge Platform — validated pipeline, IMPLEMENTED
- [x] Event Platform — 14 domain events, IMPLEMENTED
- [x] Capability Platform — registry, health, deps, IMPLEMENTED
- [x] Product Intelligence — self-describing product metadata, IMPLEMENTED
- [x] Prediction Engine — 272 tests, IMPLEMENTED (NEW)

### Capabilities IN_PROGRESS (1)
- [~] Decision Intelligence — 163 tests, FOUNDATION (40% complete)

### Key Deliverables
- Engineering Constitution
- 5 ADRs (001–006)
- 7 Provider interfaces
- 13 prediction engines + 4 analysis engines
- 5 prediction UI widgets
- 484 total tests
- 12 registered capabilities

### Dependencies Met
- [x] GymDatabase (SQLite)
- [x] EventBus singleton
- [x] Knowledge Platform pipeline
- [x] Provider interface pattern

---

## v0.6 — Recovery Intelligence ⏳

**Version:** 0.6.0  
**Identity:** Coach  
**Phase:** Alpha (Foundation)  
**RFC:** RFC-019

### Capabilities Targeted
- [ ] Recovery Intelligence — DESIGN → IMPLEMENTED
- [ ] Experience Platform — CONCEPT → DESIGN (nutrition widgets)

### Epics
| Epic | Scope | Tests |
|------|-------|-------|
| Recovery Domain | SleepLog, HRVRecord, FatigueScore, RecoverySession entities | 50 |
| Recovery Engine | Sleep analysis, fatigue trends, readiness composite | 30 |
| Deload Scheduler | Algorithm detecting accumulated fatigue, suggesting deload weeks | 20 |
| Nutrition Dashboard | Daily macro widget, meal log UI, target editing | 25 |
| Weekly Review UI | Rich dashboard section rendering WeeklyReview from GymBrain | 20 |
| Recovery Provider | IRecoveryProvider implementation wrapping RecoveryService | 10 |
| Recovery Events | SleepLogged, FatigueUpdated, ReadinessComputed, DeloadScheduled | 10 |

### Current Blocker
- Recovery Intelligence blocked by recovery-settings (UI for sleep/fatigue targets)

### Target Metrics
- **Tests:** 800+ (current: 484)
- **Capabilities COMPLETE:** 8/12
- **Overall Health:** 60+

---

## v0.7 — Prediction Intelligence ✅

**Version:** 0.7.0  
**Identity:** Analyst  
**Phase:** Alpha (Foundation)  
**RFCs:** RFC-020, RFC-020.5

### Status
**Already completed in v0.5** — accelerated delivery.

### Capabilities
- [x] Prediction Engine — CONCEPT → IMPLEMENTED (272 tests)

### Remaining Polish
- [ ] Forecast timeline chart widgets (visualize prediction trends)
- [ ] Interactive scenario builder (custom delta parameters)
- [ ] Historical trend explanations (compare explainability over time)
- [ ] Compound counterfactuals (multi-behavior what-if)

---

## v0.8 — AI Coach

**Version:** 0.8.0  
**Identity:** Coach  
**Phase:** Alpha (Growth)  
**RFC:** TBD

### Capabilities Targeted
- [ ] AI Coach — CONCEPT → DESIGN → FOUNDATION

### Epics
| Epic | Scope | Tests |
|------|-------|-------|
| Rule-to-Text NLG | Convert structured RuleResult into natural language | 40 |
| Multi-Rule Synthesis | Combine recommendations across domains | 25 |
| Adaptive Tone | Context-sensitive coaching language (motivational, analytical, urgent) | 15 |
| Progress Narrative | Weekly/monthly natural language summary | 20 |
| Explainability Enhancement | Surface GymBrain reasoning in AI Coach output | 15 |

### Target Metrics
- **Tests:** 1000+ (current: 484)
- **Capabilities COMPLETE:** 9/12
- **Overall Health:** 70+

---

## v0.9 — Adaptive Programming

**Version:** 0.9.0  
**Identity:** Autopilot  
**Phase:** Beta (Growth)  
**RFC:** TBD

### Capabilities Targeted
- [ ] Automation — CONCEPT → FOUNDATION → IMPLEMENTED
- [ ] Decision Intelligence — FOUNDATION → IMPLEMENTED

### Epics
| Epic | Scope | Tests |
|------|-------|-------|
| Auto-Adjustment Engine | Modify program parameters from recovery/nutrition/prediction | 50 |
| Dynamic Exercise Selection | Swap plateaued exercises, variety-based rotation | 30 |
| Volume Auto-Regulation | Adjust weekly volume from recovery trend, fatigue, MRV | 25 |
| Auto-Deload Scheduling | Automatic deload insertion from fatigue model | 20 |
| Recommendation Ranking | Weight and order recommendations by urgency/impact | 20 |

### Target Metrics
- **Tests:** 1100+ (current: 484)
- **Capabilities COMPLETE:** 10/12
- **Overall Health:** 75+

---

## v1.0 — Full Autopilot

**Version:** 1.0.0  
**Identity:** Operating System  
**Phase:** Stable (Optimization)

### Release Criteria (ALL must be met)
| Criterion | Target | Status |
|---|---|---|
| All 8 pillars implemented | Training, Nutrition, Recovery, Consistency, Intelligence, Automation, Prediction, Knowledge | 5/8 complete |
| Recovery module complete | Sleep, HRV, readiness, deload | NOT STARTED |
| Prediction engine live | 9 core + 4 analysis engines | COMPLETE (272 tests) |
| AI Coach integrated | NL explanations for all recommendations | NOT STARTED |
| Adaptive programming | Program auto-adjusts weekly | NOT STARTED |
| 1200+ tests | All deterministic, zero regressions | 484/1200 |
| Launch <1s | Cold start performance | TBD |
| Logging <100ms | Per-operation latency | TBD |
| Charts <500ms | Timeline/forecast chart render | TBD |
| Documentation complete | Product, architecture, ADR, user guide | IN PROGRESS |

### Capabilities COMPLETE Target
- [x] Training Intelligence
- [x] Nutrition Intelligence
- [ ] Recovery Intelligence
- [ ] Decision Intelligence
- [x] Prediction Engine
- [ ] AI Coach
- [ ] Automation
- [x] Knowledge Platform
- [x] Event Platform
- [ ] Experience Platform
- [x] Capability Platform
- [x] Product Intelligence
- [ ] Digital Twin (FOUNDATION)

### Target Metrics
- **Tests:** 1200+
- **Capabilities COMPLETE:** 12/13
- **Overall Health:** 85+

---

## v2.0 — Digital Twin

**Version:** 2.0.0  
**Identity:** Twin  
**Phase:** Mature (Expansion)

### Vision
Longitudinal athlete profile that learns from every session, meal, and sleep record. Adaptation tracking, injury risk prediction, form decay detection, and automated program evolution.

### Capabilities Targeted
- [ ] Digital Twin — CONCEPT → IMPLEMENTED
- [ ] AI Coach — FOUNDATION → ADVANCED
- [ ] Prediction Engine — IMPLEMENTED → STABLE
- [ ] Automation — IMPLEMENTED → STABLE

### Key Initiatives
| Initiative | Description |
|---|---|
| Longitudinal Athlete Model | Full history of all training, nutrition, recovery, prediction data |
| Adaptation Tracking | Measure how the user responds to different volumes, frequencies, exercises |
| Injury Risk Prediction | Flag elevated risk from form degradation, volume spikes, fatigue |
| Form Decay Detection | Identify when exercise form deteriorates from fatigue or load |
| Automated Program Evolution | Programs that evolve based on the athlete's historical response data |
| Self-Evolving Capabilities | Capabilities that auto-improve from usage patterns |

### Target Metrics
- **Tests:** 2000+
- **Capabilities COMPLETE:** 12/13 + Digital Twin IMPLEMENTED
- **Overall Health:** 90+

---

## Legend

| Symbol | Meaning |
|---|---|
| ✅ | Complete |
| ⏳ | In progress |
| [x] | Checked/complete |
| [~] | In progress |
| [ ] | Not started |
