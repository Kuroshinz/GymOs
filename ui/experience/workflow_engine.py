from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout, QWidget

from ui.command_center.theme import C, Font

logger = logging.getLogger("experience.workflow")


@dataclass
class Step:
    step_id: str
    title: str
    description: str = ""
    widget_factory: Callable[[], QWidget] | None = None
    validator: Callable[[], bool] | None = None
    optional: bool = False


@dataclass
class Workflow:
    workflow_id: str
    title: str
    steps: list[Step] = field(default_factory=list)
    on_complete: Callable[[], None] | None = None
    on_cancel: Callable[[], None] | None = None
    on_step_change: Callable[[int], None] | None = None


class WorkflowDialog(QDialog):
    def __init__(
        self,
        workflow: Workflow,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._workflow = workflow
        self._current_step = 0
        self._step_widgets: list[QWidget] = []
        self._build_ui()
        self._show_step(0)

    def _build_ui(self) -> None:
        self.setWindowTitle(self._workflow.title)
        self.setMinimumSize(600, 400)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {C.BG};
                color: {C.TEXT_PRIMARY};
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        self._title_label = QLabel("")
        self._title_label.setStyleSheet(Font.SUBHEADING)
        layout.addWidget(self._title_label)

        self._desc_label = QLabel("")
        self._desc_label.setStyleSheet(Font.MUTED)
        self._desc_label.setWordWrap(True)
        layout.addWidget(self._desc_label)

        self._content_layout = QVBoxLayout()
        layout.addLayout(self._content_layout, 1)

        self._button_box = QDialogButtonBox()
        self._button_box.setStyleSheet(f"""
            QPushButton {{
                background-color: {C.CARD_BG};
                color: {C.TEXT_PRIMARY};
                border: 1px solid {C.BORDER};
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {C.CARD_HOVER};
                border-color: {C.BORDER_HOVER};
            }}
            QPushButton#primary {{
                background-color: {C.ACCENT};
                color: #FFFFFF;
                border: none;
            }}
            QPushButton#primary:hover {{
                background-color: {C.ACCENT_HOVER};
            }}
        """)
        self._prev_btn = self._button_box.addButton("Back", QDialogButtonBox.ButtonRole.ActionRole)
        self._next_btn = self._button_box.addButton("Next", QDialogButtonBox.ButtonRole.ActionRole)
        self._cancel_btn = self._button_box.addButton("Cancel", QDialogButtonBox.ButtonRole.RejectRole)
        self._prev_btn.clicked.connect(self._on_previous)
        self._next_btn.clicked.connect(self._on_next)
        self._cancel_btn.clicked.connect(self._on_cancel)
        layout.addWidget(self._button_box)

    def _show_step(self, index: int) -> None:
        if index < 0 or index >= len(self._workflow.steps):
            return
        step = self._workflow.steps[index]
        self._title_label.setText(step.title)
        self._desc_label.setText(step.description)
        self._prev_btn.setEnabled(index > 0)
        is_last = index == len(self._workflow.steps) - 1
        self._next_btn.setText("Finish" if is_last else "Next")

        self._clear_content()
        if step.widget_factory:
            w = step.widget_factory()
            self._step_widgets.append(w)
            self._content_layout.addWidget(w)

        if self._workflow.on_step_change:
            self._workflow.on_step_change(index)

    def _clear_content(self) -> None:
        for w in self._step_widgets:
            self._content_layout.removeWidget(w)
            w.deleteLater()
        self._step_widgets.clear()

    def _on_previous(self) -> None:
        if self._current_step > 0:
            self._current_step -= 1
            self._show_step(self._current_step)

    def _on_next(self) -> None:
        step = self._workflow.steps[self._current_step]
        if step.validator and not step.validator():
            return
        if self._current_step >= len(self._workflow.steps) - 1:
            self._finish()
        else:
            self._current_step += 1
            self._show_step(self._current_step)

    def _on_cancel(self) -> None:
        if self._workflow.on_cancel:
            self._workflow.on_cancel()
        self.reject()

    def _finish(self) -> None:
        if self._workflow.on_complete:
            self._workflow.on_complete()
        self.accept()


class WorkflowEngine(QObject):
    workflow_started = Signal(str)
    workflow_completed = Signal(str)
    workflow_cancelled = Signal(str)
    step_changed = Signal(str, int)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._workflows: dict[str, Workflow] = {}

    def register(self, workflow: Workflow) -> None:
        self._workflows[workflow.workflow_id] = workflow

    def unregister(self, workflow_id: str) -> None:
        self._workflows.pop(workflow_id, None)

    def get(self, workflow_id: str) -> Workflow | None:
        return self._workflows.get(workflow_id)

    def start(self, workflow_id: str, parent: QWidget | None = None) -> bool:
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            logger.warning("Workflow '%s' not found", workflow_id)
            return False
        self.workflow_started.emit(workflow_id)
        dialog = WorkflowDialog(workflow, parent)
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            self.workflow_completed.emit(workflow_id)
        else:
            self.workflow_cancelled.emit(workflow_id)
        return True

    @property
    def all_workflows(self) -> list[Workflow]:
        return list(self._workflows.values())

    def search(self, query: str) -> list[Workflow]:
        q = query.lower()
        return [
            w for w in self._workflows.values()
            if q in w.title.lower() or q in w.workflow_id.lower()
        ]
