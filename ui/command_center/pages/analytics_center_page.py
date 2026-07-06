from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ui.design_system.components import ActivityFeed, ActivityItem
from ui.design_system.layout import (
    EditorialGrid,
    KpiItem,
    KpiStrip,
    PanelSpan,
    ScrollContainer,
    SectionPanel,
)
from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.visualization import ConfidenceGauge, WeeklyTimeline


class AnalyticsCenterPage(QWidget):
    export_report_clicked = Signal()
    compare_periods_clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()
        self._wire_buttons()

    def _wire_buttons(self) -> None:
        self._export_btn.clicked.connect(self.export_report_clicked.emit)
        self._compare_btn.clicked.connect(self.compare_periods_clicked.emit)

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

        self._build_data_wall(content_layout)
        self._build_kpi_ribbon(content_layout)
        self._build_performance_charts(content_layout)
        self._build_bottom_grid(content_layout)

        content_layout.addStretch()

    def _build_data_wall(self, parent: QVBoxLayout) -> None:
        colors = self._colors()
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.surface};
                border-bottom: 1px solid {colors.border};
            }}
        """)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(32, 32, 32, 28)
        layout.setSpacing(24)

        hero_metric = QVBoxLayout()
        hero_metric.setSpacing(4)

        self._hero_primary_value = QLabel("--")
        self._hero_primary_value.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 56px; font-weight: 800; "
            f"background: transparent; border: none;"
        )
        hero_metric.addWidget(self._hero_primary_value)

        self._hero_primary_label = QLabel("Total Volume This Week")
        self._hero_primary_label.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 13px; font-weight: 600; letter-spacing: 1px; "
            f"background: transparent; border: none;"
        )
        hero_metric.addWidget(self._hero_primary_label)
        layout.addLayout(hero_metric, 1)

        text_area = QVBoxLayout()
        text_area.setSpacing(4)

        self._hero_title = QLabel("Performance Lab")
        self._hero_title.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 24px; font-weight: 700; "
            f"background: transparent; border: none;"
        )
        text_area.addWidget(self._hero_title)

        self._hero_subtitle = QLabel("Volume trends, compliance rates, and performance metrics.")
        self._hero_subtitle.setStyleSheet(
            f"color: {colors.text_secondary}; font-size: 14px; "
            f"background: transparent; border: none;"
        )
        self._hero_subtitle.setWordWrap(True)
        text_area.addWidget(self._hero_subtitle)
        text_area.addStretch()
        layout.addLayout(text_area, 1)

        actions = QVBoxLayout()
        actions.setSpacing(8)

        self._export_btn = QPushButton("Export Report")
        self._export_btn.setStyleSheet(f"""
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
        self._export_btn.setCursor(Qt.PointingHandCursor)
        actions.addWidget(self._export_btn)

        self._compare_btn = QPushButton("Compare Periods")
        self._compare_btn.setStyleSheet(f"""
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
        self._compare_btn.setCursor(Qt.PointingHandCursor)
        actions.addWidget(self._compare_btn)

        layout.addLayout(actions)
        parent.addWidget(container)

    def _build_kpi_ribbon(self, parent: QVBoxLayout) -> None:
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
            KpiItem(label="Volume", value="--", unit="kg", accent=colors.primary),
            KpiItem(label="Compliance", value="--", unit="%", accent=colors.success),
            KpiItem(label="PRs", value="--", unit="", accent=colors.warning),
            KpiItem(label="Frequency", value="--", unit="/wk", accent=colors.info),
            KpiItem(label="Sessions", value="--", unit="", accent=colors.text_primary),
        ]
        self._kpi_strip = KpiStrip(items=kpi_items)
        layout.addWidget(self._kpi_strip)
        parent.addWidget(container)

    def _build_performance_charts(self, parent: QVBoxLayout) -> None:
        colors = self._colors()
        container = QFrame()
        container.setStyleSheet(f"QFrame {{ background-color: {colors.background}; border: none; }}")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(32, 24, 32, 0)
        container_layout.setSpacing(16)

        self._volume_section = SectionPanel(title="Weekly Volume", subtitle="Training load by day")
        self._volume_chart = WeeklyTimeline()
        self._volume_section.add_content(self._volume_chart)
        container_layout.addWidget(self._volume_section)

        grid = EditorialGrid()
        grid.set_spacing(16)
        container_layout.addWidget(grid)

        self._compliance_section = SectionPanel(title="Compliance Rate", subtitle="Program adherence", span=PanelSpan.HALF)
        self._compliance_gauge = ConfidenceGauge(width=240, height=32)
        self._compliance_gauge.set_confidence(0.0, "Overall Compliance")
        self._compliance_section.add_content(self._compliance_gauge)
        grid.add_section(self._compliance_section)

        self._pr_section = SectionPanel(title="Recent PRs", subtitle="Personal records", span=PanelSpan.HALF)
        self._pr_widget = QWidget()
        self._pr_layout = QVBoxLayout(self._pr_widget)
        self._pr_layout.setContentsMargins(0, 0, 0, 0)
        self._pr_layout.setSpacing(4)
        no_pr = QLabel("No recent PRs.")
        no_pr.setStyleSheet(f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;")
        self._pr_layout.addWidget(no_pr)
        self._pr_section.add_content(self._pr_widget)
        grid.add_section(self._pr_section)

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

        self._muscle_section = SectionPanel(title="Muscle Balance", subtitle="Volume distribution", span=PanelSpan.HALF)
        self._muscle_label = QLabel("No muscle balance data.")
        self._muscle_label.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;"
        )
        self._muscle_section.add_content(self._muscle_label)
        grid.add_section(self._muscle_section)

        activity_items = [
            ActivityItem(icon="", text="No recent activity.", timestamp="", status=""),
        ]
        self._activity_feed = ActivityFeed(items=activity_items, title="Recent Activity")
        grid.add_panel(self._activity_feed, PanelSpan.HALF)

        parent.addWidget(container)

    def update_data(self, data: Any) -> None:
        colors = self._colors()
        planning = _safe_dict(data, "planning")
        tracking = _safe_dict(data, "tracking")
        recovery = _safe_dict(data, "recovery")

        volume_data = tracking.get("weekly_volume", []) if isinstance(tracking, dict) else []
        if volume_data:
            total_vol = sum(d.get("value", 0) for d in volume_data if isinstance(d, dict))
            self._hero_primary_value.setText(f"{total_vol:,.0f}")
            self._volume_chart.set_data([(d.get("day", ""), d.get("value", 0)) for d in volume_data if isinstance(d, dict)])
        else:
            total_vol = 0
            self._hero_primary_value.setText("--")
            self._volume_chart.set_data([("M", 0), ("T", 0), ("W", 0), ("T", 0), ("F", 0), ("S", 0), ("S", 0)])

        adherence = tracking.get("adherence", 0.0) if isinstance(tracking, dict) else 0.0
        prs = tracking.get("recent_prs", []) if isinstance(tracking, dict) else []
        sessions_completed = planning.get("weekly_review", {}).get("sessions_completed", 0) if isinstance(planning, dict) else 0

        kpi_items = [
            KpiItem(label="Volume", value=f"{total_vol:,.0f}" if total_vol else "--", unit="kg", accent=colors.primary),
            KpiItem(label="Compliance", value=f"{adherence:.0f}" if adherence else "--", unit="%", accent=colors.success),
            KpiItem(label="PRs", value=str(len(prs)) if prs else "0", unit="", accent=colors.warning),
            KpiItem(label="Frequency", value=f"{sessions_completed}", unit="/wk", accent=colors.info),
            KpiItem(label="Sessions", value=str(sessions_completed), unit="", accent=colors.text_primary),
        ]
        self._kpi_strip.set_items(kpi_items)

        self._compliance_gauge.set_confidence(float(adherence) / 100.0 if float(adherence) > 1 else float(adherence))

        self._pr_layout = self._pr_widget.layout()
        self._clear_layout(self._pr_layout)
        if prs:
            for pr in prs[:5]:
                text = pr if isinstance(pr, str) else pr.get("exercise_name", str(pr))
                lbl = QLabel(f"  {text}")
                lbl.setStyleSheet(f"color: {colors.text_primary}; font-size: 13px; font-weight: 500; background: transparent; border: none;")
                self._pr_layout.addWidget(lbl)
        else:
            lbl = QLabel("No recent PRs.")
            lbl.setStyleSheet(f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;")
            self._pr_layout.addWidget(lbl)

        recovery_data = recovery.get("recovery_overview", {})
        activity_items = []
        if recovery_data:
            score = recovery_data.get("score", 0.0) or 0.0
            activity_items.append(ActivityItem(icon="", text=f"Recovery score: {score:.0f}%", timestamp="Today", status=""))
        if prs:
            for pr in prs[:2]:
                text = pr if isinstance(pr, str) else pr.get("exercise_name", str(pr))
                activity_items.append(ActivityItem(icon="", text=f"PR: {text}", timestamp="This week", status=""))
        if not activity_items:
            activity_items.append(ActivityItem(icon="", text="No recent activity.", timestamp="", status=""))
        self._activity_feed.set_items(activity_items)

        self._muscle_section.clear()
        muscles = tracking.get("muscle_balance", []) if isinstance(tracking, dict) else []
        if muscles:
            for m in muscles[:6]:
                name = m if isinstance(m, str) else m.get("name", str(m))
                vol = m.get("volume", 0) if isinstance(m, dict) else 0
                bar_width = min(200, vol // 10) if vol else 20
                lbl = QLabel(f"  {name}: {'|' * (bar_width // 4)}  {vol}kg")
                lbl.setStyleSheet(f"color: {colors.text_primary}; font-size: 12px; background: transparent; border: none;")
                self._muscle_section.add_content(lbl)
        else:
            lbl = QLabel("No muscle balance data.")
            lbl.setStyleSheet(f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;")
            self._muscle_section.add_content(lbl)

    def _clear_layout(self, layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


def _safe_dict(data: Any, key: str) -> dict:
    if isinstance(data, dict):
        return data.get(key, {})
    return getattr(data, key, {}) if hasattr(data, key) else {}
