"""Recovery Engine — rule-based fatigue detection.

Detects recovery flags based on training data:
  1. Multiple RIR 0 sets (training to failure on multiple exercises)
  2. Large rep drop across sets within an exercise
  3. Consecutive performance decline across sessions
  4. High volume sessions (potential overreaching)

Knowledge sources:
  - knowledge/recovery/fatigue.md
  - knowledge/recovery/doms.md
  - knowledge/progression/failure.md
"""

from dataclasses import dataclass, field


@dataclass
class RecoveryFlag:
    """A single recovery warning."""

    flag_type: str  # "rir_zero", "rep_drop", "decline", "high_volume"
    severity: str  # "info", "warning", "critical"
    message: str
    exercise_name: str | None = None
    detail: str = ""


@dataclass
class RecoveryReport:
    """Complete recovery analysis for a session."""

    flags: list[RecoveryFlag] = field(default_factory=list)
    has_warnings: bool = False
    should_deload: bool = False

    @property
    def severity(self) -> str:
        if self.should_deload:
            return "critical"
        if self.has_warnings:
            return "warning"
        return "ok"


class RecoveryEngine:
    """Analyses training data for fatigue and recovery signals."""

    def __init__(self, db) -> None:
        self._db = db

    def analyse_session(self, session) -> RecoveryReport:
        """Analyse a completed session for recovery flags."""
        # Import here to avoid circular imports
        from modules.workout.domain import WorkoutSession

        report = RecoveryReport()

        if not isinstance(session, WorkoutSession):
            return report

        # Flag 1: Multiple RIR 0 sets
        rir_zero_sets = []
        for ex in session.exercises:
            for s in ex.sets:
                if s.completed and s.rir is not None and s.rir == 0:
                    rir_zero_sets.append((ex.name, s.set_number))

        if len(rir_zero_sets) >= 3:
            report.flags.append(RecoveryFlag(
                flag_type="rir_zero",
                severity="warning",
                message=f"{len(rir_zero_sets)} sets trained to failure (RIR 0)",
                detail="Training to failure on multiple sets increases CNS fatigue. "
                       "Consider leaving 1-2 reps in reserve next session.",
            ))
            report.has_warnings = True
        elif len(rir_zero_sets) >= 1:
            report.flags.append(RecoveryFlag(
                flag_type="rir_zero",
                severity="info",
                message=f"{len(rir_zero_sets)} set(s) trained to failure",
                detail="Keep failure sets to a minimum, especially on compounds.",
            ))

        # Flag 2: Large rep drop across sets within an exercise
        for ex in session.exercises:
            completed_reps = [
                s.reps for s in ex.sets if s.completed and s.reps > 0
            ]
            if len(completed_reps) >= 3:
                if max(completed_reps) - min(completed_reps) >= 4:
                    report.flags.append(RecoveryFlag(
                        flag_type="rep_drop",
                        severity="info",
                        exercise_name=ex.name,
                        message=f"Rep drop in {ex.name}: "
                                f"{', '.join(str(r) for r in completed_reps)}",
                        detail=f"Drop of {max(completed_reps) - min(completed_reps)} "
                               f"reps suggests fatigue accumulation.",
                    ))
                    report.has_warnings = True

        # Flag 3: Consecutive performance decline
        for ex in session.exercises:
            decline = self._check_performance_decline(ex.name, 3)
            if decline:
                report.flags.append(RecoveryFlag(
                    flag_type="decline",
                    severity="warning",
                    exercise_name=ex.name,
                    message=f"Performance decline in {ex.name}",
                    detail=f"Volume has decreased over the last {decline} sessions. "
                           f"Consider a deload or switching exercise variation.",
                ))
                report.has_warnings = True
                if decline >= 3:
                    report.should_deload = True

        # Flag 4: High volume session
        total_sets = session.completed_sets_count
        if total_sets > 20:
            report.flags.append(RecoveryFlag(
                flag_type="high_volume",
                severity="info",
                message=f"High volume session: {total_sets} working sets",
                detail="Research suggests diminishing returns beyond 20 sets/session. "
                       "Optimal range is 10-20 sets.",
            ))

        # Flag 5: Check recent training frequency
        recent_volume = self._db.get_recent_volume(3)
        if recent_volume > 30000:  # Very high 3-day volume
            report.flags.append(RecoveryFlag(
                flag_type="high_volume",
                severity="warning",
                message="Very high training volume over last 3 days",
                detail=f"3-day volume: {recent_volume:.0f} kg. Monitor for overreaching.",
            ))
            report.has_warnings = True

        return report

    def _check_performance_decline(
        self, exercise_name: str, max_sessions: int = 3
    ) -> int:
        """Check if performance is declining across recent sessions.

        Returns the number of consecutive declining sessions (0 = no decline).
        """
        sessions = self._db.list_sessions(limit=20)
        relevant_sessions = []

        for s in sessions:
            if not s.completed_at:
                continue
            for ex in s.exercises:
                if ex.name == exercise_name:
                    vol = sum(
                        st.weight_kg * st.reps
                        for st in ex.sets
                        if st.completed and st.reps > 0
                    )
                    if vol > 0:
                        relevant_sessions.append(vol)
                    break

        if len(relevant_sessions) < 2:
            return 0

        decline_count = 0
        for i in range(1, min(len(relevant_sessions), max_sessions + 1)):
            if relevant_sessions[i] < relevant_sessions[i - 1]:
                decline_count += 1
            else:
                break

        return decline_count

    def get_dashboard_flags(self) -> RecoveryReport:
        """Get recovery flags for the dashboard view."""
        sessions = self._db.list_sessions(limit=10)
        report = RecoveryReport()

        # Check if last session had warnings
        if sessions:
            last_session = sessions[0]
            if last_session.completed_at:
                report = self.analyse_session(last_session)

        return report
