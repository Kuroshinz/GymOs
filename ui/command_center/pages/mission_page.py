from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ui.design_system.layout import (
    EditorialGrid,
    KpiItem,
    KpiStrip,
    PanelSpan,
    ScrollContainer,
    SectionPanel,
)
from ui.design_system.tokens.color import ColorScheme, color_from_scheme


class MissionPage(QWidget):
    adjust_goal_clicked = Signal()
    view_history_clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()
        self._wire_buttons()

    def _wire_buttons(self) -> None:
        self._adjust_btn.clicked.connect(self.adjust_goal_clicked.emit)
        self._history_btn.clicked.connect(self.view_history_clicked.emit)

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

        self._build_goal_card(content_layout)
        self._build_progress_ribbon(content_layout)
        self._build_decision_timeline(content_layout)
        self._build_bottom_grid(content_layout)

        content_layout.addStretch()

    def _build_goal_card(self, parent: QVBoxLayout) -> None:
        colors = self._colors()
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.surface};
                border-bottom: 1px solid {colors.border};
            }}
        """)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 32, 32, 28)
        layout.setSpacing(16)

        top = QHBoxLayout()
        top.setSpacing(16)

        text_area = QVBoxLayout()
        text_area.setSpacing(4)

        self._hero_title = QLabel("Goal Workspace")
        self._hero_title.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 28px; font-weight: 800; "
            f"background: transparent; border: none;"
        )
        text_area.addWidget(self._hero_title)

        self._hero_subtitle = QLabel("Track your mission, intent, and goal alignment.")
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

        self._adjust_btn = QPushButton("Adjust Goal")
        self._adjust_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.success};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {colors.success_hover};
            }}
        """)
        self._adjust_btn.setCursor(Qt.PointingHandCursor)
        actions.addWidget(self._adjust_btn)

        self._history_btn = QPushButton("View History")
        self._history_btn.setStyleSheet(f"""
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
                border-color: {colors.success};
                color: {colors.success};
            }}
        """)
        self._history_btn.setCursor(Qt.PointingHandCursor)
        actions.addWidget(self._history_btn)

        top.addLayout(actions)
        layout.addLayout(top)

        goal_area = QHBoxLayout()
        goal_area.setSpacing(24)

        self._goal_name = QLabel("--")
        self._goal_name.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 24px; font-weight: 700; "
            f"background: transparent; border: none;"
        )
        goal_area.addWidget(self._goal_name)

        self._progress_bar = QFrame()
        self._progress_bar.setFixedHeight(8)
        self._progress_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.border};
                border-radius: 4px;
                border: none;
            }}
        """)
        self._progress_fill = QFrame(self._progress_bar)
        self._progress_fill.setFixedHeight(8)
        self._progress_fill.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.success};
                border-radius: 4px;
                border: none;
            }}
        """)
        self._progress_fill.setFixedWidth(0)
        goal_area.addWidget(self._progress_bar, 1)

        self._goal_pct = QLabel("0%")
        self._goal_pct.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 18px; font-weight: 700; "
            f"background: transparent; border: none;"
        )
        goal_area.addWidget(self._goal_pct)

        layout.addLayout(goal_area)

        parent.addWidget(container)

    def _build_progress_ribbon(self, parent: QVBoxLayout) -> None:
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
            KpiItem(label="Week", value="--", unit="", accent=colors.text_primary),
            KpiItem(label="Rate", value="--", unit="kg/wk", accent=colors.success),
            KpiItem(label="Target", value="--", unit="kg", accent=colors.primary),
            KpiItem(label="Adherence", value="--", unit="%", accent=colors.success),
            KpiItem(label="Projected", value="--", unit="", accent=colors.info),
            KpiItem(label="Confidence", value="--", unit="%", accent=colors.accent),
        ]
        self._kpi_strip = KpiStrip(items=kpi_items)
        layout.addWidget(self._kpi_strip)
        parent.addWidget(container)

    def _build_decision_timeline(self, parent: QVBoxLayout) -> None:
        colors = self._colors()
        container = QFrame()
        container.setStyleSheet(f"QFrame {{ background-color: {colors.background}; border: none; }}")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(32, 24, 32, 0)
        container_layout.setSpacing(12)

        self._timeline_section = SectionPanel(title="Decision Timeline", subtitle="Key decisions and outcomes")

        self._timeline_widget = QWidget()
        self._timeline_layout = QVBoxLayout(self._timeline_widget)
        self._timeline_layout.setContentsMargins(0, 0, 0, 0)
        self._timeline_layout.setSpacing(6)
        no_data = QLabel("No decisions recorded.")
        no_data.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;"
        )
        self._timeline_layout.addWidget(no_data)
        self._timeline_section.add_content(self._timeline_widget)
        container_layout.addWidget(self._timeline_section)
        parent.addWidget(container)

    def _build_bottom_grid(self, parent: QVBoxLayout) -> None:
        colors = self._colors()
        container = QFrame()
        container.setStyleSheet(f"QFrame {{ background-color: {colors.background}; border: none; }}")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(32, 16, 32, 32)
        container_layout.setSpacing(16)

        grid = EditorialGrid()
        grid.set_spacing(16)
        container_layout.addWidget(grid)

        self._insight_section = SectionPanel(title="Insights", subtitle="Goal analysis", span=PanelSpan.HALF)
        self._insight_label = QLabel("No insights available.")
        self._insight_label.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;"
        )
        self._insight_section.add_content(self._insight_label)
        grid.add_section(self._insight_section)

        self._warning_section = SectionPanel(title="Alerts", subtitle="Items needing attention", span=PanelSpan.HALF)
        self._warning_label = QLabel("No alerts.")
        self._warning_label.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;"
        )
        self._warning_section.add_content(self._warning_label)
        grid.add_section(self._warning_section)

        parent.addWidget(container)

    def update_data(self, data: Any) -> None:
        colors = self._colors()
        mission = _dict_val(data, "mission")
        adaptive = _dict_val(data, "adaptive")

        intent_data = mission.get("intent", {})
        goal = intent_data.get("current_goal", "") or ""
        target = intent_data.get("target_date", "") or ""
        progress = intent_data.get("progress_percent", 0.0) or 0.0
        adherence = intent_data.get("adherence", 0.0) or 0.0
        weekly_rate = intent_data.get("weekly_rate", 0.0) or 0.0

        if goal:
            self._goal_name.setText(goal)
            self._goal_pct.setText(f"{progress:.0f}%")
            bar_width = max(8, int(self._progress_bar.width() * min(progress, 100) / 100))
            self._progress_fill.setFixedWidth(bar_width)
        else:
            self._goal_name.setText("No active goal")
            self._goal_pct.setText("0%")

        kpi_items = [
            KpiItem(label="Week", value="--", unit="", accent=colors.text_primary),
            KpiItem(label="Rate", value=f"{weekly_rate:.1f}", unit="kg/wk", accent=colors.success),
            KpiItem(label="Target", value=target, unit="", accent=colors.primary),
            KpiItem(label="Adherence", value=f"{adherence:.0f}", unit="%", accent=colors.success),
            KpiItem(label="Projected", value=target, unit="", accent=colors.info),
            KpiItem(label="Confidence", value=f"{intent_data.get('confidence', 0):.0f}", unit="%", accent=colors.accent),
        ]
        self._kpi_strip.set_items(kpi_items)

        decisions = adaptive.get("decision_timeline_items", [])
        self._clear_layout(self._timeline_layout)
        if decisions:
            for dec in decisions[:6]:
                text = dec if isinstance(dec, str) else dec.get("decision_type", str(dec))
                outcome = dec.get("outcome", "") if isinstance(dec, dict) else ""
                icon = "" if outcome else ""
                lbl = QLabel(f"  {text}" + (f"  [{outcome}]" if outcome else ""))
                lbl.setStyleSheet(
                    f"color: {colors.text_primary}; font-size: 13px; "
                    f"background: transparent; border: none;"
                )
                self._timeline_layout.addWidget(lbl)
        else:
            no_data = QLabel("No decisions recorded.")
            no_data.setStyleSheet(f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;")
            self._timeline_layout.addWidget(no_data)

        readiness_data = mission.get("training_readiness", {})
        limiting = readiness_data.get("limiting_factor", "") if readiness_data else ""
        if limiting:
            self._warning_label.setText(f"Limiting factor: {limiting}")
            self._warning_label.setStyleSheet(
                f"color: {colors.warning}; font-size: 13px; background: transparent; border: none;"
            )
        else:
            self._warning_label.setText("No alerts.")
            self._warning_label.setStyleSheet(f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;")

    def _clear_layout(self, layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


def _dict_val(data: Any, key: str) -> dict:
    val = getattr(data, key, {})
    return val if isinstance(val, dict) else {}
