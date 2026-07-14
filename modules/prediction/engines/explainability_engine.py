"""Explainability Engine — makes predictions explainable, transparent, and auditable.

Produces:
  - Top contributing factors + their weights
  - Confidence explanation
  - Evidence ranking
  - Reason chain (inference steps)
  - Natural language explanation (short, detailed, actionable)
  - Machine-readable explanation (dict for downstream consumption)
"""

from __future__ import annotations

from modules.prediction.domain import (
    ExplainabilityDetail,
    FactorContribution,
    MRExplanation,
    NLExplanation,
    Prediction,
    PredictionEvidence,
    ReasonChain,
    ReasonStep,
)


class ExplainabilityEngine:
    """Generates explainability data for a given Prediction.

    Works by analyzing the prediction's existing explanation data,
    confidence metrics, evidence, and forecast to produce a rich
    explainability detail with factor contributions, reason chains,
    NL and MR explanations.
    """

    def explain(self, prediction: Prediction) -> ExplainabilityDetail:
        factor_contribs = self._compute_factor_contributions(prediction)
        reason_chain = self._build_reason_chain(prediction, factor_contribs)
        nl = self._generate_nl_explanation(prediction, factor_contribs)
        mr = self._generate_mr_explanation(prediction, factor_contribs)
        evidence_ranking = self._rank_evidence(prediction.explanation.evidence)

        return ExplainabilityDetail(
            factor_contributions=factor_contribs,
            reason_chain=reason_chain,
            nl_explanation=nl,
            mr_explanation=mr,
            evidence_ranking=evidence_ranking,
        )

    def _compute_factor_contributions(self, prediction: Prediction) -> list[FactorContribution]:
        contribs: list[FactorContribution] = []
        expl = prediction.explanation

        # Evidence-based factors
        for ev in expl.evidence:
            contribs.append(FactorContribution(
                factor_name=f"{ev.source}:{ev.data_point}",
                contribution=ev.value * ev.relevance * 0.01,
                description=f"{ev.source} data: {ev.data_point} = {ev.value}",
                weight=ev.relevance,
            ))

        # Reasoning-based factors
        for i, reason in enumerate(expl.reasoning):
            weight = max(0.1, 0.5 - i * 0.05)
            contribs.append(FactorContribution(
                factor_name=f"reason_{i + 1}",
                contribution=0.0,
                description=reason,
                weight=weight,
            ))

        # Assumptions
        for i, assumption in enumerate(expl.assumptions):
            contribs.append(FactorContribution(
                factor_name=f"assumption_{i + 1}",
                contribution=0.0,
                description=assumption,
                weight=0.3,
            ))

        # Risk factors
        for i, risk in enumerate(expl.risk_factors):
            contribs.append(FactorContribution(
                factor_name=f"risk_{i + 1}",
                contribution=-0.1 - i * 0.05,
                direction="negative",
                description=risk,
                weight=0.4,
            ))

        # Probability as a factor
        contribs.append(FactorContribution(
            factor_name="predicted_probability",
            contribution=prediction.probability * 100,
            description=f"Model predicted {prediction.probability * 100:.1f}% probability",
            weight=1.0,
        ))

        # Sort by abs(contribution) descending
        contribs.sort(key=lambda c: abs(c.contribution), reverse=True)
        return contribs[:15]  # Top 15

    def _build_reason_chain(self, prediction: Prediction, contribs: list[FactorContribution]) -> ReasonChain:
        steps: list[ReasonStep] = []
        expl = prediction.explanation

        # Step 1: Input observation
        steps.append(ReasonStep(
            step_number=1,
            premise="Input data collected from training, nutrition, recovery providers",
            conclusion=f"Analyzing {prediction.prediction_type.label} over {prediction.window.label}",
            confidence_at_step=prediction.confidence.score,
        ))

        # Step 2: Key factors identified
        if contribs:
            top = contribs[0]
            steps.append(ReasonStep(
                step_number=2,
                premise=f"Top factor: {top.factor_name} (contribution: {top.contribution:+.2f})",
                conclusion=f"Primary driver identified with weight {top.weight:.2f}",
                confidence_at_step=prediction.confidence.score * 0.9,
            ))

        # Step 3: Evidence evaluation
        if expl.evidence:
            steps.append(ReasonStep(
                step_number=3,
                premise=f"Evaluated {len(expl.evidence)} evidence sources",
                conclusion=f"Evidence supports prediction with {prediction.confidence.score * 100:.0f}% confidence",
                confidence_at_step=prediction.confidence.score * 0.85,
            ))

        # Step 4: Assumption check
        if expl.assumptions:
            steps.append(ReasonStep(
                step_number=4,
                premise=f"Applied {len(expl.assumptions)} assumptions",
                conclusion="Prediction valid under stated assumptions",
                confidence_at_step=prediction.confidence.score * 0.8,
            ))

        # Step 5: Risk assessment
        if expl.risk_factors:
            steps.append(ReasonStep(
                step_number=5,
                premise=f"Identified {len(expl.risk_factors)} risk factors",
                conclusion=f"Risks could reduce effective confidence by {len(expl.risk_factors) * 5:.0f}%",
                confidence_at_step=prediction.confidence.score * 0.7,
            ))

        # Step 6: Final prediction
        steps.append(ReasonStep(
            step_number=6,
            premise=f"Model: {prediction.prediction_type.label} | Window: {prediction.window.label}",
            conclusion=f"Prediction: {prediction.value:.1f} (prob: {prediction.probability * 100:.1f}%)",
            confidence_at_step=prediction.confidence.score,
        ))

        return ReasonChain(
            steps=steps,
            final_conclusion=expl.summary,
            overall_confidence=prediction.confidence.score,
        )

    def _generate_nl_explanation(self, prediction: Prediction, contribs: list[FactorContribution]) -> NLExplanation:
        pred_type = prediction.prediction_type
        prob_pct = prediction.probability * 100
        conf_pct = prediction.confidence.score * 100
        window = prediction.window.label

        short = prediction.explanation.summary

        detailed_parts = [
            f"For the {pred_type.label} prediction over {window}, "
            f"the model predicts a value of {prediction.value:.1f} "
            f"with {prob_pct:.0f}% probability.",
        ]
        if contribs:
            top3 = contribs[:3]
            detailed_parts.append("Top contributing factors:")
            for c in top3:
                direction = "positive" if c.contribution >= 0 else "negative"
                detailed_parts.append(
                    f"  - {c.factor_name}: {direction} influence ({abs(c.contribution):.2f})"
                )
        if prediction.explanation.assumptions:
            detailed_parts.append("Key assumptions:")
            for a in prediction.explanation.assumptions:
                detailed_parts.append(f"  - {a}")
        if prediction.explanation.risk_factors:
            detailed_parts.append("Risk factors:")
            for r in prediction.explanation.risk_factors:
                detailed_parts.append(f"  - {r}")
        detailed_parts.append(
            f"Confidence: {conf_pct:.0f}% ({prediction.confidence.level.label}) "
            f"based on {prediction.confidence.sample_size} data points."
        )

        actionable = self._generate_actionable(prediction)

        return NLExplanation(
            short=short,
            detailed="\n".join(detailed_parts),
            actionable=actionable,
        )

    def _generate_actionable(self, prediction: Prediction) -> str:
        pred_type = prediction.prediction_type
        prob = prediction.probability
        value = prediction.value

        if pred_type.value == "next_pr_probability":
            if prob >= 0.6:
                return f"High PR chance ({prob * 100:.0f}%) — consider attempting PR on your main lift this week"
            return f"Low PR chance ({prob * 100:.0f}%) — focus on volume accumulation"

        if pred_type.value == "plateau_probability":
            if prob >= 0.5:
                return f"Plateau risk is {prob * 100:.0f}% — consider deload or exercise variation"
            return "Plateau risk is low — continue current progression"

        if pred_type.value == "recovery_decline":
            if value < 50:
                return f"Recovery forecast is {value:.0f}/100 — prioritize sleep and nutrition"
            return f"Recovery looks good ({value:.0f}/100) — maintain current habits"

        if pred_type.value == "deload_probability":
            if prob >= 0.5:
                return f"Deload probability is {prob * 100:.0f}% — schedule a deload week"
            return "No deload needed — recovery metrics are healthy"

        return prediction.explanation.summary

    def _generate_mr_explanation(self, prediction: Prediction, contribs: list[FactorContribution]) -> MRExplanation:
        return MRExplanation(
            top_factors=[
                {"name": c.factor_name, "contribution": round(c.contribution, 4),
                 "direction": c.direction, "weight": round(c.weight, 4)}
                for c in contribs[:10]
            ],
            confidence_breakdown={
                "overall_score": round(prediction.confidence.score, 4),
                "level": prediction.confidence.level.label,
                "data_quality": round(prediction.confidence.data_quality, 4),
                "sample_size": prediction.confidence.sample_size,
                "variance": round(prediction.confidence.variance, 4),
            },
            evidence_summary=[
                {"source": e.source, "data_point": e.data_point, "value": e.value, "relevance": e.relevance}
                for e in prediction.explanation.evidence
            ],
            assumptions_used=list(prediction.explanation.assumptions),
            risk_flags=list(prediction.explanation.risk_factors),
            model_version="1.0",
        )

    def _rank_evidence(self, evidence: list[PredictionEvidence]) -> list[PredictionEvidence]:
        return sorted(evidence, key=lambda e: e.relevance, reverse=True)
