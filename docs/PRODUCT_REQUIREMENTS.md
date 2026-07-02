# NEXUS — Product Requirements

## 1. Product Overview

### 1.1 Vision
NEXUS is an Intelligent Personal Performance Operating System — the single
platform that manages training, nutrition, recovery, health, learning,
productivity, and automation.

### 1.2 Target Users

| Persona | Description | Key Needs |
|---------|-------------|-----------|
| Beginner | New to gym, no tracking experience | Simple UI, guided workouts, basic progress |
| Intermediate | 1-3 years training, uses Excel/notes | Volume tracking, PR detection, progression rules |
| Advanced | 5+ years, periodised programming | RPE, fatigue management, deload scheduling |
| Coach | Manages multiple clients | Client view, program assignment, analytics |

### 1.3 MVP Users
MVP focuses on **Intermediate** persona — the user who currently tracks
workouts in Excel and wants a dedicated desktop app.

## 2. Functional Requirements

### 2.1 Workout Module (MVP — Highest Priority)

#### FR1: Workout Plans
- Create, edit, delete workout plans
- Each plan has a name, description, and ordered exercise list
- Exercises reference the knowledge/ exercise library

#### FR2: Active Workout
- Start a session from a plan
- Log sets with: weight (kg), reps, RPE (optional)
- View previous session's weights/reps for each exercise
- Mark sets as completed or skipped
- Add notes per exercise

#### FR3: Personal Records
- Auto-detect PRs (weight PR, volume PR, estimated 1RM)
- Show PR celebration on completion

#### FR4: Workout History
- View past sessions with full details
- Filter by date, exercise, muscle group

### 2.2 Dashboard (MVP)

#### FR5: Today's View
- Show today's scheduled workout (or quick-start option)
- Daily calories and protein target vs actual
- Current body weight (last logged)
- Last PR achieved
- Workout streak (consecutive days)

### 2.3 Progress (MVP)

#### FR6: Charts
- Weight trend (daily weigh-ins)
- Volume trend (weekly total volume)
- Strength trend (estimated 1RM per major lift)
- Workout frequency (sessions per week)
- All charts use PyQtGraph

### 2.4 Nutrition (MVP)

#### FR7: CSV Import
- Import CSV from Cronometer
- Display daily calories, protein, fat, carbs
- No manual food logging in MVP

### 2.5 Settings (MVP)

#### FR8: Configuration
- Unit system (kg/lb)
- Theme (light/dark)
- Workout defaults (rest timer, warm-up sets)
- Data export

## 3. Non-Functional Requirements

### 3.1 Performance
- App launches in <3 seconds
- Workout logging feels instant (<100ms response)
- Charts render in <500ms
- CSV import of 1 year of data completes in <5 seconds

### 3.2 Offline-First
- All data stored locally in SQLite
- No internet connection required
- All features work offline

### 3.3 Data Integrity
- Workout data is never lost on crash (transactional writes)
- Auto-save every 30 seconds during active workout
- Database backup on each app launch

### 3.4 UI/UX
- Dark theme default
- Keyboard-navigable workout logging
- Minimal clicks to log a set (target: 2 taps)
- Responsive to window resizing

## 4. Data Model (MVP)

```
WorkoutPlan
  ├── name
  ├── description
  └── exercises (ordered list)

WorkoutSession
  ├── plan_id
  ├── started_at
  ├── completed_at
  └── exercises (with logged sets)

ExerciseLog
  ├── session_id
  ├── exercise_id (from knowledge/)
  ├── sets
  │   ├── weight, reps, rpe, completed
  ├── notes
  └── previous_session_data (for comparison)

NutritionLog
  ├── date
  ├── calories, protein, fat, carbs
  └── source (Cronometer import)

WeightLog
  ├── date
  └── weight_kg
```

## 5. Future Features (Post-MVP)

| Feature | Target Version | Description |
|---------|---------------|-------------|
| AI Coach | v0.2 | Personalised recommendations based on training data |
| Weekly Report | v0.2 | Automated email/in-app weekly summary |
| Recovery | v0.2 | HRV, sleep, readiness scoring |
| Cronometer Sync | v0.3 | Live API sync (not CSV) |
| Wearables | v0.4 | Apple Watch, Garmin, Whoop integration |
| Plugin SDK | v0.5 | Public SDK for third-party extensions |
| Mobile App | v0.6 | Companion iOS/Android app |
| Marketplace | v1.0 | Plugin marketplace and sharing |
