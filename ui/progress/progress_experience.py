from __future__ import annotations

from datetime import date, datetime
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ui.design_system.components.chart_container import ChartContainer
from ui.design_system.components.section_header import SectionHeader
from ui.design_system.components.status_badge import StatusBadge, StatusLevel
from ui.design_system.layout import PanelSpan, SectionPanel
from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens, px_from_token
from ui.design_system.tokens.spacing import SpacingTokens
from ui.design_system.tokens.typography import TypographyTokens, font_style
from ui.design_system.visualization import WeeklyTimeline
from ui.narrative import CoachCardStack
from ui.narrative.engine import Narrative
from ui.visualization.charts import BarChart, RadarChart, TrendChart

S = SpacingTokens()
R = RadiusTokens()
T = TypographyTokens()

_px4 = px_from_token(S.s1)
_px6 = px_from_token(S.s1_5)
_px8 = px_from_token(S.s2)
_px12 = px_from_token(S.s3)
_px16 = px_from_token(S.s4)
_px24 = px_from_token(S.s6)
_px32 = px_from_token(S.s8)


class ProgressExperience(QWidget):
    def __init__(self, db: Any, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._db = db
        self._period_days = 90
        self._build_ui()

    def _colors(self):
        return color_from_scheme(ColorScheme.DARK)

    def _build_ui(self) -> None:
        from ui.design_system.layout.scroll_container import ScrollContainer
        scroll = ScrollContainer()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        main = QVBoxLayout()
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)
        scroll.content_layout.insertLayout(0, main)

        self._build_hero(main)
        self._build_period_selector(main)
        self._build_body_weight(main)
        self._build_weekly_volume(main)
        self._build_muscle_balance(main)
        self._build_personal_records(main)
        self._build_compliance(main)
        self._build_next_milestone(main)
        self._build_insights(main)

        main.addStretch()

    def _build_section_header(self, parent: QVBoxLayout, title: str, subtitle: str) -> None:
        header = SectionHeader(title=title, subtitle=subtitle)
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, _px24, 0, _px8)
        hbox.addWidget(header)
        parent.addLayout(hbox)

    def _build_hero(self, parent: QVBoxLayout) -> None:
        colors = self._colors()
        hero = QFrame()
        hero.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.surface};
                border-radius: {R.xl};
                border: 1px solid {colors.border};
            }}
        """)
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(24, 20, 24, 20)
        hero_layout.setSpacing(16)

        accent = QFrame()
        accent.setFixedWidth(4)
        accent.setStyleSheet(f"background-color: {colors.accent}; border-radius: {R.sm}; border: none;")
        hero_layout.addWidget(accent)

        text_area = QVBoxLayout()
        text_area.setSpacing(6)

        hour = datetime.now().hour
        greeting = "Good Morning" if hour < 12 else "Good Afternoon" if hour < 18 else "Good Evening"
        self._hero_greeting = QLabel(f"{greeting}")
        self._hero_greeting.setStyleSheet(f"color: {colors.text_primary}; {font_style('h4')}")
        text_area.addWidget(self._hero_greeting)

        self._hero_subtitle = QLabel("Here's how your training is progressing")
        self._hero_subtitle.setStyleSheet(f"color: {colors.text_secondary}; {font_style('body_small')}")
        self._hero_subtitle.setWordWrap(True)
        text_area.addWidget(self._hero_subtitle)

        text_area.addStretch()
        hero_layout.addLayout(text_area, 1)

        self._kpi_layout = QHBoxLayout()
        self._kpi_layout.setSpacing(_px16)
        self._kpi_labels: dict[str, QLabel] = {}
        kpi_items = [
            ("workouts", "Workouts", "--"),
            ("prs", "PRs", "--"),
            ("streak", "Streak", "--"),
            ("volume", "Volume", "--"),
        ]
        for key, label, default in kpi_items:
            kpi = QFrame()
            kpi.setStyleSheet(f"QFrame {{ background: transparent; border: none; }}")
            kpi_layout = QVBoxLayout(kpi)
            kpi_layout.setContentsMargins(0, 0, 0, 0)
            kpi_layout.setSpacing(2)

            val = QLabel(default)
            val.setStyleSheet(f"color: {colors.text_primary}; {font_style('h2')}; background: transparent;")
            val.setAlignment(Qt.AlignCenter)
            kpi_layout.addWidget(val)
            self._kpi_labels[key] = val

            lbl = QLabel(label)
            lbl.setStyleSheet(f"color: {colors.text_disabled}; {font_style('caption')}; background: transparent;")
            lbl.setAlignment(Qt.AlignCenter)
            kpi_layout.addWidget(lbl)

            self._kpi_layout.addWidget(kpi)

        hero_layout.addLayout(self._kpi_layout)
        parent.addWidget(hero)

    def _build_period_selector(self, parent: QVBoxLayout) -> None:
        colors = self._colors()
        row = QHBoxLayout()
        row.setContentsMargins(0, _px16, 0, 0)
        row.setSpacing(8)

        lbl = QLabel("Period:")
        lbl.setStyleSheet(f"color: {colors.text_secondary}; {font_style('body_small')}; background: transparent;")
        row.addWidget(lbl)

        self._period_combo = QComboBox()
        self._period_combo.addItems(["Last 30 days", "Last 90 days", "All time"])
        self._period_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {colors.surface};
                color: {colors.text_primary};
                border: 1px solid {colors.border};
                border-radius: {R.md};
                padding: 0 12px;
                {font_style('body_small')}
                min-width: 140px;
            }}
            QComboBox:focus {{ border-color: {colors.focus_ring}; }}
            QComboBox::drop-down {{ border: none; }}
        """)
        self._period_combo.currentIndexChanged.connect(self._on_period_changed)
        row.addWidget(self._period_combo)
        row.addStretch()

        parent.addLayout(row)

    def _on_period_changed(self, index: int) -> None:
        period_map = {0: 30, 1: 90, 2: 365}
        self._period_days = period_map.get(index, 90)
        self.refresh()

    def _build_body_weight(self, parent: QVBoxLayout) -> None:
        self._build_section_header(parent, "Body Weight", "Track your weight trend over time")
        self._weight_chart_container = ChartContainer(title="Body Weight", subtitle="")
        self._weight_chart = TrendChart()
        self._weight_chart_container.set_chart(self._weight_chart)
        self._weight_empty = QLabel("No body weight data logged yet")
        self._weight_empty.setStyleSheet(f"color: {self._colors().text_disabled}; {font_style('body_small')}")
        self._weight_empty.setAlignment(Qt.AlignCenter)
        parent.addWidget(self._weight_chart_container)

    def _build_weekly_volume(self, parent: QVBoxLayout) -> None:
        self._build_section_header(parent, "Weekly Volume", "Total training volume per week")
        self._volume_chart_container = ChartContainer(title="Volume (kg)", subtitle="")
        self._volume_chart = BarChart(orientation="vertical")
        self._volume_chart_container.set_chart(self._volume_chart)
        self._volume_empty = QLabel("No volume data yet. Complete a workout to see your progress.")
        self._volume_empty.setStyleSheet(f"color: {self._colors().text_disabled}; {font_style('body_small')}")
        self._volume_empty.setAlignment(Qt.AlignCenter)
        parent.addWidget(self._volume_chart_container)

    def _build_muscle_balance(self, parent: QVBoxLayout) -> None:
        self._build_section_header(parent, "Muscle Balance", "Volume distribution by muscle group")
        self._muscle_layout = QHBoxLayout()
        self._muscle_layout.setSpacing(_px16)

        self._radar_chart = RadarChart()
        self._muscle_layout.addWidget(self._radar_chart)

        self._muscle_detail = QVBoxLayout()
        self._muscle_detail.setSpacing(_px4)
        self._muscle_detail_widget = QWidget()
        self._muscle_detail_widget.setLayout(self._muscle_detail)

        self._muscle_empty = QLabel("Complete a workout to see muscle balance.")
        self._muscle_empty.setStyleSheet(f"color: {self._colors().text_disabled}; {font_style('body_small')}")
        self._muscle_empty.setAlignment(Qt.AlignCenter)

        self._muscle_empty_widget = QWidget()
        mel = QVBoxLayout(self._muscle_empty_widget)
        mel.addWidget(self._muscle_empty)

        self._muscle_layout.addWidget(self._muscle_detail_widget, 1)
        self._muscle_layout.addWidget(self._muscle_empty_widget, 1)
        self._muscle_detail_widget.hide()
        parent.addLayout(self._muscle_layout)

    def _build_personal_records(self, parent: QVBoxLayout) -> None:
        self._build_section_header(parent, "Personal Records", "Your best performances")
        self._pr_grid = QGridLayout()
        self._pr_grid.setContentsMargins(0, 0, 0, 0)
        self._pr_grid.setSpacing(_px12)

        self._pr_empty = QLabel("No PRs yet. Push yourself in your next workout!")
        self._pr_empty.setStyleSheet(f"color: {self._colors().text_disabled}; {font_style('body_small')}")
        self._pr_empty.setAlignment(Qt.AlignCenter)
        self._pr_empty.setWordWrap(True)

        self._pr_empty_widget = QWidget()
        pr_el = QVBoxLayout(self._pr_empty_widget)
        pr_el.addWidget(self._pr_empty)

        parent.addLayout(self._pr_grid)

    def _build_compliance(self, parent: QVBoxLayout) -> None:
        self._build_section_header(parent, "Compliance & Consistency", "Session adherence and recovery trend")
        self._compliance_layout = QVBoxLayout()
        self._compliance_layout.setContentsMargins(0, 0, 0, 0)
        self._compliance_layout.setSpacing(_px8)
        self._compliance_timeline = WeeklyTimeline()
        self._compliance_label = QLabel("")
        self._compliance_label.setStyleSheet(f"color: {self._colors().text_disabled}; {font_style('caption')}")
        self._compliance_label.setAlignment(Qt.AlignCenter)

        self._compliance_empty = QLabel("Compliance data will appear after completing workouts.")
        self._compliance_empty.setStyleSheet(f"color: {self._colors().text_disabled}; {font_style('body_small')}")
        self._compliance_empty.setAlignment(Qt.AlignCenter)

        self._compliance_layout.addWidget(self._compliance_empty)
        parent.addLayout(self._compliance_layout)

    def _build_next_milestone(self, parent: QVBoxLayout) -> None:
        self._build_section_header(parent, "Next Milestone", "Your closest achievement target")
        self._milestone_panel = SectionPanel(title="", subtitle="", span=PanelSpan.FULL)
        self._milestone_icon = QLabel("")
        self._milestone_title = QLabel("No milestone set")
        self._milestone_desc = QLabel("Complete workouts and log body weight to track progress toward your goals.")
        self._milestone_eta = QLabel("")
        self._milestone_empty = QLabel("Set a body weight or strength goal to see your next milestone.")
        parent.addWidget(self._milestone_panel)

    def _build_insights(self, parent: QVBoxLayout) -> None:
        self._build_section_header(parent, "Insights", "Personalised coaching notes")
        self._insights_stack = CoachCardStack()
        parent.addWidget(self._insights_stack)

    # ── Refresh ──────────────────────────────────────────────

    def refresh(self) -> None:
        self._update_hero()
        self._update_body_weight()
        self._update_weekly_volume()
        self._update_muscle_balance()
        self._update_personal_records()
        self._update_compliance()
        self._update_next_milestone()
        self._update_insights()

    def _update_hero(self) -> None:
        colors = self._colors()
        days = self._period_days

        sessions = self._db.list_sessions(limit=200) if hasattr(self._db, "list_sessions") else []
        sessions_in_period = [
            s for s in sessions
            if s.started_at and hasattr(s, "started_at")
        ]

        recent_workouts = sum(
            1 for s in sessions_in_period
            if s.completed_at
        )

        pr_count = "--"
        streak = "--"
        total_vol = "--"

        from modules.workout.application.pr_engine import PREngine
        try:
            engine = PREngine(self._db)
            prs = engine.get_best_prs()
            pr_count = str(len(prs))
        except Exception:
            pass

        sessions_7d = [s for s in sessions if s.started_at]
        try:
            from datetime import timedelta
            week_ago = datetime.now() - timedelta(days=7)
            streak_count = 0
            for s in sorted(sessions_7d, key=lambda x: x.started_at or "", reverse=True):
                if s.completed_at:
                    s_date = datetime.fromisoformat(s.started_at) if isinstance(s.started_at, str) else s.started_at
                    if s_date >= week_ago:
                        streak_count += 1
                    else:
                        break
            streak = f"{streak_count}/7"
        except Exception:
            pass

        try:
            vol_data = self._db.get_volume_by_day(days=days)
            total_vol = f"{sum(v['volume'] for v in vol_data) / 1000:.0f}k"
        except Exception:
            pass

        self._kpi_labels["workouts"].setText(str(recent_workouts))
        self._kpi_labels["prs"].setText(pr_count)
        self._kpi_labels["streak"].setText(streak)
        self._kpi_labels["volume"].setText(total_vol)

    def _update_body_weight(self) -> None:
        colors = self._colors()
        try:
            bw_data = self._db.get_body_weight_history(days=self._period_days)
        except Exception:
            bw_data = []

        if bw_data:
            series = [(w.date[-5:], w.weight_kg) for w in bw_data]
            self._weight_chart.set_data(series, colors.success)
            self._weight_chart.show()
            self._weight_empty.hide() if hasattr(self, '_weight_empty') else None
        else:
            self._weight_chart.hide()

    def _update_weekly_volume(self) -> None:
        colors = self._colors()
        try:
            vol_data = self._db.get_volume_by_day(days=self._period_days)
        except Exception:
            vol_data = []

        if vol_data:
            bars = [(v["week"][-5:], v["volume"] / 1000) for v in vol_data]
            max_val = max(v[1] for v in bars) if bars else 100.0
            self._volume_chart.set_data(bars, max_val * 1.2, colors.primary)
            self._volume_chart.show()
        else:
            self._volume_chart.hide()

    def _update_muscle_balance(self) -> None:
        colors = self._colors()
        try:
            from modules.workout.application.volume_analytics import VolumeAnalytics
            va = VolumeAnalytics(self._db)
            weekly = va.get_weekly_volume(weeks=1)
        except Exception:
            weekly = []

        if weekly and weekly[0].muscles:
            muscles = weekly[0].muscles

            axes = [(m.muscle_group.capitalize()[:4], m.total_sets) for m in muscles]
            max_sets = max(m.total_sets for m in muscles) if muscles else 1
            self._radar_chart.set_data(axes, max_sets * 1.3)

            for i in reversed(range(self._muscle_detail.count())):
                item = self._muscle_detail.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            for m in muscles:
                row = QHBoxLayout()
                row.setContentsMargins(0, _px4, 0, _px4)
                row.setSpacing(_px8)

                name_lbl = QLabel(m.muscle_group.capitalize())
                name_lbl.setStyleSheet(f"color: {colors.text_primary}; {font_style('body_small', 'bold')}; background: transparent;")
                name_lbl.setFixedWidth(80)
                row.addWidget(name_lbl)

                sets_lbl = QLabel(f"{m.total_sets} sets")
                sets_lbl.setStyleSheet(f"color: {colors.text_secondary}; {font_style('caption')}; background: transparent;")
                row.addWidget(sets_lbl)
                row.addStretch()

                status_color = colors.success if m.status == "optimal" else colors.warning if m.status in ("building", "maintenance") else colors.error
                badge = StatusBadge(text=m.status_label, level=StatusLevel.SUCCESS if m.status == "optimal" else StatusLevel.WARNING if m.status in ("building", "maintenance") else StatusLevel.ERROR, outlined=True)
                row.addWidget(badge)

                container = QWidget()
                container.setLayout(row)
                self._muscle_detail.addWidget(container)

            self._radar_chart.show()
            self._muscle_detail_widget.show()
            self._muscle_empty_widget.hide()
        else:
            self._radar_chart.hide()
            self._muscle_detail_widget.hide()
            self._muscle_empty_widget.show()

    def _update_personal_records(self) -> None:
        for i in reversed(range(self._pr_grid.count())):
            item = self._pr_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        colors = self._colors()
        try:
            from modules.workout.application.pr_engine import PREngine
            engine = PREngine(self._db)
            prs = engine.get_best_prs()
        except Exception:
            prs = []

        if prs:
            row_i, col_i = 0, 0
            for pr in prs[:6]:
                card = QFrame()
                card.setStyleSheet(f"""
                    QFrame {{
                        background-color: {colors.surface};
                        border-radius: {R.lg};
                        border: 1px solid {colors.border};
                    }}
                    QFrame:hover {{ border-color: {colors.border_hover}; }}
                """)
                layout = QVBoxLayout(card)
                layout.setContentsMargins(16, 12, 16, 12)
                layout.setSpacing(4)

                type_colors_map = {
                    "weight": colors.success,
                    "reps": colors.info,
                    "volume": colors.warning,
                    "e1rm": colors.primary,
                }
                pr_color = type_colors_map.get(pr.pr_type, colors.text_secondary)

                header = QHBoxLayout()
                header.setSpacing(8)
                name = QLabel(pr.exercise_name)
                name.setStyleSheet(f"color: {colors.text_primary}; {font_style('body_small', 'bold')}; background: transparent;")
                header.addWidget(name, 1)

                type_badge = QLabel(pr.pr_type.upper())
                type_badge.setStyleSheet(
                    f"color: {pr_color}; {font_style('caption', 'bold')}; "
                    f"background: transparent; border: 1px solid {pr_color}; "
                    f"border-radius: {R.sm}; padding: 1px 6px;"
                )
                header.addWidget(type_badge)
                layout.addLayout(header)

                val = QLabel(pr.display_value)
                val.setStyleSheet(f"color: {pr_color}; {font_style('h3')}; background: transparent;")
                layout.addWidget(val)

                if pr.improvement_text:
                    imp = QLabel(pr.improvement_text)
                    imp.setStyleSheet(f"color: {colors.success}; {font_style('caption', 'bold')}; background: transparent;")
                    layout.addWidget(imp)

                if pr.achieved_at:
                    try:
                        pr_date = datetime.fromisoformat(pr.achieved_at).date()
                        days_since = (date.today() - pr_date).days
                        date_text = f"{days_since}d ago"
                    except (ValueError, TypeError):
                        date_text = pr.achieved_at
                    dt = QLabel(date_text)
                    dt.setStyleSheet(f"color: {colors.text_disabled}; {font_style('caption')}; background: transparent;")
                    layout.addWidget(dt)

                self._pr_grid.addWidget(card, row_i, col_i)
                col_i += 1
                if col_i >= 3:
                    col_i = 0
                    row_i += 1

            self._pr_empty_widget.hide()
        else:
            self._pr_empty_widget.show()
            self._pr_grid.addWidget(self._pr_empty_widget, 0, 0)

    def _update_compliance(self) -> None:
        for i in reversed(range(self._compliance_layout.count())):
            item = self._compliance_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        colors = self._colors()
        try:
            sessions = self._db.list_sessions(limit=100)
        except Exception:
            sessions = []

        if sessions:
            from datetime import timedelta
            day_map = {0: "M", 1: "T", 2: "W", 3: "T", 4: "F", 5: "S", 6: "S"}
            week_values = [0.0] * 7

            today = datetime.now()
            for s in sessions:
                if s.started_at:
                    try:
                        s_date = datetime.fromisoformat(s.started_at) if isinstance(s.started_at, str) else s.started_at
                        delta = (today - s_date).days
                        if 0 <= delta < 7 and s.completed_at:
                            week_values[delta] = 1.0
                    except (ValueError, TypeError):
                        pass

            week_values.reverse()
            self._compliance_timeline.set_data(week_values)
            self._compliance_layout.addWidget(self._compliance_timeline)

            total = sum(week_values)
            pct = total / 7 * 100
            label = QLabel(f"{pct:.0f}% adherence this week ({int(total)}/7 sessions)")
            label.setStyleSheet(f"color: {colors.text_disabled}; {font_style('caption')}")
            label.setAlignment(Qt.AlignCenter)
            self._compliance_layout.addWidget(label)
        else:
            empty = QLabel("Compliance data will appear after completing workouts.")
            empty.setStyleSheet(f"color: {colors.text_disabled}; {font_style('body_small')}")
            empty.setAlignment(Qt.AlignCenter)
            self._compliance_layout.addWidget(empty)

    def _update_next_milestone(self) -> None:
        colors = self._colors()
        for i in reversed(range(self._milestone_panel.layout().count())):
            item = self._milestone_panel.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        try:
            bw_data = self._db.get_body_weight_history(days=90)
        except Exception:
            bw_data = []

        try:
            from modules.workout.application.pr_engine import PREngine
            prs = PREngine(self._db).get_best_prs()
        except Exception:
            prs = []

        if bw_data and len(bw_data) >= 2:
            latest = bw_data[-1].weight_kg
            earliest = bw_data[0].weight_kg
            delta = latest - earliest
            if abs(delta) >= 0.5:
                target = latest + (5.0 if delta > 0 else -5.0)
                remaining = abs(target - latest)
                direction = "gain" if delta > 0 else "lose"
                pct = min(abs(delta) / 5.0 * 100, 100)

                icon = QLabel("\u2696")
                icon.setStyleSheet(f"font-size: 28px; background: transparent; border: none;")
                self._milestone_panel.add_content(icon)

                title = QLabel(f"Next Weight Milestone: {target:.1f} kg")
                title.setStyleSheet(f"color: {colors.text_primary}; {font_style('h4')}; background: transparent;")
                self._milestone_panel.add_content(title)

                desc = QLabel(
                    f"{remaining:.1f} kg to {direction} \u00b7 "
                    f"Current: {latest:.1f} kg \u00b7 "
                    f"{'Gaining' if delta > 0 else 'Losing'} {abs(delta):.1f} kg over {len(bw_data)} entries"
                )
                desc.setStyleSheet(f"color: {colors.text_secondary}; {font_style('body_small')}; background: transparent;")
                desc.setWordWrap(True)
                self._milestone_panel.add_content(desc)

                eta_label = QLabel(f"{pct:.0f}% toward milestone")
                eta_color = colors.success if pct >= 50 else colors.warning if pct >= 25 else colors.text_disabled
                eta_label.setStyleSheet(f"color: {eta_color}; {font_style('caption', 'bold')}; background: transparent;")
                self._milestone_panel.add_content(eta_label)
                return

        if prs:
            top = prs[0]
            icon = QLabel("\ud83c\udfc6")
            icon.setStyleSheet(f"font-size: 28px; background: transparent; border: none;")
            self._milestone_panel.add_content(icon)

            title = QLabel(f"Beat Your {top.exercise_name} {top.pr_type.upper()} PR")
            title.setStyleSheet(f"color: {colors.text_primary}; {font_style('h4')}; background: transparent;")
            self._milestone_panel.add_content(title)

            desc = QLabel(
                f"Current best: {top.display_value} \u00b7 "
                f"+{top.improvement or 0:.0f}% over previous"
            )
            desc.setStyleSheet(f"color: {colors.text_secondary}; {font_style('body_small')}; background: transparent;")
            desc.setWordWrap(True)
            self._milestone_panel.add_content(desc)

            eta = QLabel("Next session is your chance to set a new PR!")
            eta.setStyleSheet(f"color: {colors.info}; {font_style('caption', 'bold')}; background: transparent;")
            self._milestone_panel.add_content(eta)
            return

        try:
            sessions = self._db.list_sessions(limit=10)
        except Exception:
            sessions = []

        if sessions:
            completed = sum(1 for s in sessions if s.completed_at)
            target_count = ((completed // 5) + 1) * 5
            remaining = target_count - completed
            icon = QLabel("\ud83d\udcc8")
            icon.setStyleSheet(f"font-size: 28px; background: transparent; border: none;")
            self._milestone_panel.add_content(icon)

            title = QLabel(f"Complete {target_count} Workouts")
            title.setStyleSheet(f"color: {colors.text_primary}; {font_style('h4')}; background: transparent;")
            self._milestone_panel.add_content(title)

            desc = QLabel(f"{remaining} more to go \u00b7 {completed} completed so far")
            desc.setStyleSheet(f"color: {colors.text_secondary}; {font_style('body_small')}; background: transparent;")
            self._milestone_panel.add_content(desc)

            pct = (completed / target_count) * 100
            pct_label = QLabel(f"{pct:.0f}% complete")
            pct_color = colors.success if pct >= 50 else colors.warning
            pct_label.setStyleSheet(f"color: {pct_color}; {font_style('caption', 'bold')}; background: transparent;")
            self._milestone_panel.add_content(pct_label)
            return

        icon = QLabel("\ud83c\udfaf")
        icon.setStyleSheet(f"font-size: 28px; background: transparent; border: none;")
        self._milestone_panel.add_content(icon)

        title = QLabel("No milestone set")
        title.setStyleSheet(f"color: {colors.text_primary}; {font_style('h4')}; background: transparent;")
        self._milestone_panel.add_content(title)

        desc = QLabel("Complete workouts and log body weight to track progress toward your goals.")
        desc.setStyleSheet(f"color: {colors.text_secondary}; {font_style('body_small')}; background: transparent;")
        desc.setWordWrap(True)
        self._milestone_panel.add_content(desc)

    def _update_insights(self) -> None:
        self._insights_stack.clear()

        try:
            from modules.workout.application.pr_engine import PREngine
            engine = PREngine(self._db)
            prs = engine.get_best_prs()
        except Exception:
            prs = []

        if prs:
            recent = prs[0]
            n = Narrative(
                title="Latest Achievement",
                summary=f"New {recent.pr_type} PR in {recent.exercise_name}: {recent.display_value}",
                body=f"You're making progress! This is {recent.improvement or 'a new'} improvement over your previous best.",
                action_items=["Keep pushing your limits", "Focus on form", "Celebrate the win"],
                source_keys=["pr_type", "exercise_name", "display_value"],
                metadata={"severity": "success"},
            )
            self._insights_stack.add_card(n)

        try:
            rec_scores = self._db.get_body_weight_history(days=14)
        except Exception:
            rec_scores = []

        if rec_scores:
            bw = rec_scores[-1]
            n2 = Narrative(
                title="Body Weight Update",
                summary=f"Current weight: {bw.weight_kg:.1f} kg",
                body="Consistent tracking helps you stay on target with your goals.",
                action_items=["Log weight daily", "Track nutrition", "Stay hydrated"],
                source_keys=["weight_kg"],
                metadata={"severity": "info"},
            )
            self._insights_stack.add_card(n2)

        if not prs and not rec_scores:
            n0 = Narrative(
                title="Welcome to Progress",
                summary="Complete your first workout to unlock progress tracking, PR detection, and personalised insights.",
                body="Your progress data will appear here after you log sessions and body weight entries.",
                action_items=["Start a workout", "Log your body weight"],
                source_keys=[],
                metadata={"severity": "info"},
            )
            self._insights_stack.add_card(n0)
