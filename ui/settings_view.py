"""Settings view — configuration, export, user info."""

import json
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from shared.version import APP_VERSION


class SettingRow(QFrame):
    """A single settings row with label and widget."""

    def __init__(self, label: str, widget: QWidget):
        super().__init__()
        self.setStyleSheet("""
            SettingRow {
                background-color: transparent;
                border-bottom: 1px solid #1E293B;
                padding: 8px 0;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(16)

        lbl = QLabel(label)
        lbl.setStyleSheet("color: #F1F5F9; font-size: 14px; font-weight: 500;")
        lbl.setFixedWidth(180)
        layout.addWidget(lbl)

        layout.addWidget(widget)
        layout.addStretch()


class SettingsView(QWidget):
    def __init__(self, db, prog_mgr=None):
        super().__init__()
        self._db = db
        self._prog_mgr = prog_mgr
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        header = QLabel("Settings")
        header.setStyleSheet("font-size: 24px; font-weight: 700; color: #F1F5F9;")
        layout.addWidget(header)

        # User info section
        info_card = QFrame()
        info_card.setStyleSheet(
            "background-color: #1E293B; border-radius: 12px; padding: 20px;"
        )
        info_layout = QVBoxLayout(info_card)
        info_layout.setSpacing(4)

        info_items = [
            ("Application", f"GymOS v{APP_VERSION}"),
            ("User", "Profile not yet configured"),
            ("Database", "SQLite (offline, local)"),
            ("Focus", "Set your priority muscles in the program"),
        ]
        self._info_labels: dict[str, QLabel] = {}
        for title, value in info_items:
            row = QHBoxLayout()
            row.setSpacing(12)
            t = QLabel(f"{title}:")
            t.setStyleSheet("color: #94A3B8; font-size: 13px;")
            t.setFixedWidth(100)
            row.addWidget(t)
            v = QLabel(value)
            v.setStyleSheet("color: #F1F5F9; font-size: 13px; font-weight: 500;")
            row.addWidget(v)
            row.addStretch()
            info_layout.addLayout(row)
            self._info_labels[title] = v

        # Split row — dynamically updated from active program
        split_row = QHBoxLayout()
        split_row.setSpacing(12)
        split_t = QLabel("Split:")
        split_t.setStyleSheet("color: #94A3B8; font-size: 13px;")
        split_t.setFixedWidth(100)
        split_row.addWidget(split_t)
        self._split_label = QLabel("Loading...")
        self._split_label.setStyleSheet("color: #F1F5F9; font-size: 13px; font-weight: 500;")
        split_row.addWidget(self._split_label)
        split_row.addStretch()
        info_layout.addLayout(split_row)

        layout.addWidget(info_card)

        # Preferences section
        prefs_card = QFrame()
        prefs_card.setStyleSheet(
            "background-color: #1E293B; border-radius: 12px; padding: 20px;"
        )
        prefs_layout = QVBoxLayout(prefs_card)
        prefs_layout.setSpacing(8)

        prefs_title = QLabel("Preferences")
        prefs_title.setStyleSheet("color: #F1F5F9; font-size: 16px; font-weight: 600; margin-bottom: 8px;")
        prefs_layout.addWidget(prefs_title)

        # Unit system
        unit_combo = QComboBox()
        unit_combo.addItems(["kg / cm", "lbs / ft"])
        unit_combo.setStyleSheet("""
            QComboBox {
                background-color: #0F172A;
                color: #F1F5F9;
                border: 1px solid #475569;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
                min-width: 120px;
            }
        """)
        prefs_layout.addWidget(SettingRow("Unit System", unit_combo))

        # Theme toggle
        theme_combo = QComboBox()
        theme_combo.addItems(["Dark (default)", "Light"])
        theme_combo.setStyleSheet(unit_combo.styleSheet())
        prefs_layout.addWidget(SettingRow("Theme", theme_combo))

        layout.addWidget(prefs_card)

        # Export section
        export_card = QFrame()
        export_card.setStyleSheet(
            "background-color: #1E293B; border-radius: 12px; padding: 20px;"
        )
        export_layout = QVBoxLayout(export_card)
        export_layout.setSpacing(8)

        export_title = QLabel("Data Export")
        export_title.setStyleSheet(
            "color: #F1F5F9; font-size: 16px; font-weight: 600; margin-bottom: 8px;"
        )
        export_layout.addWidget(export_title)

        export_json_btn = QPushButton("Export as JSON")
        export_json_btn.setFixedHeight(40)
        export_json_btn.setCursor(Qt.PointingHandCursor)
        export_json_btn.setStyleSheet("""
            QPushButton {
                background-color: #818CF8;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #6366F1; }
        """)
        export_json_btn.clicked.connect(self._export_json)
        export_layout.addWidget(export_json_btn)

        export_csv_btn = QPushButton("Export as CSV")
        export_csv_btn.setFixedHeight(40)
        export_csv_btn.setCursor(Qt.PointingHandCursor)
        export_csv_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E293B;
                color: #F1F5F9;
                border: 1px solid #475569;
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover { background-color: #334155; }
        """)
        export_csv_btn.clicked.connect(self._export_csv)
        export_layout.addWidget(export_csv_btn)

        layout.addWidget(export_card)

        layout.addStretch()

    def refresh(self):
        if self._prog_mgr:
            program = self._prog_mgr.get_active_program()
            if program:
                day_names = " / ".join(d.name for d in program.days)
                self._split_label.setText(f"{program.name} ({day_names})")
                return
        self._split_label.setText("No Active Program")

    def _export_json(self):
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Export Workout Data", "gymos_export.json",
            "JSON Files (*.json)"
        )
        if not save_path:
            return

        sessions = self._db.list_sessions(limit=1000)

        data = {
            "exported_at": datetime.now().isoformat(),
            "version": "0.1.0",
            "workouts": [],
            "body_weight": [],
        }

        for s in sessions:
            workout = {
                "day": s.day_name,
                "date": s.started_at.isoformat() if s.started_at else "",
                "duration_min": s.duration_minutes,
                "volume_kg": s.total_volume,
                "exercises": [
                    {
                        "name": e.name,
                        "sets": [
                            {
                                "set": st.set_number,
                                "weight_kg": st.weight_kg,
                                "reps": st.reps,
                                "rir": st.rir,
                            }
                            for st in e.sets
                        ],
                    }
                    for e in s.exercises
                ],
            }
            data["workouts"].append(workout)

        # Body weight history
        bw_data = self._db.get_body_weight_history(days=365)
        for w in bw_data:
            data["body_weight"].append({
                "date": w.date,
                "weight_kg": w.weight_kg,
            })

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        QMessageBox.information(
            self, "Export Complete",
            f"Exported {len(sessions)} workouts and "
            f"{len(bw_data)} body weight entries to:\n{save_path}"
        )

    def _export_csv(self):
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Export as CSV", "gymos_export.csv",
            "CSV Files (*.csv)"
        )
        if not save_path:
            return

        sessions = self._db.list_sessions(limit=1000)

        lines = ["date,day,exercise,set_number,weight_kg,reps,rir"]
        for s in sessions:
            date_str = s.started_at.strftime("%Y-%m-%d") if s.started_at else ""
            for e in s.exercises:
                for st in e.sets:
                    lines.append(
                        f"{date_str},{s.day_name},{e.name},{st.set_number},"
                        f"{st.weight_kg},{st.reps},{st.rir or ''}"
                    )

        with open(save_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

        QMessageBox.information(
            self, "Export Complete",
            f"Exported {len(sessions)} workouts to:\n{save_path}"
        )
