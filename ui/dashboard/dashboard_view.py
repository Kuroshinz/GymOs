"""Dashboard Experience 3.0 — editorial magazine layout.

Layout hierarchy (top-to-bottom, weighted by visual mass):

  ┌──────────────────────────────────────────────────────────┐
  │  HERO (45% viewport)                                     │
  │  Identity · Phase · Prediction · Metrics · Primary CTA   │
  │  "You're on track for a squat PR this week."            │
  └──────────────────────────────────────────────────────────┘
  ┌──────────────────────────────────────────────────────────┐
  │  TODAY'S MISSION                                         │
  │  Largest card · Workout hero · Muscles · CTA             │
  └──────────────────────────────────────────────────────────┘
  ┌──────────────┐  ┌──────────────────────────────────────┐
  │  RECOVERY    │  │  COACH                               │
  │  Narrative   │  │  "Your bench press is ready for..."  │
  │  38% width   │  │  62% width · Actionable              │
  └──────────────┘  └──────────────────────────────────────┘
  ┌──────────────────────────────────────┐  ┌──────────────┐
  │  PROGRESS                            │  │  PREDICTIONS │
  │  Journey · Timeline · Streak · PRs   │  │  Coaching    │
  │  62% width                           │  │  38% width   │
  └──────────────────────────────────────┘  └──────────────┘
  ┌──────────────────────────────────────────────────────────┐
  │  QUICK ACTIONS (5 interactive cards in a row)            │
  └──────────────────────────────────────────────────────────┘

Preserved: all 6 signals, controller interface, data contract.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, Signal
from PySide6.QtWidgets import QGraphicsOpacityEffect
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ui.dashboard.dashboard_controller import DashboardController
from ui.dashboard.dashboard_models import DashboardData
from ui.design_system.components.app_card import AppCard
from ui.design_system.components.empty_state import EmptyState
from ui.design_system.components.insight_card import InsightCard
from ui.design_system.components.section_header import SectionHeader
from ui.design_system.components.status_badge import StatusBadge, StatusLevel
from ui.design_system.layout import EditorialGrid, PanelSpan, ScrollContainer
from ui.design_system.tokens.color import ColorScheme, color_from_scheme, resolve_alpha
from ui.design_system.tokens.elevation import apply_elevation, glow_effect
from ui.design_system.tokens.motion import MotionTokens
from ui.design_system.tokens.radius import RadiusTokens, px_from_token
from ui.design_system.tokens.spacing import SpacingTokens
from ui.design_system.tokens.typography import TypographyTokens, font_style
from ui.design_system.visualization import GoalRing, RecoveryRing, WeeklyTimeline


_GLOW = lambda c: resolve_alpha(c, 0.35)

M = MotionTokens()
S = SpacingTokens()
R = RadiusTokens()
T = TypographyTokens()

_px2 = px_from_token(S.half)
_px4 = px_from_token(S.s1)
_px6 = px_from_token(S.s1_5)
_px8 = px_from_token(S.s2)
_px10 = px_from_token(S.s2_5)
_px12 = px_from_token(S.s3)
_px16 = px_from_token(S.s4)
_px20 = px_from_token(S.s5)
_px24 = px_from_token(S.s6)
_px28 = px_from_token(S.s7)
_px32 = px_from_token(S.s8)
_px40 = px_from_token(S.s10)
_px48 = px_from_token(S.s12)

_ANI_DURATION = 200


class _CommandCard(QFrame):
    clicked = Signal()

    def mousePressEvent(self, event) -> None:
        self.clicked.emit()
        super().mousePressEvent(event)


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

        self._last_data: DashboardData | None = None
        self._animations: list[QPropertyAnimation] = []
        self._build_ui()
        self._connect_signals()

    def _build_default_controller(self, db: Any, prog_mgr: Any) -> None:
        from modules.gymbrain.services.decision_engine import DecisionEngine
        from modules.workout.application.pr_engine import PREngine

        nutrition_provider = (
            getattr(self._nutrition_service, "provider", None)
            if self._nutrition_service
            else None
        )
        engine = (
            DecisionEngine.from_production(db=db, nutrition_provider=nutrition_provider)
            if db
            else None
        )
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

    # ── Build UI ─────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setStyleSheet("""
            DashboardView {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #050816, stop:0.5 #080C24, stop:1 #0A0E28);
            }
        """)
        self._scroll = ScrollContainer()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._scroll)

        layout = self._scroll.content_layout
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        main = QVBoxLayout()
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)
        layout.insertLayout(0, main)

        # 1. Hero — occupies roughly the first screen
        self._build_hero(main)

        # 2. Today's Mission — dominant editorial card
        self._build_section_header(main, "Today's Mission", "Your next training session")
        self._build_todays_mission(main)

        # 3. Asymmetric two-column: Recovery (38%) + Coach (62%)
        self._build_section_header(main, "Recovery & Coach", "Readiness & personalized guidance")
        self._middle_grid = EditorialGrid()
        self._middle_grid.set_spacing(_px16)
        main.addWidget(self._middle_grid)
        self._build_recovery_and_coach()

        # 4. Asymmetric two-column: Progress (62%) + Predictions (38%)
        self._build_section_header(main, "Progress & Predictions", "Your training journey")
        self._bottom_grid = EditorialGrid()
        self._bottom_grid.set_spacing(_px16)
        main.addWidget(self._bottom_grid)
        self._build_progress_and_predictions()

        # 5. Quick Actions
        self._build_section_header(main, "Quick Actions", "Common tasks")
        self._build_quick_actions(main)

        main.addStretch()

    @staticmethod
    def _build_section_header(
        parent: QVBoxLayout, title: str, subtitle: str
    ) -> None:
        header = SectionHeader(title=title, subtitle=subtitle)
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, _px28, 0, _px8)
        hbox.addWidget(header)
        parent.addLayout(hbox)

    # ── Hero ────────────────────────────────────────────────────

    def _build_hero(self, parent: QVBoxLayout) -> None:
        colors = self._colors()

        self._hero_frame = QFrame()
        self._hero_frame.setObjectName("HeroFrame")
        self._hero_frame.setMinimumHeight(320)
        self._hero_frame.setStyleSheet(f"""
            QFrame#HeroFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(12,16,51,0.85), stop:0.35 rgba(20,16,74,0.7),
                    stop:0.7 rgba(26,13,68,0.6), stop:1 rgba(10,14,40,0.5));
                border-radius: {R.xl};
                border: 1px solid rgba(139, 92, 246, 0.10);
            }}
        """)
        apply_elevation(self._hero_frame, 3, is_dark=True, bg_color=colors.surface)

        hero_layout = QVBoxLayout(self._hero_frame)
        hero_layout.setContentsMargins(_px32, _px28, _px32, _px24)
        hero_layout.setSpacing(0)

        # Top section: greeting + rings
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)

        left_area = QVBoxLayout()
        left_area.setSpacing(_px6)

        self._hero_greeting = QLabel("Good Morning")
        self._hero_greeting.setStyleSheet(
            f"color: {colors.text_primary}; {font_style('hero')}; "
            f"letter-spacing: -0.03em; background: transparent;"
        )
        left_area.addWidget(self._hero_greeting)

        self._hero_subtitle = QLabel("")
        self._hero_subtitle.setStyleSheet(
            f"color: {colors.text_secondary}; {font_style('body')}; background: transparent;"
        )
        self._hero_subtitle.setWordWrap(True)
        left_area.addWidget(self._hero_subtitle)

        left_area.addStretch()
        top_row.addLayout(left_area, 1)

        # Rings area
        rings_area = QHBoxLayout()
        rings_area.setSpacing(_px16)
        rings_area.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self._recovery_ring = RecoveryRing(size=72)
        rings_area.addWidget(self._recovery_ring)

        self._goal_ring = GoalRing(size=72)
        rings_area.addWidget(self._goal_ring)

        top_row.addLayout(rings_area)
        hero_layout.addLayout(top_row)

        hero_layout.addSpacing(_px16)

        # Motivational prediction sentence
        self._hero_prediction = QLabel("")
        self._hero_prediction.setStyleSheet(
            f"color: {colors.primary}; {font_style('body', 'bold')}; "
            f"background: transparent; padding: {S.s2} 0;"
        )
        self._hero_prediction.setWordWrap(True)
        self._hero_prediction.hide()
        hero_layout.addWidget(self._hero_prediction)

        hero_layout.addSpacing(_px8)

        # Metric clusters row
        metrics_row = QHBoxLayout()
        metrics_row.setContentsMargins(0, 0, 0, 0)
        metrics_row.setSpacing(_px24)

        metric_defs = [
            ("_hero_metric_ready", "Readiness", "success"),
            ("_hero_metric_weight", "Current", "text_primary"),
            ("_hero_metric_goal", "To Goal", "warning"),
            ("_hero_metric_streak", "Streak", "pr"),
        ]

        metric_widgets = []
        for attr_prefix, label, color_key in metric_defs:
            block = QFrame()
            block.setStyleSheet("background: transparent; border: none;")
            bl = QVBoxLayout(block)
            bl.setContentsMargins(0, 0, 0, 0)
            bl.setSpacing(_px2)

            val_label = QLabel("--")
            val_label.setStyleSheet(
                f"color: {getattr(colors, color_key, colors.text_primary)}; "
                f"{font_style('metric')}; letter-spacing: -0.03em; background: transparent;"
            )
            bl.addWidget(val_label)

            name_label = QLabel(label)
            name_label.setStyleSheet(
                f"color: {colors.text_disabled}; {font_style('caption')}; background: transparent;"
            )
            bl.addWidget(name_label)

            metrics_row.addWidget(block)
            setattr(self, f"{attr_prefix}_val", val_label)
            setattr(self, f"{attr_prefix}_lbl", name_label)

        metrics_row.addStretch()
        hero_layout.addLayout(metrics_row)

        hero_layout.addSpacing(_px16)

        # CTA row
        cta_row = QHBoxLayout()
        cta_row.setContentsMargins(0, 0, 0, 0)
        cta_row.setSpacing(_px12)

        self._hero_start_btn = QPushButton("  \u25B6  Start Workout")
        self._hero_start_btn.setCursor(Qt.PointingHandCursor)
        self._hero_start_btn.setFixedHeight(52)
        self._hero_start_btn.setMinimumWidth(200)
        self._hero_start_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(139,92,246,0.9), stop:0.5 rgba(168,85,247,0.85), stop:1 rgba(217,70,239,0.8));
                color: #FFFFFF;
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: {R.size_2xl};
                padding: 0 {S.s7};
                {font_style('body', 'bold')}
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(167,139,250,0.9), stop:0.5 rgba(192,132,252,0.85), stop:1 rgba(232,121,249,0.8));
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(124,58,237,0.95), stop:0.5 rgba(147,51,234,0.9), stop:1 rgba(192,38,211,0.85));
            }}
            QPushButton:focus {{
                border: 2px solid #A78BFA;
            }}
        """)
        self._hero_start_btn.clicked.connect(self.start_workout_clicked.emit)
        self._hero_start_btn.setAccessibleName("Start Workout")
        glow_effect(self._hero_start_btn, glow_rgba=_GLOW(colors.primary), blur=20, offset_y=0)
        cta_row.addWidget(self._hero_start_btn)

        self._hero_review_btn = QPushButton("  \u270F  Review Week")
        self._hero_review_btn.setCursor(Qt.PointingHandCursor)
        self._hero_review_btn.setFixedHeight(52)
        self._hero_review_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {colors.text_primary};
                border: 1px solid rgba(139, 92, 246, 0.12);
                border-radius: {R.size_2xl};
                padding: 0 {S.s7};
                {font_style('body', 'bold')}
            }}
            QPushButton:hover {{
                background-color: rgba(139, 92, 246, 0.10);
                border-color: rgba(139, 92, 246, 0.25);
            }}
            QPushButton:focus {{
                border: 2px solid #A78BFA;
            }}
        """)
        self._hero_review_btn.clicked.connect(self.weekly_review_clicked.emit)
        self._hero_review_btn.setAccessibleName("Review Week")
        cta_row.addWidget(self._hero_review_btn)

        cta_row.addStretch()
        hero_layout.addLayout(cta_row)

        parent.addWidget(self._hero_frame)

    # ── Today's Mission ─────────────────────────────────────────

    def _build_todays_mission(self, parent: QVBoxLayout) -> None:
        colors = self._colors()

        self._mission_card = AppCard(title="", elevated=True)
        self._mission_card.setStyleSheet(f"""
            AppCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(12,16,51,0.85), stop:0.4 rgba(17,13,61,0.7),
                    stop:0.75 rgba(22,10,56,0.6), stop:1 rgba(10,14,40,0.5));
                border-radius: {R.xl};
                border: 1px solid rgba(139, 92, 246, 0.10);
            }}
        """)

        # Accent bar using CardHeader-style left border
        mission_layout = QVBoxLayout()
        mission_layout.setContentsMargins(0, 0, 0, 0)
        mission_layout.setSpacing(_px12)

        # Workout identity
        workout_top = QHBoxLayout()
        workout_top.setContentsMargins(0, 0, 0, 0)

        self._workout_name = QLabel("")
        self._workout_name.setStyleSheet(
            f"color: {colors.text_primary}; {font_style('h2')}; "
            f"letter-spacing: -0.02em; background: transparent;"
        )
        self._workout_name.setWordWrap(True)
        workout_top.addWidget(self._workout_name, 1)

        mission_layout.addLayout(workout_top)

        self._workout_meta = QLabel("")
        self._workout_meta.setStyleSheet(
            f"color: {colors.text_secondary}; {font_style('body')}; background: transparent;"
        )
        self._workout_meta.setWordWrap(True)
        mission_layout.addWidget(self._workout_meta)

        self._workout_muscle_row = QHBoxLayout()
        self._workout_muscle_row.setContentsMargins(0, 0, 0, 0)
        self._workout_muscle_row.setSpacing(_px6)
        self._workout_muscle_container = QWidget()
        self._workout_muscle_container.setLayout(self._workout_muscle_row)
        self._workout_muscle_container.setStyleSheet("background: transparent;")
        mission_layout.addWidget(self._workout_muscle_container)

        self._mission_start_btn = QPushButton("  \u25B6  Start Workout")
        self._mission_start_btn.setCursor(Qt.PointingHandCursor)
        self._mission_start_btn.setFixedHeight(52)
        self._mission_start_btn.setMinimumWidth(200)
        self._mission_start_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(139,92,246,0.9), stop:0.5 rgba(168,85,247,0.85), stop:1 rgba(217,70,239,0.8));
                color: #FFFFFF;
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: {R.size_2xl};
                padding: 0 {S.s7};
                {font_style('body', 'bold')}
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(167,139,250,0.9), stop:0.5 rgba(192,132,252,0.85), stop:1 rgba(232,121,249,0.8));
            }}
            QPushButton:focus {{
                border: 2px solid #A78BFA;
            }}
        """)
        self._mission_start_btn.clicked.connect(self.start_workout_clicked.emit)
        self._mission_start_btn.setAccessibleName("Start Workout")
        glow_effect(self._mission_start_btn, glow_rgba=_GLOW(colors.primary), blur=16, offset_y=0)

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, _px4, 0, 0)
        btn_row.addWidget(self._mission_start_btn)
        btn_row.addStretch()
        mission_layout.addLayout(btn_row)

        self._mission_card.add_content(self._workout_name)
        self._mission_card.add_content(self._workout_meta)
        self._mission_card.add_content(self._workout_muscle_container)
        self._mission_card.add_content(self._mission_start_btn)
        self._workout_name.hide()
        self._workout_meta.hide()
        self._workout_muscle_container.hide()
        self._mission_start_btn.hide()

        self._workout_empty = EmptyState(
            icon="\U0001F3CB",
            title="No Workout Today",
            message="Import a program or start a free workout to get going.",
            action_text="Import Program",
            on_action=self.import_program_clicked.emit,
        )
        self._mission_card.add_content(self._workout_empty)

        parent.addWidget(self._mission_card)

    # ── Recovery + Coach (asymmetric: 38% / 62%) ───────────────

    def _build_recovery_and_coach(self) -> None:
        colors = self._colors()

        # ── Left: Recovery (38%) ─────────────────────────────────
        self._recovery_card = AppCard(title="Recovery", elevated=False)
        self._recovery_card.setStyleSheet(f"""
            AppCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(12,16,51,0.8), stop:1 rgba(8,12,36,0.5));
                border-radius: {R.lg};
                border: 1px solid rgba(139, 92, 246, 0.08);
            }}
        """)

        self._recovery_level_label = QLabel("--")
        self._recovery_level_label.setStyleSheet(
            f"color: {colors.text_primary}; {font_style('h3')}; "
            f"letter-spacing: -0.02em; background: transparent;"
        )
        self._recovery_card.add_content(self._recovery_level_label)

        self._recovery_score_label = QLabel("")
        self._recovery_score_label.setStyleSheet(
            f"color: {colors.text_secondary}; {font_style('body')}; background: transparent;"
        )
        self._recovery_card.add_content(self._recovery_score_label)

        self._recovery_suggested = QLabel("")
        self._recovery_suggested.setWordWrap(True)
        self._recovery_suggested.setStyleSheet(
            f"color: {colors.primary}; {font_style('body')}; "
            f"padding-top: {S.s1}; background: transparent;"
        )
        self._recovery_card.add_content(self._recovery_suggested)

        self._recovery_empty = EmptyState(
            icon="\U0001FA9D",
            title="No Recovery Data",
            message="Complete a workout to unlock recovery insights.",
        )
        self._recovery_card.add_content(self._recovery_empty)
        self._recovery_empty.hide()

        self._recovery_content = QWidget()
        self._recovery_content_layout = QVBoxLayout(self._recovery_content)
        self._recovery_content_layout.setContentsMargins(0, 0, 0, 0)
        self._recovery_content_layout.addWidget(self._recovery_level_label)
        self._recovery_content_layout.addWidget(self._recovery_score_label)
        self._recovery_content_layout.addWidget(self._recovery_suggested)

        self._middle_grid.add_panel(self._recovery_card, span=PanelSpan.QUARTER)

        # ── Right: Coach (62% = 8/12 columns) ────────────────────
        self._coach_card = AppCard(title="Coach", elevated=False)
        self._coach_card.setStyleSheet(f"""
            AppCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(17,13,61,0.85), stop:0.5 rgba(20,16,74,0.7),
                    stop:0.8 rgba(22,10,56,0.6), stop:1 rgba(12,16,51,0.5));
                border-radius: {R.lg};
                border: 1px solid rgba(139, 92, 246, 0.12);
            }}
        """)
        glow_effect(self._coach_card, glow_rgba=_GLOW(colors.primary), blur=20, offset_y=1)

        self._coach_container = QVBoxLayout()
        self._coach_container.setContentsMargins(0, 0, 0, 0)
        self._coach_container.setSpacing(_px8)
        self._coach_widget = QWidget()
        self._coach_widget.setLayout(self._coach_container)
        self._coach_card.add_content(self._coach_widget)

        self._coach_empty = EmptyState(
            icon="\U0001F9D1\u200D\U0001F3EB",
            title="Coach Is Ready",
            message="Recommendations will appear after completing workouts.",
        )
        self._coach_card.add_content(self._coach_empty)

        self._middle_grid.add_panel(self._coach_card, span=PanelSpan.TWO_THIRDS)

    # ── Progress + Predictions (asymmetric: 62% / 38%) ─────────

    def _build_progress_and_predictions(self) -> None:
        colors = self._colors()

        # ── Left: Progress (62%) ─────────────────────────────────
        self._progress_card = AppCard(title="Progress", elevated=False)
        self._progress_card.setStyleSheet(f"""
            AppCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(12,16,51,0.8), stop:1 rgba(8,12,36,0.5));
                border-radius: {R.lg};
                border: 1px solid rgba(139, 92, 246, 0.08);
            }}
        """)

        # Goal section
        goal_top = QHBoxLayout()
        goal_top.setContentsMargins(0, 0, 0, 0)

        self._goal_weight_label = QLabel("--")
        self._goal_weight_label.setStyleSheet(
            f"color: {colors.text_primary}; {font_style('metric')}; "
            f"letter-spacing: -0.03em; background: transparent;"
        )
        goal_top.addWidget(self._goal_weight_label)

        self._goal_detail_label = QLabel("")
        self._goal_detail_label.setStyleSheet(
            f"color: {colors.text_disabled}; {font_style('body')}; background: transparent;"
        )
        self._goal_detail_label.setWordWrap(True)
        goal_top.addWidget(self._goal_detail_label, 1)

        self._goal_empty = QLabel("No goal data yet.")
        self._goal_empty.setStyleSheet(
            f"color: {colors.text_disabled}; {font_style('body')}; background: transparent;"
        )
        self._goal_empty.setAlignment(Qt.AlignCenter)
        goal_top.addWidget(self._goal_empty)
        self._goal_empty.hide()

        self._progress_card.add_layout(goal_top)

        # Volume bar
        self._weekly_timeline = WeeklyTimeline()
        self._weekly_timeline.setFixedHeight(40)
        self._progress_card.add_content(self._weekly_timeline)

        self._weekly_total = QLabel("")
        self._weekly_total.setStyleSheet(
            f"color: {colors.text_disabled}; {font_style('caption')}; background: transparent;"
        )
        self._progress_card.add_content(self._weekly_total)

        self._volume_empty = QLabel("No volume data yet.")
        self._volume_empty.setStyleSheet(
            f"color: {colors.text_disabled}; {font_style('body')}; background: transparent;"
        )
        self._volume_empty.setAlignment(Qt.AlignCenter)
        self._progress_card.add_content(self._volume_empty)
        self._volume_empty.show()

        self._volume_content = QWidget()
        self._volume_content_layout = QVBoxLayout(self._volume_content)
        self._volume_content_layout.setContentsMargins(0, 0, 0, 0)
        self._volume_content_layout.addWidget(self._weekly_timeline)
        self._volume_content_layout.addWidget(self._weekly_total)
        self._volume_content.hide()

        # PRs
        self._prs_container = QVBoxLayout()
        self._prs_container.setContentsMargins(0, _px6, 0, 0)
        self._prs_container.setSpacing(_px4)

        self._prs_widget = QWidget()
        self._prs_widget.setLayout(self._prs_container)
        self._prs_widget.setStyleSheet("background: transparent;")

        self._prs_empty = QLabel("No PRs yet. Push yourself!")
        self._prs_empty.setStyleSheet(
            f"color: {colors.text_disabled}; {font_style('body')}; background: transparent;"
        )
        self._prs_empty.setAlignment(Qt.AlignCenter)
        self._prs_empty.setWordWrap(True)

        self._progress_card.add_content(self._prs_widget)
        self._progress_card.add_content(self._prs_empty)
        self._prs_widget.hide()
        self._prs_empty.show()

        self._goal_content = QWidget()
        self._goal_content_layout = QVBoxLayout(self._goal_content)
        self._goal_content_layout.setContentsMargins(0, 0, 0, 0)
        self._goal_content_layout.addWidget(self._goal_weight_label)
        self._goal_content_layout.addWidget(self._goal_detail_label)
        self._goal_content.hide()

        self._bottom_grid.add_panel(self._progress_card, span=PanelSpan.TWO_THIRDS)

        # ── Right: Predictions (38%) ─────────────────────────────
        self._predictions_card = AppCard(title="Predictions", elevated=False)
        self._predictions_card.setStyleSheet(f"""
            AppCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(12,16,51,0.8), stop:1 rgba(8,12,36,0.5));
                border-radius: {R.lg};
                border: 1px solid rgba(139, 92, 246, 0.08);
            }}
        """)

        self._predictions_container = QVBoxLayout()
        self._predictions_container.setContentsMargins(0, 0, 0, 0)
        self._predictions_container.setSpacing(_px8)
        self._predictions_widget = QWidget()
        self._predictions_widget.setLayout(self._predictions_container)
        self._predictions_widget.setStyleSheet("background: transparent;")
        self._predictions_card.add_content(self._predictions_widget)

        self._predictions_empty = EmptyState(
            icon="\U0001F52E",
            title="No Predictions Yet",
            message="AI predictions will appear after a few workouts.",
        )
        self._predictions_card.add_content(self._predictions_empty)

        self._bottom_grid.add_panel(self._predictions_card, span=PanelSpan.QUARTER)

    # ── Quick Actions ──────────────────────────────────────────

    def _build_quick_actions(self, parent: QVBoxLayout) -> None:
        colors = self._colors()

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(_px10)

        actions = [
            ("\u25B6", "Start Workout", "Begin a new session",
             self.start_workout_clicked.emit, True),
            ("\u2696", "Log Weight", "Record body weight",
             self.log_weight_clicked.emit, False),
            ("\u2B07", "Import Program", "Import from file",
             self.import_program_clicked.emit, False),
            ("\u2728", "View PRs", "Personal records",
             self.view_all_prs_clicked.emit, False),
            ("\u270F", "Review Week", "Training summary",
             self.weekly_review_clicked.emit, False),
        ]

        for i, (icon, label, tip, handler, primary) in enumerate(actions):
            card = _CommandCard()
            card.setCursor(Qt.PointingHandCursor)
            card.setFixedHeight(96)
            card.setMinimumWidth(140)
            card.setToolTip(tip)
            card.setAccessibleName(f"{label} command card")
            card.clicked.connect(handler)

            if primary:
                bg_grad = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(139,92,246,0.9), stop:0.6 rgba(168,85,247,0.85), stop:1 rgba(217,70,239,0.8))"
                bg_hover_grad = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(167,139,250,0.9), stop:0.6 rgba(192,132,252,0.85), stop:1 rgba(232,121,249,0.8))"
                bdr = "none"
                txt = "#FFFFFF"
                txt_desc = "rgba(255,255,255,0.7)"
            else:
                bg_grad = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(12,16,51,0.8), stop:1 rgba(8,12,36,0.5))"
                bg_hover_grad = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(20,24,74,0.8), stop:1 rgba(12,16,51,0.6))"
                bdr = "1px solid rgba(139, 92, 246, 0.10)"
                txt = "#F1F5F9"
                txt_desc = "#64748B"

            card.setStyleSheet(f"""
                _CommandCard {{
                    background: {bg_grad};
                    border: {bdr};
                    border-radius: {R.lg};
                }}
                _CommandCard:hover {{
                    background: {bg_hover_grad};
                }}
            """)

            if primary:
                glow_effect(card, glow_rgba=_GLOW(colors.primary), blur=16, offset_y=0)

            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(_px12, _px12, _px12, _px10)
            card_layout.setSpacing(_px4)

            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet(
                f"font-size: 22px; color: {txt}; background: transparent;"
            )
            card_layout.addWidget(icon_lbl)

            name_lbl = QLabel(label)
            name_lbl.setStyleSheet(
                f"color: {txt}; {font_style('body', 'bold')}; background: transparent;"
            )
            card_layout.addWidget(name_lbl)

            desc_lbl = QLabel(tip)
            desc_lbl.setStyleSheet(
                f"color: {txt_desc}; {font_style('caption')}; background: transparent;"
            )
            desc_lbl.setWordWrap(True)
            card_layout.addWidget(desc_lbl)

            card_layout.addStretch()

            col = i % 5
            grid.addWidget(card, 0, col)

        parent.addLayout(grid)

    # ── Connect ────────────────────────────────────────────────

    def _connect_signals(self) -> None:
        self._controller.data_updated.connect(self._on_data_updated)

    # ── Data Update ────────────────────────────────────────────

    def _on_data_updated(self, data: DashboardData) -> None:
        self._last_data = data
        self._update_hero(data)
        self._update_todays_mission(data)
        self._update_recovery(data)
        self._update_coach(data)
        self._update_progress(data)
        self._update_predictions(data)

    # ── Animation helpers ──────────────────────────────────────

    def _fade_in(self, widget: QWidget, duration: int = _ANI_DURATION) -> None:
        if not widget.isVisible():
            return
        opacity = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(opacity)
        anim = QPropertyAnimation(opacity, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start(QPropertyAnimation.DeleteWhenStopped)
        self._animations.append(anim)

    @staticmethod
    def _greeting() -> str:
        hour = datetime.now().hour
        if hour < 12:
            return "Good Morning"
        if hour < 18:
            return "Good Afternoon"
        return "Good Evening"

    # ── Update Hero ────────────────────────────────────────────

    def _update_hero(self, data: DashboardData) -> None:
        colors = self._colors()

        # Greeting
        greeting = self._greeting()
        user_name = getattr(data, "user_name", "") or ""
        title = f"{greeting}" + (f", {user_name}" if user_name else "")
        self._hero_greeting.setText(title)

        # Subtitle
        prog = getattr(data, "current_program", "") or "No Active Program"
        week = getattr(data, "mesocycle_week", 0) or 0
        split_day = getattr(data, "current_split_day", "") or ""
        parts = [prog]
        if week:
            parts.append(f"Week {week}")
        if split_day:
            parts.append(split_day)
        self._hero_subtitle.setText(" \u00b7 ".join(parts) if parts else "")

        # Rings
        rec_score = getattr(data, "recovery_score", 0.0) or 0.0
        self._recovery_ring.set_value(rec_score, 100.0, "Recovery")

        goal_target = getattr(data, "goal_progress_target", 100.0) or 100.0
        goal_current = getattr(data, "goal_progress_weight", 0.0) or 0.0
        if goal_current > 0:
            self._goal_ring.set_goal(goal_current, goal_target, "Goal", "kg")
        else:
            self._goal_ring.set_goal(0, 100, "Goal", "")

        # Motivational prediction
        recs = getattr(data, "recommendations", [])
        prediction_text = ""
        if recs:
            first = recs[0]
            title_text = getattr(first, "title", "") or ""
            if title_text:
                prediction_text = f"\u201C{title_text}\u201D"
        if not prediction_text:
            level = getattr(data, "recovery_level", "") or ""
            if level:
                level_lower = level.lower()
                if level_lower in ("low", "moderate"):
                    prediction_text = "\u201CYou're ready to train. Make it count.\u201D"
                else:
                    prediction_text = "\u201CFocus on recovery today. Rest is training too.\u201D"

        if prediction_text:
            self._hero_prediction.setText(prediction_text)
            self._hero_prediction.show()
        else:
            self._hero_prediction.hide()

        # Metrics
        rec_pct = int(rec_score)
        self._hero_metric_ready_val.setText(f"{rec_pct}")
        self._hero_metric_ready_lbl.setText("Readiness")

        weight = getattr(data, "goal_progress_weight", 0.0) or 0.0
        self._hero_metric_weight_val.setText(f"{weight:.1f}" if weight else "--")

        remaining = getattr(data, "goal_progress_remaining", 0.0) or 0.0
        if remaining:
            self._hero_metric_goal_val.setText(f"{remaining:.1f}")
            self._hero_metric_goal_lbl.setText("To Goal (kg)")
        else:
            self._hero_metric_goal_val.setText("--")
            self._hero_metric_goal_lbl.setText("To Goal")

        streak = getattr(data, "current_streak", 0) or 0
        if streak:
            self._hero_metric_streak_val.setText(f"{streak}")
            self._hero_metric_streak_lbl.setText(f"Streak (days)")
        else:
            self._hero_metric_streak_val.setText("0")
            self._hero_metric_streak_lbl.setText("Streak")

        # — No fade-in on hero to avoid flash on first render —

    # ── Update Today's Mission ──────────────────────────────────

    def _update_todays_mission(self, data: DashboardData) -> None:
        workout_name = getattr(data, "today_workout_name", "") or ""
        if workout_name:
            self._workout_empty.hide()
            self._workout_name.show()
            self._workout_meta.show()
            self._workout_muscle_container.show()
            self._mission_start_btn.show()

            self._workout_name.setText(workout_name)

            ex_count = getattr(data, "today_workout_exercise_count", 0) or 0
            duration = getattr(data, "today_workout_estimated_duration", 0) or 0

            rec_level = getattr(data, "recovery_level", "") or ""
            recovery_hint = ""
            if rec_level:
                rec_display = rec_level.capitalize().replace("_", " ")
                recovery_hint = f" \u00b7 {rec_display}"

            meta = f"{ex_count} exercises"
            if duration:
                meta += f" \u00b7 ~{duration} min"
            meta += recovery_hint
            self._workout_meta.setText(meta)

            for i in reversed(range(self._workout_muscle_row.count())):
                item = self._workout_muscle_row.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            muscles = getattr(data, "today_workout_primary_muscles", []) or []
            for m in muscles:
                badge = StatusBadge(
                    text=str(m).capitalize() if isinstance(m, str) else str(m),
                    level=StatusLevel.INFO,
                    outlined=True,
                )
                self._workout_muscle_row.addWidget(badge)

            self._fade_in(self._mission_card)
        else:
            self._workout_name.hide()
            self._workout_meta.hide()
            self._workout_muscle_container.hide()
            self._mission_start_btn.hide()
            self._workout_empty.show()

    # ── Update Recovery ────────────────────────────────────────

    def _update_recovery(self, data: DashboardData) -> None:
        colors = self._colors()
        rec_score = getattr(data, "recovery_score", 0.0) or 0.0
        level_str = getattr(data, "recovery_level", "") or ""
        suggested = getattr(data, "recovery_suggested_action", "") or ""
        flags = getattr(data, "recovery_flags", []) or []
        status = getattr(data, "recovery_status", None)

        if status is None and not level_str:
            self._recovery_empty.show()
            self._recovery_content.hide()
            return

        self._recovery_empty.hide()
        self._recovery_content.show()

        if status and not level_str:
            level_obj = getattr(status, "level", "low")
            level_str = (
                level_obj.value if hasattr(level_obj, "value") else str(level_obj).lower()
            )

        level_key = level_str.lower() if level_str else "low"

        narrative_label = {
            "low": "Ready for PR \U0001F525",
            "moderate": "Nearly recovered",
            "high": "Take it easy today",
            "very_high": "Rest day recommended",
            "critical": "Prioritize recovery",
        }.get(level_key, level_key.upper().replace("_", " "))

        score_color = colors.success
        if level_key in ("high", "very_high", "critical"):
            score_color = colors.error
        elif level_key in ("moderate", "warning"):
            score_color = colors.warning

        self._recovery_level_label.setStyleSheet(
            f"color: {score_color}; {font_style('h3')}; "
            f"letter-spacing: -0.02em; background: transparent;"
        )
        self._recovery_level_label.setText(narrative_label)

        score_text = f"Score: {rec_score:.0f}/100"
        if status:
            expl = getattr(status, "explanation", "") or ""
            if expl:
                score_text += f" \u00b7 {expl}"
        self._recovery_score_label.setText(score_text)

        if suggested:
            self._recovery_suggested.setText(f"\u2192 {suggested}")
        elif level_key in ("high", "very_high"):
            self._recovery_suggested.setText("\u2192 Prioritize sleep and nutrition")
        else:
            self._recovery_suggested.setText("\u2192 Continue your current training plan")

        self._fade_in(self._recovery_card)

    # ── Update Coach ──────────────────────────────────────────

    def _update_coach(self, data: DashboardData) -> None:
        for i in reversed(range(self._coach_container.count())):
            item = self._coach_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        recs = getattr(data, "recommendations", [])

        if not recs:
            self._coach_empty.show()
            return

        self._coach_empty.hide()

        for i, rec in enumerate(recs[:2]):
            title = (
                getattr(rec, "title", "")
                or getattr(rec, "description", f"Insight {i + 1}")
            )
            reason = getattr(rec, "reason", "") or ""
            priority = getattr(rec, "priority", 50) or 50

            badge = "Info"
            badge_level = StatusLevel.INFO
            if priority >= 70:
                badge = "High"
                badge_level = StatusLevel.WARNING
            elif priority >= 50:
                badge = "Medium"
                badge_level = StatusLevel.INFO
            else:
                badge = "Low"
                badge_level = StatusLevel.NEUTRAL

            icon = "\U0001F4E3" if i == 0 else "\U0001F4A1"
            card = InsightCard(
                icon=icon,
                title=title,
                description=reason[:200] if reason else "",
                badge_text=badge,
                badge_level=badge_level,
            )
            card.setAccessibleName(f"Coach insight {i + 1}")
            self._coach_container.addWidget(card)

        self._fade_in(self._coach_card)

    # ── Update Progress ────────────────────────────────────────

    def _update_progress(self, data: DashboardData) -> None:
        colors = self._colors()
        weight = getattr(data, "goal_progress_weight", 0.0) or 0.0
        target = getattr(data, "goal_progress_target", 0.0) or 0.0
        remaining = getattr(data, "goal_progress_remaining", 0.0) or 0.0
        weeks = getattr(data, "goal_progress_weeks", 0) or 0
        rate = getattr(data, "goal_progress_rate", 0.0) or 0.0
        quality = getattr(data, "goal_progress_quality", "") or ""
        percent = getattr(data, "goal_progress_percent", 0.0) or 0.0
        goal_date = getattr(data, "goal_progress_estimated_date", "") or ""

        if weight > 0:
            self._goal_empty.hide()
            self._goal_content.show()
            self._goal_weight_label.setText(f"{weight:.1f} kg")

            details_parts = []
            if target:
                details_parts.append(f"Target: {target:.1f} kg")
            if remaining:
                details_parts.append(f"{remaining:.1f} kg to go")
            if weeks:
                details_parts.append(f"~{weeks} weeks left")
            if rate:
                details_parts.append(f"{rate:.2f} kg/wk")
            if quality:
                quality_display = quality.replace("_", " ").title()
                details_parts.append(quality_display)
            if goal_date:
                details_parts.append(f"Est: {goal_date}")
            if percent:
                details_parts.append(f"{percent:.0f}% complete")

            self._goal_detail_label.setText(" \u00b7 ".join(details_parts))
        else:
            self._goal_empty.show()
            self._goal_content.hide()

        # Volume
        vol_data = getattr(data, "weekly_volume_data", [])
        weekly_vol = getattr(data, "weekly_volume_kg", 0.0) or 0.0

        if vol_data:
            self._volume_empty.hide()
            self._volume_content.show()
            values = []
            for v in vol_data:
                if isinstance(v, dict):
                    values.append(v.get("volume", 0.0) or 0.0)
                else:
                    values.append(float(v) if v else 0.0)
            max_v = max(values) if values else 100.0
            self._weekly_timeline.set_data(values, max_value=max_v)
            self._weekly_total.setText(f"Total: {weekly_vol:.0f} kg this week")
        else:
            self._volume_empty.show()
            self._volume_content.hide()

        # PRs
        prs = getattr(data, "recent_prs", [])
        for i in reversed(range(self._prs_container.count())):
            item = self._prs_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if prs:
            self._prs_empty.hide()
            self._prs_widget.show()

            for pr in prs[:5]:
                ex_name = (
                    pr if isinstance(pr, str)
                    else getattr(pr, "exercise_name", str(pr))
                )
                pr_type = getattr(pr, "pr_type", "") if not isinstance(pr, str) else ""
                display_val = (
                    getattr(pr, "display_value", "") if not isinstance(pr, str) else ""
                )

                row = QFrame()
                row.setStyleSheet("background: transparent; border: none;")
                row_layout = QHBoxLayout(row)
                row_layout.setContentsMargins(0, _px4, 0, _px4)
                row_layout.setSpacing(_px8)

                icon_lbl = QLabel("\u2B50")
                icon_lbl.setStyleSheet(
                    f"font-size: {T.caption_size}; background: transparent;"
                )
                icon_lbl.setFixedWidth(_px20)
                row_layout.addWidget(icon_lbl)

                name_lbl = QLabel(ex_name)
                name_lbl.setStyleSheet(
                    f"color: {colors.text_primary}; "
                    f"{font_style('caption', 'bold')}"
                )
                row_layout.addWidget(name_lbl, 1)

                if display_val or pr_type:
                    val_lbl = QLabel(
                        f"{pr_type.upper() if pr_type else ''} {display_val}"
                    )
                    val_lbl.setStyleSheet(
                        f"color: {colors.warning}; "
                        f"{font_style('caption', 'bold')}"
                    )
                    row_layout.addWidget(val_lbl)

                self._prs_container.addWidget(row)
        else:
            self._prs_empty.show()
            self._prs_widget.hide()

        self._fade_in(self._progress_card)

    # ── Update Predictions ─────────────────────────────────────

    def _update_predictions(self, data: DashboardData) -> None:
        colors = self._colors()
        for i in reversed(range(self._predictions_container.count())):
            item = self._predictions_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        recs = getattr(data, "recommendations", [])
        rec_score = getattr(data, "recovery_score", 0.0) or 0.0
        level_str = getattr(data, "recovery_level", "") or ""
        predictions = []

        if recs and len(recs) > 0:
            for rec in recs[:2]:
                title = getattr(rec, "title", "") or ""
                reason = getattr(rec, "reason", "") or ""
                coach_line = title or reason or ""
                if coach_line:
                    predictions.append(coach_line)

        if not predictions:
            if level_str:
                level_lower = level_str.lower()
                if level_lower == "low":
                    predictions.append("Low fatigue suggests you can push intensity today.")
                elif level_lower == "moderate":
                    predictions.append("Moderate fatigue — maintain current volume.")
                elif level_lower in ("high", "very_high"):
                    predictions.append("High fatigue detected. Consider a deload or rest day.")
            else:
                predictions.append("Prediction data will appear after completing workouts.")

        for pred in predictions[:2]:
            frame = QFrame()
            frame.setStyleSheet("background: transparent; border: none;")
            fl = QHBoxLayout(frame)
            fl.setContentsMargins(0, _px6, 0, _px6)
            fl.setSpacing(_px8)

            bullet = QLabel("\u25CF")
            bullet.setStyleSheet(
                f"color: {colors.primary}; "
                f"font-size: 10px; background: transparent;"
            )
            bullet.setFixedWidth(_px12)
            bullet.setAlignment(Qt.AlignTop)
            fl.addWidget(bullet)

            text = QLabel(pred)
            text.setStyleSheet(
                f"color: {colors.text_primary}; "
                f"{font_style('body')}; background: transparent;"
            )
            text.setWordWrap(True)
            fl.addWidget(text, 1)

            self._predictions_container.addWidget(frame)

        has_content = bool(predictions)
        self._predictions_widget.setVisible(has_content)
        self._predictions_empty.setVisible(not has_content)
        self._fade_in(self._predictions_card)

    # ── Public API ────────────────────────────────────────────

    def refresh(self) -> None:
        self._controller.refresh()

    def controller(self) -> DashboardController:
        return self._controller
