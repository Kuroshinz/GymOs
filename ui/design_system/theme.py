"""Global application stylesheet for micro UX polish.

Provides consistent hover, focus, selection, scrollbar, and
animation styling across the entire application.
"""

from __future__ import annotations

from ui.design_system.tokens.color import ColorScheme, color_from_scheme


def _cs(c, name: str) -> str:
    """Safely get a color attribute with fallback to 'transparent'."""
    return str(getattr(c, name, "transparent"))


def global_stylesheet(scheme: ColorScheme = ColorScheme.DARK) -> str:
    """Generate the global application stylesheet.

    Apply via app.setStyleSheet() at startup.
    """
    c = color_from_scheme(scheme)

    bg = _cs(c, "background")
    surface = _cs(c, "surface")
    surface_hover = _cs(c, "surface_hover")
    surface_active = _cs(c, "surface_active")
    border = _cs(c, "border")
    border_hover = _cs(c, "border_hover")
    primary = _cs(c, "primary")
    primary_hover = _cs(c, "primary_hover")
    primary_variant = _cs(c, "primary_variant")
    text_primary = _cs(c, "text_primary")
    text_secondary = _cs(c, "text_secondary")
    text_disabled = _cs(c, "text_disabled")
    text_inverse = _cs(c, "text_inverse")
    scrollbar_bg = _cs(c, "scrollbar_bg")
    scrollbar_handle = _cs(c, "scrollbar_handle")
    scrollbar_hover = _cs(c, "scrollbar_hover")
    focus_ring = _cs(c, "focus_ring")
    success = _cs(c, "success")
    warning = _cs(c, "warning")
    error = _cs(c, "error")

    return f"""
    QWidget {{
        background-color: {bg};
        color: {text_primary};
        font-family: "Inter", "Segoe UI", system-ui, sans-serif;
        font-size: 13px;
    }}

    QWidget:disabled {{
        color: {text_disabled};
    }}

    /* Focus indicator handled by widget-specific :focus selectors */

    QScrollBar:vertical {{
        background: {scrollbar_bg};
        width: 8px;
        margin: 0;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: {scrollbar_handle};
        min-height: 30px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {scrollbar_hover};
    }}
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {{
        background: none;
    }}

    QScrollBar:horizontal {{
        background: {scrollbar_bg};
        height: 8px;
        margin: 0;
        border-radius: 4px;
    }}
    QScrollBar::handle:horizontal {{
        background: {scrollbar_handle};
        min-width: 30px;
        border-radius: 4px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {scrollbar_hover};
    }}
    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal {{
        width: 0;
    }}
    QScrollBar::add-page:horizontal,
    QScrollBar::sub-page:horizontal {{
        background: none;
    }}

    QScrollArea {{
        border: none;
        background: transparent;
    }}

    QPushButton {{
        border: 1px solid {border};
        border-radius: 8px;
        padding: 8px 20px;
        background-color: transparent;
        color: {text_primary};
        font-size: 13px;
        font-weight: 500;
    }}
    QPushButton:hover {{
        background-color: {surface_hover};
        border-color: {primary};
    }}
    QPushButton:pressed {{
        background-color: {surface_active};
        border-color: {primary};
    }}
    QPushButton:focus {{
        border-color: {focus_ring};
    }}
    QPushButton:disabled {{
        background-color: transparent;
        color: {text_disabled};
        border-color: {border};
    }}
    QPushButton[active="true"] {{
        background-color: {primary};
        color: white;
        border-color: {primary};
    }}
    QPushButton[active="true"]:hover {{
        background-color: {primary_hover};
    }}

    QLineEdit, QTextEdit, QPlainTextEdit {{
        background-color: {bg};
        color: {text_primary};
        border: 1px solid {border};
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 13px;
        selection-background-color: {primary_variant};
        selection-color: {text_inverse};
    }}
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
        border-color: {focus_ring};
    }}
    QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover {{
        border-color: {primary};
    }}
    QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
        background-color: transparent;
        color: {text_disabled};
        border-color: {border};
    }}
    QLineEdit[readOnly="true"], QTextEdit[readOnly="true"],
    QPlainTextEdit[readOnly="true"] {{
        background-color: transparent;
    }}

    QComboBox {{
        background-color: {bg};
        color: {text_primary};
        border: 1px solid {border};
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 13px;
        min-width: 100px;
    }}
    QComboBox:hover {{
        border-color: {primary};
    }}
    QComboBox:focus {{
        border-color: {focus_ring};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 28px;
    }}
    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid {text_secondary};
        margin-right: 8px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {surface};
        color: {text_primary};
        border: 1px solid {border};
        border-radius: 6px;
        selection-background-color: {primary_variant};
        selection-color: {text_inverse};
        outline: none;
    }}

    QCheckBox, QRadioButton {{
        spacing: 8px;
        color: {text_primary};
        font-size: 13px;
    }}
    QCheckBox:disabled, QRadioButton:disabled {{
        color: {text_disabled};
    }}
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 2px solid {border};
        border-radius: 4px;
        background-color: transparent;
    }}
    QCheckBox::indicator:hover {{
        border-color: {primary};
    }}
    QCheckBox::indicator:checked {{
        background-color: {primary};
        border-color: {primary};
    }}
    QRadioButton::indicator {{
        width: 18px;
        height: 18px;
        border: 2px solid {border};
        border-radius: 10px;
        background-color: transparent;
    }}
    QRadioButton::indicator:hover {{
        border-color: {primary};
    }}
    QRadioButton::indicator:checked {{
        background-color: {primary};
        border-color: {primary};
    }}

    QSlider::groove:horizontal {{
        background: {border};
        height: 4px;
        border-radius: 2px;
    }}
    QSlider::handle:horizontal {{
        background: {primary};
        width: 16px;
        height: 16px;
        margin: -6px 0;
        border-radius: 8px;
    }}
    QSlider::handle:horizontal:hover {{
        background: {primary_hover};
        width: 20px;
        height: 20px;
        margin: -8px 0;
        border-radius: 10px;
    }}

    QProgressBar {{
        background-color: {border};
        border: none;
        border-radius: 4px;
        height: 8px;
        text-align: center;
        font-size: 10px;
        color: transparent;
    }}
    QProgressBar::chunk {{
        background-color: {primary};
        border-radius: 4px;
    }}

    QToolTip {{
        background-color: {surface};
        color: {text_primary};
        border: 1px solid {border};
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 12px;
    }}

    QMenu {{
        background-color: {surface};
        color: {text_primary};
        border: 1px solid {border};
        border-radius: 8px;
        padding: 4px;
    }}
    QMenu::item {{
        padding: 6px 24px 6px 12px;
        border-radius: 4px;
    }}
    QMenu::item:selected {{
        background-color: {primary_variant};
        color: {text_inverse};
    }}
    QMenu::item:disabled {{
        color: {text_disabled};
    }}
    QMenu::separator {{
        height: 1px;
        background: {border};
        margin: 4px 8px;
    }}

    QTabWidget::pane {{
        background: transparent;
        border: none;
        border-top: 1px solid {border};
    }}
    QTabBar::tab {{
        background: transparent;
        color: {text_secondary};
        border: none;
        padding: 8px 16px;
        font-size: 12px;
        font-weight: 500;
    }}
    QTabBar::tab:selected {{
        color: {primary};
        border-bottom: 2px solid {primary};
    }}
    QTabBar::tab:hover {{
        color: {text_primary};
    }}

    QGroupBox {{
        font-size: 13px;
        font-weight: 600;
        color: {text_primary};
        border: 1px solid {border};
        border-radius: 8px;
        margin-top: 16px;
        padding: 16px 12px 12px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 8px;
        background-color: {bg};
    }}

    QSpinBox, QDoubleSpinBox {{
        background-color: {bg};
        color: {text_primary};
        border: 1px solid {border};
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 13px;
    }}
    QSpinBox:focus, QDoubleSpinBox:focus {{
        border-color: {focus_ring};
    }}
    QSpinBox:hover, QDoubleSpinBox:hover {{
        border-color: {primary};
    }}
    QSpinBox::up-button, QDoubleSpinBox::up-button,
    QSpinBox::down-button, QDoubleSpinBox::down-button {{
        border: none;
        background: transparent;
        width: 20px;
    }}

    QHeaderView::section {{
        background-color: {surface};
        color: {text_secondary};
        border: none;
        border-bottom: 1px solid {border};
        padding: 8px 12px;
        font-size: 11px;
        font-weight: 600;
    }}
    QTableView {{
        background-color: transparent;
        border: 1px solid {border};
        border-radius: 8px;
        gridline-color: {border};
        selection-background-color: {primary_variant};
        selection-color: {text_inverse};
    }}
    QTableView::item {{
        padding: 6px 12px;
    }}
    QTableView::item:hover {{
        background-color: {surface_hover};
    }}
    """
