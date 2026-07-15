"""Dashboard data models — shared across all dashboard widgets.

Every widget reads from DashboardData. This is the single contract
between DashboardDataService and the view layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DashboardData:
    # ─── Header ──────────────────────────────────────────────
    greeting: str = "Good Morning"
    user_name: str = ""
    current_program: str = "No Active Program"
    mesocycle_week: int = 0
    current_split_day: str = ""
    current_weight: float = 0.0
    goal_weight_kg: float = 0.0
    remaining_weight: float = 0.0
    current_streak: int = 0
    total_workouts: int = 0
    weekly_volume_kg: float = 0.0
    goal_progress_estimated_date: str = ""

    # ─── Goal Progress (aliased from header for convenience) ─
    goal_progress_weight: float = 0.0
    goal_progress_target: float = 0.0
    goal_progress_remaining: float = 0.0
    goal_progress_weeks: int = 0
    goal_progress_rate: float = 0.0
    goal_progress_quality: str = ""
    goal_progress_percent: float = 0.0

    # ─── Recommendations ─────────────────────────────────────
    recommendations: list = field(default_factory=list)

    # ─── Today's Workout ─────────────────────────────────────
    today_workout_name: str = ""
    today_workout_exercise_count: int = 0
    today_workout_estimated_duration: int = 0
    today_workout_target_volume: float = 0.0
    today_workout_primary_muscles: list = field(default_factory=list)
    today_workout_warmup_status: str = ""

    # ─── Priority Muscles ────────────────────────────────────
    priority_muscles: list = field(default_factory=list)

    # ─── Recovery Status ─────────────────────────────────────
    recovery_status: Any = None
    recovery_level: str = ""
    recovery_score: float = 0.0
    recovery_flags: list = field(default_factory=list)
    recovery_suggested_action: str = ""

    # ─── Weekly Volume ───────────────────────────────────────
    weekly_volume_data: list = field(default_factory=list)

    # ─── Recent PRs ──────────────────────────────────────────
    recent_prs: list = field(default_factory=list)

    # ─── Nutrition ───────────────────────────────────────────
    nutrition_configured: bool = False
    nutrition_data: dict = field(default_factory=dict)

    # ─── Overview Metric Strip ───────────────────────────────
    # Each metric: (value_text, unit, qualifier, trend, trend_label)
    training_load: int = 0
    training_load_level: str = ""
    training_load_trend: str = ""
    calories_burned: int = 0
    calories_trend: str = ""
    active_minutes: int = 0
    active_trend: str = ""
    workout_score: int = 0
    workout_score_label: str = ""
    workout_score_trend: str = ""
    recovery_percent: int = 0
    recovery_qualifier: str = ""
    recovery_trend: str = ""

    # ─── Weekly Progress (dual series) ───────────────────────
    weekly_labels: list = field(default_factory=list)
    weekly_strength: list = field(default_factory=list)
    weekly_cardio: list = field(default_factory=list)
    week_workouts_done: int = 0
    week_workouts_target: int = 0
    week_sets_done: int = 0
    week_sets_target: int = 0
    week_volume_kg: float = 0.0
    week_volume_delta: str = ""
    week_prs: int = 0

    # ─── Muscle Group Focus ──────────────────────────────────
    # {muscle_key: "primary" | "secondary" | "untargeted"}
    muscle_focus: dict = field(default_factory=dict)

    # ─── Recent Workouts ─────────────────────────────────────
    # [{name, focus, score, date, color}]
    recent_workouts: list = field(default_factory=list)

    # ─── Recovery Vitals ─────────────────────────────────────
    # [{label, value, status}]
    recovery_vitals: list = field(default_factory=list)

    # ─── AI Coach ────────────────────────────────────────────
    ai_coach_title: str = ""
    ai_coach_body: str = ""
    ai_coach_fatigue: str = ""
    ai_coach_readiness: str = ""

    # ─── Gamification ────────────────────────────────────────
    # [{name, tier, unlocked}]
    achievements: list = field(default_factory=list)
    level: int = 0
    level_tier: str = ""
    xp_current: int = 0
    xp_target: int = 0
    milestone_label: str = ""
    body_weight_series: list = field(default_factory=list)
    body_weight_delta: str = ""
