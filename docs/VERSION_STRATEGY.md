# Version Strategy

## Versioning Scheme

GymOS uses `v0.{major}.{minor}` pre-1.0 versioning:

- **Major** (0.x) — Product evolution stage
- **Minor** (x.y) — Feature sprint within stage
- No patch versioning (pre-1.0, every change is a feature)

## Version Definitions

### v0.5 — Platform Maturity ✅

*Current version.*

| Criterion | Definition |
|-----------|------------|
| **Identity** | Platform |
| **Theme** | Architecture hardening, nutrition intelligence, standardization |
| **Key deliverables** | Engineering Constitution, 5 ADRs, 7 Protocol interfaces, DI Standard, Module Audit, Knowledge Platform, 4 Engineering Standards, Nutrition Intelligence (49 tests) |
| **Test count** | 688 |
| **Exit criteria** | All platform audits pass, no module has undocumented scaffolding, all interfaces typed |

### v0.6 — Recovery Intelligence

| Criterion | Definition |
|-----------|------------|
| **Identity** | Coach |
| **Theme** | Recovery tracking, deload scheduling, nutrition UI, weekly review |
| **Key deliverables** | Recovery domain → infrastructure → provider pipeline, deload scheduler, nutrition dashboard widgets, weekly review rendering, goal configuration UI |
| **Test count** | 800+ |
| **Exit criteria** | Recovery module fully implements IRecoveryProvider, deload rule triggers actionable recommendations, nutrition dashboard displays all tracked metrics |

### v0.7 — Prediction Engine

| Criterion | Definition |
|-----------|------------|
| **Identity** | Analyst |
| **Theme** | Trend prediction, forecasting, smart recommendations |
| **Key deliverables** | Prediction Engine (plateau timing, goal forecasting), Cronometer API sync, trend analysis on all tracked metrics, recovery provider wired into DataProvider |
| **Test count** | 900+ |
| **Exit criteria** | Prediction models validated against historical data, Cronometer sync replaces CSV workflow, all rules consider recovery data |

### v0.8 — AI Coach

| Criterion | Definition |
|-----------|------------|
| **Identity** | Coach |
| **Theme** | Natural language explanations, adaptive guidance |
| **Key deliverables** | Rule-to-natural-language generation, context-aware coaching (multi-domain analysis), adaptive rule prioritization, monthly progress narrative |
| **Test count** | 1000+ |
| **Exit criteria** | Every recommendation includes an explanation the user understands, rules adapt based on user's phase, progress narrative generated each month |

### v0.9 — Adaptive Programming

| Criterion | Definition |
|-----------|------------|
| **Identity** | Autopilot |
| **Theme** | Self-tuning programs, automated adjustments |
| **Key deliverables** | Auto-adjustment engine (modify program from recovery/nutrition), dynamic exercise selection, volume auto-regulation, deload auto-scheduling |
| **Test count** | 1100+ |
| **Exit criteria** | Program adjusts weekly without user intervention, user can override any automated decision |

### v1.0 — Full Autopilot

| Criterion | Definition |
|-----------|------------|
| **Identity** | Operating System |
| **Theme** | Complete, polished, production-ready |
| **Key deliverables** | All 7 pillars complete, recovery module full feature, prediction engine live, AI Coach integrated, adaptive programming active, 1200+ tests, performance targets met, documentation complete |
| **Exit criteria** | User opens app → trains → logs → system adapts automatically. No manual programming. No guesswork. No spreadsheets. |
