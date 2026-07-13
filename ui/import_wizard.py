"""Import Wizard — multi-step dialog for importing workout programs."""

import os

from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWizard,
    QWizardPage,
)

STYLE = """
    QWizard {
        background-color: #0F172A;
        color: #F1F5F9;
    }
    QWizardPage {
        background-color: #0F172A;
        color: #F1F5F9;
    }
    QLabel {
        color: #F1F5F9;
    }
    QPushButton {
        background-color: #818CF8;
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        padding: 8px 20px;
        font-size: 13px;
        font-weight: 600;
    }
    QPushButton:hover { background-color: #6366F1; }
    QPushButton:disabled { background-color: #475569; color: #94A3B8; }
"""


class FileSelectionPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Select File")
        self.setSubTitle("Choose a workout program file to import (.xlsx, .json, .yaml)")

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        self._path_label = QLabel("No file selected")
        self._path_label.setStyleSheet("color: #94A3B8; font-size: 14px; padding: 12px;")
        self._path_label.setWordWrap(True)
        layout.addWidget(self._path_label)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse)
        layout.addWidget(browse_btn)

        layout.addStretch()

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Workout Program",
            "",
            "Program Files (*.xlsx *.json *.yaml *.yml);;Excel (*.xlsx);;JSON (*.json);;YAML (*.yaml *.yml)",
        )
        if path:
            self._path_label.setText(path)
            self._path_label.setStyleSheet("color: #F1F5F9; font-size: 14px; padding: 12px;")

    def get_filepath(self) -> str:
        return self._path_label.text()


class PreviewPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Preview")
        self.setSubTitle("Review the parsed workout program")

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        self._name_label = QLabel("")
        self._name_label.setStyleSheet("font-size: 18px; font-weight: 700; color: #818CF8;")
        layout.addWidget(self._name_label)

        self._desc_label = QLabel("")
        self._desc_label.setStyleSheet("color: #94A3B8; font-size: 13px;")
        self._desc_label.setWordWrap(True)
        layout.addWidget(self._desc_label)

        self._stats_label = QLabel("")
        self._stats_label.setStyleSheet("color: #F1F5F9; font-size: 13px;")
        layout.addWidget(self._stats_label)

        self._day_list = QListWidget()
        self._day_list.setStyleSheet("""
            QListWidget {
                background-color: #1E293B;
                border: 1px solid #475569;
                border-radius: 8px;
                color: #F1F5F9;
                font-size: 13px;
                padding: 8px;
            }
            QListWidget::item { padding: 6px; border-bottom: 1px solid #1E293B; }
        """)
        layout.addWidget(self._day_list)

    def set_preview(self, preview: dict):
        self._name_label.setText(preview.get("name", ""))
        self._desc_label.setText(preview.get("description", ""))
        self._stats_label.setText(
            f"Days: {preview.get('day_count', 0)}  |  "
            f"Exercises: {preview.get('exercise_count', 0)}  |  "
            f"Source: {preview.get('source_file', '')}"
        )
        self._day_list.clear()
        for d in preview.get("days", []):
            ex_count = d.get("exercise_count", 0)
            text = f"{d['name']}  ({ex_count} exercises)"
            item = QListWidgetItem(text)
            self._day_list.addItem(item)


class ImportProgressPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Importing...")
        self.setSubTitle("Validating and saving the program")

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        self._progress = QProgressBar()
        self._progress.setRange(0, 0)
        self._progress.setStyleSheet("""
            QProgressBar {
                background-color: #1E293B;
                border: none;
                border-radius: 8px;
                height: 20px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #818CF8;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self._progress)

        self._status_label = QLabel("Importing program...")
        self._status_label.setStyleSheet("color: #94A3B8; font-size: 14px;")
        layout.addWidget(self._status_label)

        self._error_list = QListWidget()
        self._error_list.setStyleSheet("""
            QListWidget {
                background-color: #1E293B;
                border: 1px solid #475569;
                border-radius: 8px;
                color: #F87171;
                font-size: 12px;
                padding: 8px;
            }
        """)
        self._error_list.setVisible(False)
        layout.addWidget(self._error_list)

        layout.addStretch()

    def set_errors(self, errors: list):
        self._error_list.clear()
        for e in errors:
            msg = e.message
            if e.day:
                msg = f"[{e.day}] {msg}"
            if e.exercise:
                msg = f"{msg} ({e.exercise})"
            self._error_list.addItem(msg)
        self._error_list.setVisible(True)
        self._status_label.setText("Validation failed. Review errors below.")
        self._status_label.setStyleSheet("color: #F87171; font-size: 14px;")


class ImportWizard(QWizard):
    """Multi-step wizard for importing workout programs."""

    def __init__(self, prog_mgr, parent=None):
        super().__init__(parent)
        self._prog_mgr = prog_mgr
        self.setWindowTitle("Import Workout Program")
        self.setMinimumSize(600, 500)
        self.setStyleSheet(STYLE)

        self._file_page = FileSelectionPage()
        self._preview_page = PreviewPage()
        self._progress_page = ImportProgressPage()

        self.addPage(self._file_page)
        self.addPage(self._preview_page)
        self.addPage(self._progress_page)

        self.currentIdChanged.connect(self._on_page_changed)

    def _on_page_changed(self, page_id: int):
        if page_id == 1:
            self._do_preview()
        elif page_id == 2:
            self._do_import()

    def _do_preview(self):
        filepath = self._file_page.get_filepath()
        if not filepath or not os.path.exists(filepath):
            QMessageBox.warning(self, "Error", "Please select a valid file.")
            self.back()
            return
        try:
            preview = self._prog_mgr.preview(filepath)
            self._preview_page.set_preview(preview)
        except Exception:
            import logging
            logging.getLogger(__name__).exception("Preview failed")
            QMessageBox.critical(self, "Import Error",
                "Could not read the selected file. "
                "Please make sure it is a valid workout program "
                "(.xlsx, .json, .yaml) and try again.")
            self.back()

    def _do_import(self):
        filepath = self._file_page.get_filepath()
        try:
            program_id, result = self._prog_mgr.import_save_and_activate(filepath)
            if result.passed:
                self._progress_page._status_label.setText("Program imported and activated successfully!")
                self._progress_page._status_label.setStyleSheet("color: #4ADE80; font-size: 14px;")
                self._progress_page._progress.setRange(0, 100)
                self._progress_page._progress.setValue(100)
            else:
                self._progress_page.set_errors(result.errors)
        except Exception:
            import logging
            logging.getLogger(__name__).exception("Import failed")
            self._progress_page._status_label.setText(
                "Import failed. Please check the file and try again.")
            self._progress_page._status_label.setStyleSheet("color: #F87171; font-size: 14px;")
