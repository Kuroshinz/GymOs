from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ui.design_system.layout import (
    EditorialGrid,
    PanelSpan,
    ScrollContainer,
    SectionPanel,
)
from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.visualization import WeeklyTimeline


class RecoveryCenterPage(QWidget):
    view_details_clicked = Signal()
    view_trends_clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()
        self._wire_buttons()

    def _wire_buttons(self) -> None:
        self._detail_btn.clicked.connect(self.view_details_clicked.emit)
        self._trends_btn.clicked.connect(self.view_trends_clicked.emit)

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

        self._build_score_monument(content_layout)
        self._build_vitals_row(content_layout)
        self._build_trend_chart(content_layout)
        self._build_bottom_grid(content_layout)

        content_layout.addStretch()

    def _build_score_monument(self, parent: QVBoxLayout) -> None:
        colors = self._colors()
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.surface};
                border-bottom: 1px solid {colors.border};
            }}
        """)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(32)

        score_frame = QVBoxLayout()
        score_frame.setSpacing(8)
        score_frame.setAlignment(Qt.AlignCenter)

        self._score_value = QLabel("--")
        self._score_value.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 64px; font-weight: 800; "
            f"background: transparent; border: none;"
        )
        self._score_value.setAlignment(Qt.AlignCenter)
        score_frame.addWidget(self._score_value)

        self._score_label = QLabel("RECOVERY SCORE")
        self._score_label.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 14px; font-weight: 600; letter-spacing: 3px; "
            f"background: transparent; border: none;"
        )
        self._score_label.setAlignment(Qt.AlignCenter)
        score_frame.addWidget(self._score_label)

        self._score_bar = QFrame()
        self._score_bar.setFixedHeight(6)
        self._score_bar.setFixedWidth(200)
        self._score_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.border};
                border-radius: 3px;
                border: none;
            }}
        """)
        self._score_fill = QFrame(self._score_bar)
        self._score_fill.setFixedHeight(6)
        self._score_fill.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.warning};
                border-radius: 3px;
                border: none;
            }}
        """)
        self._score_fill.setFixedWidth(0)

        bar_container = QHBoxLayout()
        bar_container.addStretch()
        bar_container.addWidget(self._score_bar)
        bar_container.addStretch()
        score_frame.addLayout(bar_container)

        layout.addLayout(score_frame, 1)

        right_area = QVBoxLayout()
        right_area.setSpacing(16)

        text_area = QVBoxLayout()
        text_area.setSpacing(4)

        self._hero_title = QLabel("Recovery Center")
        self._hero_title.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 24px; font-weight: 700; "
            f"background: transparent; border: none;"
        )
        text_area.addWidget(self._hero_title)

        self._hero_subtitle = QLabel("Recovery score, readiness, sleep, stress, and fatigue monitoring.")
        self._hero_subtitle.setStyleSheet(
            f"color: {colors.text_secondary}; font-size: 14px; "
            f"background: transparent; border: none;"
        )
        self._hero_subtitle.setWordWrap(True)
        text_area.addWidget(self._hero_subtitle)
        right_area.addLayout(text_area)

        right_area.addStretch()

        actions = QHBoxLayout()
        actions.setSpacing(12)

        self._detail_btn = QPushButton("View Details")
        self._detail_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.warning};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {colors.warning_hover};
            }}
        """)
        self._detail_btn.setCursor(Qt.PointingHandCursor)
        actions.addWidget(self._detail_btn)

        self._trends_btn = QPushButton("View Trends")
        self._trends_btn.setStyleSheet(f"""
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
                border-color: {colors.warning};
                color: {colors.warning};
            }}
        """)
        self._trends_btn.setCursor(Qt.PointingHandCursor)
        actions.addWidget(self._trends_btn)

        right_area.addLayout(actions)
        layout.addLayout(right_area, 1)

        parent.addWidget(container)

    def _build_vitals_row(self, parent: QVBoxLayout) -> None:
        colors = self._colors()
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.background};
                border-bottom: 1px solid {colors.border};
            }}
        """)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(32, 20, 32, 20)
        layout.setSpacing(16)

        for label, key, bar_color in [("Sleep", "sleep", colors.info), ("Stress", "stress", colors.success), ("Fatigue", "fatigue", colors.warning)]:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {colors.surface};
                    border-radius: 8px;
                    border: 1px solid {colors.border};
                }}
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(16, 14, 16, 14)
            card_layout.setSpacing(8)

            lbl = QLabel(label)
            lbl.setStyleSheet(f"color: {colors.text_disabled}; font-size: 11px; font-weight: 600; background: transparent; border: none; letter-spacing: 1px;")
            card_layout.addWidget(lbl)

            val = QLabel("--")
            val.setStyleSheet(f"color: {colors.text_primary}; font-size: 32px; font-weight: 800; background: transparent; border: none;")
            card_layout.addWidget(val)

            bar = QFrame()
            bar.setFixedHeight(4)
            bar.setStyleSheet(f"""
                QFrame {{
                    background-color: {colors.border};
                    border-radius: 2px;
                    border: none;
                }}
            """)
            fill = QFrame(bar)
            fill.setFixedHeight(4)
            fill.setStyleSheet(f"background-color: {bar_color}; border-radius: 2px; border: none;")
            fill.setFixedWidth(0)
            card_layout.addWidget(bar)

            meta = QLabel("")
            meta.setStyleSheet(f"color: {colors.text_disabled}; font-size: 11px; background: transparent; border: none;")
            card_layout.addWidget(meta)

            setattr(self, f"_vital_{key}_card", card)
            setattr(self, f"_vital_{key}_value", val)
            setattr(self, f"_vital_{key}_bar", bar)
            setattr(self, f"_vital_{key}_fill", fill)
            setattr(self, f"_vital_{key}_meta", meta)

            layout.addWidget(card, 1)

        parent.addWidget(container)

    def _build_trend_chart(self, parent: QVBoxLayout) -> None:
        colors = self._colors()
        container = QFrame()
        container.setStyleSheet(f"QFrame {{ background-color: {colors.background}; border: none; }}")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(32, 24, 32, 0)
        container_layout.setSpacing(12)

        self._trend_section = SectionPanel(title="7-Day Recovery Trend", subtitle="Daily recovery score pattern")
        self._recovery_timeline = WeeklyTimeline()
        self._trend_section.add_content(self._recovery_timeline)
        container_layout.addWidget(self._trend_section)
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

        self._readiness_section = SectionPanel(title="Readiness Detail", subtitle="Preparedness & limiting factors", span=PanelSpan.HALF)
        self._readiness_label = QLabel("No readiness data.")
        self._readiness_label.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;"
        )
        self._readiness_section.add_content(self._readiness_label)
        grid.add_section(self._readiness_section)

        self._warning_section = SectionPanel(title="Warnings & Flags", subtitle="Items needing attention", span=PanelSpan.HALF)
        self._warning_label = QLabel("No warnings.")
        self._warning_label.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;"
        )
        self._warning_section.add_content(self._warning_label)
        grid.add_section(self._warning_section)

        parent.addWidget(container)

    def update_data(self, data: Any) -> None:
        colors = self._colors()
        recovery = _dict_val(data, "recovery")
        mission = _dict_val(data, "mission")

        recovery_data = recovery.get("recovery_overview", {})
        score = recovery_data.get("score", 0.0) or 0.0
        level = recovery_data.get("level", "") or ""
        trend = recovery_data.get("trend", "stable") or ""

        self._score_value.setText(f"{score:.0f}")
        self._score_label.setText(f"{level.upper()} RECOVERY" if level else "RECOVERY SCORE")
        bar_width = max(4, int(self._score_bar.width() * min(score, 100) / 100))
        self._score_fill.setFixedWidth(bar_width)

        bar_color = colors.success if score >= 70 else colors.warning if score >= 40 else colors.error
        self._score_fill.setStyleSheet(f"background-color: {bar_color}; border-radius: 3px; border: none;")

        sleep = recovery_data.get("sleep_score", 0.0) or 0.0
        stress = recovery_data.get("stress_score", 0.0) or 0.0
        fatigue = recovery_data.get("fatigue_score", 0.0) or 0.0

        for key, val, color in [("sleep", sleep, colors.info), ("stress", stress, colors.success), ("fatigue", fatigue, colors.warning)]:
            fill = getattr(self, f"_vital_{key}_fill", None)
            val_label = getattr(self, f"_vital_{key}_value", None)
            if fill:
                bw = max(4, int(fill.parentWidget().width() * min(val, 100) / 100)) if fill.parentWidget() else 0
                fill.setFixedWidth(bw)
            if val_label:
                val_label.setText(f"{val:.0f}")

        self._recovery_timeline.set_data([0, 0, 0, 0, 0, 0, 0])

        readiness_data = recovery.get("training_readiness", {}) or mission.get("training_readiness", {})
        self._readiness_section.clear()
        if readiness_data:
            r_score = readiness_data.get("score", 0.0) or 0.0
            r_level = readiness_data.get("readiness", "") or ""
            limiting = readiness_data.get("limiting_factor", "") or ""
            lbl1 = QLabel(f"Score: {r_score:.0f}  |  Level: {r_level.capitalize()}")
            lbl1.setStyleSheet(f"color: {colors.text_primary}; font-size: 16px; font-weight: 700; background: transparent; border: none;")
            self._readiness_section.add_content(lbl1)
            if limiting:
                lbl2 = QLabel(f"Limiting factor: {limiting}")
                lbl2.setStyleSheet(f"color: {colors.warning}; font-size: 13px; background: transparent; border: none;")
                self._readiness_section.add_content(lbl2)
        else:
            lbl = QLabel("No readiness data.")
            lbl.setStyleSheet(f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;")
            self._readiness_section.add_content(lbl)

        flags = recovery_data.get("flags", [])
        self._warning_section.clear()
        if flags:
            for f in flags[:4]:
                text = f if isinstance(f, str) else f.get("message", str(f))
                lbl = QLabel(f"  {text}")
                lbl.setStyleSheet(f"color: {colors.warning}; font-size: 13px; background: transparent; border: none;")
                self._warning_section.add_content(lbl)
        else:
            lbl = QLabel("No warnings.")
            lbl.setStyleSheet(f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;")
            self._warning_section.add_content(lbl)


def _dict_val(data: Any, key: str) -> dict:
    val = getattr(data, key, {})
    return val if isinstance(val, dict) else {}
