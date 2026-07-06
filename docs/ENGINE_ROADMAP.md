# Engine Roadmap

Every engine in GymOS, its current maturity, and its planned evolution.

---

## Workout Engine

**Purpose:** Plan, log, and analyze training sessions.

| Aspect | Current (v0.5) | Next (v0.6) | Future (v1.0) |
|--------|---------------|-------------|---------------|
| **Domain** | WorkoutSession, SessionExercise, SessionSet, BodyWeight | — | Mesocycle model |
| **Logging** | Weight, reps, RPE, RIR, warmup sets | — | RPE auto-calculation from RIR |
| **PR Detection** | Weight, volume, e1RM | — | Velocity-based estimation |
| **Volume** | Weekly total, per muscle group | — | Per-session fatigue-adjusted |
| **Progression** | Double progression, deload detection | Deload scheduling UI | Auto-deload insertion |
| **Tests** | 163 (via GymBrain) | — | — |

**Dependencies:** KnowledgeLoader (exercises, muscles), GymDatabase (SQLite)

---

## Nutrition Engine

**Purpose:** Track and analyze nutrition for lean bulk optimization.

| Aspect | Current (v0.5) | Next (v0.6) | Future (v1.0) |
|--------|---------------|-------------|---------------|
| **Domain** | DailyNutrition, Meal, MacroTarget, Hydration, NutritionSummary | — | Meal plans, recipes |
| **Tracking** | Manual meal log, water tracking | CSV import (already exists) | Cronometer API sync |
| **Analysis** | MacroAnalyzer, LeanBulkAnalyzer | — | Micronutrient analysis |
| **Providers** | ProductionNutritionProvider (SQLite) | — | CronometerApiProvider |
| **Events** | MealLogged, NutritionUpdated, MacroTargetChanged | — | MealPlanGenerated |
| **Dashboard** | Backend wired | Nutrition widgets | Full nutrition screen |
| **Tests** | 49 | — | — |

**Dependencies:** NutritionRepository (SQLite), EventBus, INutritionProvider

---

## Recovery Engine

**Purpose:** Track sleep, HRV, fatigue, and readiness.

| Aspect | Current (v0.5) | Next (v0.6) | Future (v1.0) |
|--------|---------------|-------------|---------------|
| **Domain** | Scaffolding only | RecoverySession, SleepLog, RecoveryScore | Wearable data models |
| **Tracking** | None | Manual sleep/fatigue logging | Wearable API import |
| **Analysis** | Event exists (RecoveryScoreUpdated) | FatigueAnalyzer integration | Readiness composite score |
| **Provider** | None | IRecoveryProvider implementation | WearableAdapter |
| **Rules** | RecoveryRule, ConsistencyRule exist | — | Sleep-debt rule |
| **Tests** | 0 | 50+ | 100+ |

**Dependencies:** EventBus, IRecoveryProvider, GymDatabase (planned recovery tables)

---

## Decision Engine (GymBrain)

**Purpose:** Evaluate rules against current state, produce ranked recommendations.

| Aspect | Current (v0.5) | Next (v0.6) | Future (v1.0) |
|--------|---------------|-------------|---------------|
| **Rules** | 18 (13 training + 5 nutrition) | + recovery rules | 30+ total |
| **Analysis** | PlateauDetector, FatigueAnalyzer, MuscleAnalyzer, GoalTracker | — | TrendAnalyzer, CorrelationAnalyzer |
| **Providers** | DataProvider (training + nutrition) | + recovery provider | + prediction provider |
| **Cache** | AnalysisCache with event-driven invalidation | — | Predictive pre-fetch |
| **Output** | Recommendation objects | WeeklyReview rendering | Natural language explanations |
| **Tests** | 163 | — | — |

**Dependencies:** All providers (ITrainingProvider, INutritionProvider, IRecoveryProvider), EventBus

---

## Prediction Engine

**Purpose:** Forecast plateaus, PR probability, recovery, bodyweight, fatigue, goal ETA, MRV risk, deload, consistency. Explain predictions, simulate scenarios, assess risk.

| Aspect | Current (v0.5) | Next (v0.7) | Future (v1.0) |
|--------|---------------|-------------|---------------|
| **Status** | Complete (RFC-020 + RFC-020.5) | UI polish | Historical trends |
| **Core Engines** | 9 engines (plateau, PR, recovery, fatigue, bodyweight, goal ETA, volume/MRV, consistency, deload) over 4 windows | — | Workout completion probability |
| **Scenario Engine** | 10 interventions (volume ±, deload early/late, calories ±, sleep ±, adherence ±) | Custom scenario parameters | Compound scenarios |
| **Counterfactual** | 5 what-if queries (sleep 8h, calories +250, miss workout, volume change, deload now) | — | Compound counterfactuals |
| **Explainability** | Factor ranking (top 15), reason chain (6-step), NL/MR explanations | Historical explainability | Trend model explanations |
| **Risk Metrics** | Stability, sensitivity, uncertainty, CI width, volatility, overall risk score/level | Configurable thresholds | Athlete-specific calibration |
| **Dashboard** | 8-card grid + 5 new widgets (scenario, risk, explainability, confidence, reason tree) | Chart integration | Timeline forecast charts |
| **Tests** | 272 | — | — |

**Dependencies:** Training (volume, PR history), Nutrition (calorie surplus), Recovery (sleep, fatigue), Knowledge (MRV thresholds)

---

## AI Coach

**Purpose:** Explain recommendations in natural language, provide adaptive guidance.

| Aspect | Current (v0.5) | Next (v0.8) | Future (v1.0) |
|--------|---------------|-------------|---------------|
| **Status** | Not started | Phase 1: rule-to-text NLG | Phase 2: context-aware coaching |
| **Explanations** | Structured evidence only | Natural language from templates | Adaptive tone and depth |
| **Context** | Single-rule evidence | Multi-rule synthesis | Full session history |
| **Interaction** | Read-only | User can ask "why?" | Conversational refinement |

**Dependencies:** GymBrain, recommendation model, NLG templates (future: small LLM)

---

## Physique Engine

**Purpose:** Track and project physique changes over time.

| Aspect | Current (v0.5) | Next | Future (v1.0+) |
|--------|---------------|------|----------------|
| **Status** | Not started | — | Phase 1: measurements |
| **Body Weight** | Trend chart (current) | — | Body composition estimation |
| **Measurements** | — | — | Shoulder/waist/arm tracking |
| **Progress Photos** | — | — | Photo timeline with metadata |

**Dependencies:** None yet (future feature)
