"""Today's workout card — shows scheduled workout details and start button."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from .base_card import DashboardCard


class WorkoutWidget(DashboardCard):
    """Displays today's scheduled workout.

    Fields:
      - Workout name
      - Exercise count
      - Estimated duration
      - Target volume
      - Primary muscles (as chips)
      - Warm-up status
      - Start Workout button
    """

    start_workout_clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="TODAY'S WORKOUT", parent=parent)

        self._empty_label = QLabel(
            "No active program. Import a workout program to get started."
        )
        self._empty_label.setStyleSheet(
            "color: #64748B; font-size: 13px; padding: 16px 0px;"
        )
        self._empty_label.setWordWrap(True)
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.hide()

        self._content_widget = QWidget()
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(10)

        # Workout name
        self._workout_name = QLabel()
        self._workout_name.setStyleSheet(
            "color: #F1F5F9; font-size: 20px; font-weight: 700;"
        )
        self._content_layout.addWidget(self._workout_name)

        # Meta row: exercise count + duration
        meta_row = QHBoxLayout()
        meta_row.setContentsMargins(0, 0, 0, 0)
        meta_row.setSpacing(10)

        self._exercise_badge = QLabel()
        self._exercise_badge.setStyleSheet(
            "background-color: #334155; color: #94A3B8; border-radius: 8px; "
            "padding: 3px 10px; font-size: 12px; font-weight: 600;"
        )
        self._exercise_badge.setFixedHeight(22)
        meta_row.addWidget(self._exercise_badge)

        self._duration_label = QLabel()
        self._duration_label.setStyleSheet("color: #94A3B8; font-size: 12px;")
        meta_row.addWidget(self._duration_label)

        self._volume_label = QLabel()
        self._volume_label.setStyleSheet("color: #94A3B8; font-size: 12px;")
        meta_row.addWidget(self._volume_label)

        meta_row.addStretch()
        self._content_layout.addLayout(meta_row)

        # Primary muscles (chips)
        self._muscle_container = QWidget()
        self._muscle_layout = QHBoxLayout(self._muscle_container)
        self._muscle_layout.setContentsMargins(0, 0, 0, 0)
        self._muscle_layout.setSpacing(6)
        self._content_layout.addWidget(self._muscle_container)

        # Warm-up status
        self._warmup_label = QLabel()
        self._warmup_label.setStyleSheet("color: #FBBF24; font-size: 12px;")
        self._warmup_label.setWordWrap(True)
        self._content_layout.addWidget(self._warmup_label)

        # Start button
        self._start_btn = QPushButton("▶ Start Workout")
        self._start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._start_btn.setFixedHeight(40)
        self._start_btn.setStyleSheet(
            "QPushButton { background-color: #818CF8; color: #F1F5F9; "
            "border-radius: 8px; font-size: 14px; font-weight: 600; border: none; } "
            "QPushButton:hover { background-color: #6D7BD8; }"
        )
        self._start_btn.clicked.connect(self.start_workout_clicked.emit)
        self._content_layout.addWidget(self._start_btn)

        self._content_layout.addStretch()

        self.add_content(self._empty_label)
        self.add_content(self._content_widget)
        self._content_widget.hide()

    def update(self, data: Any) -> None:
        """Update with dashboard data."""
        name = getattr(data, "today_workout_name", "") or ""
        ex_count = getattr(data, "today_workout_exercise_count", 0) or 0
        duration = getattr(data, "today_workout_estimated_duration", 0) or 0
        target_vol = getattr(data, "today_workout_target_volume", 0.0) or 0.0
        muscles = getattr(data, "today_workout_primary_muscles", []) or []
        warmup = getattr(data, "today_workout_warmup_status", "") or ""

        if not name:
            self._content_widget.hide()
            self._empty_label.show()
            return

        self._empty_label.hide()
        self._content_widget.show()

        self._workout_name.setText(name)
        self._exercise_badge.setText(f"{ex_count} exercises")

        dur_text = ""
        if duration:
            dur_text = f"~{duration} min"
        self._duration_label.setText(dur_text)

        vol_text = ""
        if target_vol:
            vol_text = f"{target_vol:.0f} kg target"
        self._volume_label.setText(vol_text)

        # Muscle chips
        for i in reversed(range(self._muscle_layout.count())):
            w = self._muscle_layout.itemAt(i).widget()
            if w is not None:
                w.deleteLater()

        for muscle in muscles:
            if muscle:
                chip = QLabel(muscle)
                chip.setStyleSheet(
                    "background-color: #1E293B; color: #818CF8; border: 1px solid #334155; "
                    "border-radius: 10px; padding: 2px 10px; font-size: 11px;"
                )
                chip.setFixedHeight(22)
                self._muscle_layout.addWidget(chip)

        self._muscle_layout.addStretch()

        if warmup:
            self._warmup_label.setText(warmup)
            self._warmup_label.show()
        else:
            self._warmup_label.setText(
                "Remember to warm up properly before starting your workout."
            )
            self._warmup_label.show()
