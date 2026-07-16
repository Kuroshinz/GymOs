"""Workout selection screen — editorial-quality page using canonical design system components."""

from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ui.design_system.components.app_card import AppCard
from ui.design_system.components.metric_card import MetricCard
from ui.design_system.components.section_header import SectionHeader
from ui.design_system.components.status_badge import StatusBadge, StatusLevel
from ui.design_system.components.empty_state import EmptyState
from ui.design_system.motion import AnimationFactory
from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.icon import IconTokens
from ui.design_system.tokens.radius import RadiusTokens, px_from_token
from ui.design_system.tokens.spacing import SpacingTokens
from ui.design_system.tokens.typography import TypographyTokens, font_style
from ui.design_system.layout import ScrollContainer

S = SpacingTokens()
R = RadiusTokens()
T = TypographyTokens()
Icons = IconTokens()

_r8 = px_from_token(S.s2)
_r12 = px_from_token(S.s3)
_r16 = px_from_token(S.s4)
_r24 = px_from_token(S.s6)
_r32 = px_from_token(S.s8)
_r40 = px_from_token(S.s10)

_fs_icon = px_from_token(Icons.size_2xl)
_fs_h4 = px_from_token(T.h4_size)
_fs_body = px_from_token(T.body_size)
_fs_body_sm = px_from_token(T.body_small_size)
_fs_caption = px_from_token(T.caption_size)

DAY_ICONS = {
    "Push": "\U0001F3CB",
    "Pull": "\U0001F3CB",
    "Legs": "\U0001F9B5",
    "Upper": "\U0001F4AA",
    "Lower": "\U0001F9B5",
}

DAY_DESC = {
    "Push": "Chest, Shoulders, Triceps",
    "Pull": "Back, Biceps, Rear Delts",
    "Legs": "Quads, Hamstrings, Glutes",
    "Upper": "Full Upper Body",
    "Lower": "Lower Body Power",
}


class WorkoutSelectionView(QWidget):
    workout_selected = Signal(str)

    def __init__(self, db, prog_mgr=None):
        super().__init__()
        self._db = db
        self._prog_mgr = prog_mgr
        self._active_anims: list[QPropertyAnimation] = []
        self._day_cards: list[AppCard] = []
        self._build_ui()

    def _colors(self):
        window = self.window()
        if window and hasattr(window, "_active_scheme"):
            return color_from_scheme(window._active_scheme)
        return color_from_scheme(ColorScheme.DARK)

    def _update_theme_styles(self) -> None:
        colors = self._colors()
        is_hc = colors.text_primary == "#000000"
        
        # Style metrics cards
        card_bg = colors.surface if is_hc else "rgba(20, 21, 38, 0.65)"
        card_border = colors.border if is_hc else "rgba(255, 255, 255, 0.05)"
        card_border_hover = colors.primary if is_hc else "rgba(255, 255, 255, 0.1)"
        
        glass_card_style = f"""
            QFrame {{
                background-color: {card_bg};
                border-radius: {R.xl};
                border: 1px solid {card_border};
            }}
            QFrame:hover {{
                border-color: {card_border_hover};
            }}
        """
        self._program_card.setStyleSheet(glass_card_style)
        self._weeks_card.setStyleSheet(glass_card_style)
        self._exercises_card.setStyleSheet(glass_card_style)

        # Style empty state
        for label in self._empty_state.findChildren(QLabel):
            if label == getattr(self._empty_state, "_title_label", None):
                label.setStyleSheet(
                    f"color: {colors.text_primary}; {font_style('h3', weight='semibold')}; "
                    f"background: transparent; border: none;"
                )
            elif label == getattr(self._empty_state, "_msg_label", None):
                label.setStyleSheet(
                    f"color: {colors.text_secondary}; {font_style('body')}; "
                    f"background: transparent; border: none;"
                )

        # Style day cards
        day_card_bg = colors.surface if is_hc else "rgba(20, 21, 38, 0.65)"
        day_card_border = colors.border if is_hc else "rgba(255, 255, 255, 0.05)"
        day_card_border_hover = colors.primary if is_hc else "rgba(99, 102, 241, 0.5)"
        day_card_bg_hover = colors.background if is_hc else "rgba(20, 21, 38, 0.85)"
        
        for card in self._day_cards:
            card.setStyleSheet(f"""
                AppCard {{
                    background-color: {day_card_bg};
                    border-radius: {R.xl};
                    border: 1px solid {day_card_border};
                }}
                AppCard:hover {{
                    border-color: {day_card_border_hover};
                    background-color: {day_card_bg_hover};
                }}
                AppCard:focus {{
                    border: 2px solid {colors.focus_ring};
                }}
            """)
            # Also update children labels inside the card
            for label in card.findChildren(QLabel):
                if label.property("is_title"):
                    label.setStyleSheet(
                        f"color: {colors.text_primary}; font-size: {_fs_h4}px; font-weight: 700; background: transparent;"
                    )
                elif label.property("is_desc"):
                    label.setStyleSheet(
                        f"color: {colors.text_disabled}; font-size: {_fs_caption}px; background: transparent;"
                    )

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self._update_theme_styles()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._scroll = ScrollContainer()
        layout.addWidget(self._scroll)

        scroll_layout = self._scroll.content_layout
        scroll_layout.setContentsMargins(_r32, _r24, _r32, _r24)
        scroll_layout.setSpacing(_r24)

        # ── Hero ──────────────────────────────────────────────
        hero = SectionHeader(
            title="Select Workout",
            subtitle="Choose your training session for today",
        )
        scroll_layout.addWidget(hero)

        # ── Program Summary ───────────────────────────────────
        self._summary_row = QHBoxLayout()
        self._summary_row.setSpacing(_r16)
        
        self._program_card = MetricCard(label="Program", value="--")
        self._weeks_card = MetricCard(label="Weeks", value="--")
        self._exercises_card = MetricCard(label="Exercises", value="--")

        self._summary_row.addWidget(self._program_card)
        self._summary_row.addWidget(self._weeks_card)
        self._summary_row.addWidget(self._exercises_card)
        self._summary_row.addStretch()
        scroll_layout.addLayout(self._summary_row)

        # ── Workout Days Section ─────────────────────────────
        days_header = SectionHeader(
            title="Workout Days",
            subtitle="Select a day to begin your training session",
        )
        scroll_layout.addWidget(days_header)

        self._grid = QGridLayout()
        self._grid.setSpacing(_r16)
        scroll_layout.addLayout(self._grid, stretch=1)

        # ── Empty state ───────────────────────────────────────
        self._empty_state = EmptyState(
            icon="\U0001F4F1",
            title="No Program Days",
            message="Import a workout program to get started."
        )
        self._empty_state.hide()
        scroll_layout.addWidget(self._empty_state)

        scroll_layout.addStretch()

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        focused = self.focusWidget()
        if isinstance(focused, AppCard) and event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            focused.clicked.emit()
            event.accept()
        else:
            super().keyPressEvent(event)

    def refresh(self):
        self._clear_grid()
        self._day_cards.clear()

        days = []
        if self._prog_mgr:
            days = self._prog_mgr.get_active_program_days()
        if not days:
            days = self._db.get_program_days("PPL-UL")
        if not days:
            self._empty_state.show()
            self._program_card.set_value("--")
            self._weeks_card.set_value("--")
            self._exercises_card.set_value("--")
            return

        self._empty_state.hide()

        # Update summary
        total_exercises = sum(len(d.get("exercises", [])) for d in days)
        program_name = days[0].get("program_name", "Active Program")
        self._program_card.set_value(program_name)
        self._weeks_card.set_value("1")
        self._exercises_card.set_value(str(total_exercises))

        row, col = 0, 0
        for day in days:
            name = day["name"]
            exercises = day.get("exercises", [])
            ex_count = len(exercises)

            icon = "\U0001F3CB"
            desc = "Workout"
            for key, val in DAY_ICONS.items():
                if key in name:
                    icon = val
                    break
            for key, val in DAY_DESC.items():
                if key in name:
                    desc = val
                    break

            muscle_groups = sorted(set(
                e.get("muscle_group", "") for e in exercises if e.get("muscle_group")
            ))

            card = self._build_day_card(name, icon, desc, ex_count, muscle_groups)
            card.clicked.connect(lambda checked=False, n=name: self.workout_selected.emit(n))
            self._day_cards.append(card)
            self._grid.addWidget(card, row, col)
            self._fade_in(card)
            col += 1
            if col > 2:
                col = 0
                row += 1

        self._update_theme_styles()

    def _build_day_card(self, name: str, icon: str, desc: str, ex_count: int, muscle_groups: list[str]) -> AppCard:
        colors = self._colors()
        card = AppCard(
            title="",
            interactive=True,
        )
        card.setAccessibleName(f"Workout day: {name}")
        card.setAccessibleDescription(desc)
        card.setToolTip(f"{name} \u2014 {desc}")

        inner = QVBoxLayout()
        inner.setContentsMargins(0, 0, 0, 0)
        inner.setSpacing(_r12)

        # Icon row
        icon_row = QHBoxLayout()
        icon_row.setContentsMargins(0, 0, 0, 0)
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: {_fs_icon}px; background: transparent;")
        icon_lbl.setAccessibleName(f"{name} icon")
        icon_row.addWidget(icon_lbl)
        icon_row.addStretch()
        inner.addLayout(icon_row)

        # Name
        name_lbl = QLabel(name)
        name_lbl.setProperty("is_title", True)
        name_lbl.setWordWrap(True)
        inner.addWidget(name_lbl)

        # Badge row: difficulty (approximate) + exercise count
        badge_row = QHBoxLayout()
        badge_row.setContentsMargins(0, 0, 0, 0)
        badge_row.setSpacing(_r8)

        badge_text = self._infer_difficulty(name)
        badge_level = self._difficulty_level(badge_text)
        badge = StatusBadge(text=badge_text, level=badge_level, outlined=True)
        badge_row.addWidget(badge)

        ex_badge = StatusBadge(
            text=f"{ex_count} exercises" if ex_count > 0 else "0 exercises",
            level=StatusLevel.INFO,
            outlined=True,
        )
        badge_row.addWidget(ex_badge)
        badge_row.addStretch()
        inner.addLayout(badge_row)

        # Muscle groups
        if muscle_groups:
            muscles_lbl = QLabel(", ".join(muscle_groups))
            muscles_lbl.setProperty("is_desc", True)
            muscles_lbl.setWordWrap(True)
            inner.addWidget(muscles_lbl)

        card.add_content(self._wrap_in_frame(inner))
        return card

    def _wrap_in_frame(self, layout: QVBoxLayout) -> QFrame:
        frame = QFrame()
        frame.setLayout(layout)
        frame.setStyleSheet("background: transparent; border: none;")
        return frame

    def _infer_difficulty(self, name: str) -> str:
        name_lower = name.lower()
        if any(w in name_lower for w in ("beginner", "easy", "light")):
            return "Beginner"
        if any(w in name_lower for w in ("advanced", "intense", "heavy", "hard")):
            return "Advanced"
        if any(w in name_lower for w in ("intermediate", "medium")):
            return "Intermediate"
        return "Standard"

    def _difficulty_level(self, text: str) -> StatusLevel:
        mapping = {
            "Beginner": StatusLevel.SUCCESS,
            "Intermediate": StatusLevel.WARNING,
            "Advanced": StatusLevel.ERROR,
        }
        return mapping.get(text, StatusLevel.NEUTRAL)

    def _clear_grid(self):
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _fade_in(self, widget: QWidget) -> None:
        anim = AnimationFactory.safe_fade_in(widget, duration=250)
        if anim:
            self._active_anims.append(anim)
            anim.finished.connect(lambda: self._active_anims.remove(anim) if anim in self._active_anims else None)
            anim.start()
