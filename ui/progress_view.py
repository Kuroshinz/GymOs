"""Progress view — charts for weight trend, body weight, weekly volume."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

try:
    import pyqtgraph as pg
    HAS_PQTG = True
except ImportError:
    HAS_PQTG = False


class ChartWidget(QFrame):
    """Wrapper for a PyQtGraph chart with a title."""

    def __init__(self, title: str):
        super().__init__()
        self.setStyleSheet("""
            ChartWidget {
                background-color: #1E293B;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #F1F5F9; font-size: 15px; font-weight: 600;")
        layout.addWidget(title_label)

        if HAS_PQTG:
            self.plot_widget = pg.PlotWidget()
            self.plot_widget.setBackground("#1E293B")
            self.plot_widget.showGrid(x=True, y=True, alpha=0.2)
            self.plot_widget.setLabel("left", "", color="#94A3B8")
            self.plot_widget.setLabel("bottom", "", color="#94A3B8")
            self.plot_widget.getAxis("left").setPen("#475569")
            self.plot_widget.getAxis("bottom").setPen("#475569")
            layout.addWidget(self.plot_widget)
        else:
            placeholder = QLabel("Install pyqtgraph for charts")
            placeholder.setStyleSheet("color: #64748B; font-size: 13px; padding: 40px;")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(placeholder)
            self.plot_widget = None

    def plot(self, x_data: list, y_data: list, color: str = "#818CF8"):
        if self.plot_widget is None:
            return
        self.plot_widget.clear()
        pen = pg.mkPen(color=color, width=2)
        self.plot_widget.plot(x_data, y_data, pen=pen, symbol="o",
                              symbolSize=6, symbolBrush=color)


class EmptyChart(QFrame):
    """Placeholder chart shown when no data exists."""

    def __init__(self, title: str, message: str):
        super().__init__()
        self.setStyleSheet("""
            EmptyChart {
                background-color: #1E293B;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #F1F5F9; font-size: 15px; font-weight: 600;")
        layout.addWidget(title_label)

        msg = QLabel(message)
        msg.setStyleSheet("color: #64748B; font-size: 13px; padding: 20px;")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(msg)


class ProgressView(QWidget):
    def __init__(self, db):
        super().__init__()
        self._db = db
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        header = QLabel("Progress")
        header.setStyleSheet("font-size: 24px; font-weight: 700; color: #F1F5F9;")
        layout.addWidget(header)

        # Period selector
        period_layout = QHBoxLayout()
        period_layout.setSpacing(8)

        period_label = QLabel("View:")
        period_label.setAccessibleName("Period selector label")
        period_label.setStyleSheet("color: #94A3B8; font-size: 13px;")
        period_layout.addWidget(period_label)

        self._period_combo = QComboBox()
        self._period_combo.setAccessibleName("Progress time period")
        self._period_combo.setToolTip("Select the date range for progress charts")
        self._period_combo.addItems(["Last 30 days", "Last 90 days", "All time"])
        self._period_combo.setStyleSheet("""
            QComboBox {
                background-color: #1E293B;
                color: #F1F5F9;
                border: 1px solid #475569;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
                min-width: 140px;
            }
            QComboBox:focus {
                border-color: #818CF8;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
        """)
        self._period_combo.currentIndexChanged.connect(self.refresh)
        period_layout.addWidget(self._period_combo)
        period_layout.addStretch()
        layout.addLayout(period_layout)

        # Chart: Body Weight
        self._weight_chart = ChartWidget("Body Weight")
        self._weight_chart.setAccessibleName("Body weight chart")
        layout.addWidget(self._weight_chart)

        # Chart: Weekly Volume
        self._volume_chart = ChartWidget("Weekly Volume")
        self._volume_chart.setAccessibleName("Weekly volume chart")
        layout.addWidget(self._volume_chart)

        # Chart: Volume by Muscle Group
        self._muscle_chart = ChartWidget("Volume by Muscle Group (This Week)")
        self._muscle_chart.setAccessibleName("Volume by muscle group chart")
        layout.addWidget(self._muscle_chart)

        layout.addStretch()

    def refresh(self):
        period_map = {0: 30, 1: 90, 2: 365}
        days = period_map.get(self._period_combo.currentIndex(), 90)

        # Body weight chart
        if HAS_PQTG:
            bw_data = self._db.get_body_weight_history(days=days)
            if bw_data:
                dates = [w.date[-5:] for w in bw_data]  # MM-DD
                weights = [w.weight_kg for w in bw_data]
                self._weight_chart.plot(
                    list(range(len(dates))), weights, "#4ADE80"
                )
                # Show last value
                if self._weight_chart.plot_widget:
                    self._weight_chart.plot_widget.setLabel(
                        "bottom", f"Latest: {weights[-1]:.1f} kg",
                        color="#4ADE80"
                    )

            # Volume chart
            vol_data = self._db.get_volume_by_day(days=days)
            if vol_data:
                weeks = [v["week"][-5:] for v in vol_data]
                volumes = [v["volume"] / 1000 for v in vol_data]  # Show in thousands
                self._volume_chart.plot(
                    list(range(len(weeks))), volumes, "#818CF8"
                )

            # Muscle volume chart (bar chart)
            from modules.workout.application.volume_analytics import VolumeAnalytics
            va = VolumeAnalytics(self._db)
            weekly = va.get_weekly_volume(weeks=1)
            if weekly and weekly[0].muscles:
                muscles = weekly[0].muscles
                names = [m.muscle_group.capitalize() for m in muscles]
                sets_count = [m.total_sets for m in muscles]
                if self._muscle_chart.plot_widget:
                    self._muscle_chart.plot_widget.clear()
                    colors = [m.status_color for m in muscles]
                    # Use a bar graph
                    bg = pg.BarGraphItem(
                        x=list(range(len(names))),
                        height=sets_count,
                        width=0.6,
                        brushes=colors,
                    )
                    self._muscle_chart.plot_widget.addItem(bg)
                    # Update labels to show muscle names
                    self._muscle_chart.plot_widget.getAxis("bottom").setTicks(
                        [list(enumerate(names))]
                    )
