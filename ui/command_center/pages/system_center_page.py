from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ui.design_system.components import StatusBadge, StatusLevel
from ui.design_system.layout import (
    EditorialGrid,
    KpiItem,
    KpiStrip,
    PanelSpan,
    ScrollContainer,
    SectionPanel,
)
from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.visualization import ConfidenceGauge
from ui.design_system.tokens.radius import RadiusTokens

R = RadiusTokens()



class SystemCenterPage(QWidget):
    view_logs_clicked = Signal()
    run_diagnostics_clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()
        self._wire_buttons()

    def _wire_buttons(self) -> None:
        self._logs_btn.clicked.connect(self.view_logs_clicked.emit)
        self._diag_btn.clicked.connect(self.run_diagnostics_clicked.emit)

    def _colors(self):
        return color_from_scheme(ColorScheme.DARK)

    def _build_ui(self) -> None:
        scroll = ScrollContainer()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        content_layout = scroll._wrapper.layout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self._build_status_bar(content_layout)
        self._build_kpi_ribbon(content_layout)
        self._build_capability_grid(content_layout)
        self._build_bottom_grid(content_layout)

        content_layout.addStretch()

    def _build_status_bar(self, parent: QVBoxLayout) -> None:
        colors = self._colors()
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.surface};
                border-bottom: 1px solid {colors.border};
            }}
        """)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 32, 32, 28)
        layout.setSpacing(16)

        top = QHBoxLayout()
        top.setSpacing(16)

        text_area = QVBoxLayout()
        text_area.setSpacing(4)

        self._hero_title = QLabel("Platform Console")
        self._hero_title.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 28px; font-weight: 800; "
            f"background: transparent; border: none;"
        )
        text_area.addWidget(self._hero_title)

        self._hero_subtitle = QLabel("Platform status, architecture health, and release readiness.")
        self._hero_subtitle.setStyleSheet(
            f"color: {colors.text_secondary}; font-size: 15px; "
            f"background: transparent; border: none;"
        )
        self._hero_subtitle.setWordWrap(True)
        text_area.addWidget(self._hero_subtitle)
        text_area.addStretch()
        top.addLayout(text_area, 1)

        actions = QVBoxLayout()
        actions.setSpacing(8)

        self._logs_btn = QPushButton("View Logs")
        self._logs_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.primary};
                color: white;
                border: none;
                border-radius: {R.lg};
                padding: 0 24px;
                font-size: 14px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {colors.primary_hover};
            }}
        """)
        self._logs_btn.setCursor(Qt.PointingHandCursor)
        actions.addWidget(self._logs_btn)

        self._diag_btn = QPushButton("Run Diagnostics")
        self._diag_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {colors.text_secondary};
                border: 1px solid {colors.border};
                border-radius: {R.lg};
                padding: 0 20px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                border-color: {colors.primary};
                color: {colors.primary};
            }}
        """)
        self._diag_btn.setCursor(Qt.PointingHandCursor)
        actions.addWidget(self._diag_btn)

        top.addLayout(actions)
        layout.addLayout(top)

        health_row = QHBoxLayout()
        health_row.setSpacing(24)

        self._hero_gauge = ConfidenceGauge(width=240, height=36)
        self._hero_gauge.set_confidence(0.0, "System Health")
        health_row.addWidget(self._hero_gauge)

        self._health_label = QLabel("System Health: --")
        self._health_label.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 18px; font-weight: 700; "
            f"background: transparent; border: none;"
        )
        health_row.addWidget(self._health_label)

        self._status_badge = StatusBadge(text="Unknown", level=StatusLevel.NEUTRAL)
        health_row.addWidget(self._status_badge)

        health_row.addStretch()
        layout.addLayout(health_row)
        parent.addWidget(container)

    def _build_kpi_ribbon(self, parent: QVBoxLayout) -> None:
        colors = self._colors()
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.background};
                border-bottom: 1px solid {colors.border};
            }}
        """)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 0, 32, 0)

        kpi_items = [
            KpiItem(label="Architecture", value="--", unit="%", accent=colors.primary),
            KpiItem(label="Tests", value="--", unit="%", accent=colors.success),
            KpiItem(label="Docs", value="--", unit="%", accent=colors.info),
            KpiItem(label="Capabilities", value="--", unit="/15", accent=colors.accent),
            KpiItem(label="Runtime", value="--", unit="", accent=colors.text_primary),
        ]
        self._kpi_strip = KpiStrip(items=kpi_items)
        layout.addWidget(self._kpi_strip)
        parent.addWidget(container)

    def _build_capability_grid(self, parent: QVBoxLayout) -> None:
        colors = self._colors()
        container = QFrame()
        container.setStyleSheet(f"QFrame {{ background-color: {colors.background}; border: none; }}")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(32, 24, 32, 0)
        container_layout.setSpacing(12)

        self._capability_section = SectionPanel(title="Capability Progress", subtitle="Feature completion status")

        self._capability_widget = QWidget()
        self._capability_layout = QVBoxLayout(self._capability_widget)
        self._capability_layout.setContentsMargins(0, 0, 0, 0)
        self._capability_layout.setSpacing(8)
        no_data = QLabel("No capability data.")
        no_data.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;"
        )
        self._capability_layout.addWidget(no_data)
        self._capability_section.add_content(self._capability_widget)
        container_layout.addWidget(self._capability_section)
        parent.addWidget(container)

    def _build_bottom_grid(self, parent: QVBoxLayout) -> None:
        colors = self._colors()
        container = QFrame()
        container.setStyleSheet(f"QFrame {{ background-color: {colors.background}; border: none; }}")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(32, 16, 32, 32)
        container_layout.setSpacing(16)

        grid = EditorialGrid()
        grid.set_spacing(16)
        container_layout.addWidget(grid)

        self._release_section = SectionPanel(title="Release Readiness", subtitle="Milestone progress", span=PanelSpan.HALF)
        self._release_label = QLabel("No release data.")
        self._release_label.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;"
        )
        self._release_section.add_content(self._release_label)
        grid.add_section(self._release_section)

        self._kernel_section = SectionPanel(title="Kernel Runtime", subtitle="System operations", span=PanelSpan.HALF)
        self._kernel_label = QLabel("No kernel data.")
        self._kernel_label.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;"
        )
        self._kernel_section.add_content(self._kernel_label)
        grid.add_section(self._kernel_section)

        parent.addWidget(container)

    def update_data(self, data: Any) -> None:
        colors = self._colors()
        system = _dict_val(data, "system")
        health = system.get("system_health", {})
        overall = health.get("overall", 0.0) if health else 0.0
        rating = health.get("rating", "") if health else ""

        self._hero_gauge.set_confidence(overall / 100 if overall > 1 else overall, "System Health")
        self._health_label.setText(f"System Health: {overall:.0f}%")

        if not rating:
            self._status_badge.set_text("Unknown")
            self._status_badge.set_level(StatusLevel.NEUTRAL)
        elif rating.lower() == "healthy":
            self._status_badge.set_text("Operational")
            self._status_badge.set_level(StatusLevel.SUCCESS)
        elif rating.lower() in ("degraded", "warning"):
            self._status_badge.set_text("Degraded")
            self._status_badge.set_level(StatusLevel.WARNING)
        elif rating.lower() == "critical":
            self._status_badge.set_text("Critical")
            self._status_badge.set_level(StatusLevel.ERROR)
        else:
            self._status_badge.set_text(rating.capitalize() if rating else "Unknown")
            self._status_badge.set_level(StatusLevel.NEUTRAL)

        arch = health.get("architecture", 0.0) if health else 0.0
        tests = health.get("test_coverage", 0.0) if health else 0.0
        docs = health.get("documentation", 0.0) if health else 0.0
        product = system.get("product_state", {})
        caps_active = product.get("capabilities_active", 0) if product else 0
        total_caps = product.get("total_capabilities", 15) if product else 15

        kernel = system.get("kernel_runtime", {})
        uptime = kernel.get("uptime", "--") if kernel else "--"

        kpi_items = [
            KpiItem(label="Architecture", value=f"{arch:.0f}", unit="%", accent=colors.primary),
            KpiItem(label="Tests", value=f"{tests:.0f}", unit="%", accent=colors.success),
            KpiItem(label="Docs", value=f"{docs:.0f}", unit="%", accent=colors.info),
            KpiItem(label="Capabilities", value=f"{caps_active}", unit=f"/{total_caps}", accent=colors.accent),
            KpiItem(label="Runtime", value=uptime, unit="", accent=colors.text_primary),
        ]
        self._kpi_strip.set_items(kpi_items)

        caps = system.get("capability_progress", {})
        self._capability_layout = self._capability_widget.layout()
        self._clear_layout(self._capability_layout)
        if caps:
            cap_list = caps.get("capabilities", [])
            if cap_list:
                for cap in cap_list:
                    name = cap if isinstance(cap, str) else cap.get("name", str(cap))
                    pct = cap.get("progress", 0) if isinstance(cap, dict) else 0
                    bar_blocks = max(1, pct // 10)
                    empty_blocks = max(0, 10 - bar_blocks)
                    bar = f"{'|' * bar_blocks}{'.' * empty_blocks}"
                    lbl = QLabel(f"  {name:<30} {bar} {pct}%")
                    lbl.setStyleSheet(f"color: {colors.text_primary}; font-size: 12px; background: transparent; border: none;")
                    self._capability_layout.addWidget(lbl)
            else:
                total = caps.get("total", 0) or 0
                complete = caps.get("complete", 0) or 0
                in_prog = caps.get("in_progress", 0) or 0
                not_started = caps.get("not_started", 0) or 0
                for label, val in [("Total", total), ("Complete", complete),
                                   ("In Progress", in_prog), ("Not Started", not_started)]:
                    lbl = QLabel(f"  {label}: {val}")
                    lbl.setStyleSheet(f"color: {colors.text_primary}; font-size: 12px; background: transparent; border: none;")
                    self._capability_layout.addWidget(lbl)
        else:
            lbl = QLabel("No capability data.")
            lbl.setStyleSheet(f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;")
            self._capability_layout.addWidget(lbl)

        release = system.get("release_readiness", {})
        self._release_section.clear()
        if release:
            score = release.get("readiness_score", 0.0) or 0.0
            blocking = release.get("blocking_issues", 0) or 0
            gaps = release.get("unmet_milestones", 0) or 0
            version = release.get("version", "v0.5.0") or "v0.5.0"
            lbl1 = QLabel(f"Version: {version}  |  Readiness: {score:.0f}%")
            lbl1.setStyleSheet(f"color: {colors.text_primary}; font-size: 14px; font-weight: 600; background: transparent; border: none;")
            self._release_section.add_content(lbl1)
            lbl2 = QLabel(f"Blocking issues: {blocking}  |  Unmet milestones: {gaps}")
            lbl2.setStyleSheet(f"color: {colors.text_secondary}; font-size: 13px; background: transparent; border: none;")
            self._release_section.add_content(lbl2)
        else:
            lbl = QLabel("No release data.")
            lbl.setStyleSheet(f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;")
            self._release_section.add_content(lbl)

        self._kernel_section.clear()
        if kernel:
            status = kernel.get("status", "--")
            uptime = kernel.get("uptime", "--")
            plugins = kernel.get("active_plugins", 0)
            memory = kernel.get("memory_usage", "--")
            for label, val in [("Status", status), ("Uptime", uptime),
                               ("Active Plugins", str(plugins)), ("Memory", memory)]:
                lbl = QLabel(f"  {label}: {val}")
                lbl.setStyleSheet(f"color: {colors.text_primary}; font-size: 12px; background: transparent; border: none;")
                self._kernel_section.add_content(lbl)
        else:
            lbl = QLabel("No kernel data.")
            lbl.setStyleSheet(f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;")
            self._kernel_section.add_content(lbl)

    def _clear_layout(self, layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


def _dict_val(data: Any, key: str) -> dict:
    val = getattr(data, key, {})
    return val if isinstance(val, dict) else {}
