from __future__ import annotations

from typing import Any

from PySide6.QtCore import QEasingCurve, QPointF, Qt, QVariantAnimation, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QFrame, QWidget

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.motion import MotionTokens
from ui.design_system.tokens.radius import RadiusTokens

MOTION = MotionTokens()
RADIUS = RadiusTokens()


class BaseVisualization(QFrame):
    """Foundation for all visualization components.

    Provides token-driven animation, hover/click/zoom/pan interaction,
    accessibility, and export (PNG/clipboard) as built-in capabilities.
    Subclasses override ``paintEvent`` and call ``_colors()`` for tokens.
    """

    clicked = Signal()
    double_clicked = Signal()
    hovered = Signal(str)
    value_changed = Signal(float)
    zoom_changed = Signal(float)

    def __init__(
        self,
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._color_scheme = color_scheme
        self._hovered = False
        self._selected = False
        self._zoom_level = 1.0
        self._pan_offset = QPointF(0, 0)
        self._tooltip_text = ""
        self._reduced_motion = False

        self._anim = QVariantAnimation(self)
        self._anim.valueChanged.connect(self._on_anim_value)
        self._anim.finished.connect(self._on_anim_finished)
        self._anim_target_key: str = ""

        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setAccessibleName(self.__class__.__name__)

    # ── Theme ────────────────────────────────────────────────

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def set_color_scheme(self, scheme: ColorScheme) -> None:
        self._color_scheme = scheme
        self._on_theme_changed()
        self.update()

    def _on_theme_changed(self) -> None:
        pass

    # ── Animation ────────────────────────────────────────────

    def animate(
        self,
        target: float,
        duration: int = 0,
        easing: QEasingCurve.Type = QEasingCurve.OutCubic,
        key: str = "",
    ) -> None:
        if self._reduced_motion:
            self._value = target
            self.update()
            return
        d = duration or (300 if target != 0 else 150)
        self._anim_target_key = key
        self._anim.setStartValue(self._value)
        self._anim.setEndValue(target)
        self._anim.setDuration(d)
        self._anim.setEasingCurve(easing)
        self._anim.start()

    def set_reduced_motion(self, enabled: bool) -> None:
        self._reduced_motion = enabled
        if enabled:
            self._anim.stop()

    def _on_anim_value(self, value: Any) -> None:
        self._value = float(value)
        self.update()

    def _on_anim_finished(self) -> None:
        pass

    # ── Interaction ──────────────────────────────────────────

    def enterEvent(self, event) -> None:
        self._hovered = True
        self.update()
        if self._tooltip_text:
            self.hovered.emit(self._tooltip_text)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._selected = not self._selected
            self.clicked.emit()
            self.update()
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:
        self.double_clicked.emit()
        super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event) -> None:
        delta = event.angleDelta().y() / 120
        self._zoom_level = max(0.5, min(3.0, self._zoom_level + delta * 0.1))
        self.zoom_changed.emit(self._zoom_level)
        self.update()
        super().wheelEvent(event)

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Escape:
            self._selected = False
            self.update()
        elif event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Space):
            self._selected = not self._selected
            self.clicked.emit()
            self.update()
        super().keyPressEvent(event)

    # ── Export ───────────────────────────────────────────────

    def export_png(self, path: str) -> None:
        self.grab().save(path, "PNG")

    def export_to_clipboard(self) -> None:
        QApplication.clipboard().setImage(self.grab().toImage())

    # ── Accessibility ────────────────────────────────────────

    def set_accessible_label(self, label: str) -> None:
        self.setAccessibleName(label)

    def set_accessible_description(self, desc: str) -> None:
        self.setAccessibleDescription(desc)

    def set_tooltip_text(self, text: str) -> None:
        self._tooltip_text = text
        self.setToolTip(text)

    # ── Helpers for subclasses ───────────────────────────────

    def _value_fraction(self) -> float:
        return clamp(self._value / max(self._max_value, 1.0))

    def _value_color(self, colors, fraction: float | None = None) -> str:
        f = fraction if fraction is not None else self._value_fraction()
        if f < 0.3:
            return colors.error
        if f < 0.6:
            return colors.warning
        return colors.success

    @staticmethod
    def _make_font(pixel_size: int = 12, bold: bool = False) -> QFont:
        f = QFont()
        f.setPixelSize(pixel_size)
        f.setBold(bold)
        return f


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))
