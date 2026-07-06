from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ui.dashboard.dashboard_controller import DashboardController
from ui.dashboard.dashboard_models import DashboardData
from ui.design_system.components import SectionHeader
from ui.design_system.layout import (
    EditorialGrid,
    HeroPanel,
    MetricPanel,
    PanelSpan,
    ScrollContainer,
    SectionPanel,
)
from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens
from ui.design_system.tokens.spacing import SpacingTokens
from ui.design_system.visualization import (
    GoalRing,
    RecoveryRing,
    RiskMeter,
    WeeklyTimeline,
)

S = SpacingTokens()
R = RadiusTokens()


class DashboardView(QWidget):
    start_workout_clicked = Signal()
    view_all_prs_clicked = Signal()
    weekly_review_clicked = Signal()
    view_recommendations_clicked = Signal()
    log_weight_clicked = Signal()
    import_program_clicked = Signal()

    def __init__(
        self,
        db: Any = None,
        prog_mgr: Any = None,
        nutrition_service: Any = None,
        controller: DashboardController | None = None,
    ) -> None:
        super().__init__()
        self._db = db
        self._prog_mgr = prog_mgr
        self._nutrition_service = nutrition_service

        if controller:
            self._controller = controller
        else:
            self._build_default_controller(db, prog_mgr)

        self._build_ui()
        self._connect_signals()

    def _build_default_controller(self, db: Any, prog_mgr: Any) -> None:
        from modules.gymbrain.services.decision_engine import DecisionEngine
        from modules.workout.application.pr_engine import PREngine
        nutrition_provider = getattr(self._nutrition_service, "provider", None) if self._nutrition_service else None
        engine = DecisionEngine.from_production(db=db, nutrition_provider=nutrition_provider) if db else None
        pr_engine = PREngine(db) if db else None
        self._controller = DashboardController(
            db=db,
            decision_engine=engine,
            pr_engine=pr_engine,
            prog_mgr=prog_mgr,
            nutrition_service=self._nutrition_service,
        )

    def _colors(self):
        return color_from_scheme(ColorScheme.DARK)

    def _build_ui(self) -> None:
        colors = self._colors()
        scroll = ScrollContainer()
        scroll_layout = scroll._wrapper.layout()
        scroll_layout.setContentsMargins(32, 24, 32, 32)
        scroll_layout.setSpacing(0)
        scroll_layout.setAlignment(Qt.AlignTop)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(24)
        scroll_layout.insertLayout(0, main_layout)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)

        self._build_hero_section(main_layout)
        self._build_middle_section(main_layout)
        self._build_bottom_section(main_layout)

        main_layout.addStretch()

    def _build_hero_section(self, parent: QVBoxLayout) -> None:
        colors = self._colors()

        hero = HeroPanel(
            title="Today's Mission",
            subtitle="Your readiness, goal progress, and next action at a glance.",
        )
        parent.addWidget(hero)

        self._recovery_ring = RecoveryRing(size=100)
        hero.add_content(self._recovery_ring)

        self._goal_ring = GoalRing(size=100)
        hero.add_content(self._goal_ring)

        self._hero_readiness = MetricPanel(value="--", label="Readiness", icon="")
        hero.add_content(self._hero_readiness)

        grid = EditorialGrid()
        grid.set_spacing(16)
        parent.addWidget(grid)

        self._hero_workout_section = SectionPanel(title="Next Workout", subtitle="No active program", span=PanelSpan.HALF)
        self._hero_workout_name = QLabel("")
        self._hero_workout_name.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 18px; font-weight: 700; background: transparent; border: none;"
        )
        self._hero_workout_section.add_content(self._hero_workout_name)
        grid.add_section(self._hero_workout_section)

        self._hero_rec_section = SectionPanel(title="Top Recommendation", subtitle="No recommendations", span=PanelSpan.HALF)
        grid.add_section(self._hero_rec_section)

    def _build_middle_section(self, parent: QVBoxLayout) -> None:
        colors = self._colors()

        middle_header = SectionHeader(title="Overview", subtitle="Recovery, prediction, and weekly trends")
        parent.addWidget(middle_header)

        middle_grid = EditorialGrid()
        middle_grid.set_spacing(16)
        parent.addWidget(middle_grid)

        self._recovery_section = SectionPanel(title="Recovery", subtitle="Readiness & fatigue", span=PanelSpan.THIRD)
        self._recovery_value = QLabel("--")
        self._recovery_value.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 32px; font-weight: 800; background: transparent; border: none;"
        )
        self._recovery_section.add_content(self._recovery_value)

        self._recovery_status = QLabel("")
        self._recovery_status.setStyleSheet(
            f"color: {colors.text_secondary}; font-size: 13px; background: transparent; border: none;"
        )
        self._recovery_section.add_content(self._recovery_status)
        middle_grid.add_section(self._recovery_section)

        self._prediction_section = SectionPanel(title="Prediction", subtitle="Forecast & risk", span=PanelSpan.THIRD)
        self._prediction_risk = RiskMeter(width=140, height=24)
        self._prediction_risk.set_risk(0.0, "Risk Level")
        self._prediction_section.add_content(self._prediction_risk)

        self._prediction_conf = QLabel("-- confidence")
        self._prediction_conf.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 12px; background: transparent; border: none;"
        )
        self._prediction_section.add_content(self._prediction_conf)
        middle_grid.add_section(self._prediction_section)

        self._weekly_section = SectionPanel(title="Weekly Volume", subtitle="Sets by day", span=PanelSpan.THIRD)
        self._weekly_timeline = WeeklyTimeline()
        self._weekly_section.add_content(self._weekly_timeline)
        self._weekly_total = QLabel("")
        self._weekly_total.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 12px; background: transparent; border: none;"
        )
        self._weekly_section.add_content(self._weekly_total)
        middle_grid.add_section(self._weekly_section)

    def _build_bottom_section(self, parent: QVBoxLayout) -> None:
        bottom_header = SectionHeader(title="Insights", subtitle="Explainability, milestones & timeline")
        parent.addWidget(bottom_header)

        bottom_grid = EditorialGrid()
        bottom_grid.set_spacing(16)
        parent.addWidget(bottom_grid)

        self._recommendation_section = SectionPanel(title="Recommendations", subtitle="AI-driven insights", span=PanelSpan.HALF)
        bottom_grid.add_section(self._recommendation_section)

        self._milestones_section = SectionPanel(title="Upcoming Milestones", subtitle="Your next achievements", span=PanelSpan.HALF)
        bottom_grid.add_section(self._milestones_section)

    def _connect_signals(self) -> None:
        self._controller.data_updated.connect(self._on_data_updated)

    def _on_data_updated(self, data: DashboardData) -> None:
        self._update_hero(data)
        self._update_middle(data)
        self._update_bottom(data)

    def _update_hero(self, data: DashboardData) -> None:
        rec_score = getattr(data, "recovery_score", 0.0) or 0.0
        self._recovery_ring.set_value(rec_score, 100.0, "Recovery")

        goal_pct = getattr(data, "goal_progress_percent", 0.0) or 0.0
        goal_target = getattr(data, "goal_progress_target", 100.0) or 100.0
        goal_current = getattr(data, "goal_progress_weight", 0.0) or 0.0
        if goal_current > 0:
            self._goal_ring.set_goal(goal_current, goal_target, "Goal", "kg")
        else:
            self._goal_ring.set_goal(0, 100, "Goal", "")

        readiness = getattr(data, "recovery_level", "") or "N/A"
        self._hero_readiness = MetricPanel(value=readiness.capitalize() if readiness != "N/A" else "--", label="Readiness Level")

        workout_name = getattr(data, "today_workout_name", "") or ""
        if workout_name:
            self._hero_workout_section.clear()
            self._hero_workout_name.setText(workout_name)
            self._hero_workout_section.add_content(self._hero_workout_name)
            ex_count = getattr(data, "today_workout_exercise_count", 0) or 0
            dur = getattr(data, "today_workout_estimated_duration", 0) or 0
            meta = QLabel(f"{ex_count} exercises  \u00B7  ~{dur} min" if dur else f"{ex_count} exercises")
            meta.setStyleSheet(
                f"color: {self._colors().text_disabled}; font-size: 12px; background: transparent; border: none;"
            )
            self._hero_workout_section.add_content(meta)
        else:
            self._hero_workout_section.clear()

        recs = getattr(data, "recommendations", [])
        self._hero_rec_section.clear()
        if recs:
            top = recs[0]
            title = getattr(top, "title", "") or getattr(top, "description", "Recommendation")
            t = QLabel(title)
            t.setStyleSheet(
                f"color: {self._colors().text_primary}; font-size: 14px; font-weight: 600; "
                f"background: transparent; border: none;"
            )
            t.setWordWrap(True)
            self._hero_rec_section.add_content(t)

    def _update_middle(self, data: DashboardData) -> None:
        colors = self._colors()
        rec_score = getattr(data, "recovery_score", 0.0) or 0.0
        self._recovery_value.setText(f"{rec_score:.0f}")
        rec_level = getattr(data, "recovery_level", "") or ""
        if rec_level:
            self._recovery_status.setText(rec_level.capitalize())
        else:
            self._recovery_status.setText("N/A")

        risk_val = max(0.0, min(1.0, (100 - rec_score) / 100))
        self._prediction_risk.set_risk(risk_val, "Overtraining Risk")

        vol_data = getattr(data, "weekly_volume_data", [])
        if vol_data:
            values = []
            for v in vol_data:
                if isinstance(v, dict):
                    values.append(v.get("volume", 0.0) or 0.0)
                else:
                    values.append(float(v) if v else 0.0)
            self._weekly_timeline.set_data(values, max_value=max(values) if values else 100.0)
        else:
            self._weekly_timeline.set_data([0, 0, 0, 0, 0, 0, 0])

        weekly_vol = getattr(data, "weekly_volume_kg", 0.0) or 0.0
        self._weekly_total.setText(f"Total: {weekly_vol:.0f} kg this week")

    def _update_bottom(self, data: DashboardData) -> None:
        colors = self._colors()

        recs = getattr(data, "recommendations", [])
        self._recommendation_section.clear()
        if recs:
            for i, rec in enumerate(recs[:3]):
                title = getattr(rec, "title", "") or getattr(rec, "description", f"Recommendation {i+1}")
                t = QLabel(f"\u2022  {title}")
                t.setStyleSheet(
                    f"color: {colors.text_primary}; font-size: 13px; background: transparent; border: none;"
                )
                t.setWordWrap(True)
                self._recommendation_section.add_content(t)
        else:
            empty = QLabel("No recommendations available.")
            empty.setStyleSheet(f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;")
            self._recommendation_section.add_content(empty)

        self._milestones_section.clear()
        prs = getattr(data, "recent_prs", [])
        if prs:
            for pr in prs[:3]:
                pr_name = pr if isinstance(pr, str) else getattr(pr, "exercise_name", str(pr))
                t = QLabel(f"\u2B50  {pr_name}")
                t.setStyleSheet(
                    f"color: {colors.text_primary}; font-size: 13px; background: transparent; border: none;"
                )
                self._milestones_section.add_content(t)
        else:
            empty = QLabel("No recent PRs.")
            empty.setStyleSheet(f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;")
            self._milestones_section.add_content(empty)
            goal_date = getattr(data, "goal_progress_estimated_date", "") or ""
            if goal_date:
                est = QLabel(f"Goal estimated by: {goal_date}")
                est.setStyleSheet(
                    f"color: {colors.text_secondary}; font-size: 12px; background: transparent; border: none;"
                )
                self._milestones_section.add_content(est)

    def refresh(self) -> None:
        self._controller.refresh()

    def controller(self) -> DashboardController:
        return self._controller
