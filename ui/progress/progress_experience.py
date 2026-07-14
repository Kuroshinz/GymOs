"""
Progress Experience 2.0 — Your Training Story.

Replaces data-dashboard layout with a narrative journey.
Seven sections: Hero → Journey → Strength → Body → Consistency → Coach → Achievements.
Every section answers "So what?" with narrative text.
Charts support the story — they don't replace it.

Preserves public API: refresh(), ProgressExperience(db)
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ui.design_system.components.app_card import AppCard
from ui.design_system.components.section_header import SectionHeader
from ui.design_system.components.status_badge import StatusBadge, StatusLevel
from ui.design_system.layout import PanelSpan
from ui.design_system.layout.kpi_strip import KpiItem, KpiStrip
from ui.design_system.components.chart_container import ChartContainer
from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.elevation import glow_effect
from ui.design_system.tokens.radius import RadiusTokens, px_from_token, radius_to_px
from ui.design_system.tokens.spacing import SpacingTokens
from ui.design_system.tokens.typography import font_style
from ui.design_system.visualization import WeeklyTimeline
from ui.narrative import CoachCard, CoachCardStack
from ui.narrative.engine import Narrative
from ui.visualization.charts import TrendChart

S = SpacingTokens()
R = RadiusTokens()

_px4 = px_from_token(S.s1)
_px6 = px_from_token(S.s1_5)
_px8 = px_from_token(S.s2)
_px12 = px_from_token(S.s3)
_px16 = px_from_token(S.s4)
_px20 = px_from_token(S.s5)
_px24 = px_from_token(S.s6)
_px28 = px_from_token(S.s7)
_px32 = px_from_token(S.s8)
_px40 = px_from_token(S.s10)
_px48 = px_from_token(S.s12)

_DOT_R = 6


# ── Journey Timeline ──────────────────────────────────────────────


class _JourneyTimeline(QFrame):
    """Horizontal milestone timeline with dots and labels.

    Renders a sequence of milestones connected by lines, showing
    the user's progression from starting GymOS to the present.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._milestones: list[tuple[str, str, bool]] = []  # (label, date, achieved)
        self.setFixedHeight(80)
        self.setAccessibleName("Training journey timeline")

    def set_milestones(self, milestones: list[tuple[str, str, bool]]) -> None:
        self._milestones = milestones
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        if not self._milestones:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        colors = color_from_scheme(ColorScheme.DARK)
        w = self.width()
        h = 70
        n = len(self._milestones)
        spacing = min(80, (w - 40) // max(n - 1, 1))
        total_w = spacing * (n - 1)
        start_x = (w - total_w) // 2

        # Draw connecting line
        line_y = 20
        painter.setPen(QPen(QColor(colors.border), 2))
        painter.drawLine(start_x, line_y, start_x + total_w, line_y)

        for i, (label, date_str, achieved) in enumerate(self._milestones):
            x = start_x + i * spacing

            # Dot
            if achieved:
                painter.setBrush(QColor(colors.success))
                painter.setPen(Qt.NoPen)
            else:
                painter.setBrush(QColor(colors.scrollbar_handle))
                painter.setPen(QPen(QColor(colors.border), 1))

            painter.drawEllipse(x - _DOT_R, line_y - _DOT_R, _DOT_R * 2, _DOT_R * 2)

            # Label below dot
            painter.setFont(QFont())
            painter.setPen(QColor(colors.text_secondary))
            painter.drawText(
                x - spacing // 2, line_y + _DOT_R + 4,
                spacing, 16, Qt.AlignCenter, label,
            )

            # Date above dot
            painter.setPen(QColor(colors.text_disabled))
            f2 = QFont()
            f2.setPixelSize(9)
            painter.setFont(f2)
            painter.drawText(
                x - spacing // 2, line_y - _DOT_R - 20,
                spacing, 14, Qt.AlignCenter, date_str,
            )

        painter.end()


# ── Achievement Card ──────────────────────────────────────────────


class _AchievementCard(QFrame):
    """A glowing achievement card with icon, title, date, and description."""

    def __init__(
        self,
        icon: str,
        title: str,
        description: str,
        date_earned: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._build_ui(icon, title, description, date_earned)

    def _build_ui(self, icon: str, title: str, description: str, date_earned: str) -> None:
        colors = color_from_scheme(ColorScheme.DARK)
        self.setStyleSheet(f"""
            _AchievementCard {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {R.lg};
            }}
            _AchievementCard:hover {{
                border-color: {colors.primary};
            }}
        """)
        glow_effect(self, glow_rgba=f"rgba(124, 58, 237, 0.15)", blur=16, offset_y=0)
        self.setAccessibleName(f"Achievement: {title}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(_px16, _px14, _px16, _px14)
        layout.setSpacing(_px6)
        layout.setAlignment(Qt.AlignCenter)

        icon_lbl = QLabel(icon)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet("font-size: 32px; background: transparent; border: none;")
        layout.addWidget(icon_lbl)

        t = QLabel(title)
        t.setAlignment(Qt.AlignCenter)
        t.setWordWrap(True)
        t.setStyleSheet(
            f"color: {colors.text_primary}; {font_style('body', weight='bold')}; "
            f"background: transparent; border: none;"
        )
        layout.addWidget(t)

        if description:
            d = QLabel(description)
            d.setAlignment(Qt.AlignCenter)
            d.setWordWrap(True)
            d.setStyleSheet(
                f"color: {colors.text_secondary}; {font_style('caption')}; "
                f"background: transparent; border: none;"
            )
            layout.addWidget(d)

        if date_earned:
            dt = QLabel(date_earned)
            dt.setAlignment(Qt.AlignCenter)
            dt.setStyleSheet(
                f"color: {colors.text_disabled}; {font_style('caption')}; "
                f"background: transparent; border: none;"
            )
            layout.addWidget(dt)


# ── Progress Experience (main) ────────────────────────────────────


class ProgressExperience(QWidget):
    """Narrative-first progress page with seven editorial sections.

    Preserved public API:
    - Constructor: ProgressExperience(db)
    - Method: refresh()
    - Data sources: PREngine, VolumeAnalytics, db (all unchanged)
    """

    def __init__(self, db: Any, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._db = db
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

        # Section 1: Hero
        self._hero_card = AppCard(title="", elevated=True)
        hc = QHBoxLayout()
        hc.setContentsMargins(0, 0, 0, 0)
        hc.setSpacing(_px16)
        self._hero_text_col = QVBoxLayout()
        self._hero_text_col.setSpacing(_px4)

        self._hero_narrative = QLabel("")
        self._hero_narrative.setWordWrap(True)
        self._hero_narrative.setStyleSheet(
            f"background: transparent; border: none;"
        )
        self._hero_text_col.addWidget(self._hero_narrative)

        self._hero_subtitle = QLabel("")
        self._hero_subtitle.setWordWrap(True)
        self._hero_subtitle.setStyleSheet(
            f"background: transparent; border: none;"
        )
        self._hero_text_col.addWidget(self._hero_subtitle)
        self._hero_text_col.addStretch()
        hc.addLayout(self._hero_text_col, 1)

        self._hero_kpi = KpiStrip([], color_scheme=ColorScheme.DARK)
        hc.addWidget(self._hero_kpi)

        hero_outer = QFrame()
        hero_outer.setLayout(hc)
        self._hero_card.add_content(hero_outer)
        main.addWidget(self._hero_card)

        main.addSpacing(_px24)

        # Section 2: Your Journey
        self._build_section_header(main, "Your Journey", "From first workout to today")
        self._journey = _JourneyTimeline()
        main.addWidget(self._journey)

        main.addSpacing(_px24)

        # Section 3: Strength
        self._build_section_header(main, "Strength", "Your best performances")
        self._strength_header = QLabel("")
        self._strength_header.setWordWrap(True)
        self._strength_header.setStyleSheet(
            f"background: transparent; border: none;"
        )
        main.addWidget(self._strength_header)

        self._pr_grid = QGridLayout()
        self._pr_grid.setContentsMargins(0, 0, 0, 0)
        self._pr_grid.setSpacing(_px12)
        main.addLayout(self._pr_grid)

        self._strength_empty = QLabel("")
        self._strength_empty.setAlignment(Qt.AlignCenter)
        self._strength_empty.setWordWrap(True)
        self._strength_empty.setStyleSheet(
            f"background: transparent; border: none;"
        )

        main.addSpacing(_px20)

        # Section 4: Body
        self._build_section_header(main, "Body", "Weight trend and composition")
        self._body_chart_container = ChartContainer(title="Body Weight", subtitle="Trend over time")
        self._body_chart = TrendChart()
        self._body_chart_container.set_chart(self._body_chart)
        main.addWidget(self._body_chart_container)

        self._body_narrative_widget = QFrame()
        self._body_narrative_widget.setStyleSheet("background: transparent; border: none;")
        self._body_narrative_widget.hide()
        nwl = QVBoxLayout(self._body_narrative_widget)
        nwl.setContentsMargins(0, _px8, 0, 0)

        self._body_narrative = QLabel("")
        self._body_narrative.setWordWrap(True)
        self._body_narrative.setStyleSheet(
            f"background: transparent; border: none;"
        )
        nwl.addWidget(self._body_narrative)
        main.addWidget(self._body_narrative_widget)

        self._body_empty = QLabel("")
        self._body_empty.setAlignment(Qt.AlignCenter)
        self._body_empty.setWordWrap(True)
        self._body_empty.setStyleSheet(
            f"background: transparent; border: none;"
        )
        main.addWidget(self._body_empty)
        self._body_empty.hide()

        main.addSpacing(_px20)

        # Section 5: Consistency
        self._build_section_header(main, "Consistency", "Your training rhythm")
        self._consistency_view = QFrame()
        self._consistency_view.setStyleSheet("background: transparent; border: none;")
        cvl = QVBoxLayout(self._consistency_view)
        cvl.setContentsMargins(0, 0, 0, 0)
        cvl.setSpacing(_px8)

        self._consistency_timeline = WeeklyTimeline()
        cvl.addWidget(self._consistency_timeline)

        self._adherence_label = QLabel("")
        self._adherence_label.setStyleSheet(
            f"background: transparent; border: none;"
        )
        self._adherence_label.setAlignment(Qt.AlignCenter)
        cvl.addWidget(self._adherence_label)

        self._consistency_summary = QLabel("")
        self._consistency_summary.setWordWrap(True)
        self._consistency_summary.setStyleSheet(
            f"background: transparent; border: none;"
        )
        cvl.addWidget(self._consistency_summary)

        self._consistency_empty = QLabel("")
        self._consistency_empty.setAlignment(Qt.AlignCenter)
        self._consistency_empty.setWordWrap(True)
        self._consistency_empty.setStyleSheet(
            f"background: transparent; border: none;"
        )
        self._consistency_empty.hide()

        main.addWidget(self._consistency_view)
        main.addWidget(self._consistency_empty)

        main.addSpacing(_px20)

        # Section 6: Coach
        self._build_section_header(main, "Coach", "Personalised insights")
        self._coach_stack = CoachCardStack()
        main.addWidget(self._coach_stack)

        main.addSpacing(_px20)

        # Section 7: Achievements
        self._build_section_header(main, "Achievements", "Celebrate your wins")
        self._achievement_grid = QGridLayout()
        self._achievement_grid.setContentsMargins(0, 0, 0, 0)
        self._achievement_grid.setSpacing(_px12)
        main.addLayout(self._achievement_grid)

        self._achievement_empty = QLabel("")
        self._achievement_empty.setAlignment(Qt.AlignCenter)
        self._achievement_empty.setWordWrap(True)
        self._achievement_empty.setStyleSheet(
            f"background: transparent; border: none;"
        )

        main.addStretch()

    def _build_section_header(self, parent: QVBoxLayout, title: str, subtitle: str) -> None:
        header = SectionHeader(title=title, subtitle=subtitle)
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, _px8)
        hbox.addWidget(header)
        parent.addLayout(hbox)

    # ── Refresh (unchanged public API) ──────────────────────────────

    def refresh(self) -> None:
        self._update_hero()
        self._update_journey()
        self._update_strength()
        self._update_body()
        self._update_consistency()
        self._update_coach()
        self._update_achievements()

    # ── Section 1: Hero ─────────────────────────────────────────────

    def _update_hero(self) -> None:
        colors = self._colors()
        sessions = self._safe_list_sessions(limit=200)
        completed = [s for s in sessions if getattr(s, "completed_at", None)]

        n_workouts = len(completed)
        streak_days = self._calc_streak(completed)

        from modules.workout.application.pr_engine import PREngine
        prs = []
        try:
            prs = PREngine(self._db).get_best_prs()
        except Exception:
            pass

        n_prs = len(prs)

        # Today's achievement
        today_achievement = ""
        if n_prs > 0:
            top_pr = prs[0]
            pct = getattr(top_pr, "improvement", 0) or 0
            if pct >= 5:
                today_achievement = f"{top_pr.exercise_name} +{pct:.0f}%"
        if not today_achievement and streak_days >= 7:
            today_achievement = f"{streak_days}-day streak 🔥"
        if not today_achievement and n_workouts >= 10:
            today_achievement = f"{n_workouts} workouts completed"

        # Primary narrative message
        if n_workouts >= 10:
            narrative = f"You've completed {n_workouts} workouts."
            if n_prs > 0:
                narrative += f"\nYou've set {n_prs} personal record{'s' if n_prs != 1 else ''}."
            if streak_days >= 5:
                narrative += f"\nYour {streak_days}-day streak shows incredible dedication."
            else:
                narrative += "\nYou're building real momentum."
        elif n_workouts >= 3:
            narrative = f"You've completed {n_workouts} workouts."
            narrative += "\nEvery workout builds a stronger you."
        elif n_workouts > 0:
            narrative = f"Welcome back! You've completed {n_workouts} workout{'s' if n_workouts != 1 else ''}."
            narrative += "\nConsistency is the key to progress."
        else:
            narrative = "Welcome to GymOS!\nComplete your first workout to start tracking your progress."

        self._hero_narrative.setText(narrative)
        self._hero_narrative.setStyleSheet(
            f"color: {colors.text_primary}; {font_style('h2')}; "
            f"background: transparent; border: none;"
        )

        # Today's achievement badge (replace any existing one)
        if hasattr(self, '_hero_achievement_badge') and self._hero_achievement_badge:
            self._hero_achievement_badge.deleteLater()
            self._hero_achievement_badge = None
        if today_achievement:
            self._hero_achievement_badge = StatusBadge(
                text=f"Today: {today_achievement}",
                level=StatusLevel.SUCCESS,
                outlined=True,
            )
            self._hero_text_col.insertWidget(1, self._hero_achievement_badge)

        # Subtitle
        now = datetime.now()
        hour = now.hour
        greeting = "Good morning" if hour < 12 else "good afternoon" if hour < 18 else "good evening"
        subtitle = f"{greeting.capitalize()}, here's your progress overview."
        self._hero_subtitle.setText(subtitle)
        self._hero_subtitle.setStyleSheet(
            f"color: {colors.text_secondary}; {font_style('body')}; "
            f"background: transparent; border: none;"
        )

        # KPI strip
        vol_text = "--"
        try:
            vol_data = self._db.get_volume_by_day(days=90)
            total_vol_kg = sum(v["volume"] for v in vol_data)
            vol_text = f"{total_vol_kg / 1000:.1f}k" if total_vol_kg >= 1000 else f"{int(total_vol_kg)}"
        except Exception:
            pass

        current_phase = "Building"
        if n_workouts >= 20:
            current_phase = "Growing"
        if n_workouts >= 50:
            current_phase = "Strong"

        self._hero_kpi.set_items([
            KpiItem(label="Workouts", value=str(n_workouts)),
            KpiItem(label="PRs", value=str(n_prs)),
            KpiItem(label="Streak", value=f"{streak_days}d"),
            KpiItem(label=f"Phase", value=current_phase),
            KpiItem(label="Volume", value=vol_text),
        ])

    # ── Section 2: Your Journey ─────────────────────────────────────

    def _update_journey(self) -> None:
        milestones: list[tuple[str, str, bool]] = []
        milestones.append(("Started", "", True))

        from modules.workout.application.pr_engine import PREngine
        try:
            prs = PREngine(self._db).get_best_prs()
        except Exception:
            prs = []

        # First PR milestone
        for pr in prs[:2]:
            short = pr.exercise_name[:12]
            date_str = self._format_date_short(getattr(pr, "achieved_at", ""))
            milestones.append((short, date_str, True))

        # Body weight milestone
        try:
            bw_data = self._db.get_body_weight_history(days=180)
            if len(bw_data) >= 2:
                delta = bw_data[-1].weight_kg - bw_data[0].weight_kg
                if abs(delta) >= 1.0:
                    direction = "↓" if delta < 0 else "↑"
                    milestones.append((
                        f"{direction}{abs(delta):.1f}kg",
                        bw_data[-1].date[-5:] if hasattr(bw_data[-1], "date") else "",
                        True,
                    ))
        except Exception:
            pass

        # Current
        milestones.append(("Now", "", False))
        self._journey.set_milestones(milestones)

    # ── Section 3: Strength ─────────────────────────────────────────

    def _update_strength(self) -> None:
        colors = self._colors()
        self._clear_grid(self._pr_grid)

        from modules.workout.application.pr_engine import PREngine
        try:
            engine = PREngine(self._db)
            prs = engine.get_best_prs()
        except Exception:
            prs = []

        if not prs:
            self._strength_empty.setText(
                "No PRs yet. Push yourself in your next workout!\n"
                "Every rep is a step toward a new personal record."
            )
            self._strength_empty.setStyleSheet(
                f"color: {colors.text_disabled}; {font_style('body')}; "
                f"background: transparent; border: none; padding: {S.s8};"
            )
            self._pr_grid.addWidget(self._strength_empty, 0, 0)
            self._strength_header.setText("")
            return

        # Strength narrative
        has_impressive = 0
        for pr in prs[:3]:
            if getattr(pr, "improvement", 0) and pr.improvement > 10:
                has_impressive += 1

        if has_impressive >= 2:
            narrative = f"You're on fire! {has_impressive} exercises improved by over 10%."
        elif has_impressive >= 1:
            top = prs[0]
            narrative = f"{top.exercise_name} improved by {top.improvement:.0f}%. Outstanding progress."
        elif prs:
            narrative = f"Your {len(prs)} best lifts are trending up. Keep pushing."
        else:
            narrative = ""
        self._strength_header.setText(narrative)
        self._strength_header.setStyleSheet(
            f"color: {colors.primary}; {font_style('body', weight=500)}; "
            f"background: transparent; border: none; padding-bottom: {S.s2};"
        )

        # PR cards
        row_i, col_i = 0, 0
        type_colors_map = {
            "weight": colors.success,
            "reps": colors.info,
            "volume": colors.warning,
            "e1rm": colors.primary,
        }

        for pr in prs[:6]:
            pr_color = type_colors_map.get(getattr(pr, "pr_type", ""), colors.text_secondary)
            improvement = getattr(pr, "improvement", 0) or 0
            improvement_text = getattr(pr, "improvement_text", "") or ""

            card = AppCard(title="", elevated=False, interactive=False)
            card.setStyleSheet(f"""
                AppCard {{
                    background-color: {colors.surface};
                    border: 1px solid {colors.border};
                    border-radius: {R.lg};
                }}
                AppCard:hover {{
                    border-color: {colors.primary};
                }}
            """)

            inner = QVBoxLayout()
            inner.setSpacing(_px4)
            inner.setContentsMargins(0, 0, 0, 0)

            # Exercise name
            name_lbl = QLabel(pr.exercise_name)
            name_lbl.setStyleSheet(
                f"color: {colors.text_primary}; {font_style('body', weight='bold')}; "
                f"background: transparent; border: none;"
            )
            inner.addWidget(name_lbl)

            # Value (large)
            val_lbl = QLabel(pr.display_value)
            val_lbl.setStyleSheet(
                f"color: {pr_color}; {font_style('h3')}; "
                f"background: transparent; border: none;"
            )
            inner.addWidget(val_lbl)

            # Improvement with arrow
            if improvement > 0:
                arrow = "▲"
                pct = f"{improvement:.0f}%"
                imp_lbl = QLabel(f"{arrow} +{improvement_text}" if improvement_text else f"{arrow} +{int(improvement)} ({pct})")
                imp_lbl.setStyleSheet(
                    f"color: {colors.success}; {font_style('caption', weight='bold')}; "
                    f"background: transparent; border: none;"
                )
                inner.addWidget(imp_lbl)
            elif improvement == 0:
                imp_lbl = QLabel("— No change")
                imp_lbl.setStyleSheet(
                    f"color: {colors.text_disabled}; {font_style('caption')}; "
                    f"background: transparent; border: none;"
                )
                inner.addWidget(imp_lbl)

            # Improvement narrative
            if improvement >= 10:
                narrative_text = "Excellent progress!"
            elif improvement >= 5:
                narrative_text = "Solid gains."
            elif improvement > 0:
                narrative_text = "Trending up."
            else:
                narrative_text = "Keep pushing."

            nar_lbl = QLabel(narrative_text)
            nar_lbl.setStyleSheet(
                f"color: {colors.text_secondary}; {font_style('caption')}; "
                f"background: transparent; border: none;"
            )
            inner.addWidget(nar_lbl)

            # Date
            date_str = self._format_date_short(getattr(pr, "achieved_at", ""))
            if date_str:
                dt_lbl = QLabel(date_str)
                dt_lbl.setStyleSheet(
                    f"color: {colors.text_disabled}; {font_style('caption')}; "
                    f"background: transparent; border: none;"
                )
                inner.addWidget(dt_lbl)

            inner.addStretch()
            wrapper = QFrame()
            wrapper.setLayout(inner)
            wrapper.setStyleSheet("background: transparent; border: none;")
            card.add_content(wrapper)

            self._pr_grid.addWidget(card, row_i, col_i)
            col_i += 1
            if col_i >= 3:
                col_i = 0
                row_i += 1

    # ── Section 4: Body ─────────────────────────────────────────────

    def _update_body(self) -> None:
        colors = self._colors()
        try:
            bw_data = self._db.get_body_weight_history(days=90)
        except Exception:
            bw_data = []

        if bw_data and len(bw_data) >= 2:
            series = [(w.date[-5:], w.weight_kg) for w in bw_data]
            self._body_chart.set_data(series, colors.success)
            self._body_chart.show()

            latest = bw_data[-1].weight_kg
            earliest = bw_data[0].weight_kg
            delta = latest - earliest
            weeks = max(len(bw_data) // 3, 1)

            if delta < -1.0:
                trend = f"Down {abs(delta):.1f}kg in ~{weeks} weeks. Consistent progress."
                if abs(delta) >= 3:
                    trend += " On track for your goal."
            elif delta < 0:
                trend = f"Down {abs(delta):.1f}kg. Gradual, sustainable progress."
            elif delta > 1.0:
                trend = f"Up {delta:.1f}kg in ~{weeks} weeks. Strong gains."
            else:
                trend = "Weight is stable. Perfect environment for strength gains."

            goal_hint = ""
            try:
                from modules.workout.application.pr_engine import PREngine
                if PREngine(self._db).get_best_prs():
                    goal_hint = " Your training is building strength and discipline."
            except Exception:
                pass

            self._body_narrative.setText(trend + goal_hint)
            self._body_narrative.setStyleSheet(
                f"color: {colors.text_secondary}; {font_style('body')}; "
                f"background: transparent; border: none;"
            )
            self._body_narrative.show()
            self._body_empty.hide()
        else:
            self._body_chart.hide()
            self._body_narrative.hide()
            self._body_empty.setText(
                "No weight data logged yet.\n"
                "Log your body weight in Settings to track changes and see your progress."
            )
            self._body_empty.setStyleSheet(
                f"color: {colors.text_disabled}; {font_style('body')}; "
                f"background: transparent; border: none; padding: {S.s8};"
            )
            self._body_empty.show()

    # ── Section 5: Consistency ──────────────────────────────────────

    def _update_consistency(self) -> None:
        colors = self._colors()
        # Clear all widgets from consistency layout
        layout = self._consistency_view.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                if item and item.widget():
                    item.widget().deleteLater()

        sessions = self._safe_list_sessions(limit=100)

        if not sessions:
            self._consistency_empty.setText(
                "Complete workouts regularly to build your consistency streak\n"
                "and see your training rhythm."
            )
            self._consistency_empty.setStyleSheet(
                f"color: {colors.text_disabled}; {font_style('body')}; "
                f"background: transparent; border: none; padding: {S.s8};"
            )
            self._consistency_empty.show()
            self._consistency_view.hide()
            return
        else:
            self._consistency_empty.hide()
            self._consistency_view.show()

        # Weekly timeline bar chart
        day_map = {0: "M", 1: "T", 2: "W", 3: "T", 4: "F", 5: "S", 6: "S"}
        week_values = [0.0] * 7
        today = datetime.now()
        for s in sessions:
            if getattr(s, "started_at", None) and getattr(s, "completed_at", None):
                try:
                    s_date = datetime.fromisoformat(s.started_at) if isinstance(s.started_at, str) else s.started_at
                    delta_days = (today - s_date).days
                    if 0 <= delta_days < 7:
                        week_values[delta_days] = 1.0
                except (ValueError, TypeError):
                    pass

        week_values.reverse()
        self._consistency_timeline.set_data(week_values)
        self._consistency_view.layout().addWidget(self._consistency_timeline)

        total = int(sum(week_values))
        pct = total / 7 * 100

        # Adherence badge
        if pct >= 80:
            badge_level = StatusLevel.SUCCESS
            summary = "Excellent consistency!"
        elif pct >= 60:
            badge_level = StatusLevel.WARNING
            summary = "Good consistency. Try to add one more session."
        else:
            badge_level = StatusLevel.ERROR
            summary = "Building consistency. Every session counts."

        badge = StatusBadge(
            text=f"{pct:.0f}% adherence this week",
            level=badge_level,
            outlined=True,
        )
        self._consistency_view.layout().addWidget(badge)

        # Summary
        summary_text = f"{summary} {total}/7 sessions completed."
        if total >= 5:
            summary_text += " Outstanding week."
        elif total >= 3:
            summary_text += " Solid foundation."

        self._consistency_summary.setText(summary_text)
        self._consistency_summary.setStyleSheet(
            f"color: {colors.text_secondary}; {font_style('caption')}; "
            f"background: transparent; border: none;"
        )
        self._consistency_view.layout().addWidget(self._consistency_summary)

        # Monthly context
        try:
            sessions_30d = [s for s in sessions if getattr(s, "completed_at", None)]
            total_30d = len(sessions_30d)
            avg_week = total_30d / 4.3
            monthly = f"Monthly average: {avg_week:.1f} sessions/week"
            monthly_lbl = QLabel(monthly)
            monthly_lbl.setStyleSheet(
                f"color: {colors.text_disabled}; {font_style('caption')}; "
                f"background: transparent; border: none;"
            )
            monthly_lbl.setAlignment(Qt.AlignCenter)
            self._consistency_view.layout().addWidget(monthly_lbl)
        except Exception:
            pass

    # ── Section 6: Coach ────────────────────────────────────────────

    def _update_coach(self) -> None:
        self._coach_stack.clear()
        insights: list[Narrative] = []

        # Insight 1: Performance narrative
        from modules.workout.application.pr_engine import PREngine
        try:
            prs = PREngine(self._db).get_best_prs()
            if prs:
                top = prs[0]
                pct = getattr(top, "improvement", 0) or 0
                if pct >= 10:
                    summary = f"{top.exercise_name} improved by {pct:.0f}%. Outstanding!"
                elif pct >= 5:
                    summary = f"{top.exercise_name} improved by {pct:.0f}%. Solid gains."
                else:
                    summary = f"{top.exercise_name} — trending up."
                insights.append(Narrative(
                    title="Strength Progress",
                    summary=summary,
                    body="Keep pushing your limits. Consistency drives improvement.",
                    action_items=["Track your next session", "Focus on progressive overload"],
                    source_keys=["pr_type", "exercise_name", "display_value"],
                    metadata={"severity": "success"},
                ))
        except Exception:
            pass

        # Insight 2: Volume trend
        try:
            from modules.workout.application.volume_analytics import VolumeAnalytics
            va = VolumeAnalytics(self._db)
            weekly = va.get_weekly_volume(weeks=4)
            if len(weekly) >= 2:
                recent = weekly[0].total_sets
                previous = weekly[1].total_sets
                if recent > previous:
                    pct_up = ((recent - previous) / max(previous, 1)) * 100
                    insights.append(Narrative(
                        title="Volume Increasing",
                        summary=f"Training volume up {pct_up:.0f}% this week.",
                        body="Increasing volume is a strong signal of adaptive progress. Maintain this trajectory.",
                        action_items=["Monitor recovery", "Ensure nutrition supports volume"],
                        source_keys=["total_sets", "week_label"],
                        metadata={"severity": "info"},
                    ))
                elif recent < previous and previous > 0:
                    pct_down = ((previous - recent) / max(previous, 1)) * 100
                    insights.append(Narrative(
                        title="Volume Dropped",
                        summary=f"Training volume dropped {pct_down:.0f}% this week.",
                        body="A volume drop can indicate fatigue or schedule changes. Consider adjusting your plan.",
                        action_items=["Check recovery status", "Plan next week's sessions"],
                        source_keys=["total_sets", "week_label"],
                        metadata={"severity": "warning"},
                    ))
        except Exception:
            pass

        # Insight 3: Consistency
        sessions = self._safe_list_sessions(limit=60)
        completed_sessions = [s for s in sessions if getattr(s, "completed_at", None)]
        if completed_sessions:
            n = len(completed_sessions)
            weeks_period = max(n / 3, 1)
            avg_per_week = n / weeks_period

            if avg_per_week >= 4:
                insights.append(Narrative(
                    title="Excellent Consistency",
                    summary=f"Training {avg_per_week:.1f}x/week on average.",
                    body="High training frequency correlates with better strength gains and habit formation.",
                    action_items=["Keep this pace for 2 more weeks", "Recovery becomes critical"],
                    source_keys=["completed_at"],
                    metadata={"severity": "success"},
                ))
            elif avg_per_week >= 3:
                insights.append(Narrative(
                    title="Good Consistency",
                    summary=f"Training {avg_per_week:.1f}x/week. Solid foundation.",
                    body="Adding one more session per week could accelerate your progress significantly.",
                    action_items=["Try adding one more session", "Review your weekly schedule"],
                    source_keys=["completed_at"],
                    metadata={"severity": "info"},
                ))
            elif avg_per_week >= 1:
                insights.append(Narrative(
                    title="Building Consistency",
                    summary=f"Training {avg_per_week:.1f}x/week. Every session counts.",
                    body="Consistency is the single most important factor in long-term progress.",
                    action_items=["Aim for 3 sessions next week", "Schedule your workouts"],
                    source_keys=["completed_at"],
                    metadata={"severity": "info"},
                ))

        # Add top 3 insights
        for insight in insights[:3]:
            self._coach_stack.add_card(insight)

        if not insights:
            welcome = Narrative(
                title="Welcome to Progress",
                summary="Complete your first workout to unlock personalised coaching insights.",
                body="Your coach will analyse your training, volume, and consistency to provide actionable recommendations.",
                action_items=["Start a workout", "Log your body weight"],
                source_keys=[],
                metadata={"severity": "info"},
            )
            self._coach_stack.add_card(welcome)

    # ── Section 7: Achievements ─────────────────────────────────────

    def _update_achievements(self) -> None:
        colors = self._colors()
        self._clear_grid(self._achievement_grid)
        achievements: list[tuple[str, str, str, str]] = []  # (icon, title, desc, date)

        sessions = self._safe_list_sessions(limit=200)
        completed = [s for s in sessions if getattr(s, "completed_at", None)]
        n_workouts = len(completed)

        # Workout milestones — find the highest reached and add date
        max_reached = 0
        for count in sorted(milestones_map.keys()):
            if n_workouts >= count:
                max_reached = count
        if max_reached > 0:
            label = milestones_map[max_reached]
            last_date = ""
            if completed:
                last = completed[-1]
                if getattr(last, "completed_at", None):
                    last_date = self._format_date_short(last.completed_at)
            achievements.append(("💪", label, f"Completed {max_reached} workouts", last_date))

        # Streak milestones — find the highest reached
        streak = self._calc_streak(completed)
        max_streak_reached = 0
        for days in sorted(streak_map.keys()):
            if streak >= days:
                max_streak_reached = days
        if max_streak_reached > 0:
            label = streak_map[max_streak_reached]
            achievements.append(("🔥", label, f"{max_streak_reached}-day consistency streak", "Active"))

        # PR milestones — find the highest reached with date
        pr_milestones = {1: "First PR", 5: "PR Collector", 10: "PR Machine", 25: "Legend"}
        try:
            prs = PREngine(self._db).get_best_prs()
            pr_count = len(prs)
            max_pr_reached = 0
            for count in sorted(pr_milestones.keys()):
                if pr_count >= count:
                    max_pr_reached = count
            if max_pr_reached > 0:
                label = pr_milestones[max_pr_reached]
                # Use the date of the most recent PR
                pr_date = ""
                if prs and max_pr_reached <= len(prs):
                    latest_pr = prs[min(max_pr_reached, len(prs)) - 1]
                    pr_date = self._format_date_short(getattr(latest_pr, "achieved_at", ""))
                achievements.append(("🏆", label, f"Set {max_pr_reached} personal records", pr_date))
        except Exception:
            pass

        # Volume milestones — find the highest reached
        vol_milestones = {10000: "10k Volume", 50000: "50k Volume", 100000: "100k Volume"}
        try:
            vol_data = self._db.get_volume_by_day(days=365)
            total_vol = sum(v["volume"] for v in vol_data)
            max_vol_reached = 0
            for threshold in sorted(vol_milestones.keys()):
                if total_vol >= threshold:
                    max_vol_reached = threshold
            if max_vol_reached > 0:
                label = vol_milestones[max_vol_reached]
                achievements.append(("📊", label, f"Total volume: {int(total_vol):,} kg", "Lifetime"))
        except Exception:
            pass

        if not achievements:
            self._achievement_empty.setText(
                "Complete workouts and set PRs to unlock achievements.\n"
                "Every milestone is a celebration of your dedication."
            )
            self._achievement_empty.setStyleSheet(
                f"color: {colors.text_disabled}; {font_style('body')}; "
                f"background: transparent; border: none; padding: {S.s8};"
            )
            self._achievement_grid.addWidget(self._achievement_empty, 0, 0)
            return

        row_i, col_i = 0, 0
        for icon, title, desc, date_str in achievements[:6]:
            card = _AchievementCard(icon=icon, title=title, description=desc, date_earned=date_str)
            self._achievement_grid.addWidget(card, row_i, col_i)
            col_i += 1
            if col_i >= 3:
                col_i = 0
                row_i += 1

    # ── Helpers ─────────────────────────────────────────────────────

    def _safe_list_sessions(self, limit: int = 100):
        try:
            return self._db.list_sessions(limit=limit)
        except Exception:
            return []

    def _calc_streak(self, completed: list) -> int:
        """Calculate consecutive workout streak in days."""
        if not completed:
            return 0
        dates = set()
        for s in completed:
            if getattr(s, "completed_at", None):
                try:
                    d = datetime.fromisoformat(s.completed_at) if isinstance(s.completed_at, str) else s.completed_at
                    dates.add(d.date())
                except (ValueError, TypeError):
                    pass

        if not dates:
            return 0

        today = date.today()
        streak = 0
        current = today
        while current in dates:
            streak += 1
            current -= timedelta(days=1)
        return streak

    def _format_date_short(self, date_str: str) -> str:
        if not date_str:
            return ""
        try:
            d = datetime.fromisoformat(date_str).date()
            days_since = (date.today() - d).days
            if days_since == 0:
                return "Today"
            if days_since == 1:
                return "Yesterday"
            return f"{days_since}d ago"
        except (ValueError, TypeError):
            return date_str

    def _clear_grid(self, grid: QGridLayout) -> None:
        while grid.count():
            item = grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
