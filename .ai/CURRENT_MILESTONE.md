# Current Milestone — v0.1.0 MVP

## Version

v0.1.0 MVP

## Goal

Replace the user's Excel workout tracker with a desktop application that runs daily in the gym. The app must handle workout logging, progress tracking, and basic nutrition visibility — all offline.

## User Profile for MVP

A 178 cm, 63.4 kg male on a PPL-UL split, lean bulking to 72–75 kg. Focus muscles: Shoulders, Upper Chest, Back Width, Arms. Hypertrophy-first approach using double progression.

## MVP Scope — Allowed

| Module | Description |
|--------|-------------|
| Workout | Plans, exercises, sets, reps, weight, RPE, PRs, completion flow |
| Dashboard | Today's workout, daily calories/protein, body weight, last PR, streak |
| Progress | Weight trend, volume trend, strength trend, frequency (PyQtGraph) |
| Nutrition | CSV import from Cronometer only — display daily macros |
| Settings | Unit system, theme, workout defaults, data export |

## MVP Scope — Forbidden

Do NOT implement:

- AI Coach (v0.2)
- Weekly Reports (v0.2)
- Recovery module (sleep/HRV) (v0.2)
- Deload scheduling (v0.2)
- Prediction Engine (v0.2)
- Live API sync with Cronometer (v0.3)
- Wearable integration (v0.4)
- Any social/multi-user features
- Plugin SDK or marketplace
- Cloud sync
- Voice/vision AI

## Current Sprint — Workout Module

Implement:
- Workout plan CRUD (PPL-UL templates as defaults)
- Exercise library integration from `knowledge/exercises/`
- Set logging with weight (kg), reps, RPE
- Previous session comparison
- Personal Record detection (weight PR, volume PR, e1RM PR)
- Workout completion flow with summary

## Priority Muscles in Exercise Selection

When building templates or suggesting exercises, prioritise:
1. **Shoulders** — lateral raises, overhead press, face pulls
2. **Upper Chest** — incline press, low-to-high cable flies
3. **Back Width** — lat pulldowns, pull-ups, wide rows
4. **Arms** — bicep curls, tricep extensions, hammer curls
5. Legs, glutes, hamstrings — maintain proportion but not primary focus

## Blockers

None.
