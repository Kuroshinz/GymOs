# GymOS — Product Requirements

## 1. Product Overview

### 1.1 Vision
GymOS is a personal hypertrophy operating system for ONE user.  
It exists to help the owner build the best aesthetic physique possible using data-driven training.

### 1.2 Mission
Replace the user's Excel workout tracker with a desktop application that plans, logs, analyses, and optimises every training session — all offline.

### 1.3 Primary User

| Attribute | Value |
|-----------|-------|
| Description | Male, 178 cm, 63.4 kg, lean bulking to 72-75 kg |
| Training | PPL-UL split, 5-6 days/week |
| Goal | Hypertrophy — build muscle, not strength |
| Focus | Shoulders, Upper Chest, Back Width, Arms |
| Current Tool | Excel spreadsheet (manual tracking, no analytics) |

### 1.4 Success Metrics

| Metric | Target | How |
|--------|--------|-----|
| Body weight | 63.4 → 72-75 kg | Weekly weigh-in |
| Strength progression | Linear 6+ months | Volume/1RM charts |
| Workout consistency | ≥85% sessions completed | Streak tracking |
| Nutrition compliance | Protein ≥140g, calories ≥2800 daily | Macro tracking |
| User satisfaction | Use daily, no Excel needed | Adoption metric |

---

## 2. Functional Requirements

### 2.1 Workout Module (MVP)

#### FR1: Workout Plans
- Create, edit, delete workout plans
- Each plan has name, description, ordered exercise list
- Default plans: PPL-UL templates aligned with user's focus muscles
- Exercises reference `knowledge/exercises/` library

#### FR2: Active Workout
- Start a session from a plan
- Log sets with: weight (kg), reps, RPE (optional), completed/skipped
- View previous session's weights and reps per exercise
- Auto-save every 30 seconds
- Notes per exercise

#### FR3: Personal Records
- Auto-detect PRs: weight PR, volume PR, estimated 1RM
- Celebrate PR on completion with visual highlight

#### FR4: Workout History
- View past sessions with full detail
- Filter by date, exercise, muscle group
- Compare volume and performance over time

### 2.2 Dashboard (MVP)

#### FR5: Today's View
- Scheduled workout (or rest day message)
- Daily calories + protein: target vs actual
- Current body weight with trend
- Last PR achieved
- Workout streak (consecutive days)

### 2.3 Progress (MVP)

#### FR6: Charts
- Weight trend (daily weigh-ins, 30/90 day view)
- Volume trend (weekly total, per muscle group)
- Strength trend (estimated 1RM per major lift)
- Workout frequency (sessions per week)
- All charts rendered with PyQtGraph

### 2.4 Nutrition (MVP)

#### FR7: CSV Import
- Import CSV from Cronometer
- Display daily: calories, protein, carbs, fat
- Targets vs actual visualisation
- No manual food logging in MVP

### 2.5 Settings (MVP)

#### FR8: Configuration
- Unit system (kg / lb)
- Theme (dark / light, dark default)
- Workout defaults: rest timer, warm-up sets
- Data export (JSON/CSV)
- User profile: height, current weight, goal weight, focus muscles

---

## 3. Non-Functional Requirements

### 3.1 Performance
- App launches in <3 seconds
- Workout logging: <100ms response
- Charts render in <500ms
- CSV import of 1 year data in <5 seconds

### 3.2 Offline-First
- All data stored locally in SQLite
- Zero internet required for any feature
- All features work offline at all times

### 3.3 Data Integrity
- Transactional writes on all workout data
- Auto-save every 30s during active workout
- Database backup on each app launch

### 3.4 UI/UX
- Dark theme as default
- Keyboard-navigable workout logging
- Maximum 2 taps to log a completed set
- Large tap targets (gym-ready, standing use)
- High contrast for readability at distance

---

## 4. Out of Scope (MVP)

- AI Coach and workout recommendations
- Weekly report generation
- Recovery module (sleep, HRV, readiness)
- Deload scheduling
- Live API sync (Cronometer, wearables)
- Mobile app
- Cloud sync
- Multi-user or coach features
- Social features, leaderboards, sharing
- Plugin SDK or marketplace
- Vision AI / form analysis
- Voice assistant

---

## 5. Future Roadmap

| Version | Features |
|---------|----------|
| v0.1.0 (MVP) | Workout tracking, dashboard, progress charts, nutrition import, settings |
| v0.2.0 | AI Coach, weekly report, recovery module, deload scheduling, prediction engine |
| v0.3.0 | Live Cronometer sync, Hevy sync, enhanced analytics, data import/export |
| v0.4.0 | Wearable integration (HRV/sleep), adaptive programming, progress photos |
| v0.5.0 | Form analysis, voice control, natural language queries |

---

## 6. Data Model (MVP)

```
WorkoutPlan
  ├── name, description
  └── exercises (ordered, with target sets/reps/rest)

WorkoutSession
  ├── plan_id, started_at, completed_at, duration, notes
  └── exercise_logs [ ]
        └── exercise_id, sort_order, notes
              └── sets [ ]
                    └── set_number, weight_kg, reps, rpe, is_completed, is_warmup

NutritionLog: date, calories, protein, carbs, fat, source
WeightLog: date, weight_kg
PersonalRecord: exercise_id, pr_type, value, achieved_at, session_id

Settings: key-value JSON store
```
