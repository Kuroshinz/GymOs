from __future__ import annotations

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.command_center.theme import C, Font


class PredictionCard(QFrame):
    def __init__(self, title: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(240, 130)
        self.setStyleSheet(f"""
            PredictionCard {{
                background-color: {C.CARD_BG};
                border-radius: 12px;
                border: 1px solid {C.BORDER};
                padding: 12px;
            }}
            PredictionCard:hover {{ border-color: {C.ACCENT}; }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        header = QHBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(Font.LABEL)
        header.addWidget(title_lbl)
        header.addStretch()
        self._trend_label = QLabel("")
        self._trend_label.setStyleSheet("font-size: 12px;")
        header.addWidget(self._trend_label)
        layout.addLayout(header)

        self._value_label = QLabel("--")
        self._value_label.setStyleSheet(f"color: {C.ACCENT}; font-size: 24px; font-weight: 700;")
        layout.addWidget(self._value_label)

        self._prob_label = QLabel("")
        self._prob_label.setStyleSheet(f"color: {C.TEXT_SECONDARY}; font-size: 13px;")
        layout.addWidget(self._prob_label)

        self._conf_label = QLabel("")
        self._conf_label.setStyleSheet(Font.CAPTION)
        layout.addWidget(self._conf_label)

    def set_data(self, value: str, probability: str = "", confidence: str = "",
                 trend: str = "", color: str = "") -> None:
        color = color or C.ACCENT
        self._value_label.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: 700;")
        self._value_label.setText(value)
        self._prob_label.setText(probability)
        self._conf_label.setText(confidence)

        if trend:
            trend_color = C.TEXT_SUCCESS if "up" in trend.lower() or "increasing" in trend.lower() else C.TEXT_DANGER if "down" in trend.lower() or "decreasing" in trend.lower() else C.TEXT_MUTED
            arrow = "↑" if trend_color == C.TEXT_SUCCESS else "↓" if trend_color == C.TEXT_DANGER else "→"
            self._trend_label.setText(f"{arrow} {trend}")
            self._trend_label.setStyleSheet(f"font-size: 12px; color: {trend_color};")
