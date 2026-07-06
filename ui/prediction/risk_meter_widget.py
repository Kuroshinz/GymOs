from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from modules.prediction.domain import PredictionResult, RiskMetrics
from modules.prediction.presentation import PredictionFormatter
from ui.dashboard.dashboard_widgets.base_card import DashboardCard


class RiskMeterWidget(DashboardCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="RISK METER", badge="Metrics", parent=parent)
        self._container = QVBoxLayout()
        self._container.setContentsMargins(0, 0, 0, 0)
        self._container.setSpacing(6)
        self.add_layout(self._container)
        self._empty = QLabel("No risk metrics available")
        self._empty.setStyleSheet("color: #64748B; font-size: 13px;")
        self._container.addWidget(self._empty)

    def update_data(self, result: PredictionResult | None) -> None:
        while self._container.count():
            item = self._container.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        if not result or not result.risk_metrics:
            self._container.addWidget(self._empty)
            return

        for key, rm in result.risk_metrics.items():
            section = self._build_risk_section(key, rm)
            self._container.addWidget(section)

    def _build_risk_section(self, key: str, rm: RiskMetrics) -> QWidget:
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        header = QHBoxLayout()
        label = QLabel(f"[{key}]")
        label.setStyleSheet("color: #818CF8; font-size: 11px; font-weight: 600;")
        header.addWidget(label)
        header.addStretch()

        risk_color = PredictionFormatter.risk_level_color(rm.risk_level)
        risk_badge = QLabel(f"RISK: {rm.risk_level.upper()}")
        risk_badge.setStyleSheet(
            f"color: {risk_color}; font-size: 11px; font-weight: 700; "
            f"background-color: {risk_color}22; border-radius: 4px; padding: 2px 8px;"
        )
        header.addWidget(risk_badge)
        layout.addLayout(header)

        metrics = [
            ("Stability", rm.stability, True),
            ("Sensitivity", rm.sensitivity, False),
            ("Uncertainty", rm.uncertainty, False),
            ("Volatility", rm.volatility, False),
        ]

        for metric_name, metric_value, is_good_high in metrics:
            row = QWidget()
            rl = QHBoxLayout(row)
            rl.setContentsMargins(0, 2, 0, 2)
            rl.setSpacing(8)

            name = QLabel(metric_name)
            name.setFixedWidth(90)
            name.setStyleSheet("color: #64748B; font-size: 12px;")
            rl.addWidget(name)

            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(int(metric_value * 100))
            bar.setTextVisible(False)
            bar.setFixedHeight(8)
            color = "#4ADE80" if (is_good_high and metric_value >= 0.6) or (not is_good_high and metric_value <= 0.4) else "#FBBF24" if metric_value < 0.8 else "#EF4444"
            bar.setStyleSheet(f"""
                QProgressBar {{ background-color: #1E293B; border-radius: 4px; border: none; }}
                QProgressBar::chunk {{ background-color: {color}; border-radius: 4px; }}
            """)
            rl.addWidget(bar, 1)

            val = QLabel(f"{metric_value:.2f}")
            val.setFixedWidth(40)
            val.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: 600;")
            rl.addWidget(val)

            layout.addWidget(row)

        sep = DashboardCard.make_separator()
        layout.addWidget(sep)

        total = QWidget()
        tl = QHBoxLayout(total)
        tl.setContentsMargins(0, 2, 0, 2)

        overall_label = QLabel("Overall Risk")
        overall_label.setStyleSheet("color: #94A3B8; font-size: 13px; font-weight: 600;")
        tl.addWidget(overall_label)

        overall_bar = QProgressBar()
        overall_bar.setRange(0, 100)
        overall_bar.setValue(int(rm.overall_risk_score * 100))
        overall_bar.setTextVisible(False)
        overall_bar.setFixedHeight(12)
        overall_bar.setStyleSheet(f"""
            QProgressBar {{ background-color: #1E293B; border-radius: 6px; border: none; }}
            QProgressBar::chunk {{ background-color: {risk_color}; border-radius: 6px; }}
        """)
        tl.addWidget(overall_bar, 1)

        overall_val = QLabel(f"{rm.overall_risk_score:.0%}")
        overall_val.setStyleSheet(f"color: {risk_color}; font-size: 14px; font-weight: 700;")
        overall_val.setFixedWidth(40)
        tl.addWidget(overall_val)

        layout.addWidget(total)

        if rm.confidence_interval_width > 0:
            ci = QLabel(f"CI Width: {rm.confidence_interval_width:.2f}")
            ci.setStyleSheet("color: #64748B; font-size: 11px; padding-left: 2px;")
            layout.addWidget(ci)

        return section
