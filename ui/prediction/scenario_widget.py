from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from modules.prediction.domain import PredictionResult, ScenarioResult
from modules.prediction.presentation import PredictionFormatter
from ui.dashboard.dashboard_widgets.base_card import DashboardCard


class ScenarioWidget(DashboardCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="SCENARIO COMPARISON", badge="What-If", parent=parent)
        self._container = QVBoxLayout()
        self._container.setContentsMargins(0, 0, 0, 0)
        self._container.setSpacing(6)
        self.add_layout(self._container)
        self._empty = QLabel("No scenario data available")
        self._empty.setStyleSheet("color: #64748B; font-size: 13px;")
        self._container.addWidget(self._empty)

    def update_data(self, result: PredictionResult | None) -> None:
        while self._container.count():
            item = self._container.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        if not result or not result.scenario_results:
            self._container.addWidget(self._empty)
            return

        for sr in result.scenario_results:
            card = self._build_scenario_card(sr)
            self._container.addWidget(card)

    def _build_scenario_card(self, sr: ScenarioResult) -> QWidget:
        card = QWidget()
        card.setStyleSheet("background-color: #0F172A; border-radius: 8px; border: 1px solid #334155;")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        header = QHBoxLayout()
        name = QLabel(sr.intervention.label)
        name.setStyleSheet("color: #F1F5F9; font-size: 13px; font-weight: 600;")
        header.addWidget(name)

        badge_text = "✓ Recommended" if sr.recommended else "Not Recommended"
        badge_color = "#4ADE80" if sr.recommended else "#EF4444"
        badge = QLabel(badge_text)
        badge.setStyleSheet(f"color: {badge_color}; font-size: 11px; font-weight: 600; padding: 1px 6px; border-radius: 4px;")
        header.addWidget(badge)
        header.addStretch()

        risk_badge = QLabel(f"Risk: {sr.risk_level.upper()}")
        risk_badge.setStyleSheet(f"color: {PredictionFormatter.impact_level_color(sr.risk_level)}; font-size: 11px;")
        header.addWidget(risk_badge)
        layout.addLayout(header)

        if sr.comparisons:
            for comp in sr.comparisons[:3]:
                delta_str = f"{comp.delta:+.1f} ({comp.delta_percent:+.1f}%)"
                color = "#4ADE80" if comp.is_positive else "#EF4444"
                row = DashboardCard.make_row(
                    comp.intervention.label,
                    delta_str,
                    value_color=color,
                )
                layout.addWidget(row)

        if sr.overall_assessment:
            assess = QLabel(sr.overall_assessment)
            assess.setStyleSheet("color: #94A3B8; font-size: 12px; font-style: italic; padding-top: 4px;")
            assess.setWordWrap(True)
            layout.addWidget(assess)

        return card
