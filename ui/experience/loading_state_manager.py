from __future__ import annotations

import logging

from PySide6.QtCore import QObject, Qt, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from ui.command_center.theme import C, Font

logger = logging.getLogger("experience.loading")


class SkeletonWidget(QFrame):
    def __init__(self, width: int = 200, height: int = 16, rounded: bool = True, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(width, height)
        self._rounded = rounded
        self._opacity = 0.3
        self.setStyleSheet(f"""
            SkeletonWidget {{
                background-color: {C.BORDER};
                border-radius: {'4px' if rounded else '0px'};
            }}
        """)
        self._setup_pulse()

    def _setup_pulse(self) -> None:
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._pulse)
        self._timer.start(1500)
        self._direction = 1
        self._step = 0

    def _pulse(self) -> None:
        self._step += self._direction
        if self._step >= 5:
            self._direction = -1
        elif self._step <= 0:
            self._direction = 1
        alpha = 0.2 + (self._step / 5) * 0.4
        self.setStyleSheet(f"""
            SkeletonWidget {{
                background-color: rgba(51, 65, 85, {alpha});
                border-radius: {'4px' if self._rounded else '0px'};
            }}
        """)

    def stop(self) -> None:
        self._timer.stop()


class SkeletonBlock(QFrame):
    def __init__(
        self,
        lines: int = 3,
        line_height: int = 14,
        spacing: int = 10,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {C.CARD_BG}; border-radius: 12px; border: 1px solid {C.BORDER};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(spacing)
        for _ in range(lines):
            w = int(200 + (hash(str(_)) % 100))
            skeleton = SkeletonWidget(width=w, height=line_height, parent=self)
            layout.addWidget(skeleton)
        layout.addStretch()
        self._skeletons = self.findChildren(SkeletonWidget)

    def stop(self) -> None:
        for s in self._skeletons:
            s.stop()


class LoadingOverlay(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("""
            LoadingOverlay {
                background-color: rgba(15, 23, 42, 180);
                border-radius: 0px;
            }
        """)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._spinner = QLabel("⟳")
        self._spinner.setStyleSheet(f"color: {C.ACCENT}; font-size: 36px;")
        self._spinner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._spinner)

        self._message = QLabel("Loading...")
        self._message.setStyleSheet(Font.MUTED)
        self._message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._message)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._spin)
        self._timer.start(100)
        self._angle = 0

    def set_message(self, text: str) -> None:
        self._message.setText(text)

    def _spin(self) -> None:
        self._angle = (self._angle + 45) % 360
        self._spinner.setText(chr(0x27F3))

    def stop(self) -> None:
        self._timer.stop()
        self.hide()


class ProgressIndicator(QFrame):
    def __init__(self, determinate: bool = True, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._determinate = determinate
        self.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self._bar = QProgressBar(self)
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        self._bar.setTextVisible(False)
        self._bar.setFixedHeight(4)
        self._bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {C.BORDER};
                border: none;
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {C.ACCENT};
                border-radius: 2px;
            }}
        """)
        layout.addWidget(self._bar)

        self._label = QLabel("0%")
        self._label.setStyleSheet(Font.CAPTION)
        layout.addWidget(self._label)

        if not determinate:
            self._start_indeterminate()

    def _start_indeterminate(self) -> None:
        self._bar.setRange(0, 0)

    def set_progress(self, value: int) -> None:
        if self._determinate:
            self._bar.setValue(value)
            self._label.setText(f"{value}%")

    def set_label(self, text: str) -> None:
        self._label.setText(text)


class LoadingStateManager(QObject):
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._overlays: dict[str, LoadingOverlay] = {}
        self._skeletons: dict[str, SkeletonBlock] = {}

    def show_overlay(self, key: str, parent: QWidget, message: str = "Loading...") -> LoadingOverlay:
        self.hide_overlay(key)
        overlay = LoadingOverlay(parent)
        overlay.set_message(message)
        overlay.setGeometry(parent.rect())
        overlay.show()
        overlay.raise_()
        self._overlays[key] = overlay
        return overlay

    def hide_overlay(self, key: str) -> None:
        overlay = self._overlays.pop(key, None)
        if overlay:
            overlay.stop()
            overlay.deleteLater()

    def show_skeleton(self, key: str, parent: QWidget, lines: int = 3) -> SkeletonBlock:
        self.hide_skeleton(key)
        block = SkeletonBlock(lines=lines, parent=parent)
        parent.layout().addWidget(block) if parent.layout() else None
        self._skeletons[key] = block
        return block

    def hide_skeleton(self, key: str) -> None:
        block = self._skeletons.pop(key, None)
        if block:
            block.stop()
            block.setParent(None)
            block.deleteLater()

    def hide_all(self) -> None:
        for key in list(self._overlays.keys()):
            self.hide_overlay(key)
        for key in list(self._skeletons.keys()):
            self.hide_skeleton(key)
