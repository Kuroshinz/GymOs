from __future__ import annotations

from dataclasses import dataclass, field

from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from modules.prediction.domain import (
    PredictionResult,
)
from modules.prediction.presentation import (
    PredictionViewModel,
)
from ui.prediction.confidence_breakdown_widget import ConfidenceBreakdownWidget
from ui.prediction.explainability_widget import ExplainabilityWidget
from ui.prediction.reason_tree_widget import ReasonTreeWidget
from ui.prediction.risk_meter_widget import RiskMeterWidget
from ui.prediction.scenario_widget import ScenarioWidget


@dataclass
class PredictionDashboardData:
    view_model: PredictionViewModel = field(default_factory=PredictionViewModel)
    has_data: bool = False
    result: PredictionResult | None = None


class PredictionCard(QFrame):
    def __init__(self, title: str, value: str, probability: str,
                 confidence: str, trend: str, color: str, parent=None) -> None:
        super().__init__(parent)
        self.setFixedSize(260, 140)
        self.setStyleSheet("""
            PredictionCard {
                background-color: #1E293B; border-radius: 12px;
                border: 1px solid #334155; padding: 12px;
            }
            PredictionCard:hover { border-color: #818CF8; }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        header = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: 600; text-transform: uppercase;")
        header.addWidget(title_label)
        header.addStretch()
        trend_label = QLabel(trend)
        trend_label.setStyleSheet(f"color: {color}; font-size: 13px;")
        header.addWidget(trend_label)
        layout.addLayout(header)

        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {color}; font-size: 26px; font-weight: 700;")
        layout.addWidget(value_label)

        prob_label = QLabel(probability)
        prob_label.setStyleSheet("color: #CBD5E1; font-size: 13px;")
        layout.addWidget(prob_label)

        conf_label = QLabel(confidence)
        conf_label.setStyleSheet("color: #64748B; font-size: 11px;")
        layout.addWidget(conf_label)


class PredictionDashboard(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._data: PredictionDashboardData | None = None

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        inner = QWidget()
        inner.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title = QLabel("Predictive Intelligence")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #F1F5F9;")
        layout.addWidget(title)

        subtitle = QLabel("Predict your progress, manage risk, and explore what-if scenarios")
        subtitle.setStyleSheet("color: #94A3B8; font-size: 12px; margin-bottom: 8px;")
        layout.addWidget(subtitle)

        self._card_layout = QGridLayout()
        self._card_layout.setSpacing(12)
        layout.addLayout(self._card_layout)

        self._scenario_widget = ScenarioWidget()
        self._explainability_widget = ExplainabilityWidget()
        self._reason_tree_widget = ReasonTreeWidget()
        self._confidence_widget = ConfidenceBreakdownWidget()
        self._risk_widget = RiskMeterWidget()

        self._new_widgets_row1 = QHBoxLayout()
        self._new_widgets_row1.setSpacing(12)
        self._new_widgets_row1.addWidget(self._scenario_widget, 2)
        self._new_widgets_row1.addWidget(self._risk_widget, 1)
        layout.addLayout(self._new_widgets_row1)

        self._new_widgets_row2 = QHBoxLayout()
        self._new_widgets_row2.setSpacing(12)
        self._new_widgets_row2.addWidget(self._explainability_widget, 1)
        self._new_widgets_row2.addWidget(self._confidence_widget, 1)
        layout.addLayout(self._new_widgets_row2)

        self._new_widgets_row3 = QHBoxLayout()
        self._new_widgets_row3.setSpacing(12)
        self._new_widgets_row3.addWidget(self._reason_tree_widget)
        layout.addLayout(self._new_widgets_row3)

        scroll.setWidget(inner)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)

    def refresh(self, data: PredictionDashboardData | None = None) -> None:
        if data is not None:
            self._data = data
        if self._data is None:
            return
        vm = self._data.view_model
        result = self._data.result
        self._clear_cards()

        cards_data = [
            ("PR Probability", vm.pr_prediction),
            ("Plateau Risk", vm.plateau_prediction),
            ("Recovery Forecast", vm.recovery_forecast),
            ("Bodyweight Trend", vm.bodyweight_forecast),
            ("Goal ETA", vm.goal_eta),
            ("MRV Risk", vm.mrv_risk),
            ("Deload Risk", vm.deload_probability),
            ("Consistency", vm.consistency_forecast),
        ]

        for i, (title, widget_data) in enumerate(cards_data):
            if widget_data.has_data:
                card = PredictionCard(
                    title=title,
                    value=widget_data.value,
                    probability=f"Probability: {widget_data.probability}",
                    confidence=widget_data.confidence,
                    trend=widget_data.trend_direction,
                    color=widget_data.score_color,
                )
                self._card_layout.addWidget(card, i // 4, i % 4)

        self._scenario_widget.update_data(result)
        self._risk_widget.update_data(result)
        self._explainability_widget.update_data(result)
        self._confidence_widget.update_data(result)
        self._reason_tree_widget.update_data(result)

    def _clear_cards(self) -> None:
        while self._card_layout.count():
            item = self._card_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
