"""Sleep & Stress Widget — shows sleep and stress metrics side by side."""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QHBoxLayout, QLabel, QProgressBar, QVBoxLayout, QWidget

from ui.dashboard.dashboard_widgets.base_card import DashboardCard


class MetricCard(QWidget):
    """A single metric mini-card with label, value, and progress bar."""

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        self._title = QLabel(title)
        self._title.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: 600;")
        layout.addWidget(self._title)

        self._value = QLabel("--")
        self._value.setStyleSheet("color: #F1F5F9; font-size: 20px; font-weight: 700;")
        layout.addWidget(self._value)

        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setTextVisible(False)
        self._progress.setFixedHeight(6)
        self._progress.setStyleSheet("""
            QProgressBar { background-color: #1E293B; border-radius: 3px; border: none; }
            QProgressBar::chunk { border-radius: 3px; }
        """)
        layout.addWidget(self._progress)

        self._detail = QLabel("")
        self._detail.setStyleSheet("color: #64748B; font-size: 11px;")
        layout.addWidget(self._detail)

    def update_metric(self, value: float, max_val: float, detail: str = "",
                      color: str = "#4ADE80") -> None:
        pct = min(int(value / max_val * 100), 100) if max_val > 0 else 0
        self._value.setText(f"{value:.1f}" if value != int(value) else f"{int(value)}")
        self._progress.setValue(pct)
        self._progress.setStyleSheet(f"""
            QProgressBar {{ background-color: #1E293B; border-radius: 3px; border: none; }}
            QProgressBar::chunk {{ background-color: {color}; border-radius: 3px; }}
        """)
        self._detail.setText(detail)


class SleepStressWidget(DashboardCard):
    """Side-by-side sleep and stress metrics."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="SLEEP & STRESS", parent=parent)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(12)

        self._sleep_card = MetricCard("SLEEP")
        row.addWidget(self._sleep_card)

        self._stress_card = MetricCard("STRESS")
        row.addWidget(self._stress_card)

        container = QWidget()
        container.setLayout(row)
        self.add_content(container)

    def update_data(self, data: Any) -> None:
        sleep_score = getattr(data, "recovery_sleep_score", 0.0) or 0.0
        sleep_hours = getattr(data, "recovery_sleep_hours", 0.0) or 0.0
        stress_score = getattr(data, "recovery_stress_score", 0.0) or 0.0

        sleep_color = "#4ADE80" if sleep_score >= 60 else "#FB923C" if sleep_score >= 40 else "#EF4444"
        stress_color = "#4ADE80" if stress_score <= 40 else "#FB923C" if stress_score <= 60 else "#EF4444"

        self._sleep_card.update_metric(sleep_score, 100, f"{sleep_hours:.1f}h", sleep_color)
        self._stress_card.update_metric(100 - stress_score, 100,
                                        f"Level: {stress_score:.0f}/100", stress_color)
