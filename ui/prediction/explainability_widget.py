from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QProgressBar, QVBoxLayout, QWidget

from modules.prediction.domain import (
    ExplainabilityDetail,
    FactorContribution,
    PredictionResult,
)
from ui.dashboard.dashboard_widgets.base_card import DashboardCard


class ExplainabilityWidget(DashboardCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="PREDICTION EXPLANATION", badge="Top Factors", parent=parent)
        self._container = QVBoxLayout()
        self._container.setContentsMargins(0, 0, 0, 0)
        self._container.setSpacing(6)
        self.add_layout(self._container)
        self._empty = QLabel("No explanation data available")
        self._empty.setStyleSheet("color: #64748B; font-size: 13px;")
        self._container.addWidget(self._empty)

    def update_data(self, result: PredictionResult | None) -> None:
        while self._container.count():
            item = self._container.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        if not result or not result.explainability:
            self._container.addWidget(self._empty)
            return

        for key, detail in result.explainability.items():
            section = self._build_detail_section(key, detail)
            self._container.addWidget(section)

    def _build_detail_section(self, key: str, detail: ExplainabilityDetail) -> QWidget:
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        header = QLabel(f"[{key}]")
        header.setStyleSheet("color: #818CF8; font-size: 11px; font-weight: 600; padding: 2px 0;")
        layout.addWidget(header)

        if detail.factor_contributions:
            for fc in detail.factor_contributions[:6]:
                row = self._build_factor_row(fc)
                layout.addWidget(row)

        if detail.nl_explanation and detail.nl_explanation.short:
            nl = QLabel(detail.nl_explanation.short)
            nl.setStyleSheet("color: #CBD5E1; font-size: 12px; font-style: italic; padding-top: 4px;")
            nl.setWordWrap(True)
            layout.addWidget(nl)

        if detail.nl_explanation and detail.nl_explanation.actionable:
            actionable = QLabel(f"→ {detail.nl_explanation.actionable}")
            actionable.setStyleSheet("color: #4ADE80; font-size: 12px; padding-top: 2px;")
            actionable.setWordWrap(True)
            layout.addWidget(actionable)

        return section

    @staticmethod
    def _build_factor_row(fc: FactorContribution) -> QWidget:
        row = QWidget()
        rl = QHBoxLayout(row)
        rl.setContentsMargins(0, 2, 0, 2)
        rl.setSpacing(8)

        name = QLabel(fc.factor_name)
        name.setFixedWidth(140)
        name.setStyleSheet("color: #64748B; font-size: 12px;")
        rl.addWidget(name)

        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(int(abs(fc.contribution) * 100))
        bar.setTextVisible(False)
        bar.setFixedHeight(8)
        color = "#4ADE80" if fc.direction == "positive" else "#EF4444"
        bar.setStyleSheet(f"""
            QProgressBar {{ background-color: #1E293B; border-radius: 4px; border: none; }}
            QProgressBar::chunk {{ background-color: {color}; border-radius: 4px; }}
        """)
        rl.addWidget(bar, 1)

        val = QLabel(f"{fc.contribution:+.2f}")
        val.setFixedWidth(50)
        val.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: 600;")
        rl.addWidget(val)

        return row
