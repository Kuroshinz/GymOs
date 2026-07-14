from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRectF, QTimer, Qt
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QFrame, QWidget

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens, radius_to_px

R = RadiusTokens()


class WeeklyTimeline(QFrame):
    def __init__(
        self,
        days: Sequence[str] | None = None,
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._color_scheme = color_scheme
        self._days: list[str] = list(days) if days else ["M", "T", "W", "T", "F", "S", "S"]
        self._values: list[float] = [0.0] * len(self._days)
        self._labels: list[str] = [""] * len(self._days)
        self._max_value = 100.0
        self._anim_progress = 1.0
        self._anim_target_values: list[float] = []
        self._reduced_motion = False
        self.setFixedHeight(80)

    def set_reduced_motion(self, enabled: bool) -> None:
        self._reduced_motion = enabled
        if enabled:
            self._anim_progress = 1.0

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def set_data(self, values: Sequence[float], labels: Sequence[str] | None = None, max_value: float = 100.0) -> None:
        self._values = list(values)
        self._max_value = max(max_value, 1.0)
        if labels:
            self._labels = list(labels)
        if len(self._values) < len(self._days):
            self._values.extend([0.0] * (len(self._days) - len(self._values)))
        if self._reduced_motion:
            self._anim_progress = 1.0
            self.update()
        else:
            self._anim_progress = 0.0
            self._anim_target_values = list(self._values)
            self._values = [0.0] * len(self._days)
            self._animate_bars()

    def _animate_bars(self) -> None:
        steps = max(10, 250 // 16)
        step = 0

        def _tick() -> None:
            nonlocal step
            step += 1
            progress = min(step / steps, 1.0)
            eased = 1.0 - (1.0 - progress) ** 3
            self._anim_progress = eased
            for i in range(len(self._days)):
                target = self._anim_target_values[i] if i < len(self._anim_target_values) else 0.0
                self._values[i] = round(target * eased, 1)
            self.update()
            if step < steps:
                QTimer.singleShot(16, _tick)

        QTimer.singleShot(16, _tick)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        colors = self._colors()
        w = self.width()
        h = 60
        n = len(self._days)
        if n == 0 or self._anim_progress <= 0.0:
            return

        bar_w = min(32, (w - 20) // n - 6)
        spacing = (w - 20 - bar_w * n) // max(n - 1, 1)
        if spacing < 4:
            spacing = 4
        start_x = 10

        for i, day in enumerate(self._days):
            x = start_x + i * (bar_w + spacing)
            fraction = min(self._values[i] / self._max_value, 1.0) if self._max_value > 0 else 0.0
            bar_h = max(int(fraction * (h - 20)), 0)
            bar_y = h - 10 - bar_h

            bar_color = colors.primary
            if fraction < 0.3:
                bar_color = colors.error
            elif fraction < 0.6:
                bar_color = colors.warning

            painter.setBrush(QColor(bar_color))
            painter.setPen(Qt.NoPen)
            r = radius_to_px(R.sm)
            painter.drawRoundedRect(x, bar_y, bar_w, bar_h, r, r)

            font = QFont()
            font.setPixelSize(10)
            painter.setFont(font)
            painter.setPen(QColor(colors.text_disabled))
            painter.drawText(QRectF(x, h - 8, bar_w, 14), Qt.AlignCenter, day)

        painter.end()
