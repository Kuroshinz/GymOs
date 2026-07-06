# Engine Matrix

Every engine in GymOS, its purpose, inputs, outputs, dependencies, health, and evolution.

---

## Workout Engine

| Attribute | Value |
|---|---|
| **Purpose** | Plan, log, and analyze training sessions |
| **Owner** | GymOS Team |
| **Current Maturity** | IMPLEMENTED |
| **Target Maturity** | STABLE |
| **Health** | 78/100 |
| **Tests** | 163 (via GymBrain) |
| **Location** | `modules/workout/` |

### Inputs
- Exercise definitions (from Knowledge Platform)
- Session logs (weight, reps, RPE, RIR, warmup sets)
- Program templates (from ProgramManager)

### Outputs
- WorkoutSession, SessionExercise, SessionSet entities
- PR events (weight, volume, e1RM)
- Volume analysis (weekly, per muscle group)
- Progression detection (double progression, deload)

### Dependencies
- KnowledgeLoader (exercises, muscles)
- GymDatabase (SQLite)
- EventBus

### Future Evolution
| Version | Enhancement |
|---|---|
| v0.8 | Mesocycle model |
| v1.0 | RPE auto-calculation from RIR |
| v1.0 | Velocity-based estimation |
| v1.0 | Per-session fatigue-adjusted volume |
| v1.0 | Auto-deload insertion |

---

## Nutrition Engine

| Attribute | Value |
|---|---|
| **Purpose** | Track and analyze nutrition for lean bulk optimization |
| **Owner** | GymOS Team |
| **Current Maturity** | IMPLEMENTED |
| **Target Maturity** | STABLE |
| **Health** | 74/100 |
| **Tests** | 49 |
| **Location** | `modules/nutrition/` |

### Inputs
- Meal logs (manual entry)
- Macro targets (protein, calories, carbs, fat)
- Water logs
- CSV imports from Cronometer

### Outputs
- DailyNutrition, Meal, MacroTarget, Hydration entities
- MacroAnalyzer reports (daily/weekly macro adherence)
- LeanBulkAnalyzer reports (surplus/deficit, gain rate)
- Nutrition events (MealLogged, NutritionUpdated, MacroTargetChanged)

### Dependencies
- NutritionRepository (SQLite)
- EventBus
- INutritionProvider

### Future Evolution
| Version | Enhancement |
|---|---|
| v0.6 | Nutrition dashboard widgets |
| v0.7 | Cronometer API sync |
| v1.0 | Micronutrient analysis |
| v1.0 | Meal plans, recipes |

---

## Recovery Engine

| Attribute | Value |
|---|---|
| **Purpose** | Track sleep, HRV, fatigue, readiness |
| **Owner** | GymOS Team |
| **Current Maturity** | DESIGN |
| **Target Maturity** | IMPLEMENTED |
| **Health** | 15/100 |
| **Tests** | 0 |
| **Location** | `modules/recovery/` |

### Inputs
- Sleep logs (manual, future: wearable import)
- HRV data (future: wearable)
- Fatigue scores (manual)
- Soreness/DOMS ratings (manual)

### Outputs
- RecoverySession, SleepLog, RecoveryScore entities (planned)
- Fatigue trends (planned)
- Readiness composite score (planned)
- Deload recommendations (planned)
- Recovery events (planned)

### Dependencies
- EventBus (wired)
- IRecoveryProvider (not implemented)
- GymDatabase (planned recovery tables)

### Future Evolution
| Version | Enhancement |
|---|---|
| v0.6 | Manual sleep/fatigue logging |
| v0.6 | FatigueAnalyzer integration |
| v0.6 | IRecoveryProvider implementation |
| v0.7 | Readiness composite score |
| v0.8 | Sleep-debt rule |
| v1.0 | Wearable API import |

---

## Decision Engine (GymBrain)

| Attribute | Value |
|---|---|
| **Purpose** | Evaluate rules against current state, produce ranked recommendations |
| **Owner** | GymOS Team |
| **Current Maturity** | FOUNDATION |
| **Target Maturity** | IMPLEMENTED |
| **Health** | 40/100 |
| **Tests** | 163 |
| **Location** | `modules/gymbrain/` |

### Inputs
- Training data (volume, PRs, fatigue, consistency)
- Nutrition data (macro adherence, surplus/deficit)
- Recovery data (when wired)
- Knowledge thresholds (from Knowledge Platform)

### Outputs
- 18 deterministic rules (13 training + 5 nutrition)
- Recommendation objects with priority, confidence, evidence
- PlateauDetector analysis
- FatigueAnalyzer analysis
- MuscleAnalyzer (volume balance, weak points)
- GoalTracker (weight goal progress)
- Events (RecommendationCreated, WeeklyReviewGenerated)

### Dependencies
- ITrainingProvider (wired)
- INutritionProvider (wired)
- IRecoveryProvider (not yet wired)
- EventBus
- AnalysisCache with event-driven invalidation

### Future Evolution
| Version | Enhancement |
|---|---|
| v0.6 | + recovery rules |
| v0.6 | WeeklyReview rendering |
| v0.7 | + recovery provider |
| v0.8 | TrendAnalyzer, CorrelationAnalyzer |
| v0.8 | Natural language explanations |
| v1.0 | + prediction provider |
| v1.0 | 30+ total rules |

---

## Prediction Engine

| Attribute | Value |
|---|---|
| **Purpose** | Forecast athlete states, explain predictions, simulate scenarios, quantify risk |
| **Owner** | GymOS Team |
| **Current Maturity** | IMPLEMENTED |
| **Target Maturity** | STABLE |
| **Health** | 82/100 |
| **Tests** | 272 |
| **Location** | `modules/prediction/` |

### Inputs
- Training data (volume, PR history, RIR, consistency)
- Nutrition data (calorie surplus, adherence)
- Recovery data (sleep, fatigue, recovery scores)
- Knowledge thresholds (MRV, deload frequency)

### Outputs — Core (9 engines x 4 windows)
| Engine | Predicts | Key Metrics |
|---|---|---|
| PlateauPredictionEngine | Plateau probability | Volume change, RIR, days since weight change |
| PRPredictionEngine | PR probability | Volume trend, consistency, recovery, deload status |
| RecoveryPredictionEngine | Recovery decline | Sleep/stress/volume trends, deload recency |
| FatiguePredictionEngine | Fatigue accumulation | Volume, sleep, stress, deload recency |
| BodyweightPredictionEngine | Bodyweight trend | Calorie surplus, adherence, BW history |
| GoalEtaPredictionEngine | Goal ETA | Current/goal BW, surplus, adherence |
| VolumePredictionEngine | MRV violation risk | Weekly volumes, estimated MRV, RPE |
| ConsistencyPredictionEngine | Consistency decay | Streak, completion rate, missed sessions |
| DeloadPredictionEngine | Deload probability | Weeks since deload, fatigue, recovery |

### Outputs — Analysis (4 engines)
| Engine | Produces | Purpose |
|---|---|---|
| PredictionScenarioEngine | ScenarioResult, ScenarioRanking | 10 what-if interventions |
| CounterfactualEngine | CounterfactualResult | 5 behavioral what-ifs |
| ExplainabilityEngine | ExplainabilityDetail | Factor ranking, reason chain, NL+MR |
| RiskEngine | RiskMetrics | Stability, sensitivity, uncertainty, volatility |

### Dependencies
- Training (volume, PR history)
- Nutrition (calorie surplus)
- Recovery (sleep, fatigue)
- Knowledge (MRV thresholds)
- PredictionRepository (SQLite)
- EventBus (6 prediction events)

### Future Evolution
| Version | Enhancement |
|---|---|
| v0.7 | Workout completion probability engine |
| v0.7 | Custom scenario parameters |
| v0.8 | Historical trend explanations |
| v1.0 | Compound counterfactuals |
| v1.0 | Athlete-specific risk calibration |
| v1.0 | Forecast timeline chart widgets |

---

## AI Coach Engine

| Attribute | Value |
|---|---|
| **Purpose** | Explain recommendations in natural language, provide adaptive guidance |
| **Owner** | GymOS Team |
| **Current Maturity** | CONCEPT |
| **Target Maturity** | DESIGN |
| **Health** | 1/100 |
| **Tests** | 0 |
| **Location** | TBD |

### Inputs (Planned)
- RuleResult from GymBrain
- PredictionResult from Prediction Engine
- User context (current phase, goals, preferences)

### Outputs (Planned)
- Natural language explanations (short, detailed, actionable)
- Multi-rule synthesized recommendations
- Adaptive tone and depth
- Weekly progress narrative

### Dependencies
- GymBrain (all rules and analyzers)
- Prediction Engine
- NLG templates

### Future Evolution
| Version | Enhancement |
|---|---|
| v0.8 | Rule-to-text NLG |
| v0.8 | Multi-rule synthesis |
| v0.8 | Adaptive tone |
| v0.9 | Context-aware recommendations |
| v1.0 | Full session history awareness |

---

## Automation Engine

| Attribute | Value |
|---|---|
| **Purpose** | Reduce manual decisions through data-driven programming |
| **Owner** | GymOS Team |
| **Current Maturity** | CONCEPT |
| **Target Maturity** | IMPLEMENTED |
| **Health** | 2/100 |
| **Tests** | 0 |
| **Location** | TBD |

### Inputs (Planned)
- Recovery data (fatigue, readiness)
- Nutrition data (surplus/deficit)
- Prediction data (risk, scenarios, forecasts)
- GymBrain recommendations

### Outputs (Planned)
- Auto-adjusted program parameters
- Dynamic exercise suggestions
- Volume regulation recommendations
- Auto-scheduled deload weeks

### Dependencies
- Recovery Engine
- Prediction Engine
- GymBrain
- Workout Engine

### Future Evolution
| Version | Enhancement |
|---|---|
| v0.9 | Auto-adjustment engine |
| v0.9 | Dynamic exercise selection |
| v0.9 | Volume auto-regulation |
| v0.9 | Auto-deload scheduling |
| v1.0 | Full weekly auto-adjustment |

---

## Knowledge Engine

| Attribute | Value |
|---|---|
| **Purpose** | Single source of truth for all fitness science |
| **Owner** | GymOS Team |
| **Current Maturity** | IMPLEMENTED |
| **Target Maturity** | STABLE |
| **Health** | 65/100 |
| **Tests** | 0 (pipeline tested via integration) |
| **Location** | `knowledge/` (data), `modules/knowledge/` (pipeline) |

### Inputs
- Exercise definitions (JSON, 95+)
- Muscle group taxonomy (52 definitions)
- Progression rules (deload, RIR, RPE, failure)
- Nutrition guidelines (macro targets, micronutrients)
- Recovery science (sleep, HRV, fatigue)

### Outputs
- Validated knowledge records
- Exercise/muscle/progression lookups
- Evidence-backed recommendations
- Citations and scientific references

### Dependencies
- Knowledge loader → cache → validator → service pipeline
- No external dependencies (local files only)

### Future Evolution
| Version | Enhancement |
|---|---|
| v0.6 | Recovery knowledge expansion |
| v0.8 | Synergist/antagonist muscle relationships |
| v1.0 | User-custom exercises |
| v1.0 | Hot-reload, version management |

---

## Physique Engine

| Attribute | Value |
|---|---|
| **Purpose** | Track and project physique changes over time |
| **Owner** | GymOS Team |
| **Current Maturity** | CONCEPT |
| **Target Maturity** | DESIGN |
| **Health** | 0/100 |
| **Tests** | 0 |
| **Location** | TBD |

### Inputs (Planned)
- Body weight logs (existing)
- Body measurements (shoulders, waist, arms, etc.)
- Progress photos

### Outputs (Planned)
- Body composition estimation
- Measurement trends
- Progress photo timeline

### Dependencies
- Workout Engine (body weight already tracked)

### Future Evolution
| Version | Enhancement |
|---|---|
| v2.0 | Body composition estimation |
| v2.0 | Measurement tracking |
| v2.0 | Progress photo timeline |
