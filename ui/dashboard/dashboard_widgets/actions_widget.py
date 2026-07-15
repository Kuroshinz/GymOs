"""Dashboard Actions + Records widget — quick actions and recent PRs."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ui.dashboard.dashboard_models import DashboardData
from ui.design_system.components.empty_state import EmptyState
from ui.design_system.layout import EditorialGrid, PanelSpan
from ui.design_system.tokens.color import ColorScheme, color_from_scheme, resolve_alpha
from ui.design_system.tokens.elevation import apply_elevation, glow_effect
from ui.design_system.tokens.radius import RadiusTokens, px_from_token
from ui.design_system.tokens.spacing import SpacingTokens
from ui.design_system.tokens.typography import TypographyTokens, font_style

S = SpacingTokens()
R = RadiusTokens()
T = TypographyTokens()

_pxf = px_from_token
_px2 = _pxf(S.half)
_px4 = _pxf(S.s1)
_px6 = _pxf(S.s1_5)
_px8 = _pxf(S.s2)
_px10 = _pxf(S.s2_5)
_px12 = _pxf(S.s3)
_px16 = _pxf(S.s4)
_px20 = _pxf(S.s5)
_px24 = _pxf(S.s6)
_px28 = _pxf(S.s7) if hasattr(S, 's7') else 28


class _CommandCard(QFrame):
    """Clickable action card used in the actions panel."""
    clicked = Signal()

    def mousePressEvent(self, event) -> None:
        self.clicked.emit()
        super().mousePressEvent(event)


class ActionsWidget(QFrame):
    """Quick action buttons and recent personal records.

    Signals mirror the original DashboardView signals for action cards.
    """

    start_workout_clicked = Signal()
    log_weight_clicked = Signal()
    set_goal_clicked = Signal()
    import_program_clicked = Signal()
    view_all_prs_clicked = Signal()
    weekly_review_clicked = Signal()

    def __init__(self, motion: Any = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._motion = motion
        self._build_ui()

    def set_motion_service(self, motion: Any) -> None:
        self._motion = motion

    def _colors(self):
        return color_from_scheme(ColorScheme.DARK)

    def _build_ui(self) -> None:
        self.setStyleSheet("ActionsWidget { background: transparent; }")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        grid = EditorialGrid()
        grid.set_spacing(_px16)
        layout.addWidget(grid)

        self._build_records_panel(grid)
        self._build_actions_panel(grid)

    def _build_records_panel(self, grid: EditorialGrid) -> None:
        colors = self._colors()

        self._records_card = QFrame()
        self._records_card.setObjectName("RecordsCard")
        self._records_card.setStyleSheet(
            f"""
            QFrame#RecordsCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(15,18,55,220), stop:1 rgba(8,12,36,140));
                border-radius: {R.xl};
                border: 1px solid {resolve_alpha(colors.primary, 0.08)};
            }}
        """
        )
        apply_elevation(self._records_card, 1, is_dark=True, bg_color=colors.surface)

        rl = QVBoxLayout(self._records_card)
        rl.setContentsMargins(_px24, _px20, _px24, _px20)
        rl.setSpacing(_px12)

        self._prs_container = QVBoxLayout()
        self._prs_container.setContentsMargins(0, 0, 0, 0)
        self._prs_container.setSpacing(_px8)
        self._prs_widget = QWidget()
        self._prs_widget.setLayout(self._prs_container)
        self._prs_widget.setStyleSheet("background: transparent;")
        rl.addWidget(self._prs_widget)

        self._prs_empty = EmptyState(
            icon="\U0001F31F",
            title="No Records Yet",
            message="Push yourself! PRs will appear here after great workouts.",
        )
        rl.addWidget(self._prs_empty)

        self._prs_widget.hide()

        grid.add_panel(self._records_card, span=PanelSpan.TWO_THIRDS)

        if self._motion:
            self._motion.bind_hover_elevation(self._records_card)

    def _build_actions_panel(self, grid: EditorialGrid) -> None:
        colors = self._colors()

        actions_card = QFrame()
        actions_card.setObjectName("ActionsCard")
        actions_card.setStyleSheet(
            f"""
            QFrame#ActionsCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(15,18,55,220), stop:1 rgba(8,12,36,140));
                border-radius: {R.xl};
                border: 1px solid {resolve_alpha(colors.primary, 0.08)};
            }}
        """
        )

        al = QVBoxLayout(actions_card)
        al.setContentsMargins(_px16, _px16, _px16, _px16)
        al.setSpacing(_px10)

        actions = [
            ("\u25B6", "Start Workout", "Begin a new session", self.start_workout_clicked.emit, True),
            ("\u2696", "Log Weight", "Record body weight", self.log_weight_clicked.emit, False),
            ("\U0001F3AF", "Set Goal", "Target weight & surplus", self.set_goal_clicked.emit, False),
            ("\u2B07", "Import Program", "Import from file", self.import_program_clicked.emit, False),
            ("\u2728", "View PRs", "Personal records", self.view_all_prs_clicked.emit, False),
            ("\u270F", "Review Week", "Training summary", self.weekly_review_clicked.emit, False),
        ]

        for icon, label, tip, handler, primary in actions:
            card = _CommandCard()
            card.setCursor(Qt.PointingHandCursor)
            card.setFixedHeight(88)
            card.setToolTip(tip)
            card.setAccessibleName(f"{label} action card")
            card.clicked.connect(handler)

            if primary:
                bg = (
                    "qlineargradient(x1:0, y1:0, x2:1, y2:1, "
                    "stop:0 rgba(99,102,241,0.95), stop:0.6 rgba(139,92,246,0.9), stop:1 rgba(167,139,250,0.85))"
                )
                bg_hover = (
                    "qlineargradient(x1:0, y1:0, x2:1, y2:1, "
                    "stop:0 rgba(129,140,248,0.95), stop:0.6 rgba(167,139,250,0.9), stop:1 rgba(196,181,253,0.85))"
                )
                bdr = "none"
                txt = "#FFFFFF"
                txt_desc = "rgba(255,255,255,0.7)"
            else:
                bg = (
                    "qlineargradient(x1:0, y1:0, x2:1, y2:1, "
                    "stop:0 rgba(15,18,55,220), stop:1 rgba(8,12,36,140))"
                )
                bg_hover = (
                    "qlineargradient(x1:0, y1:0, x2:1, y2:1, "
                    "stop:0 rgba(22,26,78,220), stop:1 rgba(12,16,51,170))"
                )
                bdr = f"1px solid {resolve_alpha(colors.primary, 0.10)}"
                txt = colors.text_primary
                txt_desc = colors.text_disabled

            card.setStyleSheet(
                f"""
                _CommandCard {{
                    background: {bg};
                    border: {bdr};
                    border-radius: {R.lg};
                }}
                _CommandCard:hover {{
                    background: {bg_hover};
                }}
            """
            )

            if primary:
                glow_effect(card, glow_rgba=resolve_alpha(colors.primary, 0.35), blur=16, offset_y=0)

            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(_px16, _px12, _px16, _px12)
            card_layout.setSpacing(_px4)

            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet(f"font-size: 22px; color: {txt}; background: transparent;")
            card_layout.addWidget(icon_lbl)

            name_lbl = QLabel(label)
            name_lbl.setStyleSheet(f"color: {txt}; font-size: 14px; font-weight: 700; background: transparent;")
            card_layout.addWidget(name_lbl)

            desc_lbl = QLabel(tip)
            desc_lbl.setStyleSheet(f"color: {txt_desc}; font-size: 12px; font-weight: 400; background: transparent;")
            card_layout.addWidget(desc_lbl)

            card_layout.addStretch()
            al.addWidget(card)

        al.addStretch()
        grid.add_panel(actions_card, span=PanelSpan.QUARTER)

    # ── Public API ─────────────────────────────────────────────

    def update_data(self, data: DashboardData) -> None:
        """Update PRs list from dashboard data."""
        self._update_prs(data)

    def _update_prs(self, data: DashboardData) -> None:
        colors = self._colors()
        prs = getattr(data, "recent_prs", [])

        for _ in reversed(range(self._prs_container.count())):
            item = self._prs_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if prs:
            self._prs_empty.hide()
            self._prs_widget.show()

            for pr in prs[:5]:
                ex_name = (
                    pr if isinstance(pr, str)
                    else getattr(pr, "exercise_name", str(pr))
                )
                pr_type = getattr(pr, "pr_type", "") if not isinstance(pr, str) else ""
                display_val = (
                    getattr(pr, "display_value", "") if not isinstance(pr, str) else ""
                )

                row = QFrame()
                row.setStyleSheet("background: transparent; border: none;")
                row_layout = QHBoxLayout(row)
                row_layout.setContentsMargins(0, _px6, 0, _px6)
                row_layout.setSpacing(_px12)

                icon_lbl = QLabel("\u2B50")
                icon_lbl.setStyleSheet(f"font-size: 16px; background: transparent;")
                icon_lbl.setFixedWidth(24)
                row_layout.addWidget(icon_lbl)

                name_lbl = QLabel(ex_name)
                name_lbl.setStyleSheet(
                    f"color: {colors.text_primary}; font-size: 14px; font-weight: 600; background: transparent;"
                )
                row_layout.addWidget(name_lbl, 1)

                if display_val or pr_type:
                    val_lbl = QLabel(f"{pr_type.upper() if pr_type else ''} {display_val}")
                    val_lbl.setStyleSheet(
                        f"color: {colors.warning}; font-size: 13px; font-weight: 700; background: transparent;"
                    )
                    row_layout.addWidget(val_lbl)

                self._prs_container.addWidget(row)
        else:
            self._prs_empty.show()
            self._prs_widget.hide()
