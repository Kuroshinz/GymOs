from __future__ import annotations

import logging
from PySide6.QtCore import QObject
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QMainWindow, QSystemTrayIcon, QStyle

logger = logging.getLogger("ui.desktop_integration")


class DesktopIntegrationManager(QObject):
    """Manages system tray, notifications, and desktop integrations."""

    def __init__(self, main_window: QMainWindow) -> None:
        super().__init__(main_window)
        self._window = main_window
        self._tray_icon: QSystemTrayIcon | None = None
        self._setup_tray()

    def _setup_tray(self) -> None:
        if not QSystemTrayIcon.isSystemTrayAvailable():
            logger.warning("System tray is not available on this platform")
            return

        # Load a default computer or message icon from style
        app_icon = self._window.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        
        self._tray_icon = QSystemTrayIcon(app_icon, self._window)
        self._tray_icon.setToolTip("GymOS")

        # Tray menu
        menu = QMenu()
        
        show_action = QAction("Show Dashboard", self)
        show_action.triggered.connect(self._show_window)
        menu.addAction(show_action)

        hide_action = QAction("Hide to Tray", self)
        hide_action.triggered.connect(self._hide_window)
        menu.addAction(hide_action)
        
        menu.addSeparator()
        
        quit_action = QAction("Quit GymOS", self)
        quit_action.triggered.connect(self._quit_app)
        menu.addAction(quit_action)
        
        self._tray_icon.setContextMenu(menu)
        
        # Click/Double click trigger
        self._tray_icon.activated.connect(self._tray_activated)
        self._tray_icon.show()
        logger.info("System tray initialized successfully")

    def _tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            if self._window.isVisible():
                self._hide_window()
            else:
                self._show_window()

    def _show_window(self) -> None:
        self._window.show()
        self._window.raise_()
        self._window.activateWindow()

    def _hide_window(self) -> None:
        self._window.hide()

    def _quit_app(self) -> None:
        if self._tray_icon:
            self._tray_icon.hide()
        self._window.close()

    def send_notification(
        self,
        title: str,
        message: str,
        icon_type: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.MessageIcon.Information
    ) -> None:
        """Send a native OS notification via the system tray."""
        if self._tray_icon and self._tray_icon.isVisible():
            self._tray_icon.showMessage(title, message, icon_type, 5000)
