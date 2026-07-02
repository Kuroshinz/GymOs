from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFrame,
    QProgressBar, QSizePolicy
)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QTimer, Signal
from PySide6.QtGui import QFont, QPainter, QColor, QBrush, QPen, QLinearGradient, QPainterPath


STYLE_CARD = """
QFrame#card {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(30, 30, 45, 0.95),
        stop:1 rgba(20, 20, 35, 0.95));
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.06);
}
"""

STYLE_CARD_HOVER = """
QFrame#card:hover {
    border: 1px solid rgba(124, 58, 237, 0.3);
}
"""

STYLE_VALUE = """
font-size: 28px;
font-weight: 700;
color: #ffffff;
"""

STYLE_LABEL = """
font-size: 12px;
font-weight: 500;
color: #888;
"""

STYLE_ACCENT = """
font-size: 12px;
font-weight: 600;
color: #7c3aed;
"""


class Card(QFrame):
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet(STYLE_CARD)
        self.setMinimumSize(160, 120)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 14, 16, 14)
        self._layout.setSpacing(6)

        if title:
            self.title_label = QLabel(title)
            self.title_label.setStyleSheet(STYLE_LABEL)
            self._layout.addWidget(self.title_label)

        self.value_label = QLabel("--")
        self.value_label.setStyleSheet(STYLE_VALUE)
        self.value_label.setWordWrap(True)
        self._layout.addWidget(self.value_label)

        self.subtitle_label = QLabel("")
        self.subtitle_label.setStyleSheet(STYLE_LABEL)
        self._layout.addWidget(self.subtitle_label)

        self._layout.addStretch()

    def set_value(self, value: str):
        self.value_label.setText(value)

    def set_subtitle(self, text: str):
        self.subtitle_label.setText(text)
        self.subtitle_label.setVisible(bool(text))

    def set_accent(self, text: str):
        self.subtitle_label.setStyleSheet(STYLE_ACCENT)
        self.subtitle_label.setText(text)


class StatRow(QFrame):
    def __init__(self, label="", value="", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet(STYLE_CARD)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)

        lbl = QLabel(label)
        lbl.setStyleSheet(STYLE_LABEL)
        layout.addWidget(lbl)

        layout.addStretch()

        self.val = QLabel(value)
        self.val.setStyleSheet("font-size: 14px; font-weight: 600; color: #fff;")
        layout.addWidget(self.val)

    def set_value(self, v):
        self.val.setText(str(v))


class ProgressRing(QWidget):
    def __init__(self, value=0, max_value=100, color="#7c3aed", bg_color="rgba(255,255,255,0.05)", size=120, stroke=8, parent=None):
        super().__init__(parent)
        self._value = value
        self._max = max_value
        self._color = color
        self._bg = bg_color
        self._size = size
        self._stroke = stroke
        self.setFixedSize(size, size)
        self._target_value = value
        self._anim = QPropertyAnimation(self, b"value")
        self._anim.setDuration(800)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

    def set_value_animated(self, value):
        self._target_value = value
        self._anim.setStartValue(self._value)
        self._anim.setEndValue(value)
        self._anim.start()

    def set_value(self, value):
        self._value = value
        self.update()

    def value(self):
        return self._value

    value = property(value, set_value)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(self._stroke, self._stroke, -self._stroke, -self._stroke)
        pct = min(self._value / self._max, 1.0) if self._max > 0 else 0

        pen_bg = QPen(QColor(self._bg))
        pen_bg.setWidth(self._stroke)
        pen_bg.setCapStyle(Qt.RoundCap)
        painter.setPen(pen_bg)
        painter.drawArc(rect, 0, 360 * 16)

        pen_fg = QPen(QColor(self._color))
        pen_fg.setWidth(self._stroke)
        pen_fg.setCapStyle(Qt.RoundCap)
        painter.setPen(pen_fg)
        span = int(360 * 16 * pct)
        painter.drawArc(rect, 90 * 16, -span)

        font = QFont("Inter", 14, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QColor("#ffffff"))
        painter.drawText(rect, Qt.AlignCenter, f"{int(pct * 100)}%")

        painter.end()


class MiniButton(QPushButton):
    def __init__(self, text="", icon_text="", parent=None):
        super().__init__(parent)
        self.setText(f"{icon_text} {text}" if icon_text else text)
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #7c3aed, stop:1 #6d28d9);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 18px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #8b5cf6, stop:1 #7c3aed);
            }
            QPushButton:pressed {
                background: #5b21b6;
            }
        """)
        self.setCursor(Qt.PointingHandCursor)


class AccomplishmentBadge(QFrame):
    def __init__(self, text="", icon="🏆", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet(STYLE_CARD)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(8)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 18px;")
        layout.addWidget(icon_lbl)

        txt = QLabel(text)
        txt.setStyleSheet("font-size: 12px; color: #ccc;")
        txt.setWordWrap(True)
        layout.addWidget(txt, 1)


class SectionHeader(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            font-size: 18px;
            font-weight: 700;
            color: #ffffff;
            padding: 8px 0px;
        """)
