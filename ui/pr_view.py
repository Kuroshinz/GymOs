"""Personal Records screen — displays all PRs with best weight, reps, volume, e1RM using Qt Quick."""

from datetime import date, datetime
from typing import Any

from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import QVBoxLayout, QWidget
from PySide6.QtQuickWidgets import QQuickWidget


class PRView(QWidget):
    """Personal Records screen — displays all PRs using Qt Quick (QML)."""

    def __init__(self, db_or_repo: Any) -> None:
        super().__init__()
        from shared.interfaces import IProgressRepository
        from shared.database.repositories import SQLiteProgressRepository

        if isinstance(db_or_repo, IProgressRepository):
            self._progress_repo = db_or_repo
            self._db = getattr(db_or_repo, "_db", db_or_repo)
        else:
            self._progress_repo = SQLiteProgressRepository(db_or_repo)
            self._db = db_or_repo

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # QQuickWidget hosting the premium QML scene
        self._quick_widget = QQuickWidget()
        self._quick_widget.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self._quick_widget.setAttribute(Qt.WA_AlwaysStackOnTop, True)
        self._quick_widget.setClearColor(Qt.transparent)

        import os
        from shared.helpers.resources import resource_path
        qml_path = resource_path(os.path.join("ui", "resources", "qml", "PRView.qml"))
        self._quick_widget.setSource(QUrl.fromLocalFile(qml_path))

        layout.addWidget(self._quick_widget)

    def refresh(self) -> None:
        """Reload PR data from the repository and push to QML context."""
        from modules.workout.application.pr_engine import PREngine

        engine = PREngine(self._progress_repo)
        prs = engine.get_best_prs()

        prs_data = []
        for pr in prs:
            pr_date_text = ""
            if pr.achieved_at:
                try:
                    pr_date = datetime.fromisoformat(pr.achieved_at).date()
                    days_since = (date.today() - pr_date).days
                    pr_date_text = f"{pr_date.strftime('%b %d, %Y')} · {days_since}d ago"
                except (ValueError, TypeError):
                    pr_date_text = pr.achieved_at

            prs_data.append({
                "exercise_name": pr.exercise_name,
                "pr_type": pr.pr_type,
                "display_value": pr.display_value,
                "improvement_text": pr.improvement_text or "",
                "date_text": pr_date_text
            })

        context = self._quick_widget.rootContext()
        context.setContextProperty("prModel", prs_data)
