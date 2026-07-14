"""Recovery Timeline Widget — shows recent recovery scores as a mini timeline."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.dashboard.dashboard_widgets.base_card import DashboardCard


class Dot(QLabel):
    """A single dot in the timeline."""

    def __init__(self, score: float, label: str, parent: QWidget | None = None) -> None:
        super().__init__("●", parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        color = "#4ADE80" if score >= 80 else "#FBBF24" if score >= 60 else "#FB923C" if score >= 40 else "#EF4444"
        self.setStyleSheet(f"font-size: 20px; color: {color};")


class RecoveryTimelineWidget(DashboardCard):
    """Mini timeline showing the last 7 recovery scores."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="RECOVERY TIMELINE", parent=parent)

        self._timeline_row = QHBoxLayout()
        self._timeline_row.setContentsMargins(0, 4, 0, 4)
        self._timeline_row.setSpacing(4)

        self._dots: list[tuple[Dot, QLabel]] = []
        for _ in range(7):
            dot = Dot(0, "")
            date_lbl = QLabel("--")
            date_lbl.setStyleSheet("color: #64748B; font-size: 9px;")
            date_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            col = QVBoxLayout()
            col.setContentsMargins(0, 0, 0, 0)
            col.setSpacing(0)
            col.addWidget(dot, 0, Qt.AlignmentFlag.AlignCenter)
            col.addWidget(date_lbl, 0, Qt.AlignmentFlag.AlignCenter)
            container = QWidget()
            container.setLayout(col)
            self._timeline_row.addWidget(container)
            self._dots.append((dot, date_lbl))

        timeline_container = QWidget()
        timeline_container.setLayout(self._timeline_row)
        self.add_content(timeline_container)

        self._avg_label = QLabel("")
        self._avg_label.setStyleSheet("color: #94A3B8; font-size: 11px;")
        self._avg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_content(self._avg_label)

    def update_data(self, data: Any) -> None:
        scores = getattr(data, "recovery_scores", []) or []

        for i, (dot, date_lbl) in enumerate(self._dots):
            if i < len(scores):
                score = scores[i]
                if isinstance(score, dict):
                    score_val = score.get("overall_score", 0)
                    date_str = score.get("date", "")
                else:
                    score_val = getattr(score, "overall_score", 0) if hasattr(score, "overall_score") else score
                    date_str = getattr(score, "date", "") if hasattr(score, "date") else ""
                dot.setText("●")
                color = "#4ADE80" if score_val >= 80 else "#FBBF24" if score_val >= 60 else "#FB923C" if score_val >= 40 else "#EF4444"
                dot.setStyleSheet(f"font-size: 20px; color: {color};")
                if date_str and len(date_str) >= 5:
                    date_lbl.setText(date_str[-5:])
                else:
                    date_lbl.setText(f"D{i+1}")
            else:
                dot.setText("○")
                dot.setStyleSheet("font-size: 20px; color: #334155;")
                date_lbl.setText("")

        avg = sum(
            (s if isinstance(s, (int, float)) else
             (s.get("overall_score", 0) if isinstance(s, dict) else getattr(s, "overall_score", 0)))
            for s in scores
        ) / len(scores) if scores else 0
        self._avg_label.setText(f"7-day avg: {avg:.1f}/100" if scores else "")
