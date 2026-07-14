from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.command_center.theme import C, Font


class ConfidenceIndicator(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(60, 60)
        self._score = 0.0
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        self._label = QLabel("0%")
        self._label.setStyleSheet("font-size: 14px; font-weight: 700;")
        layout.addWidget(self._label, 0, Qt.AlignCenter)

    def set_score(self, score: float) -> None:
        self._score = max(0.0, min(1.0, score))
        pct = int(self._score * 100)
        self._label.setText(f"{pct}%")
        color = C.TEXT_SUCCESS if self._score >= 0.8 else C.TEXT_WARN if self._score >= 0.5 else C.TEXT_DANGER
        self._label.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {color};")
        border_color = color
        self.setStyleSheet(f"""
            ConfidenceIndicator {{
                background-color: {C.CARD_BG};
                border-radius: 30px;
                border: 2px solid {border_color};
            }}
        """)

    @property
    def score(self) -> float:
        return self._score


class ConfidenceBar(QFrame):
    def __init__(self, label: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._label_text = label
        self._score = 0.0
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)

        if self._label_text:
            lbl = QLabel(self._label_text)
            lbl.setStyleSheet(Font.CAPTION)
            lbl.setFixedWidth(100)
            layout.addWidget(lbl)

        self._bar_bg = QFrame()
        self._bar_bg.setFixedHeight(8)
        self._bar_bg.setStyleSheet(f"background-color: {C.BORDER}; border-radius: 4px;")
        bar_layout = QHBoxLayout(self._bar_bg)
        bar_layout.setContentsMargins(0, 0, 0, 0)

        self._bar_fill = QFrame()
        self._bar_fill.setFixedHeight(8)
        self._bar_fill.setStyleSheet(f"background-color: {C.ACCENT}; border-radius: 4px;")
        bar_layout.addWidget(self._bar_fill)
        bar_layout.addStretch()
        layout.addWidget(self._bar_bg, 1)

        self._pct_label = QLabel("0%")
        self._pct_label.setStyleSheet(Font.CAPTION)
        self._pct_label.setFixedWidth(36)
        layout.addWidget(self._pct_label)

    def set_score(self, score: float) -> None:
        self._score = max(0.0, min(1.0, score))
        pct = int(self._score * 100)
        self._pct_label.setText(f"{pct}%")
        fill_width = int(max(self._bar_bg.width() * self._score, 0))
        if fill_width > 0:
            self._bar_fill.setFixedWidth(fill_width)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        fill_width = int(max(self._bar_bg.width() * self._score, 0))
        if fill_width > 0:
            self._bar_fill.setFixedWidth(fill_width)
