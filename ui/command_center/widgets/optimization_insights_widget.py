from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.command_center.models import OptimizationInsightData
from ui.command_center.theme import C, Font
from ui.command_center.visualization.confidence_indicator import ConfidenceIndicator
from ui.dashboard.dashboard_widgets.base_card import DashboardCard


class OptimizationInsightsWidget(DashboardCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="Optimization Insights", badge=f"{C.ACCENT}", parent=parent)
        self._build_ui()

    def _build_ui(self) -> None:
        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)
        self._patterns_label = self._make_stat("Patterns")
        self._reliable_label = self._make_stat("Reliable")
        self._avg_conf_label = self._make_stat("Avg Confidence")
        stats_row.addWidget(self._patterns_label)
        stats_row.addWidget(self._reliable_label)
        stats_row.addWidget(self._avg_conf_label)
        stats_row.addStretch()
        self.add_layout(stats_row)

        self._insights_list = QVBoxLayout()
        self._insights_list.setContentsMargins(0, 8, 0, 0)
        self._insights_list.setSpacing(4)
        self.add_layout(self._insights_list)

    def _make_stat(self, label: str) -> QWidget:
        frame = QWidget()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)
        val = QLabel("--")
        val.setStyleSheet(Font.STAT_VALUE)
        layout.addWidget(val)
        lbl = QLabel(label)
        lbl.setStyleSheet(Font.STAT_LABEL)
        layout.addWidget(lbl)
        return frame

    def _set_stat(self, widget: QWidget, value: str) -> None:
        labels = widget.findChildren(QLabel)
        if labels:
            labels[0].setText(value)

    def update_data(self, data: object) -> None:
        optimization = getattr(data, "optimization_insights", None)
        if optimization is not None:
            self.set_data(optimization)

    def set_data(self, data: OptimizationInsightData) -> None:
        self._set_stat(self._patterns_label, str(data.total_patterns))
        self._set_stat(self._reliable_label, str(data.reliable_patterns))
        self._set_stat(self._avg_conf_label, f"{data.avg_confidence:.0%}")

        self._clear_insights()
        for insight in data.insights[:5]:
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 3, 0, 3)
            row_layout.setSpacing(6)

            indicator = ConfidenceIndicator()
            indicator.set_score(insight.get("confidence", 0.0))
            indicator.setFixedSize(36, 36)
            row_layout.addWidget(indicator)

            text = QLabel(insight.get("title", ""))
            text.setStyleSheet(f"color: {C.TEXT_SECONDARY}; font-size: 12px;")
            text.setWordWrap(True)
            row_layout.addWidget(text, 1)
            self._insights_list.addWidget(row)

    def _clear_insights(self) -> None:
        for _i in reversed(range(self._insights_list.count())):
            item = self._insights_list.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
