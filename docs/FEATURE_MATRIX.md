# GymOS — Feature Matrix

## Legend
- ✅ MVP (v0.1)
- 🔄 In Progress
- 📋 Planned (v0.2+)
- ❌ Out of Scope

## Training

| Feature | Status | Priority | Notes |
|---------|--------|----------|-------|
| Workout plan CRUD | ✅ | Critical | PPL-UL default templates |
| Exercise library integration | ✅ | Critical | From knowledge/exercises/ |
| Set logging (weight, reps, RPE) | ✅ | Critical | Quick, 2-tap logging |
| Previous session comparison | ✅ | High | Auto-show last session data |
| Personal Record detection | ✅ | High | Weight, volume, e1RM |
| Workout completion flow | ✅ | High | Summary, time, volume |
| Rest timer | 📋 | Medium | Auto-start after set log |
| Warm-up set tracking | 📋 | Low | Optional logging |
| RPE auto-calculation | 📋 | Low | Based on reps in reserve |
| AI Coach recommendations | 📋 | Medium | v0.2 |
| Deload scheduling | 📋 | Medium | v0.2 |
| Adaptive programming | 📋 | Low | v0.4 |
| Form analysis (vision AI) | ❌ | - | v0.5 if ever |

## Dashboard

| Feature | Status | Priority | Notes |
|---------|--------|----------|-------|
| Today's scheduled workout | ✅ | Critical | Or rest day message |
| Daily calories vs target | ✅ | High | Progress bar |
| Daily protein vs target | ✅ | High | Progress bar |
| Current body weight | ✅ | Medium | With trend arrow |
| Last PR highlight | ✅ | Medium | Celebration effect |
| Workout streak | ✅ | Medium | Fire icon for 5+ days |
| Weekly summary | 📋 | Low | v0.2 |

## Progress

| Feature | Status | Priority | Notes |
|---------|--------|----------|-------|
| Weight trend chart | ✅ | High | 30/90 day |
| Volume trend chart | ✅ | High | Weekly, by muscle group |
| Strength (1RM) trend | ✅ | High | Per major lift |
| Frequency chart | ✅ | Medium | Sessions/week |
| Muscle group balance | 📋 | Low | Volume distribution |
| Progress photos | 📋 | Low | v0.4 |
| Body measurements | 📋 | Low | v0.4 |

## Nutrition

| Feature | Status | Priority | Notes |
|---------|--------|----------|-------|
| Cronometer CSV import | ✅ | High | 1-click import |
| Daily macro display | ✅ | High | Calories, protein, carbs, fat |
| Target vs actual visualisation | ✅ | High | Dashboard + nutrition view |
| Weekly nutrition summary | 📋 | Low | v0.2 |
| Live Cronometer sync | 📋 | Medium | v0.3 |
| Meal suggestions | ❌ | - | Out of scope |

## Recovery

| Feature | Status | Priority | Notes |
|---------|--------|----------|-------|
| Deload tracking | 📋 | Medium | v0.2 |
| Sleep logging | 📋 | Low | v0.2 |
| HRV integration | 📋 | Low | v0.3 |
| Readiness score | 📋 | Low | v0.3 |
| Fatigue management | 📋 | Low | v0.3 |

## Settings

| Feature | Status | Priority | Notes |
|---------|--------|----------|-------|
| Unit system (kg/lb) | ✅ | Medium | |
| Theme toggle (dark/light) | ✅ | Medium | Dark default |
| Rest timer defaults | ✅ | Low | |
| Data export (JSON/CSV) | ✅ | Low | |
| User profile editing | ✅ | Medium | Height, weight, goals |
| Data import/restore | 📋 | Low | |

## Platform

| Feature | Status | Priority | Notes |
|---------|--------|----------|-------|
| Offline-first | ✅ | Critical | No internet required |
| Database backups | ✅ | High | On each launch |
| Keyboard navigation | ✅ | Medium | |
| Auto-save during workout | ✅ | High | Every 30 seconds |
| Crash recovery | ✅ | High | Transactional writes |

## Out of Scope (Permanently)

| Feature | Reason |
|---------|--------|
| Social features / friends | Single-user application |
| Leaderboards / competitions | Not goal-aligned |
| Plugin marketplace | Not needed for single user |
| Multi-user / coach features | Single user, one coach = user |
| Cloud sync | Offline-first; manual backup is sufficient |
| Mobile app (MVP) | Desktop-first; mobile not planned |
| Voice assistant | Low priority, high complexity |
| Meal planning / recipes | Cronometer handles nutrition logging |
