"""Deload Scheduler Widget — interface to view mesocycle progress and trigger deloads."""

from __future__ import annotations

from typing import Any
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens
from ui.design_system.tokens.typography import font_style

R = RadiusTokens()


class DeloadScheduler(QFrame):
    """Visual panel showing mesocycle progress and triggering active-set reduction deload weeks."""

    def __init__(self, db: Any = None, prog_mgr: Any = None, recovery_service: Any = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._db = db
        self._prog_mgr = prog_mgr
        self._recovery_service = recovery_service
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        c = color_from_scheme(ColorScheme.DARK)
        self.setStyleSheet(f"""
            DeloadScheduler {{
                background-color: {c.surface_elevated};
                border: 1px solid {c.border};
                border-radius: {R.lg};
                padding: 20px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Title
        title = QLabel("DELOAD SCHEDULER")
        title.setStyleSheet(f"color: {c.primary}; font-size: 11px; font-weight: 700; letter-spacing: 1px;")
        layout.addWidget(title)

        # Status row
        status_layout = QHBoxLayout()
        self._status_label = QLabel("Status: Active Training")
        self._status_label.setStyleSheet(f"color: {c.text_primary}; font-size: 14px; font-weight: 600;")
        status_layout.addWidget(self._status_label)

        self._week_label = QLabel("Week 1")
        self._week_label.setStyleSheet(f"color: {c.text_secondary}; font-size: 12px;")
        status_layout.addStretch()
        status_layout.addWidget(self._week_label)
        layout.addLayout(status_layout)

        # Progress bar to deload
        self._progress = QProgressBar()
        self._progress.setFixedHeight(6)
        self._progress.setTextVisible(False)
        self._progress.setRange(0, 4)
        self._progress.setValue(1)
        self._progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: rgba(255, 255, 255, 0.05);
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: {c.primary};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(self._progress)

        description = QLabel(
            "Training at high volumes causes fatigue accumulation. A deload week "
            "reduces training volume by 50% to allow connective tissue recovery and prevent injury."
        )
        description.setWordWrap(True)
        description.setStyleSheet(f"color: {c.text_disabled}; font-size: 12px; line-height: 16px;")
        layout.addWidget(description)

        # Action Button
        self._btn = QPushButton("Trigger Deload Week")
        self._btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {c.primary};
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #6366F1;
            }}
            QPushButton:disabled {{
                background-color: {c.surface};
                color: {c.text_disabled};
            }}
        """)
        self._btn.clicked.connect(self._on_btn_clicked)
        layout.addWidget(self._btn)

    def refresh(self) -> None:
        """Update the scheduler values from the program manager and recovery service."""
        c = color_from_scheme(ColorScheme.DARK)
        
        # Determine week
        meso_week = 1
        active_prog = "No Program"
        if self._prog_mgr:
            try:
                active_prog = self._prog_mgr.get_active_name()
                total = 0
                if self._db:
                    sessions = self._db.list_sessions(limit=100)
                    total = sum(1 for s in sessions if s.completed_at)
                days_count = self._prog_mgr.get_active_day_count()
                if days_count > 0:
                    meso_week = (total // days_count) + 1
            except Exception:
                pass

        self._week_label.setText(f"{active_prog} · Week {meso_week}")

        # Determine scheduled deload week (normally every 4 weeks for newbies)
        deload_target = 4
        current_step = meso_week % deload_target
        if current_step == 0:
            current_step = deload_target
        self._progress.setRange(0, deload_target)
        self._progress.setValue(current_step)

        # Check if deload is active in recovery service
        is_active = False
        active_plan = None
        if self._recovery_service:
            active_plan = self._recovery_service.get_active_deload()
            if active_plan:
                is_active = True

        if is_active and active_plan:
            self._status_label.setText(f"Status: DELOAD WEEK ACTIVE (until {active_plan.end_date})")
            self._status_label.setStyleSheet(f"color: {c.warning}; font-size: 14px; font-weight: 600;")
            self._btn.setText("Complete Deload Early")
            self._progress.setStyleSheet(f"""
                QProgressBar {{ background-color: rgba(255, 255, 255, 0.05); border: none; border-radius: 4px; }}
                QProgressBar::chunk {{ background-color: {c.warning}; border-radius: 4px; }}
            """)
        else:
            self._status_label.setText("Status: Active Training Block")
            self._status_label.setStyleSheet(f"color: {c.success}; font-size: 14px; font-weight: 600;")
            self._btn.setText("Trigger Deload Week")
            self._progress.setStyleSheet(f"""
                QProgressBar {{ background-color: rgba(255, 255, 255, 0.05); border: none; border-radius: 4px; }}
                QProgressBar::chunk {{ background-color: {c.primary}; border-radius: 4px; }}
            """)

    def _on_btn_clicked(self) -> None:
        if not self._recovery_service:
            return

        active_plan = self._recovery_service.get_active_deload()
        if active_plan:
            # Complete early
            self._recovery_service.complete_deload(active_plan.id)
            QMessageBox.information(
                self, "Deload Completed",
                "Your deload week has been completed early. Training targets returned to normal volume."
            )
        else:
            # Trigger new deload
            self._recovery_service.trigger_manual_deload("Manually triggered via Deload Scheduler UI")
            QMessageBox.warning(
                self, "Deload Activated",
                "Deload week is now active! All exercise sets in your active workout sessions are reduced by 50% for 7 days."
            )

        self.refresh()
