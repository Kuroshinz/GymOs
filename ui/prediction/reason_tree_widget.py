from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from modules.prediction.domain import ExplainabilityDetail, PredictionResult
from modules.prediction.presentation import PredictionFormatter
from ui.dashboard.dashboard_widgets.base_card import DashboardCard


class ReasonTreeWidget(DashboardCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="REASON TREE", badge="Inference Chain", parent=parent)
        self._container = QVBoxLayout()
        self._container.setContentsMargins(0, 0, 0, 0)
        self._container.setSpacing(6)
        self.add_layout(self._container)
        self._empty = QLabel("No reason chain data available")
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

        has_chain = False
        for key, detail in result.explainability.items():
            if detail.reason_chain and detail.reason_chain.steps:
                has_chain = True
                section = self._build_chain_section(key, detail)
                self._container.addWidget(section)

        if not has_chain:
            self._container.addWidget(self._empty)

    def _build_chain_section(self, key: str, detail: ExplainabilityDetail) -> QWidget:
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        header = QLabel(f"[{key}]")
        header.setStyleSheet("color: #818CF8; font-size: 11px; font-weight: 600; padding: 2px 0;")
        layout.addWidget(header)

        chain = detail.reason_chain
        for step in chain.steps:
            step_widget = self._build_step(step.step_number, step.premise, step.conclusion, step.confidence_at_step)
            layout.addWidget(step_widget)

        if chain.final_conclusion:
            sep = DashboardCard.make_separator()
            layout.addWidget(sep)
            conclusion = QLabel(f"∴ {chain.final_conclusion}")
            conclusion.setStyleSheet("color: #F1F5F9; font-size: 13px; font-weight: 600; padding-top: 4px;")
            conclusion.setWordWrap(True)
            layout.addWidget(conclusion)

        return section

    @staticmethod
    def _build_step(step_num: int, premise: str, conclusion: str, confidence: float) -> QWidget:
        card = QWidget()
        card.setStyleSheet("background-color: #0F172A; border-radius: 6px; border: 1px solid #334155;")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(2)

        header = QHBoxLayout()
        num = QLabel(f"Step {step_num}")
        num.setStyleSheet("color: #818CF8; font-size: 11px; font-weight: 600;")
        header.addWidget(num)
        header.addStretch()
        conf = QLabel(f"confidence: {confidence:.0%}")
        conf.setStyleSheet(f"color: {PredictionFormatter.impact_level_color('low' if confidence < 0.5 else 'moderate' if confidence < 0.8 else 'high')}; font-size: 11px;")
        header.addWidget(conf)
        layout.addLayout(header)

        if premise:
            p = QLabel(f"Premise: {premise}")
            p.setStyleSheet("color: #94A3B8; font-size: 12px; padding-left: 8px;")
            p.setWordWrap(True)
            layout.addWidget(p)

        if conclusion:
            c = QLabel(f"→ {conclusion}")
            c.setStyleSheet("color: #CBD5E1; font-size: 12px; font-weight: 500; padding-left: 8px;")
            c.setWordWrap(True)
            layout.addWidget(c)

        return card
