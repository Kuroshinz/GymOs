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
from ui.design_system.visualization import ConfidenceGauge, PredictionTimeline, RiskMeter
from ui.design_system.tokens.radius import RadiusTokens

R = RadiusTokens()



class PredictionCenterPage(QWidget):
    run_scenario_clicked = Signal()
    export_report_clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()
        self._wire_buttons()

    def _wire_buttons(self) -> None:
        self._scenario_btn.clicked.connect(self.run_scenario_clicked.emit)
        self._export_btn.clicked.connect(self.export_report_clicked.emit)

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

        self._build_confidence_hero(content_layout)
        self._build_kpi_ribbon(content_layout)
        self._build_timeline(content_layout)
        self._build_scenario_grid(content_layout)

        content_layout.addStretch()

    def _build_confidence_hero(self, parent: QVBoxLayout) -> None:
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

        self._hero_title = QLabel("Forecast Studio")
        self._hero_title.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 28px; font-weight: 800; "
            f"background: transparent; border: none;"
        )
        text_area.addWidget(self._hero_title)

        self._hero_subtitle = QLabel("Forecasts, trends, projections, and confidence assessment.")
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

        self._scenario_btn = QPushButton("Run Scenario")
        self._scenario_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.info};
                color: white;
                border: none;
                border-radius: {R.lg};
                padding: 0 24px;
                font-size: 14px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {colors.info_hover};
            }}
        """)
        self._scenario_btn.setCursor(Qt.PointingHandCursor)
        actions.addWidget(self._scenario_btn)

        self._export_btn = QPushButton("Export Report")
        self._export_btn.setStyleSheet(f"""
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
                border-color: {colors.info};
                color: {colors.info};
            }}
        """)
        self._export_btn.setCursor(Qt.PointingHandCursor)
        actions.addWidget(self._export_btn)

        top.addLayout(actions)
        layout.addLayout(top)

        confidence_row = QHBoxLayout()
        confidence_row.setSpacing(24)

        self._hero_gauge = ConfidenceGauge(width=240, height=36)
        self._hero_gauge.set_confidence(0.0, "Forecast Confidence")
        confidence_row.addWidget(self._hero_gauge)

        self._hero_risk = RiskMeter(width=140, height=24)
        self._hero_risk.set_risk(0.0, "Overall Risk")
        confidence_row.addWidget(self._hero_risk)

        confidence_row.addStretch()

        self._conf_label = QLabel("Forecast Confidence: --")
        self._conf_label.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 16px; font-weight: 600; "
            f"background: transparent; border: none;"
        )
        confidence_row.addWidget(self._conf_label)

        layout.addLayout(confidence_row)
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
            KpiItem(label="PR", value="--", unit="kg", accent=colors.warning),
            KpiItem(label="Volume", value="--", unit="kg", accent=colors.primary),
            KpiItem(label="Weight", value="--", unit="kg", accent=colors.info),
            KpiItem(label="Recovery", value="--", unit="%", accent=colors.success),
            KpiItem(label="Adherence", value="--", unit="%", accent=colors.accent),
            KpiItem(label="Risk", value="--", unit="", accent=colors.warning),
            KpiItem(label="Lower", value="--", unit="kg", accent=colors.text_disabled),
            KpiItem(label="Upper", value="--", unit="kg", accent=colors.text_primary),
            KpiItem(label="Trend", value="--", unit="", accent=colors.success),
        ]
        self._kpi_strip = KpiStrip(items=kpi_items)
        layout.addWidget(self._kpi_strip)
        parent.addWidget(container)

    def _build_timeline(self, parent: QVBoxLayout) -> None:
        colors = self._colors()
        container = QFrame()
        container.setStyleSheet(f"QFrame {{ background-color: {colors.background}; border: none; }}")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(32, 24, 32, 0)
        container_layout.setSpacing(12)

        self._timeline_section = SectionPanel(title="Prediction Timeline", subtitle="Projected trends over time")
        self._prediction_timeline = PredictionTimeline()
        self._timeline_section.add_content(self._prediction_timeline)
        container_layout.addWidget(self._timeline_section)
        parent.addWidget(container)

    def _build_scenario_grid(self, parent: QVBoxLayout) -> None:
        colors = self._colors()
        container = QFrame()
        container.setStyleSheet(f"QFrame {{ background-color: {colors.background}; border: none; }}")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(32, 16, 32, 32)
        container_layout.setSpacing(16)

        grid = EditorialGrid()
        grid.set_spacing(16)
        container_layout.addWidget(grid)

        self._scenario_section = SectionPanel(title="Scenarios", subtitle="What-if analysis", span=PanelSpan.HALF)
        self._scenario_label = QLabel("No scenarios available.")
        self._scenario_label.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;"
        )
        self._scenario_section.add_content(self._scenario_label)
        grid.add_section(self._scenario_section)

        self._risk_section = SectionPanel(title="Risk Assessment", subtitle="Identified risks", span=PanelSpan.HALF)
        self._risk_label = QLabel("No risks identified.")
        self._risk_label.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;"
        )
        self._risk_section.add_content(self._risk_label)
        grid.add_section(self._risk_section)

        parent.addWidget(container)

    def update_data(self, data: Any) -> None:
        colors = self._colors()
        prediction = _dict_val(data, "prediction")
        pred_data = prediction.get("prediction_summary", {})

        predictions = pred_data.get("predictions", [])
        points = []
        for i, p in enumerate(predictions[:7]):
            if isinstance(p, dict):
                label = p.get("label", f"P{i+1}")
                val = p.get("value", 0.0) or 0.0
                date = p.get("date", label)
                points.append((date, label, val))
            else:
                points.append((f"P{i+1}", str(p), float(p) if isinstance(p, (int, float)) else 0.0))

        if points:
            self._prediction_timeline.set_data(points)

        acc = pred_data.get("accuracy", 0.0) or 0.0
        trend = pred_data.get("trend", "stable") or "stable"
        risk = 0.5
        if trend in ("declining", "down"):
            risk = 0.7
        elif trend in ("improving", "up"):
            risk = 0.3

        self._hero_risk.set_risk(risk, "Risk Outlook")
        self._hero_gauge.set_confidence(acc / 100 if acc > 1 else acc, "Forecast Accuracy")
        self._conf_label.setText(f"Forecast Confidence: {acc:.1f}%  |  Trend: {trend.capitalize()}")

        kpi_items = [
            KpiItem(label="PR", value=f"{pred_data.get('pr_forecast', 0):.0f}", unit="kg", accent=colors.warning),
            KpiItem(label="Volume", value=f"{pred_data.get('volume_forecast', 0):.0f}", unit="kg", accent=colors.primary),
            KpiItem(label="Weight", value="--", unit="kg", accent=colors.info),
            KpiItem(label="Recovery", value=f"{pred_data.get('recovery_forecast', 0):.0f}", unit="%", accent=colors.success),
            KpiItem(label="Adherence", value=f"{pred_data.get('adherence_forecast', 0):.0f}", unit="%", accent=colors.accent),
            KpiItem(label="Risk", value=trend.capitalize(), unit="", accent=colors.warning),
            KpiItem(label="Lower", value=f"{pred_data.get('lower_bound', 0):.1f}", unit="kg", accent=colors.text_disabled),
            KpiItem(label="Upper", value=f"{pred_data.get('upper_bound', 0):.1f}", unit="kg", accent=colors.text_primary),
            KpiItem(label="Trend", value=trend.upper(), unit="", accent=colors.success),
        ]
        self._kpi_strip.set_items(kpi_items)

        scenarios = pred_data.get("scenarios", [])
        self._scenario_section.clear()
        if scenarios:
            for s in scenarios[:3]:
                text = s if isinstance(s, str) else s.get("name", str(s))
                lbl = QLabel(f"  {text}")
                lbl.setStyleSheet(f"color: {colors.text_primary}; font-size: 13px; background: transparent; border: none;")
                self._scenario_section.add_content(lbl)
        else:
            lbl = QLabel("No scenarios available.")
            lbl.setStyleSheet(f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;")
            self._scenario_section.add_content(lbl)

        risks = pred_data.get("risks", [])
        self._risk_section.clear()
        if risks:
            for r in risks[:3]:
                text = r if isinstance(r, str) else r.get("description", str(r))
                level = r.get("level", "low") if isinstance(r, dict) else "low"
                lbl = QLabel(f"  [{level.upper()}] {text}")
                lbl.setStyleSheet(f"color: {colors.warning if level in ('high', 'medium') else colors.text_primary}; font-size: 13px; background: transparent; border: none;")
                self._risk_section.add_content(lbl)
        else:
            lbl = QLabel("No risks identified.")
            lbl.setStyleSheet(f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;")
            self._risk_section.add_content(lbl)


def _dict_val(data: Any, key: str) -> dict:
    val = getattr(data, key, {})
    return val if isinstance(val, dict) else {}
