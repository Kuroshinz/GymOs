from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ui.design_system.components.insight_card import InsightCard
from ui.design_system.components.section_header import SectionHeader
from ui.design_system.components.status_badge import StatusBadge, StatusLevel
from ui.design_system.layout import EditorialGrid, PanelSpan, SectionPanel
from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens, px_from_token
from ui.design_system.tokens.spacing import SpacingTokens
from ui.design_system.tokens.typography import TypographyTokens, font_style
from ui.design_system.visualization import RecoveryRing, TrendIndicator, WeeklyTimeline

S = SpacingTokens()
R = RadiusTokens()
T = TypographyTokens()

_px4 = px_from_token(S.s1)
_px6 = px_from_token(S.s1_5)
_px8 = px_from_token(S.s2)
_px12 = px_from_token(S.s3)
_px16 = px_from_token(S.s4)
_px24 = px_from_token(S.s6)
_px32 = px_from_token(S.s8)


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


class RecoveryDashboard(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _colors(self):
        return color_from_scheme(ColorScheme.DARK)

    def _build_ui(self) -> None:
        from ui.design_system.layout.scroll_container import ScrollContainer
        scroll = ScrollContainer()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        main = QVBoxLayout()
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)
        scroll.content_layout.insertLayout(0, main)

        self._build_hero(main)

        self._build_section_header(main, "Recovery Summary", "Sleep, stress and fatigue drivers")
        self._drivers_grid = EditorialGrid()
        self._drivers_grid.set_spacing(_px16)
        main.addWidget(self._drivers_grid)
        self._build_driver_cards()

        self._build_section_header(main, "Weekly Recovery", "7-day recovery score trend")
        self._weekly_container = QVBoxLayout()
        self._weekly_container.setContentsMargins(0, 0, 0, 0)
        self._weekly_container.setSpacing(_px8)
        main.addLayout(self._weekly_container)

        self._build_section_header(main, "Today's Recommendation", "Personalised guidance")
        self._rec_container = QVBoxLayout()
        self._rec_container.setContentsMargins(0, 0, 0, 0)
        self._rec_container.setSpacing(_px8)
        main.addLayout(self._rec_container)

        main.addStretch()

    def _build_section_header(self, parent: QVBoxLayout, title: str, subtitle: str) -> None:
        header = SectionHeader(title=title, subtitle=subtitle)
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, _px24, 0, _px8)
        hbox.addWidget(header)
        parent.addLayout(hbox)

    def _build_hero(self, parent: QVBoxLayout) -> None:
        colors = self._colors()
        hero = QFrame()
        hero.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.surface};
                border-radius: {R.xl};
                border: 1px solid {colors.border};
            }}
        """)
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(24, 20, 24, 20)
        hero_layout.setSpacing(16)

        accent = QFrame()
        accent.setFixedWidth(4)
        accent.setStyleSheet(f"background-color: {colors.primary}; border-radius: {R.sm}; border: none;")
        hero_layout.addWidget(accent)

        text_area = QVBoxLayout()
        text_area.setSpacing(6)

        title = QLabel("Recovery Intelligence")
        title.setStyleSheet(f"color: {colors.text_primary}; {font_style('h4')}")
        text_area.addWidget(title)

        self._hero_subtitle = QLabel("How your body is responding to training")
        self._hero_subtitle.setStyleSheet(f"color: {colors.text_secondary}; {font_style('body_small')}")
        self._hero_subtitle.setWordWrap(True)
        text_area.addWidget(self._hero_subtitle)

        text_area.addStretch()
        hero_layout.addLayout(text_area, 1)

        content_area = QHBoxLayout()
        content_area.setSpacing(12)

        self._recovery_ring = RecoveryRing(size=90)
        content_area.addWidget(self._recovery_ring)

        self._hero_score = QLabel("--")
        self._hero_score.setStyleSheet(f"color: {colors.text_primary}; {font_style('h2')}")
        self._hero_score.setAlignment(Qt.AlignCenter)
        content_area.addWidget(self._hero_score)

        self._hero_level = StatusBadge("--", StatusLevel.NEUTRAL, outlined=True)
        content_area.addWidget(self._hero_level)

        self._hero_trend = TrendIndicator()
        content_area.addWidget(self._hero_trend)

        hero_layout.addLayout(content_area)
        parent.addWidget(hero)

    def _build_driver_cards(self) -> None:
        colors = self._colors()

        self._sleep_panel = SectionPanel(title="Sleep", subtitle="Recovery through rest", span=PanelSpan.THIRD)
        self._sleep_score_label = QLabel("--")
        self._sleep_score_label.setStyleSheet(f"color: {colors.text_primary}; {font_style('h3')}")
        self._sleep_panel.add_content(self._sleep_score_label)
        self._sleep_detail = QLabel("")
        self._sleep_detail.setStyleSheet(f"color: {colors.text_disabled}; {font_style('caption')}")
        self._sleep_panel.add_content(self._sleep_detail)
        self._sleep_empty = QLabel("No sleep data")
        self._sleep_empty.setStyleSheet(f"color: {colors.text_disabled}; {font_style('body_small')}")
        self._sleep_empty.setAlignment(Qt.AlignCenter)
        self._sleep_panel.add_content(self._sleep_empty)
        self._sleep_score_label.hide()
        self._sleep_detail.hide()
        self._drivers_grid.add_section(self._sleep_panel)

        self._stress_panel = SectionPanel(title="Stress", subtitle="Daily stress load", span=PanelSpan.THIRD)
        self._stress_score_label = QLabel("--")
        self._stress_score_label.setStyleSheet(f"color: {colors.text_primary}; {font_style('h3')}")
        self._stress_panel.add_content(self._stress_score_label)
        self._stress_detail = QLabel("")
        self._stress_detail.setStyleSheet(f"color: {colors.text_disabled}; {font_style('caption')}")
        self._stress_panel.add_content(self._stress_detail)
        self._stress_empty = QLabel("No stress data")
        self._stress_empty.setStyleSheet(f"color: {colors.text_disabled}; {font_style('body_small')}")
        self._stress_empty.setAlignment(Qt.AlignCenter)
        self._stress_panel.add_content(self._stress_empty)
        self._stress_score_label.hide()
        self._stress_detail.hide()
        self._drivers_grid.add_section(self._stress_panel)

        self._fatigue_panel = SectionPanel(title="Fatigue", subtitle="Muscular fatigue level", span=PanelSpan.THIRD)
        self._fatigue_score_label = QLabel("--")
        self._fatigue_score_label.setStyleSheet(f"color: {colors.text_primary}; {font_style('h3')}")
        self._fatigue_panel.add_content(self._fatigue_score_label)
        self._fatigue_detail = QLabel("")
        self._fatigue_detail.setStyleSheet(f"color: {colors.text_disabled}; {font_style('caption')}")
        self._fatigue_panel.add_content(self._fatigue_detail)
        self._fatigue_empty = QLabel("No fatigue data")
        self._fatigue_empty.setStyleSheet(f"color: {colors.text_disabled}; {font_style('body_small')}")
        self._fatigue_empty.setAlignment(Qt.AlignCenter)
        self._fatigue_panel.add_content(self._fatigue_empty)
        self._fatigue_score_label.hide()
        self._fatigue_detail.hide()
        self._drivers_grid.add_section(self._fatigue_panel)

    def refresh(self, data: Any) -> None:
        self._update_hero(data)
        self._update_drivers(data)
        self._update_weekly(data)
        self._update_recommendation(data)

    @staticmethod
    def _score_color(value: float, invert: bool = False) -> str:
        colors_obj = color_from_scheme(ColorScheme.DARK)
        if invert:
            if value <= 30:
                return colors_obj.success
            if value <= 50:
                return colors_obj.warning
            return colors_obj.error
        if value >= 80:
            return colors_obj.success
        if value >= 60:
            return colors_obj.warning
        return colors_obj.error

    def _update_hero(self, data: Any) -> None:
        colors = self._colors()
        score = getattr(data, "recovery_score", 0.0) or 0.0
        level = getattr(data, "recovery_level", "") or ""

        self._recovery_ring.set_value(score, 100.0, "Recovery")
        self._hero_score.setText(f"{score:.0f}" if score else "--")
        self._hero_score.setStyleSheet(
            f"color: {self._score_color(score)}; {font_style('h2')}"
        )

        level_key = level.lower() if level else "unknown"
        level_display = level_key.upper().replace("_", " ")
        level_enum = StatusLevel.SUCCESS
        if level_key in ("critical", "very_high", "high"):
            level_enum = StatusLevel.ERROR
        elif level_key in ("moderate", "warning", "caution"):
            level_enum = StatusLevel.WARNING
        elif level_key in ("good", "ready"):
            level_enum = StatusLevel.SUCCESS
        else:
            level_enum = StatusLevel.NEUTRAL
        self._hero_level.set_level(level_enum)
        self._hero_level.setText(level_display if level else "--")

        trend_data = getattr(data, "recovery_trend", None) or {}
        if isinstance(trend_data, dict):
            direction = str(trend_data.get("direction", "stable"))
        else:
            direction = str(getattr(trend_data, "direction", "stable"))
            if hasattr(direction, "value"):
                direction = direction.value

        if score:
            self._hero_trend.set_trend(direction.capitalize(), "")
        else:
            self._hero_trend.hide()

    def _update_drivers(self, data: Any) -> None:
        sleep_score = getattr(data, "recovery_sleep_score", 0.0) or 0.0
        sleep_hours = getattr(data, "recovery_sleep_hours", 0.0) or 0.0
        stress_score = getattr(data, "recovery_stress_score", 0.0) or 0.0
        fatigue_score = getattr(data, "recovery_fatigue_score", 0.0) or 0.0

        if sleep_score:
            self._sleep_score_label.show()
            self._sleep_detail.show()
            self._sleep_empty.hide()
            self._sleep_score_label.setText(f"{sleep_score:.0f}/100")
            self._sleep_score_label.setStyleSheet(
                f"color: {self._score_color(sleep_score)}; {font_style('h3')}"
            )
            detail = f"{sleep_hours:.1f}h" if sleep_hours else ""
            self._sleep_detail.setText(detail)
        else:
            self._sleep_score_label.hide()
            self._sleep_detail.hide()
            self._sleep_empty.show()

        if stress_score:
            self._stress_score_label.show()
            self._stress_detail.show()
            self._stress_empty.hide()
            self._stress_score_label.setText(f"{stress_score:.0f}/100")
            self._stress_score_label.setStyleSheet(
                f"color: {self._score_color(stress_score, invert=True)}; {font_style('h3')}"
            )
            self._stress_detail.setText(f"Level: {stress_score:.0f}")
        else:
            self._stress_score_label.hide()
            self._stress_detail.hide()
            self._stress_empty.show()

        if fatigue_score:
            self._fatigue_score_label.show()
            self._fatigue_detail.show()
            self._fatigue_empty.hide()
            self._fatigue_score_label.setText(f"{fatigue_score:.0f}/100")
            self._fatigue_score_label.setStyleSheet(
                f"color: {self._score_color(fatigue_score, invert=True)}; {font_style('h3')}"
            )
            level = "low"
            if fatigue_score >= 70:
                level = "very_high"
            elif fatigue_score >= 50:
                level = "high"
            elif fatigue_score >= 30:
                level = "moderate"
            self._fatigue_detail.setText(f"Level: {level.upper().replace('_', ' ')}")
        else:
            self._fatigue_score_label.hide()
            self._fatigue_detail.hide()
            self._fatigue_empty.show()

    def _update_weekly(self, data: Any) -> None:
        for i in reversed(range(self._weekly_container.count())):
            item = self._weekly_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        weekly = getattr(data, "recovery_weekly", []) or []
        scores = getattr(data, "recovery_scores", []) or []
        colors_obj = self._colors()

        score_values = []
        if scores:
            for s in scores:
                if isinstance(s, dict):
                    score_values.append(s.get("overall_score", 0))
                else:
                    score_values.append(
                        getattr(s, "overall_score", 0) if hasattr(s, "overall_score") else float(s) if s else 0
                    )
        elif weekly:
            for w in weekly[:7]:
                val = w.get("average", 0) if isinstance(w, dict) else getattr(w, "average", 0)
                if val:
                    score_values.append(val)

        if score_values and any(score_values):
            timeline = WeeklyTimeline()
            timeline.set_data(score_values)
            self._weekly_container.addWidget(timeline)
            avg = sum(score_values) / len(score_values)
            avg_lbl = QLabel(f"Average: {avg:.1f}/100")
            avg_lbl.setStyleSheet(f"color: {colors_obj.text_disabled}; {font_style('caption')}")
            avg_lbl.setAlignment(Qt.AlignCenter)
            self._weekly_container.addWidget(avg_lbl)
        else:
            empty = QLabel("No recovery score history yet")
            empty.setStyleSheet(f"color: {colors_obj.text_disabled}; {font_style('body_small')}")
            empty.setAlignment(Qt.AlignCenter)
            self._weekly_container.addWidget(empty)

    def _update_recommendation(self, data: Any) -> None:
        for i in reversed(range(self._rec_container.count())):
            item = self._rec_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        colors_obj = self._colors()
        action = getattr(data, "recovery_action", "") or ""
        level = getattr(data, "recovery_level", "") or ""
        flags = getattr(data, "recovery_flags", []) or []

        if action:
            card = InsightCard(
                icon="\u2192",
                title="Suggested Action",
                description=action,
                badge_text="Action",
                badge_level=StatusLevel.INFO,
            )
            self._rec_container.addWidget(card)

        if flags:
            for flag in flags[:3]:
                msg = getattr(flag, "message", str(flag)) if not isinstance(flag, str) else flag
                sev = getattr(flag, "severity", "info") if not isinstance(flag, str) else "info"
                if hasattr(sev, "value"):
                    sev = sev.value
                badge_level = StatusLevel.WARNING if sev in ("critical", "high", "warning") else StatusLevel.INFO
                card = InsightCard(
                    icon="\u26a0",
                    title="Flag",
                    description=msg[:160],
                    badge_text=sev.upper(),
                    badge_level=badge_level,
                )
                self._rec_container.addWidget(card)
        elif not action and level:
            card = InsightCard(
                icon="\u2714",
                title="No Action Needed",
                description="Continue your current training plan. Recovery metrics look good.",
                badge_text="OK",
                badge_level=StatusLevel.SUCCESS,
            )
            self._rec_container.addWidget(card)
        else:
            empty = QLabel("Complete a workout to start receiving recovery insights.")
            empty.setStyleSheet(f"color: {colors_obj.text_disabled}; {font_style('body_small')}")
            empty.setAlignment(Qt.AlignCenter)
            empty.setWordWrap(True)
            self._rec_container.addWidget(empty)
