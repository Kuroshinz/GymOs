from __future__ import annotations

from typing import Any

from ui.narrative.engine import Narrative


def risk_alerts(
    alerts: list[dict[str, Any]] | None = None,
    **kwargs: Any,
) -> Narrative:
    if not alerts:
        return Narrative(
            title="Risk Alerts",
            summary="No risk alerts. All clear.",
            source_keys=["risk_alerts"],
            metadata={"severity": "info"},
        )

    body_parts = []
    detail_parts = []
    actions = []
    severities = set()

    for i, alert in enumerate(alerts):
        title = alert.get("title", f"Alert {i + 1}")
        desc = alert.get("description", "")
        severity = alert.get("severity", "info")
        action = alert.get("action", "")
        severities.add(severity)

        body_parts.append(f"{title}: {desc}")
        detail_parts.append(f"[{severity.upper()}] {title} \u2014 {desc}")
        if action:
            actions.append(action)

    max_severity = "critical" if "critical" in severities else (
        "warning" if "warning" in severities else "info"
    )

    return Narrative(
        title=f"Risk Alerts ({len(alerts)})",
        summary=f"{len(alerts)} alert(s) active. Highest severity: {max_severity}.",
        body="\n".join(body_parts),
        detail="\n".join(detail_parts),
        action_items=actions,
        source_keys=["risk_alerts"],
        metadata={"severity": max_severity},
    )
