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
from ui.design_system.visualization import ConfidenceGauge


class AdaptiveCenterPage(QWidget):
    review_decision_clicked = Signal()
    run_simulation_clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()
        self._wire_buttons()

    def _wire_buttons(self) -> None:
        self._review_btn.clicked.connect(self.review_decision_clicked.emit)
        self._simulate_btn.clicked.connect(self.run_simulation_clicked.emit)

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

        self._build_flow_hero(content_layout)
        self._build_kpi_ribbon(content_layout)
        self._build_decision_timeline(content_layout)
        self._build_bottom_grid(content_layout)

        content_layout.addStretch()

    def _build_flow_hero(self, parent: QVBoxLayout) -> None:
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

        self._hero_title = QLabel("Optimization Center")
        self._hero_title.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 28px; font-weight: 800; "
            f"background: transparent; border: none;"
        )
        text_area.addWidget(self._hero_title)

        self._hero_subtitle = QLabel("Track adaptations, decisions, and strategy evolution over time.")
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

        self._review_btn = QPushButton("Review Decision")
        self._review_btn.setStyleSheet(f"""
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
        self._review_btn.setCursor(Qt.PointingHandCursor)
        actions.addWidget(self._review_btn)

        self._simulate_btn = QPushButton("Run Simulation")
        self._simulate_btn.setStyleSheet(f"""
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
        self._simulate_btn.setCursor(Qt.PointingHandCursor)
        actions.addWidget(self._simulate_btn)

        top.addLayout(actions)
        layout.addLayout(top)

        flow_row = QHBoxLayout()
        flow_row.setSpacing(24)

        self._hero_gauge = ConfidenceGauge(width=200, height=30)
        self._hero_gauge.set_confidence(0.0, "Optimization Score")
        flow_row.addWidget(self._hero_gauge)

        self._flow_label = QLabel("Adaptation Flow: --")
        self._flow_label.setStyleSheet(
            f"color: {colors.text_secondary}; font-size: 14px; font-weight: 500; "
            f"background: transparent; border: none;"
        )
        flow_row.addWidget(self._flow_label)

        flow_row.addStretch()

        self._score_label = QLabel("Optimization: --")
        self._score_label.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 18px; font-weight: 700; "
            f"background: transparent; border: none;"
        )
        flow_row.addWidget(self._score_label)

        layout.addLayout(flow_row)
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
            KpiItem(label="Adaptations", value="--", unit="", accent=colors.success),
            KpiItem(label="Decisions", value="--", unit="", accent=colors.primary),
            KpiItem(label="Confidence", value="--", unit="%", accent=colors.accent),
            KpiItem(label="Impacts", value="--", unit="", accent=colors.info),
            KpiItem(label="Rollback", value="--", unit="%", accent=colors.warning),
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

        self._decision_section = SectionPanel(title="Decision Timeline", subtitle="Recent decisions and outcomes")

        self._decision_widget = QWidget()
        self._decision_layout = QVBoxLayout(self._decision_widget)
        self._decision_layout.setContentsMargins(0, 0, 0, 0)
        self._decision_layout.setSpacing(6)
        no_data = QLabel("No decisions recorded.")
        no_data.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;"
        )
        self._decision_layout.addWidget(no_data)
        self._decision_section.add_content(self._decision_widget)
        container_layout.addWidget(self._decision_section)
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

        self._strategy_section = SectionPanel(title="Strategy Summary", subtitle="Current optimization strategy", span=PanelSpan.HALF)
        self._strategy_label = QLabel("No strategy data.")
        self._strategy_label.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;"
        )
        self._strategy_section.add_content(self._strategy_label)
        grid.add_section(self._strategy_section)

        self._rec_section = SectionPanel(title="Recommendations", subtitle="Suggested optimizations", span=PanelSpan.HALF)
        self._rec_label = QLabel("No recommendations.")
        self._rec_label.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;"
        )
        self._rec_section.add_content(self._rec_label)
        grid.add_section(self._rec_section)

        parent.addWidget(container)

    def update_data(self, data: Any) -> None:
        colors = self._colors()
        adaptive = _dict_val(data, "adaptive")

        timeline = adaptive.get("adaptive_timeline_items", [])
        decisions = adaptive.get("decision_timeline_items", [])

        adaptations_count = len(timeline)
        decisions_count = len(decisions)

        avg_conf = 0.0
        if decisions:
            confs = [d.get("confidence", 0.0) for d in decisions if isinstance(d, dict)]
            avg_conf = sum(confs) / len(confs) if confs else 0.0

        impacts = sum(1 for d in decisions if isinstance(d, dict) and d.get("impact", 0) > 0) if decisions else 0
        rollbacks = sum(1 for d in decisions if isinstance(d, dict) and d.get("outcome", "") == "rollback") if decisions else 0
        rollback_pct = (rollbacks / decisions_count * 100) if decisions_count else 0

        kpi_items = [
            KpiItem(label="Adaptations", value=str(adaptations_count), unit="", accent=colors.success),
            KpiItem(label="Decisions", value=str(decisions_count), unit="", accent=colors.primary),
            KpiItem(label="Confidence", value=f"{avg_conf:.0f}", unit="%", accent=colors.accent),
            KpiItem(label="Impacts", value=str(impacts), unit="", accent=colors.info),
            KpiItem(label="Rollback", value=f"{rollback_pct:.0f}", unit="%", accent=colors.warning),
        ]
        self._kpi_strip.set_items(kpi_items)

        self._hero_gauge.set_confidence(avg_conf / 100 if avg_conf > 1 else avg_conf, "Decision Confidence")
        self._score_label.setText(f"Optimization: {avg_conf:.0f}%")
        flow_parts = []
        if timeline:
            for item in timeline[:3]:
                text = item if isinstance(item, str) else item.get("adaptation_type", str(item))
                flow_parts.append(text)
        self._flow_label.setText(f"Adaptation Flow: {' > '.join(flow_parts) if flow_parts else '--'}")

        self._decision_layout = self._decision_widget.layout()
        self._clear_layout(self._decision_layout)
        if decisions:
            for dec in decisions[:6]:
                text = dec if isinstance(dec, str) else dec.get("decision_type", str(dec))
                outcome = dec.get("outcome", "") if isinstance(dec, dict) else ""
                icon = ""
                outcome_str = f"  [{outcome}]" if outcome else ""
                lbl = QLabel(f"  {icon}  {text}{outcome_str}")
                lbl.setStyleSheet(f"color: {colors.text_primary}; font-size: 13px; background: transparent; border: none;")
                self._decision_layout.addWidget(lbl)
        else:
            no_data = QLabel("No decisions recorded.")
            no_data.setStyleSheet(f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;")
            self._decision_layout.addWidget(no_data)

        self._strategy_section.clear()
        strategies = adaptive.get("strategies", [])
        if strategies:
            for s in strategies[:3]:
                text = s if isinstance(s, str) else s.get("name", str(s))
                lbl = QLabel(f"  {text}")
                lbl.setStyleSheet(f"color: {colors.text_primary}; font-size: 13px; background: transparent; border: none;")
                self._strategy_section.add_content(lbl)
        else:
            lbl = QLabel("No strategy data.")
            lbl.setStyleSheet(f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;")
            self._strategy_section.add_content(lbl)

        recs = adaptive.get("recommendations", [])
        self._rec_section.clear()
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

    def _clear_layout(self, layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


def _dict_val(data: Any, key: str) -> dict:
    val = getattr(data, key, {})
    return val if isinstance(val, dict) else {}
