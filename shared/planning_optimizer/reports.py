"""Planning Optimizer Reports — Markdown report generation for optimization results."""

from __future__ import annotations

from shared.planning_optimizer.domain import (
    OptimizationCandidate,
    OptimizationResult,
)
from shared.planning_optimizer.metrics import OptimizerMetrics


class PlanningOptimizerReports:
    """Generates formatted reports for optimization runs and metrics."""

    @staticmethod
    def generate_optimization_report(result: OptimizationResult) -> str:
        lines: list[str] = []
        lines.append("=" * 60)
        lines.append("OPTIMIZATION REPORT")
        lines.append("=" * 60)
        lines.append(f"Result ID:    {result.result_id}")
        lines.append(f"Request ID:   {result.request_id}")
        lines.append(f"Status:       {result.status.label}")
        lines.append(f"Duration:     {result.duration_seconds:.1f}s")
        lines.append(f"Completed:    {result.completed_at}")
        lines.append("")

        lines.append(f"Generations:       {result.total_generations}")
        lines.append(f"Candidates Eval:   {result.total_evaluated}")
        lines.append(f"Feasible Count:    {result.feasible_count}")
        lines.append(f"Success Rate:      {result.success_rate:.1%}")
        lines.append("")

        lines.append("-" * 60)
        lines.append("BEST CANDIDATE")
        lines.append("-" * 60)
        if result.best_candidate:
            c = result.best_candidate
            lines.append(f"Candidate ID:   {c.candidate_id}")
            lines.append(f"Generation:     {c.generation}")
            lines.append(f"Rank:           {c.rank}")
            lines.append(f"Overall Score:  {c.scores.overall:.3f}")
            lines.append("")
            lines.append("Component Scores:")
            lines.append(f"  Scientific:    {c.scores.scientific_score:.3f}")
            lines.append(f"  Recovery:      {c.scores.recovery_score:.3f}")
            lines.append(f"  Hypertrophy:   {c.scores.hypertrophy_score:.3f}")
            lines.append(f"  Compliance:    {c.scores.compliance_score:.3f}")
            lines.append(f"  Risk:          {c.scores.risk_score:.3f}")
        else:
            lines.append("No feasible candidate found.")
        lines.append("")
        lines.append(result.best_score_summary)
        lines.append("=" * 60)
        return "\n".join(lines)

    @staticmethod
    def generate_candidate_report(candidate: OptimizationCandidate) -> str:
        lines: list[str] = []
        lines.append("-" * 50)
        lines.append(f"CANDIDATE: {candidate.candidate_id[:12]}")
        lines.append("-" * 50)
        lines.append(f"Generation:   {candidate.generation}")
        lines.append(f"Rank:         {candidate.rank}")
        lines.append(f"Status:       {candidate.status.label}")
        lines.append(f"Feasible:     {candidate.is_feasible}")
        lines.append("")
        lines.append("Scores:")
        lines.append(f"  Overall:     {candidate.scores.overall:.3f}")
        lines.append(f"  Scientific:  {candidate.scores.scientific_score:.3f}")
        lines.append(f"  Recovery:    {candidate.scores.recovery_score:.3f}")
        lines.append(f"  Hypertrophy: {candidate.scores.hypertrophy_score:.3f}")
        lines.append(f"  Compliance:  {candidate.scores.compliance_score:.3f}")
        lines.append(f"  Risk:        {candidate.scores.risk_score:.3f}")
        if candidate.constraint_violations:
            lines.append("")
            lines.append("Violations:")
            for v in candidate.constraint_violations[:5]:
                lines.append(f"  - {v}")
        lines.append("-" * 50)
        return "\n".join(lines)

    @staticmethod
    def generate_metrics_report(metrics: OptimizerMetrics) -> str:
        lines: list[str] = []
        lines.append("=" * 60)
        lines.append("OPTIMIZER METRICS REPORT")
        lines.append("=" * 60)
        lines.append(f"Total Optimizations:         {metrics.total_optimizations}")
        lines.append(f"Total Candidates Generated:  {metrics.total_candidates_generated}")
        lines.append(f"Total Feasible:              {metrics.total_feasible_candidates}")
        lines.append(f"Total Generations Run:       {metrics.total_generations_run}")
        lines.append("")
        lines.append(f"Average Best Score:          {metrics.average_best_score:.3f}")
        lines.append(f"Best Score Ever:             {metrics.best_score_ever:.3f}")
        lines.append(f"Average Success Rate:        {metrics.average_success_rate:.1%}")
        lines.append(f"Average Duration:            {metrics.average_duration_seconds:.1f}s")
        lines.append("")
        lines.append(f"Overall Efficiency:          {metrics.overall_efficiency:.1%}")
        lines.append(f"Avg Generations per Run:     {metrics.average_generations_per_run:.1f}")
        lines.append(f"Best Result ID:              {metrics.best_result_id}")
        lines.append("=" * 60)
        return "\n".join(lines)

    @staticmethod
    def generate_summary_report(
        result: OptimizationResult | None = None,
        metrics: OptimizerMetrics | None = None,
    ) -> str:
        lines: list[str] = []
        lines.append("=" * 60)
        lines.append("OPTIMIZER SUMMARY")
        lines.append("=" * 60)
        if result:
            lines.append("Latest Optimization:")
            lines.append(f"  Score:  {result.final_score:.3f}")
            lines.append(f"  Eval:   {result.total_evaluated} candidates")
            lines.append(f"  Feas:   {result.feasible_count} feasible")
            lines.append(f"  Gen:    {result.total_generations}")
            lines.append("")
        if metrics:
            lines.append("Aggregate Metrics:")
            lines.append(f"  Runs:          {metrics.total_optimizations}")
            lines.append(f"  Best Ever:     {metrics.best_score_ever:.3f}")
            lines.append(f"  Avg Score:     {metrics.average_best_score:.3f}")
            lines.append(f"  Success Rate:  {metrics.average_success_rate:.1%}")
        lines.append("=" * 60)
        return "\n".join(lines)
