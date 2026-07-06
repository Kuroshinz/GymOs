# Dashboard Widgets Reference

Each widget is a self-contained `DashboardCard` subclass in `ui/dashboard/dashboard_widgets/`.

---

## Header Widget (`header_widget.py`)

**Class:** `DashboardHeader`

**Purpose:** Top-level greeting and key performance indicators.

**Fields displayed:**
- Time-based greeting ("Good Morning", "Good Afternoon", "Good Evening") with user name
- Current program name
- Weight / Goal weight
- Current streak (consecutive training days)
- Total workouts completed
- Weekly volume (kg)
- Mesocycle week number
- Current split day

**Widget ID:** `DashboardHeader` (no base card — custom layout)

---

## Goal Progress Widget (`goal_progress_widget.py`)

**Class:** `GoalProgressWidget`

**Purpose:** Bodyweight goal tracking with progress bar.

**Fields displayed:**
- Current weight (large, prominent)
- Goal weight
- Remaining weight to goal
- Estimated weeks remaining
- Weekly gain rate (kg/week)
- Lean bulk quality assessment
- Progress bar (% toward goal)

**Empty state:** "No body weight data yet. Log your first weight to track progress."

**Data source:** `DecisionEngine.get_goal_progress()` ➜ `GoalProgress` model

---

## Recommendation Widget (`recommendation_widget.py`)

**Class:** `RecommendationWidget`

**Purpose:** Display the highest-priority recommendation from GymBrain's rule engine.

**Fields displayed:**
- Title (from recommendation)
- Priority badge (CRITICAL / HIGH / MEDIUM / LOW)
- Confidence percentage
- Description / reason
- Rule name
- Action to take
- Evidence summary (expandable)

**Interactions:**
- **Show/Hide evidence** — toggle button to expand/collapse evidence details
- **Dismiss** — temporarily hides the recommendation until next refresh
- **Mark Completed** — hides the recommendation

**Empty state:** "No recommendations. Keep up the great work!"

**Data source:** `DecisionEngine.get_today_recommendations()` ➜ `Recommendation` list

---

## Workout Widget (`workout_widget.py`)

**Class:** `WorkoutWidget`

**Purpose:** Show today's scheduled workout details and provide a start button.

**Fields displayed:**
- Workout day name
- Exercise count (badge)
- Estimated duration (minutes)
- Target volume (kg)
- Primary muscle groups (as chips/tags)
- Warm-up status note (intelligent: extended if fatigue is high)
- Start Workout button

**Empty state:** "No active program. Import a workout program to get started."

**Data source:** `ProgramManager.get_active_program_days()` + fatigue analysis

---

## Priority Muscles Widget (`priority_muscles_widget.py`)

**Class:** `PriorityMusclesWidget`

**Purpose:** Per-muscle training status — volume sufficiency and recovery.

**Fields per muscle:**
- Status dot (color-coded: red=bellow MEV, yellow=building, green=optimal, blue=maintenance, red=above MRV)
- Muscle name
- Current effective sets / Target range (MEV-MAV)
- Trend arrow (↑ improving, ↗ slightly improving, → stable, ↘ declining, ↓ declining)
- Recovery status (text)
- Weakness / recommendation text

**Empty state:** "No priority muscles defined. Set your training priorities in the program settings."

**Data source:** `DecisionEngine.get_priority_muscles()` ➜ `MuscleAnalysisResult` list

---

## Recovery Widget (`recovery_widget.py`)

**Class:** `RecoveryWidget`

**Purpose:** Display systemic fatigue and recovery status with color-coded severity.

**Fields displayed:**
- Large indicator dot (🟢 green = low fatigue, 🟡 yellow = moderate, 🔴 red = high, ⛔ dark red = very high)
- Fatigue level display with icon
- Score (0-100)
- Explanation text
- Recovery flags with severity (info/warning/critical)
- Suggested action

**Color coding:**
| Level | Color | Meaning |
|-------|-------|---------|
| Low | `#4ADE80` green | Training freely |
| Moderate | `#FBBF24` yellow | Manageable fatigue |
| High | `#F87171` red | Consider reducing volume |
| Very High | `#EF4444` dark red | Deload recommended |

**Empty state:** "No recovery data yet. Complete a workout to get recovery insights."

**Data source:** `DecisionEngine.get_recovery_status()` ➜ `FatigueResult`

---

## Volume Widget (`volume_widget.py`)

**Class:** `VolumeWidget`

**Purpose:** Weekly training volume breakdown by muscle group.

**Fields per muscle:**
- Muscle name
- Effective sets (number, color-coded by status)
- Target range (MEV-MAV)
- Frequency (x/week)
- Trend arrow

**Header row:** Column labels (Muscle, Sets, Target, Freq, Trend)

**Empty state:** "No volume data yet. Complete a workout to see weekly volume."

**Data source:** Priority muscles from `DecisionEngine.get_priority_muscles()`

---

## PR Widget (`pr_widget.py`)

**Class:** `PRWidget`

**Purpose:** Show last 5 personal records with navigation to full PR history.

**Fields per PR:**
- PR type emoji + label (Weight PR 🏋️, Volume PR 📈, Rep PR 🔁, Est. 1RM 💪)
- Exercise name
- Value (display_value)
- Improvement percentage
- Date achieved

**Actions:**
- **View All PRs** button — emits `view_all_prs_clicked` signal

**Empty state:** "No personal records yet. Push yourself in your next workout!"

**Data source:** `PREngine.get_latest_prs(limit=5)` ➜ `PersonalRecord` list

---

## Nutrition Widget (`nutrition_widget.py`)

**Class:** `NutritionWidget`

**Purpose:** Placeholder for future Nutrition Intelligence integration.

**When NOT configured:**
- "Nutrition tracking not configured." message
- "Set your daily targets to track calories..." guidance
- "Configure Nutrition" button (emits `configure_nutrition_clicked` signal)

**When configured (future):**
- Calories (current/target)
- Protein (current/target)
- Carbs (current/target)
- Fat (current/target)
- Hydration (current/target)

**Integration path:** Set `DashboardData.nutrition_configured = True` and
populate `nutrition_data` with macro dicts.

**Data source:** Not yet implemented — placeholder for Nutrition module.

---

## Quick Actions Widget (`quick_actions_widget.py`)

**Class:** `QuickActionsWidget`

**Purpose:** One-click buttons for common dashboard tasks.

**Buttons:**
| Button | Style | Signal |
|--------|-------|--------|
| ▶ Start Workout | Primary (purple) | `start_workout_clicked` |
| ⚖️ Log Body Weight | Secondary | `log_weight_clicked` |
| 📥 Import Program | Secondary | `import_program_clicked` |
| 📊 Weekly Review | Secondary | `weekly_review_clicked` |
| 📋 Recommendations | Secondary (full width) | `view_recommendations_clicked` |

**Future buttons** (when modules are implemented): Log Meal, Sleep, Recovery.

---

*See also: [DASHBOARD.md](DASHBOARD.md), [DASHBOARD_ARCHITECTURE.md](DASHBOARD_ARCHITECTURE.md)*
