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
from ui.design_system.visualization import WeeklyTimeline
from ui.design_system.tokens.radius import RadiusTokens

R = RadiusTokens()



class PlanningPage(QWidget):
    adjust_week_clicked = Signal()
    view_program_clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()
        self._wire_buttons()

    def _wire_buttons(self) -> None:
        self._adjust_btn.clicked.connect(self.adjust_week_clicked.emit)
        self._view_program_btn.clicked.connect(self.view_program_clicked.emit)

    def _colors(self):
        return color_from_scheme(ColorScheme.DARK)

    def _build_ui(self) -> None:
        scroll = ScrollContainer()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        content_layout = scroll._wrapper.layout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self._build_cycle_hero(content_layout)
        self._build_kpi_ribbon(content_layout)
        self._build_volume_chart(content_layout)
        self._build_sessions_grid(content_layout)

        content_layout.addStretch()

    def _build_cycle_hero(self, parent: QVBoxLayout) -> None:
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

        self._hero_title = QLabel("Planning Studio")
        self._hero_title.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 28px; font-weight: 800; "
            f"background: transparent; border: none;"
        )
        text_area.addWidget(self._hero_title)

        self._hero_subtitle = QLabel("Cycle overview, weekly volume, and session planning.")
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

        self._adjust_btn = QPushButton("Adjust Week")
        self._adjust_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.primary};
                color: white;
                border: none;
                border-radius: {R.lg};
                padding: 0 24px;
                font-size: 14px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {colors.primary_hover};
            }}
        """)
        self._adjust_btn.setCursor(Qt.PointingHandCursor)
        actions.addWidget(self._adjust_btn)

        self._view_program_btn = QPushButton("View Program")
        self._view_program_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {colors.text_secondary};
                border: 1px solid {colors.border};
                border-radius: {R.lg};
                padding: 0 20px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                border-color: {colors.primary};
                color: {colors.primary};
            }}
        """)
        self._view_program_btn.setCursor(Qt.PointingHandCursor)
        actions.addWidget(self._view_program_btn)

        top.addLayout(actions)
        layout.addLayout(top)

        progress_row = QHBoxLayout()
        progress_row.setSpacing(16)

        self._cycle_name = QLabel("--")
        self._cycle_name.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 20px; font-weight: 700; "
            f"background: transparent; border: none;"
        )
        progress_row.addWidget(self._cycle_name)

        self._week_progress = QFrame()
        self._week_progress.setFixedHeight(8)
        self._week_progress.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.border};
                border-radius: {R.sm};
                border: none;
            }}
        """)
        self._week_fill = QFrame(self._week_progress)
        self._week_fill.setFixedHeight(8)
        self._week_fill.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.primary};
                border-radius: {R.sm};
                border: none;
            }}
        """)
        self._week_fill.setFixedWidth(0)
        progress_row.addWidget(self._week_progress, 1)

        self._week_label = QLabel("Week 0/0")
        self._week_label.setStyleSheet(
            f"color: {colors.text_secondary}; font-size: 14px; font-weight: 500; "
            f"background: transparent; border: none;"
        )
        progress_row.addWidget(self._week_label)

        layout.addLayout(progress_row)

        self._phase_label = QLabel("")
        self._phase_label.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 13px; "
            f"background: transparent; border: none;"
        )
        layout.addWidget(self._phase_label)

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
            KpiItem(label="Sets/Wk", value="--", unit="", accent=colors.text_primary),
            KpiItem(label="PRs", value="--", unit="", accent=colors.warning),
            KpiItem(label="Deload", value="--", unit="", accent=colors.info),
            KpiItem(label="Recovery", value="--", unit="%", accent=colors.success),
        ]
        self._kpi_strip = KpiStrip(items=kpi_items)
        layout.addWidget(self._kpi_strip)
        parent.addWidget(container)

    def _build_volume_chart(self, parent: QVBoxLayout) -> None:
        colors = self._colors()
        container = QFrame()
        container.setStyleSheet(f"QFrame {{ background-color: {colors.background}; border: none; }}")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(32, 24, 32, 0)
        container_layout.setSpacing(12)

        self._volume_section = SectionPanel(title="Weekly Volume Trend", subtitle="Sets and load progression")
        self._volume_timeline = WeeklyTimeline()
        self._volume_section.add_content(self._volume_timeline)
        container_layout.addWidget(self._volume_section)
        parent.addWidget(container)

    def _build_sessions_grid(self, parent: QVBoxLayout) -> None:
        colors = self._colors()
        container = QFrame()
        container.setStyleSheet(f"QFrame {{ background-color: {colors.background}; border: none; }}")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(32, 16, 32, 32)
        container_layout.setSpacing(16)

        grid = EditorialGrid()
        grid.set_spacing(16)
        container_layout.addWidget(grid)

        self._sessions_section = SectionPanel(title="This Week's Sessions", subtitle="Training log", span=PanelSpan.HALF)
        self._sessions_label = QLabel("No sessions logged.")
        self._sessions_label.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;"
        )
        self._sessions_section.add_content(self._sessions_label)
        grid.add_section(self._sessions_section)

        self._rec_section = SectionPanel(title="Recommendations", subtitle="Program adjustments", span=PanelSpan.HALF)
        self._rec_label = QLabel("No recommendations.")
        self._rec_label.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;"
        )
        self._rec_section.add_content(self._rec_label)
        grid.add_section(self._rec_section)

        parent.addWidget(container)

    def update_data(self, data: Any) -> None:
        colors = self._colors()
        planning = _dict_val(data, "planning")
        meso = planning.get("current_mesocycle", {})
        review = planning.get("weekly_review", {})

        name = meso.get("name", "") or ""
        goal = meso.get("goal", "") or ""
        phase = meso.get("phase", "") or ""
        week = meso.get("week", 0) or 0
        total = meso.get("total_weeks", 0) or 0
        vol_progress = meso.get("volume_progress", 0.0) or 0.0
        deload = meso.get("next_deload_in", 0) or 0

        if name:
            self._cycle_name.setText(name)
            self._week_label.setText(f"Week {week}/{total}")
            bar_width = max(8, int(self._week_progress.width() * (week / max(total, 1))))
            self._week_fill.setFixedWidth(bar_width)
            self._phase_label.setText(f"Phase: {phase}  |  Goal: {goal}")
        else:
            self._cycle_name.setText("No active cycle")
            self._week_label.setText("")

        sessions = review.get("sessions_completed", 0) if review else 0
        total_s = review.get("total_sessions", 0) if review else 0
        prs = review.get("prs_set", 0) if review else 0

        kpi_items = [
            KpiItem(label="Volume", value=f"{vol_progress:.0f}", unit="kg", accent=colors.primary),
            KpiItem(label="Sets/Wk", value=f"{review.get('total_volume', 0) / 7:.0f}" if review else "--", unit="", accent=colors.text_primary),
            KpiItem(label="PRs", value=str(prs), unit="", accent=colors.warning),
            KpiItem(label="Deload", value=f"W{week + deload}" if deload else "--", unit="", accent=colors.info),
            KpiItem(label="Recovery", value=f"{review.get('recovery_avg', 0):.0f}" if review else "--", unit="%", accent=colors.success),
        ]
        self._kpi_strip.set_items(kpi_items)

        vol_data = planning.get("volume_data", [])
        if not vol_data and review:
            vol_data = [review.get("total_volume", 0) / 7] * 7
        self._volume_timeline.set_data(
            vol_data if vol_data else [0, 0, 0, 0, 0, 0, 0],
            max_value=max(vol_data) if vol_data else 100.0,
        )

        self._sessions_section.clear()
        if sessions:
            lbl = QLabel(f"Completed: {sessions}/{total_s} sessions")
            lbl.setStyleSheet(f"color: {colors.text_primary}; font-size: 14px; font-weight: 600; background: transparent; border: none;")
            self._sessions_section.add_content(lbl)
            if review.get("notes"):
                for note in review["notes"][:3]:
                    n = QLabel(f"  {note}")
                    n.setStyleSheet(f"color: {colors.text_secondary}; font-size: 12px; background: transparent; border: none;")
                    self._sessions_section.add_content(n)
        else:
            lbl = QLabel("No sessions logged this week.")
            lbl.setStyleSheet(f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;")
            self._sessions_section.add_content(lbl)

        self._rec_section.clear()
        recs = planning.get("recommendations", [])
        if recs:
            for r in recs[:3]:
                text = r if isinstance(r, str) else r.get("message", str(r))
                lbl = QLabel(f"  {text}")
                lbl.setStyleSheet(f"color: {colors.text_primary}; font-size: 13px; background: transparent; border: none;")
                lbl.setWordWrap(True)
                self._rec_section.add_content(lbl)
        else:
            lbl = QLabel("No recommendations.")
            lbl.setStyleSheet(f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;")
            self._rec_section.add_content(lbl)


def _dict_val(data: Any, key: str) -> dict:
    val = getattr(data, key, {})
    return val if isinstance(val, dict) else {}
