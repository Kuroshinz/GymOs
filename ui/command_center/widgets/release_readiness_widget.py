from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.command_center.models import ReleaseReadinessData
from ui.command_center.theme import C, Font
from ui.command_center.visualization.confidence_indicator import ConfidenceBar
from ui.dashboard.dashboard_widgets.base_card import DashboardCard


class ReleaseReadinessWidget(DashboardCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="Release Readiness", parent=parent)
        self._build_ui()

    def _build_ui(self) -> None:
        row = QHBoxLayout()
        row.setSpacing(16)
        self._version_label = QLabel("--")
        self._version_label.setStyleSheet("font-size: 28px; font-weight: 700;")
        row.addWidget(self._version_label)

        info = QVBoxLayout()
        info.setSpacing(2)
        self._milestone_label = QLabel("")
        self._milestone_label.setStyleSheet(Font.MUTED)
        info.addWidget(self._milestone_label)
        self._issues_label = QLabel("")
        self._issues_label.setStyleSheet(Font.CAPTION)
        info.addWidget(self._issues_label)
        row.addLayout(info, 1)
        self.add_layout(row)

        self._readiness_bar = ConfidenceBar("Readiness")
        self.add_content(self._readiness_bar)

        self._gaps_list = QVBoxLayout()
        self._gaps_list.setContentsMargins(0, 4, 0, 0)
        self._gaps_list.setSpacing(2)
        self.add_layout(self._gaps_list)

    def set_data(self, data: ReleaseReadinessData) -> None:
        self._version_label.setText(data.version or "--")
        self._milestone_label.setText(f"Milestone: {data.milestone}" if data.milestone else "")
        issues = []
        if data.blocking_issues:
            issues.append(f"{data.blocking_issues} blocking")
        if data.unmet_milestones:
            issues.append(f"{data.unmet_milestones} unmet milestones")
        self._issues_label.setText(" · ".join(issues) if issues else "All clear")
        self._readiness_bar.set_score(data.readiness_score)

        self._clear_gaps()
        for gap in data.gaps:
            lbl = QLabel(f"• {gap}")
            lbl.setStyleSheet(f"color: {C.TEXT_SECONDARY}; font-size: 12px;")
            self._gaps_list.addWidget(lbl)

    def _clear_gaps(self) -> None:
        for i in reversed(range(self._gaps_list.count())):
            item = self._gaps_list.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
