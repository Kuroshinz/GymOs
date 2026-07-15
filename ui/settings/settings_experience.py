from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
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

from shared.version import (
    APP_DESCRIPTION,
    APP_NAME,
    APP_VERSION,
    BUILD_DATE,
    BUILD_NUMBER,
    COPYRIGHT,
    DATABASE_VERSION,
    PROTOCOL_VERSION,
    RELEASE_CHANNEL,
    SCHEMA_VERSION,
)
from ui.design_system.components.section_header import SectionHeader
from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens, px_from_token
from ui.design_system.tokens.spacing import SpacingTokens
from ui.design_system.tokens.typography import TypographyTokens, font_style

S = SpacingTokens()
R = RadiusTokens()
T = TypographyTokens()

_px4 = px_from_token(S.s1)
_px8 = px_from_token(S.s2)
_px12 = px_from_token(S.s3)
_px16 = px_from_token(S.s4)
_px20 = px_from_token(S.s5)
_px24 = px_from_token(S.s6)
_px32 = px_from_token(S.s8)

_CONTRIBUTORS = [
    ("GymOS Contributors", "Core Architecture & Development"),
    ("Open Source Community", "Libraries & Support"),
]

_LICENSE_TEXT = (
    f"MIT License\n\n{COPYRIGHT}\n\n"
    "Permission is hereby granted, free of charge, to any person "
    "obtaining a copy of this software and associated documentation "
    "files (the \"Software\"), to deal in the Software without "
    "restriction, including without limitation the rights to use, "
    "copy, modify, merge, publish, distribute, sublicense, and/or "
    "sell copies of the Software, and to permit persons to whom "
    "the Software is furnished to do so, subject to the following "
    "conditions:\n\n"
    "The above copyright notice and this permission notice shall "
    "be included in all copies or substantial portions of the "
    "Software.\n\n"
    "THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY "
    "KIND, EXPRESS OR IMPLIED, including but not limited to the "
    "warranties of MERCHANTABILITY, FITNESS FOR A PARTICULAR "
    "PURPOSE AND NONINFRINGEMENT."
)


class SettingsExperience(QWidget):
    def __init__(self, db: Any, prog_mgr: Any = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._db = db
        self._prog_mgr = prog_mgr
        self._build_ui()

    def _colors(self):
        return color_from_scheme(ColorScheme.DARK)

    def _build_ui(self) -> None:
        from ui.design_system.layout.scroll_container import ScrollContainer
        scroll = ScrollContainer()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        main = QVBoxLayout()
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)
        scroll.content_layout.insertLayout(0, main)

        self._build_hero(main)
        self._build_profile(main)
        self._build_goals(main)
        self._build_preferences(main)
        self._build_appearance(main)
        self._build_notifications(main)
        self._build_data_backup(main)
        self._build_about(main)

        main.addStretch()

    def _build_section_header(self, parent: QVBoxLayout, title: str, subtitle: str) -> None:
        header = SectionHeader(title=title, subtitle=subtitle)
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, _px24, 0, _px8)
        hbox.addWidget(header)
        parent.addLayout(hbox)

    def _card(self, colors) -> str:
        return f"""
            QFrame {{
                background-color: {colors.surface};
                border-radius: {R.lg};
                border: 1px solid {colors.border};
            }}
        """

    def _label_row(self, label: str, value_widget: QWidget) -> QFrame:
        colors = self._colors()
        row = QFrame()
        row.setStyleSheet("QFrame { background: transparent; border: none; }")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, _px4, 0, _px4)
        row_layout.setSpacing(_px12)

        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {colors.text_secondary}; {font_style('body_small')}; background: transparent;")
        lbl.setFixedWidth(160)
        row_layout.addWidget(lbl)

        row_layout.addWidget(value_widget, 1)
        return row

    def _value_label(self, text: str) -> QLabel:
        colors = self._colors()
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {colors.text_primary}; {font_style('body_small', 'bold')}; background: transparent;")
        return lbl

    def _combo(self, items: list[str], accessible_name: str = "", tooltip: str = "") -> QComboBox:
        colors = self._colors()
        cb = QComboBox()
        cb.addItems(items)
        if accessible_name:
            cb.setAccessibleName(accessible_name)
        if tooltip:
            cb.setToolTip(tooltip)
        cb.setStyleSheet(f"""
            QComboBox {{
                background-color: {colors.background};
                color: {colors.text_primary};
                border: 1px solid {colors.border};
                border-radius: {R.md};
                padding: 0 12px;
                {font_style('body_small')}
                min-width: 140px;
            }}
            QComboBox:focus {{ border-color: {colors.focus_ring}; }}
            QComboBox::drop-down {{ border: none; }}
        """)
        return cb

    def _primary_button(self, text: str, accessible_name: str = "", tooltip: str = "") -> QPushButton:
        colors = self._colors()
        btn = QPushButton(text)
        if accessible_name:
            btn.setAccessibleName(accessible_name)
        if tooltip:
            btn.setToolTip(tooltip)
        btn.setFixedHeight(40)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.primary};
                color: {colors.text_inverse};
                border: 1px solid transparent;
                border-radius: {R.md};
                padding: 0 20px;
                {font_style('body_small', 'bold')}
            }}
            QPushButton:hover {{ background-color: {colors.primary_hover}; }}
            QPushButton:focus {{ border-color: {colors.focus_ring}; }}
        """)
        return btn

    def _secondary_button(self, text: str, accessible_name: str = "", tooltip: str = "") -> QPushButton:
        colors = self._colors()
        btn = QPushButton(text)
        if accessible_name:
            btn.setAccessibleName(accessible_name)
        if tooltip:
            btn.setToolTip(tooltip)
        btn.setFixedHeight(40)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.surface};
                color: {colors.text_primary};
                border: 1px solid {colors.border};
                border-radius: {R.md};
                padding: 0 20px;
                {font_style('body_small')}
            }}
            QPushButton:hover {{ background-color: {colors.surface_hover}; border-color: {colors.border_hover}; }}
            QPushButton:focus {{ border-color: {colors.focus_ring}; }}
        """)
        return btn

    def _separator(self) -> QFrame:
        colors = self._colors()
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {colors.border}; border: none;")
        return sep

    # ── Sections ──────────────────────────────────────────────

    def _build_hero(self, parent: QVBoxLayout) -> None:
        colors = self._colors()
        hero = QFrame()
        hero.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.surface};
                border-radius: {R.xl};
                border: 1px solid {colors.border};
            }}
        """)
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(24, 20, 24, 20)
        hero_layout.setSpacing(16)

        accent = QFrame()
        accent.setFixedWidth(4)
        accent.setStyleSheet(f"background-color: {colors.accent}; border-radius: {R.sm}; border: none;")
        hero_layout.addWidget(accent)

        text_area = QVBoxLayout()
        text_area.setSpacing(6)

        title = QLabel("Settings & Personalization")
        title.setStyleSheet(f"color: {colors.text_primary}; {font_style('h3')}")
        text_area.addWidget(title)

        subtitle = QLabel("Configure your profile, preferences, and application settings")
        subtitle.setStyleSheet(f"color: {colors.text_secondary}; {font_style('body_small')}")
        subtitle.setWordWrap(True)
        text_area.addWidget(subtitle)

        text_area.addStretch()
        hero_layout.addLayout(text_area, 1)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(_px4)
        app_name = QLabel(f"{APP_NAME} v{APP_VERSION}")
        app_name.setStyleSheet(f"color: {colors.text_primary}; {font_style('subtitle', 'bold')}; background: transparent;")
        app_name.setAlignment(Qt.AlignRight)
        info_layout.addWidget(app_name)
        channel = QLabel(f"{RELEASE_CHANNEL} \u00b7 build {BUILD_NUMBER}")
        channel.setStyleSheet(f"color: {colors.text_disabled}; {font_style('caption')}; background: transparent;")
        channel.setAlignment(Qt.AlignRight)
        info_layout.addWidget(channel)

        info_widget = QWidget()
        info_widget.setLayout(info_layout)
        info_widget.setStyleSheet("background: transparent; border: none;")
        hero_layout.addWidget(info_widget)

        parent.addWidget(hero)

    def _build_profile(self, parent: QVBoxLayout) -> None:
        self._build_section_header(parent, "Profile", "Your personal information and body stats")
        colors = self._colors()
        card = QFrame()
        card.setStyleSheet(self._card(colors))
        layout = QVBoxLayout(card)
        layout.setContentsMargins(_px20, _px16, _px20, _px16)
        layout.setSpacing(_px4)

        self._profile_name = self._value_label("Not configured")
        layout.addWidget(self._label_row("Name", self._profile_name))

        self._profile_email = self._value_label("Not configured")
        layout.addWidget(self._label_row("Email", self._profile_email))

        layout.addWidget(self._separator())

        self._profile_height = self._value_label("-- cm")
        layout.addWidget(self._label_row("Height", self._profile_height))

        self._profile_weight = self._value_label("-- kg")
        layout.addWidget(self._label_row("Weight", self._profile_weight))

        parent.addWidget(card)

    def _build_goals(self, parent: QVBoxLayout) -> None:
        self._build_section_header(parent, "Goals", "Your training and body composition targets")
        colors = self._colors()
        card = QFrame()
        card.setStyleSheet(self._card(colors))
        layout = QVBoxLayout(card)
        layout.setContentsMargins(_px20, _px16, _px20, _px16)
        layout.setSpacing(_px4)

        self._goal_type = self._value_label("Not set")
        layout.addWidget(self._label_row("Goal Type", self._goal_type))

        self._goal_target = self._value_label("--")
        layout.addWidget(self._label_row("Target", self._goal_target))

        self._goal_current = self._value_label("--")
        layout.addWidget(self._label_row("Current", self._goal_current))

        self._goal_deadline = self._value_label("No deadline")
        layout.addWidget(self._label_row("Deadline", self._goal_deadline))

        parent.addWidget(card)

    def _build_preferences(self, parent: QVBoxLayout) -> None:
        self._build_section_header(parent, "Preferences", "Training, nutrition, and measurement settings")
        colors = self._colors()
        card = QFrame()
        card.setStyleSheet(self._card(colors))
        layout = QVBoxLayout(card)
        layout.setContentsMargins(_px20, _px16, _px20, _px16)
        layout.setSpacing(_px4)

        unit_combo = self._combo(["kg / cm", "lbs / ft"], accessible_name="Unit System", tooltip="Choose your preferred measurement units")
        layout.addWidget(self._label_row("Unit System", unit_combo))

        training_combo = self._combo(
            ["Push/Pull/Legs", "PPL-UL", "Upper/Lower", "Full Body", "Bro Split"],
            accessible_name="Training Style",
            tooltip="Your preferred training split style",
        )
        layout.addWidget(self._label_row("Training Style", training_combo))

        nutrition_combo = self._combo(
            ["Lean Bulk", "Maintenance", "Cut", "Reverse Diet"],
            accessible_name="Nutrition Approach",
            tooltip="Your nutritional approach",
        )
        layout.addWidget(self._label_row("Nutrition", nutrition_combo))

        recovery_combo = self._combo(
            ["Maximize Performance", "Balance Lifestyle", "Minimize Effort"],
            accessible_name="Recovery Priority",
            tooltip="How you prioritise recovery",
        )
        layout.addWidget(self._label_row("Recovery Priority", recovery_combo))

        risk_combo = self._combo(
            ["Conservative", "Moderate", "Aggressive"],
            accessible_name="Risk Level",
            tooltip="Training risk tolerance",
        )
        layout.addWidget(self._label_row("Risk Level", risk_combo))

        parent.addWidget(card)

    def _build_appearance(self, parent: QVBoxLayout) -> None:
        self._build_section_header(parent, "Appearance", "Theme and visual preferences")
        colors = self._colors()
        card = QFrame()
        card.setStyleSheet(self._card(colors))
        layout = QVBoxLayout(card)
        layout.setContentsMargins(_px20, _px16, _px20, _px16)
        layout.setSpacing(_px4)

        self._theme_combo = self._combo(
            ["Dark (default)", "Light", "High Contrast"],
            accessible_name="Theme",
            tooltip="Change the application color scheme. High contrast improves visibility.",
        )
        self._theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        layout.addWidget(self._label_row("Theme", self._theme_combo))

        parent.addWidget(card)

    def _build_notifications(self, parent: QVBoxLayout) -> None:
        self._build_section_header(parent, "Notifications", "Control which notifications you receive")
        colors = self._colors()
        card = QFrame()
        card.setStyleSheet(self._card(colors))
        layout = QVBoxLayout(card)
        layout.setContentsMargins(_px20, _px16, _px20, _px16)
        layout.setSpacing(_px4)

        self._notif_workout = QCheckBox("Workout Reminders")
        self._notif_workout.setChecked(True)
        self._notif_recovery = QCheckBox("Recovery Alerts")
        self._notif_recovery.setChecked(True)
        self._notif_progress = QCheckBox("Progress Insights")
        self._notif_progress.setChecked(True)
        self._notif_weekly = QCheckBox("Weekly Summary")
        self._notif_weekly.setChecked(False)

        for cb in (self._notif_workout, self._notif_recovery, self._notif_progress, self._notif_weekly):
            cb.setStyleSheet(f"""
                QCheckBox {{
                    color: {colors.text_primary};
                    {font_style('body_small')};
                    spacing: 8px;
                    padding: 4px 0;
                }}
                QCheckBox::indicator {{
                    width: 18px;
                    height: 18px;
                    border: 2px solid {colors.border};
                    border-radius: {R.sm};
                    background-color: transparent;
                }}
                QCheckBox::indicator:hover {{
                    border-color: {colors.primary};
                }}
                QCheckBox::indicator:checked {{
                    background-color: {colors.primary};
                    border-color: {colors.primary};
                }}
            """)
            layout.addWidget(cb)

        parent.addWidget(card)

    def _build_data_backup(self, parent: QVBoxLayout) -> None:
        self._build_section_header(parent, "Data & Backup", "Export, import, and manage your data")
        colors = self._colors()
        card = QFrame()
        card.setStyleSheet(self._card(colors))
        layout = QVBoxLayout(card)
        layout.setContentsMargins(_px20, _px16, _px20, _px16)
        layout.setSpacing(_px12)

        export_label = QLabel("Export your workout data for external analysis or safekeeping.")
        export_label.setStyleSheet(f"color: {colors.text_secondary}; {font_style('body_small')}; background: transparent;")
        export_label.setWordWrap(True)
        layout.addWidget(export_label)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(_px12)

        export_json = self._primary_button("Export as JSON", accessible_name="Export data as JSON", tooltip="Export all workout data to a JSON file")
        export_json.clicked.connect(self._export_json)
        btn_row.addWidget(export_json)

        export_csv = self._secondary_button("Export as CSV", accessible_name="Export data as CSV", tooltip="Export all workout data to a CSV file")
        export_csv.clicked.connect(self._export_csv)
        btn_row.addWidget(export_csv)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        layout.addWidget(self._separator())

        backup_info = QLabel("Backups are stored locally in the data/backups directory.")
        backup_info.setStyleSheet(f"color: {colors.text_disabled}; {font_style('caption')}; background: transparent;")
        backup_info.setWordWrap(True)
        layout.addWidget(backup_info)

        info_row = QHBoxLayout()
        info_row.setSpacing(_px8)

        db_label = QLabel("Database:")
        db_label.setStyleSheet(f"color: {colors.text_secondary}; {font_style('caption')}; background: transparent;")
        info_row.addWidget(db_label)

        self._db_info = QLabel("SQLite (offline, local)")
        self._db_info.setStyleSheet(f"color: {colors.text_primary}; {font_style('caption', 'bold')}; background: transparent;")
        info_row.addWidget(self._db_info)
        info_row.addStretch()
        layout.addLayout(info_row)

        parent.addWidget(card)

    def _build_about(self, parent: QVBoxLayout) -> None:
        self._build_section_header(parent, "About", f"About {APP_NAME}")
        colors = self._colors()
        card = QFrame()
        card.setStyleSheet(self._card(colors))
        layout = QVBoxLayout(card)
        layout.setContentsMargins(_px20, _px16, _px20, _px16)
        layout.setSpacing(_px8)

        name = QLabel(APP_NAME)
        name.setStyleSheet(f"color: {colors.text_primary}; {font_style('h4')}; background: transparent;")
        layout.addWidget(name)

        desc = QLabel(APP_DESCRIPTION)
        desc.setStyleSheet(f"color: {colors.text_secondary}; {font_style('body_small')}; background: transparent;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addWidget(self._separator())

        build_fields = [
            ("Version", APP_VERSION),
            ("Build", str(BUILD_NUMBER)),
            ("Release Channel", RELEASE_CHANNEL),
            ("Build Date", BUILD_DATE),
            ("Schema Version", str(SCHEMA_VERSION)),
            ("Database Version", str(DATABASE_VERSION)),
            ("Protocol Version", PROTOCOL_VERSION),
        ]
        for label, value in build_fields:
            row = self._label_row(label, self._value_label(value))
            layout.addWidget(row)

        layout.addWidget(self._separator())

        layout.addWidget(self._separator())

        for name, role in _CONTRIBUTORS:
            c_name = QLabel(name)
            c_name.setStyleSheet(f"color: {colors.text_primary}; {font_style('body_small', 'bold')}; background: transparent;")
            layout.addWidget(c_name)
            c_role = QLabel(role)
            c_role.setStyleSheet(f"color: {colors.text_disabled}; {font_style('caption')}; background: transparent;")
            layout.addWidget(c_role)

        layout.addWidget(self._separator())

        license_btn = self._secondary_button("View License", tooltip="View the MIT License")
        license_btn.clicked.connect(self._show_license)
        layout.addWidget(license_btn)

        copyright_label = QLabel(COPYRIGHT)
        copyright_label.setStyleSheet(f"color: {colors.text_disabled}; {font_style('caption')}; background: transparent;")
        layout.addWidget(copyright_label)

        parent.addWidget(card)

    def _show_license(self) -> None:
        QMessageBox.information(self, f"{APP_NAME} License", _LICENSE_TEXT)

    # ── Theme ─────────────────────────────────────────────────

    def _on_theme_changed(self, index: int) -> None:
        from ui.design_system.tokens.color import ColorScheme
        window = self.window()
        if window is None:
            return
        if index == 0:
            scheme = ColorScheme.DARK
            high_contrast = False
        elif index == 1:
            scheme = ColorScheme.LIGHT
            high_contrast = False
        else:
            scheme = ColorScheme.HIGH_CONTRAST
            high_contrast = True
        from ui.design_system.theme import global_stylesheet
        window.setStyleSheet(global_stylesheet(scheme))
        experience = getattr(window, "_experience", None)
        if experience and hasattr(experience, "accessibility"):
            experience.accessibility.set_high_contrast(high_contrast)

    # ── Refresh ───────────────────────────────────────────────

    def refresh(self) -> None:
        self._refresh_profile()
        self._refresh_goals()
        self._refresh_preferences()

    def _refresh_profile(self) -> None:
        colors = self._colors()
        try:
            bw = self._db.get_latest_body_weight()
            if bw and hasattr(bw, "weight_kg"):
                self._profile_weight.setText(f"{bw.weight_kg:.1f} kg")
                self._profile_weight.setStyleSheet(
                    f"color: {colors.text_primary}; {font_style('body_small', 'bold')}; background: transparent;"
                )
        except Exception:
            pass

    def _refresh_goals(self) -> None:
        try:
            goals = getattr(self._prog_mgr, "get_active_goals", lambda: [])()
            if goals:
                g = goals[0]
                self._goal_type.setText(g.goal_type.label if hasattr(g.goal_type, "label") else str(g.goal_type))
                self._goal_target.setText(f"{g.target} kg" if g.target else "--")
                self._goal_current.setText(f"{g.current} kg" if g.current else "--")
                if g.deadline:
                    self._goal_deadline.setText(g.deadline.strftime("%b %d, %Y") if hasattr(g.deadline, "strftime") else str(g.deadline))
        except Exception:
            pass

    def _refresh_preferences(self) -> None:
        if self._prog_mgr:
            try:
                program = self._prog_mgr.get_active_program()
                if program:
                    " / ".join(d.name for d in program.days)
            except Exception:
                pass

    # ── Export ────────────────────────────────────────────────

    def _export_json(self) -> None:
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

    def _export_csv(self) -> None:
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
