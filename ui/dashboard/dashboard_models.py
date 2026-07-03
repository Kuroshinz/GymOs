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
