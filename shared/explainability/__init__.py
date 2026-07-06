from __future__ import annotations

from shared.explainability.platform import ExplainabilityPlatform


def create_explainability_platform() -> ExplainabilityPlatform:
    return ExplainabilityPlatform()


__all__ = ["create_explainability_platform", "ExplainabilityPlatform"]
