"""Serializers — capability registry to/from dict and JSON."""

from __future__ import annotations

import json
from typing import Any

from shared.capabilities.capability import Capability
from shared.capabilities.registry import CapabilityRegistry


def capability_to_dict(capability: Capability) -> dict[str, Any]:
    """Serialize a single capability to a dict."""
    return {
        "capability_id": capability.capability_id,
        "name": capability.name,
        "description": capability.description,
        "category": capability.category,
        "owner": capability.owner,
        "status": capability.status.name,
        "version_introduced": capability.version_introduced,
        "target_version": capability.target_version,
        "current_maturity": capability.current_maturity.name,
        "target_maturity": capability.target_maturity.name,
        "health": {
            "overall": capability.health.overall,
            "architecture": capability.health.architecture,
            "test_coverage": capability.health.test_coverage,
            "documentation": capability.health.documentation,
            "platform": capability.health.platform,
        },
        "completion": {
            "current_percent": capability.completion.current_percent,
            "target_percent": capability.completion.target_percent,
            "remaining_tasks": capability.completion.remaining_tasks,
            "total_tasks": capability.completion.total_tasks,
        },
        "technical_debt": {
            "total_items": capability.technical_debt.total_items,
            "critical": capability.technical_debt.critical,
            "high": capability.technical_debt.high,
            "medium": capability.technical_debt.medium,
            "low": capability.technical_debt.low,
        },
        "dependencies": list(capability.dependencies),
        "blocked_by": list(capability.blocked_by),
        "used_by": list(capability.used_by),
        "risk_level": capability.risk_level.name,
        "priority": capability.priority.name,
        "documentation_links": list(capability.documentation_links),
    }


def registry_to_dict(registry: CapabilityRegistry) -> dict[str, Any]:
    """Serialize the entire registry to a dict."""
    return {
        "capability_count": len(registry),
        "capabilities": [capability_to_dict(c) for c in registry.list_all()],
    }


def registry_to_json(registry: CapabilityRegistry, indent: int = 2) -> str:
    """Serialize the entire registry to a JSON string."""
    return json.dumps(registry_to_dict(registry), indent=indent)
