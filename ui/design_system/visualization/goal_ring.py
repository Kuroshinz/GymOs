from __future__ import annotations

from PySide6.QtCore import QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QFrame, QWidget

from ui.design_system.tokens.color import ColorScheme, color_from_scheme


class GoalRing(QFrame):
    def __init__(
        self,
        size: int = 140,
        stroke_width: int = 10,
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._current = 0.0
        self._target = 100.0
        self._ring_size = size
        self._stroke = stroke_width
        self._label = ""
        self._unit = ""
        self._color_scheme = color_scheme
        self._anim_progress = 1.0
        self._anim_target = 0.0
        self._anim_display = 0.0
        self._reduced_motion = False
        self.setFixedSize(size + 20, size)

    def set_reduced_motion(self, enabled: bool) -> None:
        self._reduced_motion = enabled
        if enabled:
            self._anim_progress = 1.0
            self._anim_display = self._current
            self.update()

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def set_goal(self, current: float, target: float, label: str = "", unit: str = "") -> None:
        self._current = current
        self._target = max(target, 1.0)
        self._label = label
        self._unit = unit
        if self._reduced_motion:
            self._anim_display = current
            self.update()
        else:
            self._anim_target = current
            self._anim_progress = 0.0
            self._anim_display = 0.0
            self._animate_ring()

    def _animate_ring(self) -> None:
        steps = max(10, 300 // 16)
        step = 0

        def _tick() -> None:
            nonlocal step
            step += 1
            progress = min(step / steps, 1.0)
            eased = 1.0 - (1.0 - progress) ** 3
            self._anim_progress = eased
            self._anim_display = self._anim_target * eased
            self.update()
            if step < steps:
                QTimer.singleShot(16, _tick)

        QTimer.singleShot(16, _tick)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        colors = self._colors()
        center = self._ring_size / 2 + 10
        radius = self._ring_size / 2 - self._stroke
        fraction = min(self._anim_display / self._target, 1.0)

        bg_pen = QPen(QColor(colors.scrollbar_handle), self._stroke)
        bg_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(bg_pen)
        painter.drawArc(QRectF(center - radius, center - radius, radius * 2, radius * 2), 0, 360 * 16)

        fg_pen = QPen(QColor(colors.primary), self._stroke)
        fg_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(fg_pen)
        span = int(fraction * 360 * 16)
        painter.drawArc(QRectF(center - radius, center - radius, radius * 2, radius * 2), 90 * 16, -span)

        display_val = self._anim_display
        current_str = f"{display_val:.1f}" if display_val != int(display_val) else str(int(display_val))
        font = QFont()
        font.setPixelSize(20)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(colors.text_primary))
        painter.drawText(QRectF(0, center - 20, self._ring_size + 20, 26), Qt.AlignCenter, current_str)

        if self._unit:
            font2 = QFont()
            font2.setPixelSize(11)
            painter.setFont(font2)
            painter.setPen(QColor(colors.text_disabled))
            painter.drawText(QRectF(0, center + 6, self._ring_size + 20, 16), Qt.AlignCenter, self._unit)

        painter.end()
