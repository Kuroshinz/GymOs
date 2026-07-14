from __future__ import annotations

from PySide6.QtWidgets import QGridLayout, QLabel, QWidget

from ui.command_center.models import PredictionSummaryData
from ui.command_center.theme import C, Font
from ui.command_center.visualization.prediction_card import PredictionCard
from ui.dashboard.dashboard_widgets.base_card import DashboardCard


class PredictionSummaryWidget(DashboardCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="Prediction Summary", parent=parent)
        self._grid = QGridLayout()
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setSpacing(8)
        self._cards: list[PredictionCard] = []
        for _ in range(4):
            card = PredictionCard()
            self._cards.append(card)
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for card, (r, c) in zip(self._cards, positions, strict=True):
            self._grid.addWidget(card, r, c)
        self.add_layout(self._grid)

        self._accuracy_label = QLabel("")
        self._accuracy_label.setStyleSheet(Font.CAPTION)
        self.add_content(self._accuracy_label)

    def update_data(self, data: object) -> None:
        pred = getattr(data, "prediction_summary", None)
        if pred is not None:
            self.set_data(pred)

    def set_data(self, data: PredictionSummaryData) -> None:
        for i, pred in enumerate(data.predictions[:4]):
            if i < len(self._cards):
                self._cards[i].set_data(
                    value=pred.get("value", "--"),
                    probability=pred.get("probability", ""),
                    confidence=pred.get("confidence", ""),
                    trend=pred.get("trend", ""),
                    color=pred.get("color", C.ACCENT),
                )

        accuracy_text = f"Overall Accuracy: {data.accuracy:.0%} · Trend: {data.trend}"
        self._accuracy_label.setText(accuracy_text)
