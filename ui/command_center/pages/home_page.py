from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ui.design_system.components import (
    ActivityFeed,
    ActivityItem,
    InsightCard,
    WarningBanner,
)
from ui.design_system.layout import (
    EditorialGrid,
    KpiItem,
    KpiStrip,
    PanelSpan,
    ScrollContainer,
    SectionPanel,
)
from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.visualization import GoalRing, RecoveryRing


class HomePage(QWidget):
    start_workout_clicked = Signal()
    log_weight_clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()
        self._wire_buttons()

    def _wire_buttons(self) -> None:
        self._start_btn.clicked.connect(self.start_workout_clicked.emit)
        self._log_weight_btn.clicked.connect(self.log_weight_clicked.emit)

    def _colors(self):
        return color_from_scheme(ColorScheme.DARK)

    def _build_ui(self) -> None:
        colors = self._colors()
        scroll = ScrollContainer()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        content_layout = scroll._wrapper.layout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self._build_hero_area(content_layout)
        self._build_kpi_strip(content_layout)
        self._build_content_grid(content_layout)
        self._build_bottom_ribbon(content_layout)

        content_layout.addStretch()

    def _build_hero_area(self, parent: QVBoxLayout) -> None:
        colors = self._colors()
        hero_container = QFrame()
        hero_container.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.surface};
                border-bottom: 1px solid {colors.border};
            }}
        """)
        hero_layout = QVBoxLayout(hero_container)
        hero_layout.setContentsMargins(32, 32, 32, 28)
        hero_layout.setSpacing(16)

        top = QHBoxLayout()
        top.setSpacing(24)

        rings = QHBoxLayout()
        rings.setSpacing(16)

        self._recovery_ring = RecoveryRing(size=80)
        rings.addWidget(self._recovery_ring)

        self._goal_ring = GoalRing(size=80)
        rings.addWidget(self._goal_ring)

        top.addLayout(rings)

        text_area = QVBoxLayout()
        text_area.setSpacing(4)

        self._hero_title = QLabel("Executive Dashboard")
        self._hero_title.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 28px; font-weight: 800; "
            f"background: transparent; border: none;"
        )
        text_area.addWidget(self._hero_title)

        self._hero_subtitle = QLabel("Your command center for training intelligence, recovery, and performance.")
        self._hero_subtitle.setStyleSheet(
            f"color: {colors.text_secondary}; font-size: 15px; "
            f"background: transparent; border: none;"
        )
        self._hero_subtitle.setWordWrap(True)
        text_area.addWidget(self._hero_subtitle)

        text_area.addStretch()
        top.addLayout(text_area, 1)

        actions = QVBoxLayout()
        actions.setSpacing(8)

        self._start_btn = QPushButton("Start Workout")
        self._start_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.primary};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {colors.primary_hover};
            }}
        """)
        self._start_btn.setCursor(Qt.PointingHandCursor)
        actions.addWidget(self._start_btn)

        self._log_weight_btn = QPushButton("Log Weight")
        self._log_weight_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {colors.text_secondary};
                border: 1px solid {colors.border};
                border-radius: 8px;
                padding: 8px 24px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                border-color: {colors.primary};
                color: {colors.primary};
            }}
        """)
        self._log_weight_btn.setCursor(Qt.PointingHandCursor)
        actions.addWidget(self._log_weight_btn)

        top.addLayout(actions)

        hero_layout.addLayout(top)

        readiness_row = QHBoxLayout()
        readiness_row.setSpacing(24)

        self._hero_readiness = QLabel("Readiness: --")
        self._hero_readiness.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 16px; font-weight: 600; "
            f"background: transparent; border: none;"
        )
        readiness_row.addWidget(self._hero_readiness)

        self._hero_today = QLabel("Today's Plan: --")
        self._hero_today.setStyleSheet(
            f"color: {colors.text_secondary}; font-size: 14px; "
            f"background: transparent; border: none;"
        )
        readiness_row.addWidget(self._hero_today)

        readiness_row.addStretch()
        hero_layout.addLayout(readiness_row)

        parent.addWidget(hero_container)

    def _build_kpi_strip(self, parent: QVBoxLayout) -> None:
        colors = self._colors()
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.background};
                border-bottom: 1px solid {colors.border};
            }}
        """)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 0, 32, 0)

        kpi_items = [
            KpiItem(label="Recovery", value="--", unit="%", accent=colors.success),
            KpiItem(label="Readiness", value="--", unit="%", accent=colors.primary),
            KpiItem(label="Volume", value="--", unit="kg", accent=colors.info),
            KpiItem(label="Sessions", value="--", unit="/wk", accent=colors.text_primary),
            KpiItem(label="Adherence", value="--", unit="%", accent=colors.success),
            KpiItem(label="Goal", value="--", unit="%", accent=colors.accent),
            KpiItem(label="Sleep", value="--", unit="hrs", accent=colors.info),
            KpiItem(label="PRs", value="--", unit="mo", accent=colors.warning),
        ]
        self._kpi_strip = KpiStrip(items=kpi_items)
        layout.addWidget(self._kpi_strip)
        parent.addWidget(container)

    def _build_content_grid(self, parent: QVBoxLayout) -> None:
        colors = self._colors()
        container = QFrame()
        container.setStyleSheet(f"QFrame {{ background-color: {colors.background}; border: none; }}")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(32, 24, 32, 0)
        container_layout.setSpacing(16)

        grid = EditorialGrid()
        grid.set_spacing(16)
        container_layout.addWidget(grid)

        self._insights_section = SectionPanel(title="Top Insights", subtitle="AI-driven analysis", span=PanelSpan.TWO_THIRDS)
        self._insights_widget = QWidget()
        self._insights_widget_layout = QVBoxLayout(self._insights_widget)
        self._insights_widget_layout.setContentsMargins(0, 0, 0, 0)
        self._insights_widget_layout.setSpacing(8)
        no_data = QLabel("No insights available.")
        no_data.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;"
        )
        self._insights_widget_layout.addWidget(no_data)
        self._insights_section.add_content(self._insights_widget)
        grid.add_section(self._insights_section)

        activity_items = [
            ActivityItem(icon="", text="No recent activity.", timestamp="", status=""),
        ]
        self._activity_feed = ActivityFeed(items=activity_items, title="Recent Activity")
        grid.add_panel(self._activity_feed, PanelSpan.THIRD)

        parent.addWidget(container)

    def _build_bottom_ribbon(self, parent: QVBoxLayout) -> None:
        colors = self._colors()
        container = QFrame()
        container.setStyleSheet(f"QFrame {{ background-color: {colors.background}; border: none; }}")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(32, 16, 32, 32)
        container_layout.setSpacing(12)

        self._warning_banner = WarningBanner(
            icon="", message="No warnings.", level="info",
        )
        container_layout.addWidget(self._warning_banner)

        rec_grid = QHBoxLayout()
        rec_grid.setSpacing(16)

        self._rec_section = SectionPanel(title="Recommendation", subtitle="Next best action", span=PanelSpan.HALF)
        self._rec_label = QLabel("No recommendations available.")
        self._rec_label.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;"
        )
        self._rec_section.add_content(self._rec_label)
        rec_grid.addWidget(self._rec_section)

        self._milestones_section = SectionPanel(title="Recent PRs", subtitle="Personal records", span=PanelSpan.HALF)
        self._milestones_label = QLabel("No recent PRs.")
        self._milestones_label.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;"
        )
        self._milestones_section.add_content(self._milestones_label)
        rec_grid.addWidget(self._milestones_section)

        container_layout.addLayout(rec_grid)
        parent.addWidget(container)

    def update_data(self, data: Any) -> None:
        colors = self._colors()
        mission = _safe_dict(data, "mission")
        recovery = _safe_dict(data, "recovery")
        prediction = _safe_dict(data, "prediction")
        knowledge = _safe_dict(data, "knowledge")
        planning = _safe_dict(data, "planning")

        recovery_data = recovery.get("recovery_overview", {})
        score = recovery_data.get("score", 0.0) or 0.0
        level = recovery_data.get("level", "") or ""
        self._recovery_ring.set_value(score, 100, "Recovery")

        readiness_data = recovery.get("training_readiness", {}) or mission.get("training_readiness", {})
        readiness_score = readiness_data.get("score", 0.0) or 0.0
        readiness_level = readiness_data.get("readiness", "") or ""
        self._goal_ring.set_goal(readiness_score, 100, "Readiness", "%")

        self._hero_readiness.setText(f"Readiness: {readiness_level.capitalize() if readiness_level else '--'}  ({readiness_score:.0f}%)")

        meso = planning.get("current_mesocycle", {})
        name = meso.get("name", "") or ""
        week = meso.get("week", 0)
        total = meso.get("total_weeks", 0)
        if name:
            self._hero_today.setText(f"Today's Plan: {name} — Week {week}/{total}")
        else:
            self._hero_today.setText("Today's Plan: No active program")

        kpi_items = [
            KpiItem(label="Recovery", value=f"{score:.0f}", unit="%", accent=colors.success),
            KpiItem(label="Readiness", value=f"{readiness_score:.0f}", unit="%", accent=colors.primary),
            KpiItem(label="Volume", value=f"{recovery_data.get('weekly_volume', 0):.0f}", unit="kg", accent=colors.info),
            KpiItem(label="Sessions", value=f"{planning.get('weekly_review', {}).get('sessions_completed', 0)}", unit="/wk", accent=colors.text_primary),
            KpiItem(label="Adherence", value=f"{planning.get('weekly_review', {}).get('adherence_rate', 0):.0f}", unit="%", accent=colors.success),
            KpiItem(label="Goal", value=f"{mission.get('intent', {}).get('progress_percent', 0):.0f}", unit="%", accent=colors.accent),
            KpiItem(label="Sleep", value=f"{recovery_data.get('sleep_score', 0):.0f}", unit="%", accent=colors.info),
            KpiItem(label="PRs", value="--", unit="mo", accent=colors.warning),
        ]
        self._kpi_strip.set_items(kpi_items)

        insights = knowledge.get("optimization_insights", {})
        insight_list = insights.get("insights", [])
        self._clear_layout(self._insights_widget_layout)
        if insight_list:
            for ins in insight_list[:4]:
                text = ins if isinstance(ins, str) else ins.get("text", str(ins))
                card = InsightCard(icon="", title=text, description="", badge_text="AI")
                self._insights_widget_layout.addWidget(card)
        else:
            no_data = QLabel("No insights available.")
            no_data.setStyleSheet(f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;")
            self._insights_widget_layout.addWidget(no_data)

        updates = knowledge.get("knowledge_updates", []) or knowledge.get("updates", [])
        activity_items = []
        if updates:
            for upd in updates[:5]:
                text = upd if isinstance(upd, str) else upd.get("statement", str(upd))
                activity_items.append(ActivityItem(icon="", text=text, timestamp="", status=""))
        if not activity_items:
            activity_items.append(ActivityItem(icon="", text="No recent activity.", timestamp="", status=""))
        self._activity_feed.set_items(activity_items)

        flags = recovery_data.get("flags", [])
        if flags:
            flag_text = "; ".join(str(f) for f in flags[:2])
            self._warning_banner.deleteLater()
            self._warning_banner = WarningBanner(icon="", message=flag_text, level="warning")
            bottom_container = self._warning_banner.parentWidget()
        else:
            self._warning_banner.deleteLater()
            self._warning_banner = WarningBanner(icon="", message="All systems nominal.", level="success")

        recs = planning.get("recommendations", []) or mission.get("recommendations", [])
        self._rec_section.clear()
        if recs:
            rec_text = recs[0] if isinstance(recs[0], str) else recs[0].get("message", str(recs[0]))
            self._rec_label = QLabel(rec_text)
            self._rec_label.setStyleSheet(
                f"color: {colors.text_primary}; font-size: 14px; font-weight: 600; "
                f"background: transparent; border: none;"
            )
            self._rec_label.setWordWrap(True)
            self._rec_section.add_content(self._rec_label)
        else:
            self._rec_label = QLabel("No recommendations.")
            self._rec_label.setStyleSheet(f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;")
            self._rec_section.add_content(self._rec_label)

    def _clear_layout(self, layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


def _safe_dict(data: Any, key: str) -> dict:
    val = getattr(data, key, {})
    return val if isinstance(val, dict) else {}
