"""Weekly Recovery Widget — shows weekly recovery averages."""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QGridLayout, QLabel, QWidget

from ui.dashboard.dashboard_widgets.base_card import DashboardCard


class WeeklyRecoveryWidget(DashboardCard):
    """Shows weekly recovery averages in a compact grid."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="WEEKLY RECOVERY", parent=parent)

        self._grid = QGridLayout()
        self._grid.setContentsMargins(0, 4, 0, 4)
        self._grid.setSpacing(8)

        headers = ["Week", "Avg Score", "Sleep", "Fatigue"]
        for col, h in enumerate(headers):
            lbl = QLabel(h)
            lbl.setStyleSheet("color: #64748B; font-size: 11px; font-weight: 600;")
            self._grid.addWidget(lbl, 0, col)

        self._week_labels: list[QLabel] = []
        self._score_labels: list[QLabel] = []
        self._sleep_labels: list[QLabel] = []
        self._fatigue_labels: list[QLabel] = []

        for row in range(4):
            wl = QLabel(f"W{row+1}")
            wl.setStyleSheet("color: #94A3B8; font-size: 12px;")
            self._grid.addWidget(wl, row + 1, 0)
            self._week_labels.append(wl)

            sl = QLabel("--")
            sl.setStyleSheet("color: #F1F5F9; font-size: 12px;")
            self._grid.addWidget(sl, row + 1, 1)
            self._score_labels.append(sl)

            spl = QLabel("--")
            spl.setStyleSheet("color: #94A3B8; font-size: 12px;")
            self._grid.addWidget(spl, row + 1, 2)
            self._sleep_labels.append(spl)

            fl = QLabel("--")
            fl.setStyleSheet("color: #94A3B8; font-size: 12px;")
            self._grid.addWidget(fl, row + 1, 3)
            self._fatigue_labels.append(fl)

        container = QWidget()
        container.setLayout(self._grid)
        self.add_content(container)

    def update_data(self, data: Any) -> None:
        weekly = getattr(data, "recovery_weekly", None) or []
        if isinstance(weekly, list):
            for i in range(min(len(weekly), 4)):
                w = weekly[i]
                if isinstance(w, dict):
                    week_label = w.get("week", f"W{i+1}")
                    avg = w.get("average", 0)
                else:
                    week_label = getattr(w, "week", f"W{i+1}")
                    avg = getattr(w, "average", 0)

                if len(week_label) > 7:
                    week_label = week_label[-5:]
                self._week_labels[i].setText(week_label)
                score_color = "#4ADE80" if avg >= 80 else "#FBBF24" if avg >= 60 else "#EF4444"
                self._score_labels[i].setStyleSheet(f"color: {score_color}; font-size: 12px; font-weight: 600;")
                self._score_labels[i].setText(f"{avg:.0f}")
