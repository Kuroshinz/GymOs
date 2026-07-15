"""Recovery Experience 2.0 — narrative-first recovery conversation.

Layout hierarchy (top-to-bottom, one story):

  ┌──────────────────────────────────────────────────────────┐
  │  HERO                                                    │
  │  RecoveryRing + dominant state label + narrative + CTA   │
  │  "Training Ready — You're fully recovered."              │
  └──────────────────────────────────────────────────────────┘
  ┌──────────────────────────────────────────────────────────┐
  │  RECOVERY SUMMARY — Sleep · Fatigue · Readiness          │
  │  Narrative first, numbers second for each driver         │
  └──────────────────────────────────────────────────────────┘
  ┌──────────────────────────────────────────────────────────┐
  │  RECOVERY DRIVERS — "Why am I at this state?"            │
  │  Bullet-point factor breakdown with impact deltas        │
  └──────────────────────────────────────────────────────────┘
  ┌──────────────────────────────────────────────────────────┐
  │  COACH — Largest insight section                         │
  │  Natural-language narratives (max 3)                     │
  └──────────────────────────────────────────────────────────┘
  ┌──────────────────────────────────────────────────────────┐
  │  TREND — Weekly recovery chart + "So what?"             │
  └──────────────────────────────────────────────────────────┘
  ┌──────────────────────────────────────────────────────────┐
  │  TODAY — Green / Amber / Red recommendation + reasoning  │
  └──────────────────────────────────────────────────────────┘
  ┌──────────────────────────────────────────────────────────┐
  │  WHAT IF — Counterfactual cards (sleep, volume, etc.)    │
  └──────────────────────────────────────────────────────────┘
  ┌──────────────────────────────────────────────────────────┐
  │  HISTORY — Timeline + milestones                         │
  └──────────────────────────────────────────────────────────┘

Preserved: RecoveryDashboardData dataclass, refresh(data) API, same business logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.design_system.components.app_card import AppCard
from ui.design_system.components.chart_container import ChartContainer
from ui.design_system.components.section_header import SectionHeader
from ui.design_system.components.status_badge import StatusBadge, StatusLevel
from ui.design_system.layout import EditorialGrid, PanelSpan, ScrollContainer
from ui.design_system.tokens.color import ColorScheme, color_from_scheme, resolve_alpha
from ui.design_system.tokens.elevation import ElevationTokens, apply_elevation
from ui.design_system.tokens.motion import MotionTokens
from ui.design_system.tokens.radius import RadiusTokens, px_from_token
from ui.design_system.tokens.spacing import SpacingTokens
from ui.design_system.tokens.typography import TypographyTokens, font_style
from ui.design_system.visualization import RecoveryRing, TrendChart, WeeklyTimeline
from ui.narrative.cards import CoachCardStack
from ui.narrative.engine import Narrative

M = MotionTokens()
S = SpacingTokens()
R = RadiusTokens()
T = TypographyTokens()
E = ElevationTokens()

_pxf = px_from_token
_px4 = _pxf(S.s1)
_px6 = _pxf(S.s1_5)
_px8 = _pxf(S.s2)
_px12 = _pxf(S.s3)
_px16 = _pxf(S.s4)
_px20 = _pxf(S.s5)
_px24 = _pxf(S.s6)
_px32 = _pxf(S.s8)
_px40 = _pxf(S.s10)


# ─── Data Contract ─────────────────────────────────────────────────


@dataclass
class RecoveryDashboardData:
    recovery_score: float = 0.0
    recovery_level: str = ""
    recovery_flags: list = field(default_factory=list)
    recovery_sleep_score: float = 0.0
    recovery_sleep_hours: float = 0.0
    recovery_stress_score: float = 0.0
    recovery_fatigue_score: float = 0.0
    recovery_trend: Any = None
    recovery_active_deload: Any = None
    recovery_scores: list = field(default_factory=list)
    recovery_scores_count: int = 0
    recovery_weekly: list = field(default_factory=list)
    recovery_action: str = ""


# ─── Helpers ───────────────────────────────────────────────────────


def _score_to_state(score: float) -> tuple[str, str, str, StatusLevel]:
    """Map recovery score → (state_label, narrative, cta_text, status_level)."""
    if score >= 80:
        return (
            "Training Ready",
            "You're fully recovered. Today's session is appropriate for PR attempts.",
            "Proceed to Workout",
            StatusLevel.SUCCESS,
        )
    if score >= 60:
        return (
            "Good to Train",
            "You're recovered enough to train. Focus on technique and avoid failure sets.",
            "Start Workout",
            StatusLevel.SUCCESS,
        )
    if score >= 40:
        return (
            "Train with Caution",
            "Recovery is reduced. Consider reducing volume by 20% today.",
            "Reduce Volume",
            StatusLevel.WARNING,
        )
    if score >= 20:
        return (
            "Needs Rest",
            "Significant fatigue detected. Consider a light session or rest day.",
            "Take Rest Day",
            StatusLevel.WARNING,
        )
    return (
        "Deload Recommended",
        "Critical fatigue levels. A deload week is strongly recommended.",
        "Plan Deload",
        StatusLevel.ERROR,
    )


def _score_color(score: float) -> str:
    colors = color_from_scheme(ColorScheme.DARK)
    if score >= 80:
        return colors.success
    if score >= 60:
        return colors.info
    return colors.error


def _trend_narrative(trend: Any) -> str:
    """Generate a one-sentence trend narrative from trend data."""
    if trend is None:
        return ""
    if isinstance(trend, dict):
        direction = str(trend.get("direction", "stable")).lower()
        slope = trend.get("slope", 0.0)
    else:
        direction = str(getattr(trend, "direction", "stable")).lower()
        if hasattr(direction, "value"):
            direction = direction.value
        slope = getattr(trend, "slope", 0.0) if hasattr(trend, "slope") else 0.0

    if direction in ("improving", "increasing"):
        return f"Recovery has been improving. Trend: {slope:+.1f}/day."
    if direction in ("declining", "decreasing"):
        return f"Recovery has been declining. Trend: {slope:+.1f}/day."
    if direction == "volatile":
        return "Recovery has been fluctuating. Monitor for consistency."
    return "Recovery has been stable over the past week."


def _extract_score_values(scores: list) -> list[float]:
    """Extract numeric score values from a list of score objects."""
    values = []
    for s in scores:
        if isinstance(s, (int, float)):
            values.append(float(s))
        elif isinstance(s, dict):
            values.append(float(s.get("overall_score", 0)))
        else:
            values.append(float(getattr(s, "overall_score", 0)))
    return [v for v in values if v > 0]


# ─── Recovery Drivers Widget ──────────────────────────────────────


class _RecoveryDrivers(QFrame):
    """Bullet-point recovery driver explanations."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("RecoveryDrivers")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(_px8)

    def set_data(self, data: RecoveryDashboardData) -> None:
        self._clear_layout()
        colors = color_from_scheme(ColorScheme.DARK)
        score = data.recovery_score
        sleep = data.recovery_sleep_score
        fatigue = data.recovery_fatigue_score
        stress = data.recovery_stress_score
        flags = data.recovery_flags or []
        has_data = score > 0

        if not has_data:
            self._add_empty(colors)
            return

        drivers = self._build_drivers(score, sleep, fatigue, stress, flags, colors)
        for icon, text, detail in drivers:
            self._add_driver_row(icon, text, detail, colors)

    def _build_drivers(
        self, score: float, sleep: float, fatigue: float, stress: float,
        flags: list, colors: Any
    ) -> list[tuple[str, str, str]]:
        drivers = []
        if sleep >= 70:
            drivers.append(
                ("😴", "Sleep quality is good", f"Score: {sleep:.0f}/100")
            )
        elif sleep >= 40:
            drivers.append(
                ("😴", "Sleep quality is moderate", f"Score: {sleep:.0f}/100. Aim for 7-9 hours.")
            )
        else:
            drivers.append(
                ("😴", "Sleep quality needs improvement", f"Score: {sleep:.0f}/100. Prioritise rest.")
            )

        if fatigue <= 30:
            drivers.append(
                ("⚡", "Fatigue levels are low", f"Score: {fatigue:.0f}/100. You're fresh.")
            )
        elif fatigue <= 50:
            drivers.append(
                ("⚡", "Fatigue is moderate", f"Score: {fatigue:.0f}/100. Manage volume carefully.")
            )
        else:
            drivers.append(
                ("⚡", "Fatigue is elevated", f"Score: {fatigue:.0f}/100. Consider lighter work.")
            )

        if stress <= 30:
            drivers.append(
                ("🧘", "Stress levels are low", f"Score: {stress:.0f}/100. Good environment for training.")
            )
        elif stress <= 60:
            drivers.append(
                ("🧘", "Stress is moderate", f"Score: {stress:.0f}/100. Monitor for accumulation.")
            )
        else:
            drivers.append(
                ("🧘", "Stress is high", f"Score: {stress:.0f}/100. May impact recovery.")
            )

        for flag in flags[:2]:
            msg = getattr(flag, "message", str(flag)) if not isinstance(flag, str) else flag
            drivers.append(
                ("📋", msg[:80], getattr(flag, "detail", "") if not isinstance(flag, str) else "")
            )

        return drivers

    def _add_driver_row(self, icon: str, text: str, detail: str, colors: Any) -> None:
        row = QFrame()
        row.setStyleSheet("background: transparent; border: none;")
        rl = QHBoxLayout(row)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(_px12)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 18px; background: transparent;")
        icon_lbl.setFixedWidth(28)
        rl.addWidget(icon_lbl)

        col = QVBoxLayout()
        col.setSpacing(2)

        txt = QLabel(text)
        txt.setStyleSheet(f"color: {colors.text_primary}; {font_style('body')}; background: transparent;")
        txt.setWordWrap(True)
        col.addWidget(txt)

        if detail:
            det = QLabel(detail)
            det.setStyleSheet(f"color: {colors.text_disabled}; {font_style('caption')}; background: transparent;")
            det.setWordWrap(True)
            col.addWidget(det)

        rl.addLayout(col, 1)
        self._layout.addWidget(row)

    def _add_empty(self, colors: Any) -> None:
        empty = QLabel("Complete a workout to see your recovery drivers.")
        empty.setStyleSheet(f"color: {colors.text_disabled}; {font_style('body')}; background: transparent;")
        empty.setWordWrap(True)
        empty.setAlignment(Qt.AlignCenter)
        self._layout.addWidget(empty)

    def _clear_layout(self) -> None:
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


# ─── Counterfactual Card ──────────────────────────────────────────


class _CounterfactualCard(AppCard):
    """'What If' scenario card with impact preview."""

    def __init__(
        self, icon: str, action: str, impact: str, impact_pct: float,
        action_color: str, parent: QWidget | None = None,
    ) -> None:
        super().__init__(title="", elevated=True, parent=parent)
        self.setObjectName("CounterfactualCard")
        self.setAccessibleName(f"What if: {action}")

        colors = color_from_scheme(ColorScheme.DARK)

        # Clear the default AppCard body layout — rebuild with our custom content
        while self.layout().count():
            old = self.layout().takeAt(0)
            if old.layout():
                self.layout().removeItem(old.layout())
            elif old.widget():
                old.widget().deleteLater()

        # Icon + action row
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(_px8)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 28px; background: transparent;")
        row.addWidget(icon_lbl)

        col = QVBoxLayout()
        col.setSpacing(2)

        what_if = QLabel("What if...")
        what_if.setStyleSheet(f"color: {colors.text_disabled}; {font_style('caption')}; background: transparent;")
        col.addWidget(what_if)

        action_lbl = QLabel(action)
        action_lbl.setStyleSheet(f"color: {colors.text_primary}; {font_style('body', weight='semibold')}; background: transparent;")
        action_lbl.setWordWrap(True)
        col.addWidget(action_lbl)

        row.addLayout(col, 1)
        self.layout().addLayout(row)

        impact_lbl = QLabel(impact)
        impact_lbl.setStyleSheet(f"color: {action_color}; {font_style('h3')}; background: transparent;")
        self.layout().addWidget(impact_lbl)

        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(int(impact_pct * 100))
        bar.setTextVisible(False)
        bar.setFixedHeight(6)
        bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {colors.surface_hover};
                border-radius: 3px;
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {resolve_alpha(action_color, 0.6)};
                border-radius: 3px;
            }}
        """)
        self.layout().addWidget(bar)

        conf_lbl = QLabel(f"{impact_pct * 100:.0f}% confidence")
        conf_lbl.setStyleSheet(f"color: {colors.text_disabled}; {font_style('caption')}; background: transparent;")
        self.layout().addWidget(conf_lbl)


# ─── Recovery Dashboard ───────────────────────────────────────────


class RecoveryDashboard(QWidget):
    """Narrative-first recovery conversation. Answers: 'Can I train hard today?'"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _colors(self):
        return color_from_scheme(ColorScheme.DARK)

    # ── Build UI ─────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setStyleSheet("RecoveryDashboard { background: transparent; }")
        self._scroll = ScrollContainer()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._scroll)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._scroll.content_layout.insertLayout(0, layout)

        main = QVBoxLayout()
        main.setContentsMargins(0, 0, _px32, _px40)
        main.setSpacing(0)
        layout.insertLayout(0, main)

        # 1. Hero
        self._build_hero(main)

        main.addSpacing(_px32)

        # 2. Recovery Summary
        self._build_section_header(main, "Recovery Summary", "Sleep \u00b7 Fatigue \u00b7 Readiness")
        self._summary_grid = EditorialGrid()
        self._summary_grid.set_spacing(_px16)
        main.addWidget(self._summary_grid)
        self._build_summary_cards()

        main.addSpacing(_px24)

        # 3. Recovery Drivers
        self._build_section_header(main, "Why?", "What\u2019s driving your recovery state")
        self._drivers_widget = _RecoveryDrivers()
        main.addWidget(self._drivers_widget)

        main.addSpacing(_px24)

        # 4. Coach
        self._build_section_header(main, "Coach Insights", "Personalised guidance")
        self._coach_stack = CoachCardStack()
        main.addWidget(self._coach_stack)

        main.addSpacing(_px24)

        # 5. Weekly Trend
        self._build_section_header(main, "Weekly Trend", "7-day recovery score trend")
        self._trend_container = QVBoxLayout()
        self._trend_container.setContentsMargins(0, 0, 0, 0)
        self._trend_container.setSpacing(_px8)
        main.addLayout(self._trend_container)

        main.addSpacing(_px24)

        # 6. Today's Recommendation
        self._build_section_header(main, "Today\u2019s Recommendation", "What should you do?")
        self._rec_card = AppCard(title="", elevated=True)
        main.addWidget(self._rec_card)

        main.addSpacing(_px24)

        # 7. What If...
        self._build_section_header(main, "What If\u2026", "Small changes, big impact")
        self._counterfactual_grid = EditorialGrid()
        self._counterfactual_grid.set_spacing(_px16)
        main.addWidget(self._counterfactual_grid)

        main.addSpacing(_px24)

        # 8. Recovery History
        self._build_section_header(main, "Recovery History", "Your recovery journey")
        self._history_container = QVBoxLayout()
        self._history_container.setContentsMargins(0, 0, 0, 0)
        self._history_container.setSpacing(_px8)
        main.addLayout(self._history_container)

        main.addStretch()

    def _build_section_header(self, parent: QVBoxLayout, title: str, subtitle: str) -> None:
        header = SectionHeader(title=title, subtitle=subtitle)
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, _px8)
        hbox.addWidget(header)
        parent.addLayout(hbox)

    # ── Hero ──────────────────────────────────────────────────────

    def _build_hero(self, parent: QVBoxLayout) -> None:
        colors = self._colors()

        self._hero_frame = QFrame()
        self._hero_frame.setObjectName("RecoveryHero")
        self._hero_frame.setMinimumHeight(240)
        self._hero_frame.setStyleSheet(f"""
            QFrame#RecoveryHero {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(12,16,51,200), stop:0.35 rgba(20,16,74,180),
                    stop:0.7 rgba(26,13,68,160), stop:1 rgba(10,14,40,120));
                border-radius: {R.xl};
                border: 1px solid {resolve_alpha(colors.primary, 0.10)};
            }}
        """)
        apply_elevation(self._hero_frame, 3, is_dark=True, bg_color=colors.surface)

        hero_layout = QHBoxLayout(self._hero_frame)
        hero_layout.setContentsMargins(_px32, _px24, _px32, _px24)
        hero_layout.setSpacing(_px24)

        # Left: RecoveryRing + text
        left = QHBoxLayout()
        left.setSpacing(_px20)

        self._hero_ring = RecoveryRing(size=100)
        left.addWidget(self._hero_ring)

        text_col = QVBoxLayout()
        text_col.setSpacing(_px6)

        self._hero_state_label = QLabel("--")
        self._hero_state_label.setStyleSheet(
            f"color: {colors.text_primary}; {font_style('h2')}; "
            f"letter-spacing: -0.02em; background: transparent;"
        )
        text_col.addWidget(self._hero_state_label)

        self._hero_narrative = QLabel("")
        self._hero_narrative.setStyleSheet(
            f"color: {colors.text_secondary}; {font_style('body')}; background: transparent;"
        )
        self._hero_narrative.setWordWrap(True)
        text_col.addWidget(self._hero_narrative)

        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(_px16)
        kpi_row.setContentsMargins(0, _px8, 0, 0)

        self._hero_trend_badge = StatusBadge("", StatusLevel.NEUTRAL, outlined=True)
        kpi_row.addWidget(self._hero_trend_badge)

        self._hero_score_mini = QLabel("")
        self._hero_score_mini.setStyleSheet(
            f"color: {colors.text_disabled}; {font_style('caption')}; background: transparent;"
        )
        kpi_row.addWidget(self._hero_score_mini)

        self._hero_deload_badge = StatusBadge("", StatusLevel.NEUTRAL, outlined=True)
        self._hero_deload_badge.hide()
        kpi_row.addWidget(self._hero_deload_badge)

        kpi_row.addStretch()
        text_col.addLayout(kpi_row)

        left.addLayout(text_col, 1)
        hero_layout.addLayout(left, 1)

        # Right: CTA
        right = QVBoxLayout()
        right.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        right.setSpacing(_px8)

        self._hero_cta = QPushButton("  \u25B6  Proceed to Workout")
        self._hero_cta.setAccessibleName("Recovery action: Proceed to Workout")
        self._hero_cta.setFocusPolicy(Qt.StrongFocus)
        self._hero_cta.setMinimumHeight(48)
        self._hero_cta.setMinimumWidth(200)
        self._hero_cta.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(124,58,237,0.95), stop:0.5 rgba(147,51,234,0.9), stop:1 rgba(192,38,211,0.85));
                color: white;
                border-radius: {R.size_2xl};
                padding: 0 {S.s7};
                {font_style('body', 'bold')}
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(139,92,246,0.95), stop:0.5 rgba(167,139,250,0.9), stop:1 rgba(192,132,252,0.85));
            }}
            QPushButton:focus {{
                border: 2px solid {colors.focus_ring};
            }}
        """)
        right.addWidget(self._hero_cta)

        self._hero_cta_sub = QLabel("Based on current recovery metrics")
        self._hero_cta_sub.setStyleSheet(
            f"color: {colors.text_disabled}; {font_style('caption')}; background: transparent;"
        )
        self._hero_cta_sub.setAlignment(Qt.AlignRight)
        right.addWidget(self._hero_cta_sub)

        hero_layout.addLayout(right)

        parent.addWidget(self._hero_frame)

    # ── Recovery Summary ─────────────────────────────────────────

    def _build_summary_cards(self) -> None:
        colors = self._colors()

        # Sleep card
        self._sleep_card = AppCard(title="Sleep", elevated=False)
        self._sleep_narrative = QLabel("--")
        self._sleep_narrative.setStyleSheet(
            f"color: {colors.text_primary}; {font_style('h3')}; "
            f"letter-spacing: -0.02em; background: transparent;"
        )
        self._sleep_card.add_content(self._sleep_narrative)
        self._sleep_detail = QLabel("")
        self._sleep_detail.setStyleSheet(
            f"color: {colors.text_secondary}; {font_style('body')}; background: transparent;"
        )
        self._sleep_card.add_content(self._sleep_detail)
        self._sleep_empty = QLabel("No sleep data \u2014 Connect a wearable or log manually.")
        self._sleep_empty.setStyleSheet(
            f"color: {colors.text_disabled}; {font_style('body_small')}; background: transparent;"
        )
        self._sleep_empty.setWordWrap(True)
        self._sleep_empty.setAlignment(Qt.AlignCenter)
        self._sleep_card.add_content(self._sleep_empty)
        self._sleep_narrative.hide()
        self._sleep_detail.hide()
        self._summary_grid.add_panel(self._sleep_card, span=PanelSpan.QUARTER)

        # Fatigue card
        self._fatigue_card = AppCard(title="Fatigue", elevated=False)
        self._fatigue_narrative = QLabel("--")
        self._fatigue_narrative.setStyleSheet(
            f"color: {colors.text_primary}; {font_style('h3')}; "
            f"letter-spacing: -0.02em; background: transparent;"
        )
        self._fatigue_card.add_content(self._fatigue_narrative)
        self._fatigue_detail = QLabel("")
        self._fatigue_detail.setStyleSheet(
            f"color: {colors.text_secondary}; {font_style('body')}; background: transparent;"
        )
        self._fatigue_card.add_content(self._fatigue_detail)
        self._fatigue_empty = QLabel("No fatigue data yet.")
        self._fatigue_empty.setStyleSheet(
            f"color: {colors.text_disabled}; {font_style('body_small')}; background: transparent;"
        )
        self._fatigue_empty.setAlignment(Qt.AlignCenter)
        self._fatigue_card.add_content(self._fatigue_empty)
        self._fatigue_narrative.hide()
        self._fatigue_detail.hide()
        self._summary_grid.add_panel(self._fatigue_card, span=PanelSpan.QUARTER)

        # Readiness card (wider)
        self._readiness_card = AppCard(title="Readiness", elevated=True)
        self._readiness_narrative = QLabel("--")
        self._readiness_narrative.setStyleSheet(
            f"color: {colors.text_primary}; {font_style('h3')}; "
            f"letter-spacing: -0.02em; background: transparent;"
        )
        self._readiness_card.add_content(self._readiness_narrative)
        self._readiness_detail = QLabel("")
        self._readiness_detail.setStyleSheet(
            f"color: {colors.text_secondary}; {font_style('body')}; background: transparent;"
        )
        self._readiness_card.add_content(self._readiness_detail)
        self._readiness_empty = QLabel("Complete a workout to unlock readiness insights.")
        self._readiness_empty.setStyleSheet(
            f"color: {colors.text_disabled}; {font_style('body_small')}; background: transparent;"
        )
        self._readiness_empty.setWordWrap(True)
        self._readiness_empty.setAlignment(Qt.AlignCenter)
        self._readiness_card.add_content(self._readiness_empty)
        self._readiness_narrative.hide()
        self._readiness_detail.hide()
        self._summary_grid.add_panel(self._readiness_card, span=PanelSpan.HALF)

    # ── Refresh ──────────────────────────────────────────────────

    def refresh(self, data: Any) -> None:
        self._update_hero(data)
        self._update_summary(data)
        self._drivers_widget.set_data(data)
        self._update_coach(data)
        self._update_trend(data)
        self._update_recommendation(data)
        self._update_counterfactuals(data)
        self._update_history(data)

    # ── Update: Hero ─────────────────────────────────────────────

    def _update_hero(self, data: Any) -> None:
        colors = self._colors()
        score = getattr(data, "recovery_score", 0.0) or 0.0
        level = getattr(data, "recovery_level", "") or ""
        trend = getattr(data, "recovery_trend", None)
        active_deload = getattr(data, "recovery_active_deload", None)

        self._hero_ring.set_value(score, 100.0, "Recovery")

        if score > 0:
            state_label, narrative, cta_text, status_lvl = _score_to_state(score)
            self._hero_state_label.setText(state_label)
            self._hero_state_label.setStyleSheet(
                f"color: {_score_color(score)}; {font_style('h2')}; "
                f"letter-spacing: -0.02em; background: transparent;"
            )
            self._hero_narrative.setText(narrative)
            self._hero_cta.setText(f"  \u25B6  {cta_text}")
            self._hero_cta_sub.setText(f"Score: {score:.0f}/100 \u00b7 {level.upper() if level else ''}")

            # Trend badge
            if isinstance(trend, dict):
                direction = str(trend.get("direction", "stable")).lower()
            else:
                direction = str(getattr(trend, "direction", "stable")).lower() if trend else "stable"
                if hasattr(direction, "value"):
                    direction = direction.value

            trend_level = StatusLevel.SUCCESS
            trend_text = "Stable"
            if direction in ("improving", "increasing"):
                trend_level = StatusLevel.SUCCESS
                trend_text = "Improving"
            elif direction in ("declining", "decreasing"):
                trend_level = StatusLevel.WARNING
                trend_text = "Declining"
            elif direction == "volatile":
                trend_level = StatusLevel.WARNING
                trend_text = "Volatile"

            self._hero_trend_badge.set_level(trend_level)
            self._hero_trend_badge.setText(trend_text)
            self._hero_trend_badge.show()
            # Calculate 7-day average from scores
            score_vals = _extract_score_values(getattr(data, "recovery_scores", []) or [])
            if score_vals:
                avg = sum(score_vals) / len(score_vals)
                self._hero_score_mini.setText(f"7-day avg: {avg:.0f}/100")
            else:
                self._hero_score_mini.setText("")

            # Deload badge
            if active_deload:
                end = getattr(active_deload, "end_date", "") if hasattr(active_deload, "end_date") else ""
                self._hero_deload_badge.setText(f"Deload until {end}" if end else "Deload active")
                self._hero_deload_badge.set_level(StatusLevel.INFO)
                self._hero_deload_badge.show()
            else:
                self._hero_deload_badge.hide()
        else:
            self._hero_state_label.setText("No Recovery Data")
            self._hero_state_label.setStyleSheet(
                f"color: {colors.text_secondary}; {font_style('h2')}; "
                f"letter-spacing: -0.02em; background: transparent;"
            )
            self._hero_narrative.setText("Complete a workout to unlock recovery insights. GymOS will analyse your training data to calculate sleep quality, fatigue levels, and training readiness.")
            self._hero_cta.setText("  \u25B6  Start Training")
            self._hero_cta_sub.setText("First workout creates your baseline")
            self._hero_trend_badge.hide()
            self._hero_score_mini.setText("")
            self._hero_deload_badge.hide()

    # ── Update: Summary ─────────────────────────────────────────

    def _update_summary(self, data: Any) -> None:
        colors = self._colors()
        sleep_score = getattr(data, "recovery_sleep_score", 0.0) or 0.0
        sleep_hours = getattr(data, "recovery_sleep_hours", 0.0) or 0.0
        fatigue_score = getattr(data, "recovery_fatigue_score", 0.0) or 0.0
        stress_score = getattr(data, "recovery_stress_score", 0.0) or 0.0
        score = getattr(data, "recovery_score", 0.0) or 0.0

        # Sleep
        if sleep_score:
            sleep_label = "Good" if sleep_score >= 70 else "Fair" if sleep_score >= 40 else "Needs Work"
            self._sleep_narrative.setText(sleep_label)
            self._sleep_narrative.setStyleSheet(
                f"color: {_score_color(sleep_score)}; {font_style('h3')}; "
                f"letter-spacing: -0.02em; background: transparent;"
            )
            self._sleep_detail.setText(f"{sleep_hours:.1f}h \u00b7 Score: {sleep_score:.0f}/100")
            self._sleep_narrative.show()
            self._sleep_detail.show()
            self._sleep_empty.hide()
        else:
            self._sleep_narrative.hide()
            self._sleep_detail.hide()
            self._sleep_empty.show()

        # Fatigue
        if fatigue_score:
            fatigue_label = "Low" if fatigue_score <= 30 else "Moderate" if fatigue_score <= 50 else "High"
            self._fatigue_narrative.setText(fatigue_label)
            fc = colors.success if fatigue_score <= 30 else colors.warning if fatigue_score <= 50 else colors.error
            self._fatigue_narrative.setStyleSheet(
                f"color: {fc}; {font_style('h3')}; "
                f"letter-spacing: -0.02em; background: transparent;"
            )
            self._fatigue_detail.setText(f"Score: {fatigue_score:.0f}/100")
            self._fatigue_narrative.show()
            self._fatigue_detail.show()
            self._fatigue_empty.hide()
        else:
            self._fatigue_narrative.hide()
            self._fatigue_detail.hide()
            self._fatigue_empty.show()

        # Readiness
        if score:
            readiness_label = "Ready" if score >= 80 else "Good to Train" if score >= 60 else "Fatigued"
            self._readiness_narrative.setText(readiness_label)
            self._readiness_narrative.setStyleSheet(
                f"color: {_score_color(score)}; {font_style('h3')}; "
                f"letter-spacing: -0.02em; background: transparent;"
            )
            self._readiness_detail.setText(f"Score: {score:.0f}/100 \u00b7 Stress: {stress_score:.0f}/100")
            self._readiness_narrative.show()
            self._readiness_detail.show()
            self._readiness_empty.hide()
        else:
            self._readiness_narrative.hide()
            self._readiness_detail.hide()
            self._readiness_empty.show()

    # ── Update: Coach ────────────────────────────────────────────

    def _update_coach(self, data: Any) -> None:
        self._coach_stack.clear()
        self._colors()
        score = getattr(data, "recovery_score", 0.0) or 0.0
        sleep_score = getattr(data, "recovery_sleep_score", 0.0) or 0.0
        sleep_hours = getattr(data, "recovery_sleep_hours", 0.0) or 0.0
        fatigue_score = getattr(data, "recovery_fatigue_score", 0.0) or 0.0
        stress_score = getattr(data, "recovery_stress_score", 0.0) or 0.0
        flags = getattr(data, "recovery_flags", []) or []
        getattr(data, "recovery_level", "") or ""

        cards_added = 0

        if score == 0 and not flags:
            self._coach_stack.add_card(Narrative(
                title="Coach Is Ready",
                summary="Complete a workout to start receiving personalised recovery insights and coaching recommendations.",
                body="GymOS will analyse your training data to provide natural-language guidance on your recovery, readiness, and training optimisation.",
                metadata={"severity": "info"},
            ))
            return

        # Coach card 1: Recovery Overview
        if score > 0:
            upper_status = "Upper body is fully recovered."
            lower_status = ""
            if fatigue_score > 50:
                lower_status = "Lower body still carries moderate fatigue."
            elif fatigue_score > 70:
                lower_status = "Lower body fatigue is elevated. Consider reducing leg volume."
            else:
                lower_status = "Lower body recovery looks good."

            session_verdict = "appropriate for a standard session."
            if score >= 80:
                session_verdict = "appropriate for PR attempts."
            elif score < 40:
                session_verdict = "should be a light recovery session."

            self._coach_stack.add_card(Narrative(
                title="Recovery Overview",
                summary=(
                    f"You recovered well overnight. {upper_status} "
                    f"{lower_status} Today's session is {session_verdict}"
                ),
                body=f"Recovery score: {score:.0f}/100. Fatigue: {fatigue_score:.0f}/100. "
                     f"Stress: {stress_score:.0f}/100.",
                metadata={"severity": "success" if score >= 60 else "warning"},
            ))
            cards_added += 1

        # Coach card 2: Sleep Insight (if room)
        if sleep_score > 0 and cards_added < 3:
            sleep_insight = (
                f"Your sleep score is {sleep_score:.0f}/100 with {sleep_hours:.1f}h "
                f"of sleep. "
            )
            if sleep_score >= 70:
                sleep_insight += "Sleep quality is supporting your recovery well."
            elif sleep_score >= 40:
                sleep_insight += "Aiming for 7-9 hours could further improve readiness."
            else:
                sleep_insight += "Prioritising sleep quality and duration would significantly boost recovery."

            self._coach_stack.add_card(Narrative(
                title="Sleep & Recovery",
                summary=sleep_insight,
                metadata={"severity": "info"},
            ))

        # Coach card 3: Key flags or training load insight (max 3 total)
        if flags and cards_added < 3:
            for flag in flags[:2]:
                if cards_added >= 3:
                    break
                msg = getattr(flag, "message", str(flag)) if not isinstance(flag, str) else flag
                detail = getattr(flag, "detail", "") if not isinstance(flag, str) else ""
                sev = getattr(flag, "severity", "info") if not isinstance(flag, str) else "info"
                self._coach_stack.add_card(Narrative(
                    title="Recovery Signal",
                    summary=msg[:160],
                    body=detail[:240] if detail else "",
                    metadata={"severity": sev},
                ))
                cards_added += 1
        elif score >= 60 and cards_added < 3:
            self._coach_stack.add_card(Narrative(
                title="Training Recommendation",
                summary="Your recovery metrics support a standard training session. "
                        "Focus on quality reps and aim for RIR 1-2 on working sets.",
                metadata={"severity": "success"},
            ))

    # ── Update: Trend ────────────────────────────────────────────

    def _update_trend(self, data: Any) -> None:
        self._clear_layout(self._trend_container)
        colors = self._colors()
        scores = getattr(data, "recovery_scores", []) or []
        weekly = getattr(data, "recovery_weekly", []) or []
        trend = getattr(data, "recovery_trend", None)

        score_values = _extract_score_values(scores)

        if not score_values and weekly:
            for w in weekly[:7]:
                val = w.get("average", 0) if isinstance(w, dict) else getattr(w, "average", 0)
                if val:
                    score_values.append(float(val))

        if score_values:
            chart_container = ChartContainer(title="Weekly Recovery Trend", subtitle="") if hasattr(ChartContainer, '__init__') else QFrame()
            chart = TrendChart()
            chart.set_data(score_values)
            if hasattr(chart_container, 'set_widget'):
                chart_container.set_widget(chart)
                self._trend_container.addWidget(chart_container)
            else:
                self._trend_container.addWidget(chart)

            avg = sum(score_values) / len(score_values)
            narrative = _trend_narrative(trend)
            trend_lbl = QLabel(
                f"{narrative} 7-day average: {avg:.0f}/100"
                if narrative else f"7-day average: {avg:.0f}/100"
            )
            trend_lbl.setStyleSheet(
                f"color: {colors.text_secondary}; {font_style('body')}; background: transparent;"
            )
            trend_lbl.setWordWrap(True)
            trend_lbl.setAlignment(Qt.AlignCenter)
            self._trend_container.addWidget(trend_lbl)
        else:
            empty = QLabel("Weekly recovery data will appear here after completing workouts.")
            empty.setStyleSheet(
                f"color: {colors.text_disabled}; {font_style('body_small')}; background: transparent;"
            )
            empty.setWordWrap(True)
            empty.setAlignment(Qt.AlignCenter)
            self._trend_container.addWidget(empty)

    # ── Update: Recommendation ───────────────────────────────────

    def _update_recommendation(self, data: Any) -> None:
        self._clear_card_body(self._rec_card)
        colors = self._colors()
        score = getattr(data, "recovery_score", 0.0) or 0.0
        action = getattr(data, "recovery_action", "") or ""
        getattr(data, "recovery_level", "") or ""
        flags = getattr(data, "recovery_flags", []) or []

        if score > 0:
            state_label, _, _, status_lvl = _score_to_state(score)

            if score >= 70:
                badge_text = "Proceed Normally"
                badge_level = StatusLevel.SUCCESS
                reasoning = (
                    "Recovery metrics support a standard session. "
                    "Target RIR 1-2 on working sets."
                )
            elif score >= 40:
                badge_text = "Reduce Volume"
                badge_level = StatusLevel.WARNING
                reasoning = (
                    f"Recovery is reduced ({score:.0f}/100). "
                    "Consider reducing volume by 20% or taking a lighter session."
                )
            else:
                badge_text = "Recovery Only"
                badge_level = StatusLevel.ERROR
                reasoning = (
                    f"Recovery is critical ({score:.0f}/100). "
                    "Light activity or rest recommended today."
                )

            if action:
                reasoning = action

            status_badge = StatusBadge(text=badge_text, level=badge_level, outlined=False)
            self._rec_card.add_content(status_badge)

            action_lbl = QLabel(state_label)
            action_lbl.setStyleSheet(
                f"color: {_score_color(score)}; {font_style('h3')}; background: transparent;"
            )
            self._rec_card.add_content(action_lbl)

            reason_lbl = QLabel(reasoning)
            reason_lbl.setStyleSheet(
                f"color: {colors.text_secondary}; {font_style('body')}; background: transparent;"
            )
            reason_lbl.setWordWrap(True)
            self._rec_card.add_content(reason_lbl)

            if flags:
                for flag in flags[:2]:
                    msg = getattr(flag, "message", str(flag)) if not isinstance(flag, str) else flag
                    detail = (
                        getattr(flag, "detail", "") if not isinstance(flag, str) else ""
                    )
                    flag_lbl = QLabel(f"\u26a0 {msg[:120]}")
                    flag_lbl.setStyleSheet(
                        f"color: {colors.warning}; {font_style('body')}; background: transparent;"
                    )
                    flag_lbl.setWordWrap(True)
                    self._rec_card.add_content(flag_lbl)
                    if detail:
                        detail_lbl = QLabel(detail[:200])
                        detail_lbl.setStyleSheet(
                            f"color: {colors.text_disabled}; {font_style('caption')}; background: transparent;"
                        )
                        detail_lbl.setWordWrap(True)
                        self._rec_card.add_content(detail_lbl)
        else:
            empty = QLabel("Complete a workout to start receiving recovery recommendations.")
            empty.setStyleSheet(
                f"color: {colors.text_disabled}; {font_style('body_small')}; background: transparent;"
            )
            empty.setWordWrap(True)
            empty.setAlignment(Qt.AlignCenter)
            self._rec_card.add_content(empty)

    # ── Update: Counterfactuals ──────────────────────────────────

    def _update_counterfactuals(self, data: Any) -> None:
        self._counterfactual_grid.clear()
        colors = self._colors()
        score = getattr(data, "recovery_score", 0.0) or 0.0
        fatigue_score = getattr(data, "recovery_fatigue_score", 0.0) or 0.0

        if score == 0:
            return

        # Define default counterfactual scenarios
        scenarios = []

        # Sleep +1h → Recovery +8
        scenarios.append(_CounterfactualCard(
            icon="\U0001F634",
            action="Sleep +1 hour",
            impact="Recovery +8 points",
            impact_pct=0.85,
            action_color=colors.success,
        ))

        # Volume -5 sets → Readiness +5
        if fatigue_score > 30:
            scenarios.append(_CounterfactualCard(
                icon="\U0001F4C9",
                action="Reduce volume by 5 sets",
                impact="Readiness +5 points",
                impact_pct=0.65,
                action_color=colors.warning,
            ))

        # Hydrate → Fatigue -10
        scenarios.append(_CounterfactualCard(
            icon="\U0001F4A7",
            action="Increase hydration",
            impact="Fatigue -10 points",
            impact_pct=0.40,
            action_color=colors.info,
        ))

        for card in scenarios:
            self._counterfactual_grid.add_panel(card, span=PanelSpan.THIRD)

    # ── Update: History ──────────────────────────────────────────

    def _update_history(self, data: Any) -> None:
        self._clear_layout(self._history_container)
        colors = self._colors()
        scores = getattr(data, "recovery_scores", []) or []
        score_values = _extract_score_values(scores)

        if score_values:
            # Timeline visualization
            timeline = WeeklyTimeline()
            timeline.set_data(score_values)
            self._history_container.addWidget(timeline)

            # Milestones narrative
            milestones = []
            avg = sum(score_values) / len(score_values)
            milestones.append(f"Average score: {avg:.0f}/100 over {len(score_values)} days")

            best = max(score_values)
            worst = min(score_values)
            if best > 0:
                milestones.append(f"Best day: {best:.0f}/100")
            if worst > 0:
                milestones.append(f"Lowest: {worst:.0f}/100")

            if len(score_values) >= 3:
                recent = score_values[-3:]
                recent_avg = sum(recent) / len(recent)
                if recent_avg > avg + 5:
                    milestones.append("Recovery has been trending above average recently")
                elif recent_avg < avg - 5:
                    milestones.append("Recovery has been below average recently \u2014 consider more rest")

            ml = QLabel("\n".join(f"\u2022 {m}" for m in milestones))
            ml.setStyleSheet(
                f"color: {colors.text_secondary}; {font_style('body')}; background: transparent;"
            )
            ml.setWordWrap(True)
            self._history_container.addWidget(ml)
        else:
            empty = QLabel("Recovery history will appear here after completing workouts.")
            empty.setStyleSheet(
                f"color: {colors.text_disabled}; {font_style('body_small')}; background: transparent;"
            )
            empty.setWordWrap(True)
            empty.setAlignment(Qt.AlignCenter)
            self._history_container.addWidget(empty)

    # ── Layout Helpers ───────────────────────────────────────────

    @staticmethod
    def _clear_layout(layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    @staticmethod
    def _clear_card_body(card: AppCard) -> None:
        """Remove all content widgets from an AppCard's body."""
        # AppCard stores content in self._body
        body = getattr(card, "_body", None)
        if body is None:
            return
        while body.count():
            item = body.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
