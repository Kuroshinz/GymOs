from __future__ import annotations

import logging
from typing import Any

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QShortcut
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QMessageBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ui.command_center.controller import CommandCenterController
from ui.command_center.models import CommandCenterData
from ui.command_center.navigation.breadcrumb import Breadcrumb
from ui.command_center.navigation.command_palette import CommandPalette
from ui.command_center.pages.adaptive_center_page import AdaptiveCenterPage
from ui.command_center.pages.analytics_center_page import AnalyticsCenterPage
from ui.command_center.pages.home_page import HomePage
from ui.command_center.pages.knowledge_center_page import KnowledgeCenterPage
from ui.command_center.pages.mission_page import MissionPage
from ui.command_center.pages.planning_page import PlanningPage
from ui.command_center.pages.prediction_center_page import PredictionCenterPage
from ui.command_center.pages.recovery_center_page import RecoveryCenterPage
from ui.command_center.pages.system_center_page import SystemCenterPage
from ui.design_system.components import NavigationItem, NavigationRail, SearchBar
from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.spacing import SpacingTokens
from ui.dialogs import (
    AIConfigurationDialog,
    GoalAdjustmentDialog,
    LogWeightDialog,
    SystemLogViewerDialog,
)
from ui.intelligence import IntelligencePage

logger = logging.getLogger("command_center")
S = SpacingTokens()


class CommandCenter(QWidget):
    def __init__(
        self,
        db: Any = None,
        decision_engine: Any = None,
        pr_engine: Any = None,
        prog_mgr: Any = None,
        nutrition_service: Any = None,
        recovery_service: Any = None,
        prediction_service: Any = None,
        capability_registry: Any = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._db = db
        self._prog_mgr = prog_mgr
        self._decision_engine = decision_engine
        self._pr_engine = pr_engine
        self._nutrition_service = nutrition_service
        self._recovery_service = recovery_service
        self._prediction_service = prediction_service
        self._capability_registry = capability_registry
        self._controller = CommandCenterController(
            db=db, decision_engine=decision_engine, pr_engine=pr_engine,
            prog_mgr=prog_mgr, nutrition_service=nutrition_service,
            recovery_service=recovery_service, prediction_service=prediction_service,
            capability_registry=capability_registry,
        )
        self._pages: dict[str, QWidget] = {}
        self._current_page = "home"
        self._refresh_timer = QTimer()
        self._build_ui()
        self._connect_signals()

    def _colors(self):
        return color_from_scheme(ColorScheme.DARK)

    def _build_ui(self) -> None:
        colors = self._colors()
        self.setStyleSheet(f"background-color: {colors.background};")

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        nav_items = [
            NavigationItem("home", "Executive", "\U0001F3E0"),
            NavigationItem("mission", "Goals", "\U0001F9E0"),
            NavigationItem("planning", "Planning", "\U0001F4CB"),
            NavigationItem("prediction", "Forecast", "\U0001F52E"),
            NavigationItem("recovery", "Recovery", "\U0001F9CD"),
            NavigationItem("knowledge", "Knowledge", "\U0001F4DA"),
            NavigationItem("adaptive", "Optimize", "\U0001F4A1"),
            NavigationItem("intelligence", "Briefing", "\U0001F4AC"),
            NavigationItem("analytics", "Lab", "\U0001F4CA"),
            NavigationItem("system", "Console", "\u2699\uFE0F"),
        ]
        self._nav_rail = NavigationRail(items=nav_items)
        self._nav_rail.item_selected.connect(self._navigate)
        main_layout.addWidget(self._nav_rail)

        center = QVBoxLayout()
        center.setContentsMargins(0, 0, 0, 0)
        center.setSpacing(0)

        top_bar = QFrame()
        top_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.surface};
                border-bottom: 1px solid {colors.border};
            }}
        """)
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(24, 8, 24, 8)
        top_layout.setSpacing(12)

        self._breadcrumb = Breadcrumb()
        top_layout.addWidget(self._breadcrumb, 1)

        self._search = SearchBar(placeholder="Search pages...", shortcut_hint="Ctrl+K")
        self._search.search_submitted.connect(self._handle_command)
        top_layout.addWidget(self._search)

        center.addWidget(top_bar)

        self._stack = QStackedWidget()
        self._stack.setStyleSheet(f"background-color: {colors.background};")
        center.addWidget(self._stack, 1)

        main_layout.addLayout(center, 1)
        self._init_pages()

    def _init_pages(self) -> None:
        home = HomePage()
        mission = MissionPage()
        planning = PlanningPage()
        prediction = PredictionCenterPage()
        recovery = RecoveryCenterPage()
        knowledge = KnowledgeCenterPage()
        adaptive = AdaptiveCenterPage()
        intelligence = IntelligencePage()
        analytics = AnalyticsCenterPage()
        system = SystemCenterPage()

        home.start_workout_clicked.connect(lambda: self._navigate("mission"))
        home.log_weight_clicked.connect(self._on_log_weight)

        mission.adjust_goal_clicked.connect(self._on_adjust_goal)
        mission.view_history_clicked.connect(lambda: self._navigate("analytics"))

        planning.adjust_week_clicked.connect(lambda: self._navigate("mission"))
        planning.view_program_clicked.connect(self._on_view_program)

        prediction.run_scenario_clicked.connect(self._on_run_scenario)
        prediction.export_report_clicked.connect(self._on_export_report)

        recovery.view_details_clicked.connect(self._on_view_details)
        recovery.view_trends_clicked.connect(lambda: self._navigate("analytics"))

        knowledge.explore_graph_clicked.connect(self._on_explore_graph)
        knowledge.search_knowledge_clicked.connect(self._on_search_knowledge)

        adaptive.review_decision_clicked.connect(self._on_review_decision)
        adaptive.run_simulation_clicked.connect(self._on_run_simulation)

        analytics.export_report_clicked.connect(self._on_export_report)
        analytics.compare_periods_clicked.connect(self._on_compare_periods)

        system.view_logs_clicked.connect(self._on_view_logs)
        system.run_diagnostics_clicked.connect(self._on_run_diagnostics)

        intelligence.generate_briefing_clicked.connect(self._on_generate_briefing)
        intelligence.configure_ai_clicked.connect(self._on_configure_ai)

        pages_config = [
            ("home", home), ("mission", mission), ("planning", planning),
            ("prediction", prediction), ("recovery", recovery),
            ("knowledge", knowledge), ("adaptive", adaptive),
            ("intelligence", intelligence), ("analytics", analytics),
            ("system", system),
        ]
        for page_id, page_widget in pages_config:
            self._pages[page_id] = page_widget
            self._stack.addWidget(page_widget)

        self._breadcrumb.set_path("home")
        self._nav_rail.set_active("home")
        self._stack.setCurrentWidget(self._pages["home"])

    def _connect_signals(self) -> None:
        self._controller.data_updated.connect(self._on_data_updated)
        palette_shortcut = QShortcut(Qt.CTRL | Qt.Key_K, self)
        palette_shortcut.activated.connect(self._open_command_palette)
        self._breadcrumb.crumb_clicked.connect(self._navigate)
        self._setup_refresh_timer()

    def _setup_refresh_timer(self) -> None:
        self._refresh_timer.setInterval(60000)
        self._refresh_timer.timeout.connect(self._auto_refresh)
        self._refresh_timer.start()

    def _navigate(self, page_id: str) -> None:
        if page_id in self._pages:
            self._current_page = page_id
            self._stack.setCurrentWidget(self._pages[page_id])
            self._nav_rail.set_active(page_id)
            path = [page_id]
            if page_id != "home":
                path = ["home", page_id]
            parent_pages = {
                "mission": "intelligence", "prediction": "intelligence",
                "recovery": "analytics", "knowledge": "intelligence",
                "adaptive": "intelligence",
            }
            if page_id in parent_pages:
                path = ["home", parent_pages[page_id], page_id]
            self._breadcrumb.set_path(*path)
            self._search.clear()

    def _open_command_palette(self) -> None:
        palette = CommandPalette(self)
        palette.command_selected.connect(self._handle_command)
        palette.exec()

    def _handle_command(self, cmd: str) -> None:
        page_map = {
            "home": "home", "executive": "home",
            "mission": "mission", "goals": "mission",
            "planning": "planning",
            "prediction": "prediction", "forecast": "prediction",
            "recovery": "recovery",
            "knowledge": "knowledge", "explorer": "knowledge",
            "adaptive": "adaptive", "optimize": "adaptive",
            "intelligence": "intelligence", "briefing": "intelligence",
            "analytics": "analytics", "lab": "analytics",
            "system": "system", "console": "system",
        }
        target = page_map.get(cmd)
        if target:
            self._navigate(target)

    # ─── Button Action Handlers ────────────────────────────────────────

    def _on_log_weight(self) -> None:
        if not self._db or not hasattr(self._db, "save_body_weight"):
            QMessageBox.warning(self, "Log Weight", "Database not available.")
            return
        dlg = LogWeightDialog(current_weight=70.0, parent=self)
        dlg.weight_logged.connect(lambda w, d, n: self._save_weight(w, d, n))
        dlg.exec()

    def _save_weight(self, weight: float, date_str: str, notes: str) -> None:
        if self._db and hasattr(self._db, "save_body_weight"):
            from uuid import uuid4

            from modules.workout.domain import BodyWeight
            entry = BodyWeight(id=uuid4().hex[:36], date=date_str, weight_kg=weight, notes=notes)
            self._db.save_body_weight(entry)
            QMessageBox.information(self, "Weight Logged", f"Body weight set to {weight:.1f} kg")

    def _on_adjust_goal(self) -> None:
        if self._decision_engine and hasattr(self._decision_engine, "get_goal_progress"):
            try:
                progress = self._decision_engine.get_goal_progress()
                goal_name = getattr(progress, "goal_name", "Training Goal") if not isinstance(progress, dict) else progress.get("goal_name", "Training Goal")
                pct = getattr(progress, "progress_percent", 0) if not isinstance(progress, dict) else progress.get("progress_percent", 0)
            except Exception:
                goal_name, pct = "Training Goal", 0.0
            dlg = GoalAdjustmentDialog(current_goal=goal_name, progress_percent=float(pct), parent=self)
            dlg.goal_adjusted.connect(lambda g, p: QMessageBox.information(
                self, "Goal Adjusted", f"Goal '{g}' adjusted to {p:.0f}%"
            ))
            dlg.exec()
        else:
            QMessageBox.information(self, "Adjust Goal", "Decision engine not available.")

    def _on_view_program(self) -> None:
        if self._prog_mgr:
            prog = self._prog_mgr.get_active_program()
            if prog:
                name = getattr(prog, "name", "Unknown")
                days = getattr(prog, "days", [])
                msg = f"Program: {name}\nDays: {len(days)}\n"
                for d in days:
                    day_name = getattr(d, "name", "?")
                    ex_names = getattr(d, "exercises", [])
                    msg += f"  {day_name}: {len(ex_names)} exercises\n"
                QMessageBox.information(self, "Active Program", msg)
            else:
                QMessageBox.information(self, "Active Program", "No active program.")

    def _on_run_scenario(self) -> None:
        if self._prediction_service and hasattr(self._prediction_service, "generate_all_predictions"):
            result = self._prediction_service.generate_all_predictions()
            count = getattr(result, "total_predictions", 0)
            QMessageBox.information(self, "Scenario", f"Generated {count} predictions")

    def _on_export_report(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Export Report", "gymos_export.json", "JSON (*.json)")
        if path and self._db and hasattr(self._db, "list_sessions"):
            import datetime
            import json
            sessions = self._db.list_sessions(limit=1000)
            data = {
                "exported_at": datetime.datetime.now().isoformat(),
                "version": "0.5.0",
                "workouts": [vars(s) if hasattr(s, "__dict__") else str(s) for s in sessions],
            }
            with open(path, "w") as f:
                json.dump(data, f, indent=2, default=str)
            QMessageBox.information(self, "Export", f"Exported to {path}")

    def _on_view_details(self) -> None:
        self._navigate("recovery")

    def _on_explore_graph(self) -> None:
        from shared.graph.graph import KnowledgeGraph
        try:
            kg = KnowledgeGraph()
            stats = kg.get_statistics() if hasattr(kg, "get_statistics") else {}
            nodes = stats.get("total_nodes", 0) if isinstance(stats, dict) else 0
            edges = stats.get("total_edges", 0) if isinstance(stats, dict) else 0
            QMessageBox.information(self, "Knowledge Graph", f"{nodes} topics, {edges} connections")
        except Exception:
            QMessageBox.information(self, "Knowledge Graph", "Knowledge graph is ready")

    def _on_search_knowledge(self) -> None:
        from PySide6.QtWidgets import QInputDialog
        query, ok = QInputDialog.getText(self, "Search Knowledge", "Enter search term:")
        if ok and query:
            try:
                from shared.knowledge_evolution.query import KnowledgeQueryEngine
                engine = KnowledgeQueryEngine()
                results = engine.query(query) if hasattr(engine, "query") else []
                count = len(results) if results else 0
                QMessageBox.information(self, "Search Results", f"Found {count} results for '{query}'")
            except Exception:
                QMessageBox.information(self, "Search", "Search not available")

    def _on_review_decision(self) -> None:
        self._navigate("intelligence")

    def _on_run_simulation(self) -> None:
        self._on_run_scenario()

    def _on_compare_periods(self) -> None:
        QMessageBox.information(self, "Compare Periods",
            "Select two date ranges to compare. "
            "This feature is available in a future update.")

    def _on_view_logs(self) -> None:
        dlg = SystemLogViewerDialog(parent=self)
        dlg.start_auto_refresh()
        dlg.exec()
        dlg.stop_auto_refresh()

    def _on_run_diagnostics(self) -> None:
        try:
            from shared.kernel.kernel_health import compute_product_health
            health = compute_product_health()
            overall = getattr(health, "overall", 0.0)
            arch = getattr(health, "architecture_health", 0.0)
            eng = getattr(health, "engineering_health", 0.0)
            msg = (
                f"System Status:\n"
                f"  Overall: {overall:.1f}%\n"
                f"  Stability: {arch:.1f}%\n"
                f"  Performance: {eng:.1f}%"
            )
            QMessageBox.information(self, "System Status", msg)
        except Exception:
            QMessageBox.information(self, "Diagnostics", "Health engine not available.")

    def _on_generate_briefing(self) -> None:
        self._navigate("prediction")

    def _on_configure_ai(self) -> None:
        dlg = AIConfigurationDialog(parent=self)
        dlg.config_applied.connect(lambda cfg: QMessageBox.information(
            self, "AI Configuration",
            f"Configuration applied:\n"
            f"  Mode: {cfg['model']}\n"
            f"  Detail: {cfg['detail_level']}/10\n"
            f"  Auto-analyze: {cfg['auto_analyze']}"
        ))
        dlg.exec()

    def _on_data_updated(self, data: CommandCenterData) -> None:
        for page in self._pages.values():
            if hasattr(page, "update_data"):
                page.update_data(data)

    def refresh(self) -> None:
        self._controller.refresh()

    def refresh_section(self, section: str) -> None:
        self._controller.refresh_section(section)

    def _auto_refresh(self) -> None:
        self._controller.refresh()

    def controller(self) -> CommandCenterController:
        return self._controller
