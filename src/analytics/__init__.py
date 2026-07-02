import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import date, timedelta
from src.services import (
    WeightService, WorkoutService, NutritionService, RecoveryService,
    MuscleHeatmapService, SleepService
)
import json


class ChartBuilder:
    @staticmethod
    def _config():
        return {
            "displayModeBar": False,
            "responsive": True,
            "staticPlot": False,
        }

    @staticmethod
    def _theme_layout(title="", height=300):
        return {
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "font": {"color": "#e0e0e0", "family": "Inter, system-ui, sans-serif"},
            "title": {"text": title, "font": {"size": 14, "color": "#ffffff"}, "x": 0.5},
            "margin": {"l": 40, "r": 20, "t": 40, "b": 40},
            "height": height,
            "hovermode": "x unified",
            "xaxis": {"gridcolor": "rgba(255,255,255,0.05)", "zerolinecolor": "rgba(255,255,255,0.1)", "color": "#888"},
            "yaxis": {"gridcolor": "rgba(255,255,255,0.05)", "zerolinecolor": "rgba(255,255,255,0.1)", "color": "#888"},
        }

    @staticmethod
    def weight_chart(user_id: int, days: int = 30) -> go.Figure:
        entries = WeightService.get_recent(user_id, days)
        if not entries:
            fig = go.Figure()
            fig.update_layout(**ChartBuilder._theme_layout("Weight Progress", 250))
            fig.add_annotation(text="No data yet", x=0.5, y=0.5, showarrow=False, font={"color": "#666"})
            return fig

        dates = [e.date for e in entries]
        weights = [e.weight_kg for e in entries]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates, y=weights, mode="lines+markers",
            name="Weight", line=dict(color="#7c3aed", width=3),
            marker=dict(size=6, color="#7c3aed"),
            fill="tozeroy", fillcolor="rgba(124,58,237,0.08)"
        ))

        if len(weights) >= 3:
            import numpy as np
            x_nums = list(range(len(weights)))
            z = np.polyfit(x_nums, weights, 1)
            p = np.poly1d(z)
            trend = [p(i) for i in x_nums]
            fig.add_trace(go.Scatter(
                x=dates, y=trend, mode="lines",
                name="Trend", line=dict(color="#f59e0b", width=2, dash="dash")
            ))

        fig.update_layout(**ChartBuilder._theme_layout("Weight Progress", 250))
        return fig

    @staticmethod
    def calories_chart(user_id: int, days: int = 7) -> go.Figure:
        weekly = NutritionService.get_weekly_calories(user_id)
        if not weekly:
            fig = go.Figure()
            fig.update_layout(**ChartBuilder._theme_layout("Calories", 200))
            fig.add_annotation(text="No data", x=0.5, y=0.5, showarrow=False, font={"color": "#666"})
            return fig

        dates = [w["date"] for w in weekly]
        cals = [w["calories"] for w in weekly]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=dates, y=cals, name="Calories",
            marker_color="#7c3aed", marker_line_color="#7c3aed",
            marker_line_width=0, opacity=0.8
        ))

        user = __import__("src.models", fromlist=["User"])
        user_obj = __import__("src.services", fromlist=["UserService"]).UserService.get_or_create_user()
        fig.add_hline(
            y=user_obj.target_calories,
            line_dash="dash", line_color="#f59e0b",
            annotation_text=f"Target: {user_obj.target_calories}",
            annotation_font_color="#f59e0b"
        )

        fig.update_layout(**ChartBuilder._theme_layout("Daily Calories", 200))
        return fig

    @staticmethod
    def protein_chart(user_id: int, days: int = 7) -> go.Figure:
        weekly = NutritionService.get_weekly_calories(user_id)
        if not weekly:
            fig = go.Figure()
            fig.update_layout(**ChartBuilder._theme_layout("Protein", 200))
            fig.add_annotation(text="No data", x=0.5, y=0.5, showarrow=False, font={"color": "#666"})
            return fig

        dates = [w["date"] for w in weekly]
        protein = [w["protein"] for w in weekly]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=dates, y=protein, name="Protein",
            marker_color="#10b981", marker_line_color="#10b981",
            marker_line_width=0, opacity=0.8
        ))

        user_obj = __import__("src.services", fromlist=["UserService"]).UserService.get_or_create_user()
        fig.add_hline(
            y=user_obj.target_protein_g,
            line_dash="dash", line_color="#f59e0b",
            annotation_text=f"Target: {user_obj.target_protein_g}g",
            annotation_font_color="#f59e0b"
        )

        fig.update_layout(**ChartBuilder._theme_layout("Daily Protein", 200))
        return fig

    @staticmethod
    def workout_volume_chart(user_id: int, days: int = 30) -> go.Figure:
        session = __import__("src.database", fromlist=["get_session"]).get_session()
        try:
            from src.models import WorkoutSession, WorkoutExercise, ExerciseSet
            cutoff = date.today() - timedelta(days=days)
            results = session.query(
                WorkoutSession.date,
                WorkoutSession.name,
                func.sum(ExerciseSet.weight_kg * ExerciseSet.reps).label("volume")
            ).join(
                WorkoutExercise, WorkoutExercise.session_id == WorkoutSession.id
            ).join(
                ExerciseSet, ExerciseSet.workout_exercise_id == WorkoutExercise.id
            ).filter(
                WorkoutSession.user_id == user_id,
                WorkoutSession.date >= cutoff,
                WorkoutSession.is_completed == True,
                ExerciseSet.is_warmup == False
            ).group_by(WorkoutSession.id).order_by(WorkoutSession.date).all()

            fig = go.Figure()
            if results:
                dates = [r.date for r in results]
                volumes = [round(r.volume, 1) for r in results]
                names = [r.name or r.date.strftime("%a") for r in results]

                fig.add_trace(go.Bar(
                    x=dates, y=volumes, name="Volume",
                    marker_color="#7c3aed", opacity=0.8,
                    text=[f"{int(v):,}kg" for v in volumes],
                    textposition="outside", textfont={"size": 9, "color": "#aaa"}
                ))
            else:
                fig.add_annotation(text="No workout data", x=0.5, y=0.5, showarrow=False, font={"color": "#666"})

            fig.update_layout(**ChartBuilder._theme_layout("Workout Volume", 250))
            return fig
        finally:
            session.close()

    @staticmethod
    def muscle_volume_chart(user_id: int, days: int = 30) -> go.Figure:
        volumes = WorkoutService.get_muscle_volume(user_id, days)
        if not volumes:
            fig = go.Figure()
            fig.update_layout(**ChartBuilder._theme_layout("Muscle Volume", 250))
            fig.add_annotation(text="No data", x=0.5, y=0.5, showarrow=False, font={"color": "#666"})
            return fig

        muscles = list(volumes.keys())
        vols = list(volumes.values())

        colors = ["#7c3aed", "#10b981", "#f59e0b", "#ef4444", "#3b82f6",
                  "#ec4899", "#14b8a6", "#f97316", "#8b5cf6", "#06b6d4"]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=muscles, y=vols, name="Volume",
            marker_color=[colors[i % len(colors)] for i in range(len(muscles))],
            text=[f"{int(v):,}" for v in vols],
            textposition="outside", textfont={"size": 9, "color": "#aaa"}
        ))

        fig.update_layout(**ChartBuilder._theme_layout("Muscle Volume (30d)", 250))
        return fig

    @staticmethod
    def recovery_chart(user_id: int, days: int = 7) -> go.Figure:
        session = __import__("src.database", fromlist=["get_session"]).get_session()
        try:
            from src.models import DailyRecovery
            cutoff = date.today() - timedelta(days=days)
            records = session.query(DailyRecovery).filter(
                DailyRecovery.user_id == user_id,
                DailyRecovery.date >= cutoff
            ).order_by(DailyRecovery.date).all()

            fig = go.Figure()
            if records:
                dates = [r.date for r in records]
                fig.add_trace(go.Scatter(
                    x=dates, y=[r.recovery_score for r in records],
                    mode="lines+markers", name="Recovery",
                    line=dict(color="#10b981", width=3),
                    marker=dict(size=6, color="#10b981"),
                    fill="tozeroy", fillcolor="rgba(16,185,129,0.08)"
                ))
                fig.add_trace(go.Scatter(
                    x=dates, y=[r.fatigue_score * 10 for r in records],
                    mode="lines+markers", name="Fatigue (scaled)",
                    line=dict(color="#ef4444", width=2, dash="dash"),
                    marker=dict(size=5, color="#ef4444")
                ))
            else:
                fig.add_annotation(text="No recovery data", x=0.5, y=0.5, showarrow=False, font={"color": "#666"})

            fig.update_layout(**ChartBuilder._theme_layout("Recovery & Fatigue", 250))
            return fig
        finally:
            session.close()

    @staticmethod
    def workout_frequency_chart(user_id: int, weeks: int = 8) -> go.Figure:
        session = __import__("src.database", fromlist=["get_session"]).get_session()
        try:
            from src.models import WorkoutSession
            weekly_counts = {}
            for i in range(weeks):
                wk_start = date.today() - timedelta(days=7 * i + 6)
                wk_end = date.today() - timedelta(days=7 * i)
                count = session.query(WorkoutSession).filter(
                    WorkoutSession.user_id == user_id,
                    WorkoutSession.date >= wk_start,
                    WorkoutSession.date <= wk_end,
                    WorkoutSession.is_completed == True
                ).count()
                weekly_counts[wk_start.strftime("%b %d")] = count

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=list(reversed(list(weekly_counts.keys()))),
                y=list(reversed(list(weekly_counts.values()))),
                marker_color="#8b5cf6", opacity=0.8,
                text=list(reversed(list(weekly_counts.values()))),
                textposition="outside", textfont={"size": 10, "color": "#aaa"}
            ))

            fig.update_layout(**ChartBuilder._theme_layout("Weekly Workouts", 200))
            return fig
        finally:
            session.close()

    @staticmethod
    def sleep_chart(user_id: int, days: int = 7) -> go.Figure:
        sleeps = SleepService.get_recent(user_id, days)
        if not sleeps:
            fig = go.Figure()
            fig.update_layout(**ChartBuilder._theme_layout("Sleep", 200))
            fig.add_annotation(text="No sleep data", x=0.5, y=0.5, showarrow=False, font={"color": "#666"})
            return fig

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[s.date for s in sleeps],
            y=[s.hours for s in sleeps],
            name="Hours",
            marker_color="#3b82f6", opacity=0.8,
            marker_line_width=0,
            text=[f"{s.hours}h" for s in sleeps],
            textposition="outside", textfont={"size": 9, "color": "#aaa"}
        ))
        fig.add_hline(y=8, line_dash="dash", line_color="#f59e0b",
                      annotation_text="8h target", annotation_font_color="#f59e0b")

        fig.update_layout(**ChartBuilder._theme_layout("Sleep", 200))
        return fig

    @staticmethod
    def water_chart(user_id: int, days: int = 7) -> go.Figure:
        session = __import__("src.database", fromlist=["get_session"]).get_session()
        try:
            from src.models import WaterLog
            from sqlalchemy import func
            cutoff = date.today() - timedelta(days=days)
            results = session.query(
                WaterLog.date,
                func.sum(WaterLog.amount_ml).label("total")
            ).filter(
                WaterLog.user_id == user_id,
                WaterLog.date >= cutoff
            ).group_by(WaterLog.date).order_by(WaterLog.date).all()

            fig = go.Figure()
            if results:
                fig.add_trace(go.Bar(
                    x=[r.date for r in results],
                    y=[r.total / 1000 for r in results],
                    name="Water",
                    marker_color="#06b6d4", opacity=0.8,
                    text=[f"{r.total / 1000:.1f}L" for r in results],
                    textposition="outside", textfont={"size": 9, "color": "#aaa"}
                ))

                user_obj = __import__("src.services", fromlist=["UserService"]).UserService.get_or_create_user()
                fig.add_hline(
                    y=user_obj.target_water_ml / 1000,
                    line_dash="dash", line_color="#f59e0b",
                    annotation_text=f"{user_obj.target_water_ml / 1000:.1f}L target",
                    annotation_font_color="#f59e0b"
                )
            else:
                fig.add_annotation(text="No water data", x=0.5, y=0.5, showarrow=False, font={"color": "#666"})

            fig.update_layout(**ChartBuilder._theme_layout("Water Intake", 200))
            return fig
        finally:
            session.close()

    @staticmethod
    def goal_progress_chart(current: float, target: float) -> go.Figure:
        pct = min(100, (current / target) * 100) if target > 0 else 0
        fig = go.Figure()
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=current,
            number={"suffix": "kg", "font": {"color": "#fff", "size": 24}},
            delta={"reference": target, "increasing": {"color": "#10b981"}},
            gauge={
                "axis": {"range": [None, target * 1.2], "tickcolor": "#666", "tickfont": {"color": "#888"}},
                "bar": {"color": "#7c3aed", "thickness": 0.4},
                "bgcolor": "rgba(255,255,255,0.05)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, target * 0.5], "color": "rgba(239,68,68,0.2)"},
                    {"range": [target * 0.5, target * 0.85], "color": "rgba(245,158,11,0.2)"},
                    {"range": [target * 0.85, target], "color": "rgba(16,185,129,0.2)"},
                ],
                "threshold": {
                    "line": {"color": "#f59e0b", "width": 4},
                    "thickness": 0.75,
                    "value": target
                }
            }
        ))
        fig.update_layout(**ChartBuilder._theme_layout("", 250))
        return fig


def html_from_figure(fig: go.Figure) -> str:
    return fig.to_html(
        include_plotlyjs="cdn",
        full_html=False,
        config=ChartBuilder._config()
    )


# Fix for SQLAlchemy func reference
from sqlalchemy import func
