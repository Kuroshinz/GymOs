from __future__ import annotations

from enum import Enum


class EvidenceSource(Enum):
    DECISION_ENGINE = "decision_engine"
    PREDICTION = "prediction"
    RECOVERY = "recovery"
    PLANNING = "planning"
    INTENT = "intent"
    KNOWLEDGE = "knowledge"
    ADAPTIVE = "adaptive"
    OPTIMIZATION = "optimization"

    @property
    def label(self) -> str:
        labels = {
            "decision_engine": "Decision Engine",
            "prediction": "Prediction",
            "recovery": "Recovery",
            "planning": "Planning",
            "intent": "Intent",
            "knowledge": "Knowledge",
            "adaptive": "Adaptive Programming",
            "optimization": "Optimization",
        }
        return labels.get(self.value, self.value)


class EvidenceType(Enum):
    RECOMMENDATION = "recommendation"
    PREDICTION = "prediction"
    SCORE = "score"
    ANALYSIS = "analysis"
    CONSTRAINT = "constraint"
    RULE = "rule"
    PATTERN = "pattern"
    INSIGHT = "insight"
    DECISION = "decision"
    GOAL = "goal"

    @property
    def label(self) -> str:
        return self.value.replace("_", " ").title()


class ReasonNodeType(Enum):
    INTENT = "intent"
    KNOWLEDGE = "knowledge"
    RECOVERY = "recovery"
    PREDICTION = "prediction"
    DECISION = "decision"
    RECOMMENDATION = "recommendation"

    @property
    def label(self) -> str:
        return self.value.title()


class CounterfactualAction(Enum):
    INCREASE_VOLUME = "increase_volume"
    MAINTAIN_VOLUME = "maintain_volume"
    DECREASE_VOLUME = "decrease_volume"
    INCREASE_FREQUENCY = "increase_frequency"
    DECREASE_FREQUENCY = "decrease_frequency"
    MODIFY_EXERCISE = "modify_exercise"
    ADJUST_NUTRITION = "adjust_nutrition"
    ADJUST_RECOVERY = "adjust_recovery"
    ADJUST_INTENSITY = "adjust_intensity"
    ADJUST_GOAL = "adjust_goal"

    @property
    def label(self) -> str:
        labels = {
            "increase_volume": "Increase Volume",
            "maintain_volume": "Maintain Volume",
            "decrease_volume": "Decrease Volume",
            "increase_frequency": "Increase Frequency",
            "decrease_frequency": "Decrease Frequency",
            "modify_exercise": "Modify Exercise Selection",
            "adjust_nutrition": "Adjust Nutrition Target",
            "adjust_recovery": "Adjust Recovery Protocol",
            "adjust_intensity": "Adjust Intensity",
            "adjust_goal": "Adjust Goal Priority",
        }
        return labels.get(self.value, self.value.replace("_", " ").title())


class TraceNodeType(Enum):
    RFC = "rfc"
    CAPABILITY = "capability"
    DECISION = "decision"
    RECOMMENDATION = "recommendation"
    UI = "ui"

    @property
    def label(self) -> str:
        return self.value.upper() if self.value == "rfc" else self.value.title()


class ReportFormat(Enum):
    MARKDOWN = "markdown"
    JSON = "json"
    TIMELINE = "timeline"
    TREE = "tree"
    EVIDENCE = "evidence"
    RECOMMENDATION = "recommendation"

    @property
    def label(self) -> str:
        return self.value.title()
