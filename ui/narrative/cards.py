from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.typography import font_style
from ui.narrative.engine import Narrative


class CoachCard(QFrame):
    """A coach-style narrative card with progressive disclosure."""

    expand_clicked = Signal()
    action_clicked = Signal(str)

    def __init__(
        self,
        narrative: Narrative,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._narrative = narrative
        self._expanded = False
        self._build_ui()

    def _build_ui(self) -> None:
        colors = color_from_scheme(ColorScheme.DARK)

        self.setObjectName("CoachCard")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        header = QHBoxLayout()
        header.setSpacing(8)

        severity_map = {
            "critical": colors.error,
            "warning": colors.warning,
            "info": colors.info,
            "success": colors.success,
        }
        sev = self._narrative.metadata.get("severity", "info")
        severity_color = severity_map.get(sev, colors.text_primary)
        indicator = QFrame()
        indicator.setFixedSize(8, 8)
        indicator.setObjectName("severityIndicator")
        indicator.setStyleSheet(
            f"#severityIndicator {{ background-color: {severity_color}; border-radius: 4px; }}"
        )
        header.addWidget(indicator)

        title_label = QLabel(self._narrative.title)
        title_label.setStyleSheet(font_style("subtitle", weight=600))
        header.addWidget(title_label, 1)

        self._toggle_btn = QPushButton("▸" if not self._expanded else "▾")
        self._toggle_btn.setFixedSize(28, 28)
        self._toggle_btn.setAccessibleName("Expand card" if not self._expanded else "Collapse card")
        self._toggle_btn.setStyleSheet("border: none; font-size: 14px;")
        self._toggle_btn.clicked.connect(self._toggle)
        header.addWidget(self._toggle_btn)

        layout.addLayout(header)

        self._summary_label = QLabel(self._narrative.summary)
        self._summary_label.setWordWrap(True)
        self._summary_label.setStyleSheet(font_style("body") + f" color: {colors.text_secondary};")
        self._summary_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout.addWidget(self._summary_label)

        self._body_widget = QWidget()
        body_layout = QVBoxLayout(self._body_widget)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(4)

        if self._narrative.body:
            body_label = QLabel(self._narrative.body)
            body_label.setWordWrap(True)
            body_label.setStyleSheet(font_style("body") + f" color: {colors.text_primary};")
            body_layout.addWidget(body_label)

        if self._narrative.action_items:
            actions_label = QLabel("Actions:")
            actions_label.setStyleSheet(font_style("caption", weight=600))
            body_layout.addWidget(actions_label)

            for item in self._narrative.action_items:
                action_btn = QPushButton(f"  \u2192 {item}")
                action_btn.setFlat(True)
                action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                action_btn.setStyleSheet(
                    f"text-align: left; padding: 2px 0; {font_style('caption')} color: {colors.primary};"
                )
                action_btn.clicked.connect(lambda checked, a=item: self.action_clicked.emit(a))
                body_layout.addWidget(action_btn)

        body_layout.addStretch()
        self._body_widget.setVisible(self._expanded)
        layout.addWidget(self._body_widget)

    def _toggle(self) -> None:
        self._expanded = not self._expanded
        self._body_widget.setVisible(self._expanded)
        self._toggle_btn.setText("\u25BE" if self._expanded else "\u25B8")
        self._toggle_btn.setAccessibleName("Collapse card" if self._expanded else "Expand card")
        self.expand_clicked.emit()

    def narrative(self) -> Narrative:
        return self._narrative


class CoachCardStack(QFrame):
    """Vertical stack of CoachCards."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(8)
        self._layout.addStretch()
        self._cards: list[CoachCard] = []

    def add_card(self, narrative: Narrative) -> None:
        card = CoachCard(narrative, self)
        self._cards.append(card)
        self._layout.insertWidget(self._layout.count() - 1, card)

    def clear(self) -> None:
        for card in self._cards:
            card.deleteLater()
        self._cards.clear()

    def narratives(self) -> list[Narrative]:
        return [c.narrative() for c in self._cards]
