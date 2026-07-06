# Product Pillars

Every future feature must belong to one of these seven pillars.

---

## 1. Training

**Core principle:** Optimized PPL-UL programming with double progression.

| Component | Current (v0.5) | Target (v1.0) |
|-----------|---------------|---------------|
| Program management | Import, activate, switch | Create, edit, share templates |
| Exercise library | 95+ from knowledge/ | Custom exercise creation |
| Set logging | Weight, reps, RPE, RIR | Velocity-based, RPE auto-calc |
| PR detection | Weight, volume, e1RM | Velocity-based, rep-speed |
| Volume analysis | Weekly per muscle group | Per-session fatigue-adjusted |
| Progression | Double progression, deload detection | Auto-deload, auto-progression |
| Mesocycle | Not tracked | Full mesocycle lifecycle |

---

## 2. Nutrition

**Core principle:** Lean bulk macro tracking with GymBrain integration.

| Component | Current (v0.5) | Target (v1.0) |
|-----------|---------------|---------------|
| Macro tracking | Manual meal log | Cronometer API sync |
| Hydration | Manual water log | Auto-reminder |
| Analysis | MacroAnalyzer, LeanBulkAnalyzer | Micronutrient, meal timing |
| Targets | Default targets | Dynamic targets based on weight/gains |
| Integration | Nutrition provider in GymBrain | Nutrition-aware programming |
| Import | CSV from Cronometer | Live API import |

---

## 3. Recovery

**Core principle:** Fatigue management, deload timing, readiness assessment.

| Component | Current (v0.5) | Target (v1.0) |
|-----------|---------------|---------------|
| Sleep tracking | Not implemented | Manual + wearable import |
| HRV | Not implemented | Wearable integration |
| Fatigue | GymBrain analysis | Real-time readiness score |
| Deload | Rule-based detection | Auto-scheduling |
| Integration | Event exists (RecoveryScoreUpdated) | Full provider in GymBrain |

---

## 4. Consistency

**Core principle:** Streak tracking, habit formation, session adherence.

| Component | Current (v0.5) | Target (v1.0) |
|-----------|---------------|---------------|
| Streak tracking | Consecutive days count | Quality-adjusted streak |
| Session adherence | Total workouts count | Missed-session analysis |
| Habit formation | — | Streak-based motivation, milestones |
| Notifications | — | Nudge on missed days |

---

## 5. Intelligence

**Core principle:** Deterministic rule engine — explainable, rankable recommendations.

| Component | Current (v0.5) | Target (v1.0) |
|-----------|---------------|---------------|
| Rule engine | 18 rules, priority × confidence | 30+ rules, adaptive prioritization |
| Analysis | 4 analyzers (plateau, fatigue, muscle, goals) | + trend, correlation, prediction |
| Recommendations | Structured objects | Natural language explanations |
| Determinism | Same data → same output | Same (never use LLM for rules) |
| Explainability | Evidence field per recommendation | Full traceability UI |

---

## 6. Automation

**Core principle:** Reduce manual decisions — data-driven programming.

| Component | Current (v0.5) | Target (v1.0) |
|-----------|---------------|---------------|
| Program adjustment | Manual | Auto-adjusted weekly (user approves) |
| Exercise selection | Fixed per program | Dynamic — swaps plateaued exercises |
| Volume regulation | Manual | Auto-regulated from recovery trend |
| Deload scheduling | Rule trigger | Auto-inserted deload weeks |
| Goal progression | Manual target | Auto-adjusted targets from progress |

---

## 7. Prediction

**Core principle:** Forecast athlete states, explain predictions, simulate what-if scenarios, quantify risk.

| Component | Current (v0.5) | Target (v1.0) |
|-----------|---------------|---------------|
| Core engines | 9 types x 4 windows = 36 predictions | + Workout completion probability |
| Scenario simulation | 10 interventions | Custom parameters, compound scenarios |
| Counterfactual analysis | 5 what-if queries | Compound counterfactuals |
| Explainability | Factor ranking, reason chain, NL + MR | Historical trend explanations |
| Risk assessment | 5 metrics + composite score | Athlete-specific calibration |
| Dashboard | 8-card grid + 5 analysis widgets | Timeline charts, scenario presets |
| Tests | 272 | 300+ |

---

## 8. Knowledge

**Core principle:** Single source of truth for all fitness science.

| Component | Current (v0.5) | Target (v1.0) |
|-----------|---------------|---------------|
| Exercises | 95+ definitions | User-custom exercises |
| Muscles | 52 definitions | Synergist/antagonist relationships |
| Progression | Volume, deload, RIR, RPE, failure | Periodization models |
| Nutrition | Protein, calories, carbs, fat, fiber, hydration | Meal timing, supplement protocols |
| Recovery | Sleep, HRV, fatigue, DOMS | Individualized recovery profiles |
| Research | Summaries | Citation-linked evidence base |
| Pipeline | Loader → Cache → Validator → Service | Hot-reload, version management |

---

## Cross-Pillar Dependencies

```
Training ◄──── Nutrition (energy availability)
Training ◄──── Recovery (fatigue management)
Training ◄──── Intelligence (GymBrain rules)
Training ◄──── Knowledge (exercise definitions)

Nutrition ◄─── Knowledge (macro guidelines)
Nutrition ◄─── Intelligence (deficit/surplus detection)

Recovery ◄──── Knowledge (sleep, fatigue science)
Recovery ◄──── Intelligence (fatigue analysis, deload detection)

Intelligence ◄─ Knowledge (thresholds, scientific ranges)
Intelligence ◄─ Training + Nutrition + Recovery (data sources)

Automation ◄─── Intelligence (rules drive automation decisions)
Automation ◄─── All pillars (data sources)

Knowledge ◄──── Research (evidence base)
Knowledge ─────► All pillars (authoritative data)

Prediction ◄─── Training (volume, PR history)
Prediction ◄─── Nutrition (calorie surplus, adherence)
Prediction ◄─── Recovery (sleep, fatigue, readiness)
Prediction ◄─── Intelligence (GymBrain context)
Prediction ◄─── Knowledge (MRV thresholds, scientific ranges)
Prediction ─────► Automation (prediction-driven decisions)
Prediction ─────► Intelligence (explainability, scenario data)
```

## Feature Classification

Every feature proposal must be tagged with its primary pillar:

> **Feature:** Auto-deload scheduling  
> **Pillar:** Recovery (primary) + Automation (secondary) + Intelligence (tertiary)  
> **Rationale:** Uses fatigue data to auto-schedule deload weeks  
> **Target version:** v0.6 (Recovery Intelligence)
