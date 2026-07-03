# GymOS Dashboard

The Dashboard is the central intelligence hub of GymOS. When the user opens
GymOS before training, the Dashboard answers:

- **What should I train today?** — Today's scheduled workout
- **Am I recovering well?** — Recovery status from GymBrain fatigue analysis
- **Which muscle needs attention?** — Priority muscles with volume deficits
- **Should I increase weight?** — Progression recommendations from the rule engine
- **Am I progressing toward my goal?** — Bodyweight goal tracking

## Architecture Philosophy

- **Dashboard contains presentation only.** Business logic lives in GymBrain.
- **The Dashboard never duplicates GymBrain calculations.** All intelligence flows
  through the `DecisionEngine` public API.
- **No decorative widgets.** Every card answers "What should the user do next?"

## Widget Layout (Top to Bottom)

1. **Header** — Greeting, program info, key metrics (weight, streak, volume, week)
2. **Goal Progress** — Current weight vs goal, gain rate, estimated completion
3. **Today's Recommendation** — Highest-priority GymBrain recommendation
4. **Today's Workout** — Scheduled workout details with Start button
5. **Priority Muscles** — Volume status per muscle (MEV/MAV, recovery, trend)
6. **Recovery Status** — Fatigue level with color coding (green/yellow/red)
7. **Weekly Volume** — Top muscles with effective sets, frequency, trend
8. **Recent PRs** — Last 5 personal records
9. **Nutrition Summary** — Placeholder (future Nutrition Intelligence)
10. **Quick Actions** — One-click buttons for common tasks

## Data Flow

```
GymDatabase + KnowledgeLoader
        │
        ▼
  ProductionDataProvider
        │
        ▼
  DecisionEngine (GymBrain Core)
   ├─ MuscleAnalyzer
   ├─ FatigueAnalyzer
   ├─ GoalTracker
   ├─ PlateauDetector
   └─ RuleEngine → Recommendations
        │
        ▼
  DashboardDataService
   └─ fetch_all() → DashboardData
        │
        ▼
  DashboardController
   ├─ data_updated signal
   └─ Event subscriptions
        │
        ▼
  DashboardView
   └─ 10 Widgets
```

## Event Subscriptions

The DashboardController subscribes to these domain events for live updates:

| Event | Action |
|-------|--------|
| `WorkoutCompleted` | Refresh workout, volume, recovery, PRs |
| `BodyWeightUpdated` | Refresh header, goal progress |
| `RecommendationsUpdated` | Refresh recommendations |
| `ExerciseKnowledgeUpdated` | Invalidate cache, full refresh |
| `ProgramActivated` | Invalidate cache, full refresh |
| `ProgramImported` | Invalidate cache, full refresh |

## Empty States

Every widget handles the case where no data is available:

- No workouts → Helpful message + guidance
- No recommendations → "Keep up the great work!"
- No body weight → "Log your first weight"
- No program → "Import a workout program"
- No PRs → "Push yourself in your next workout!"
- No nutrition config → "Nutrition tracking not configured."

## Performance Targets

- Initial load: **<100 ms**
- Refresh after event: **<50 ms**
- Reuses GymBrain's `AnalysisCache` (300s TTL)
- Avoids unnecessary queries through section-level refresh

---

*See also: [DASHBOARD_ARCHITECTURE.md](DASHBOARD_ARCHITECTURE.md),
[DASHBOARD_WIDGETS.md](DASHBOARD_WIDGETS.md)*
