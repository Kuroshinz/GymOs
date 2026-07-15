"""Validators — capability registry integrity checks.

Stateless validation functions.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from shared.capabilities.enums import CapabilityMaturity, CapabilityStatus
from shared.capabilities.registry import CapabilityRegistry

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ValidationError:
    """A single validation error found in the capability registry."""
    field: str
    message: str
    severity: str = "error"  # error, warning


@dataclass(frozen=True)
class ValidationResult:
    """Complete validation result for the capability registry."""
    is_valid: bool
    errors: tuple[ValidationError, ...] = field(default_factory=tuple)


def validate_duplicate_ids(registry: CapabilityRegistry) -> list[ValidationError]:
    """Check for duplicate capability IDs (handled by registry itself, but belt-and-suspenders)."""
    errors: list[ValidationError] = []
    seen: dict[str, list[str]] = {}
    for cap in registry.list_all():
        if cap.capability_id not in seen:
            seen[cap.capability_id] = []
        seen[cap.capability_id].append(cap.name)
    for cid, names in seen.items():
        if len(names) > 1:
            errors.append(ValidationError(
                field="capability_id",
                message=f"Duplicate capability_id '{cid}' used by: {', '.join(names)}",
            ))
    return errors


def validate_dependency_cycles(registry: CapabilityRegistry) -> list[ValidationError]:
    """Check for direct self-referencing dependencies."""
    errors: list[ValidationError] = []
    for cap in registry.list_all():
        if cap.capability_id in cap.dependencies:
            errors.append(ValidationError(
                field="dependencies",
                message=f"Capability '{cap.name}' depends on itself",
            ))
    return errors


def validate_missing_owners(registry: CapabilityRegistry) -> list[ValidationError]:
    """Check that all capabilities have an owner."""
    errors: list[ValidationError] = []
    for cap in registry.list_all():
        if not cap.owner:
            errors.append(ValidationError(
                field="owner",
                message=f"Capability '{cap.name}' has no owner",
            ))
    return errors


def validate_invalid_maturity(registry: CapabilityRegistry) -> list[ValidationError]:
    """Check that maturity values are valid."""
    errors: list[ValidationError] = []
    levels = list(CapabilityMaturity)
    for cap in registry.list_all():
        if cap.current_maturity not in levels:
            errors.append(ValidationError(
                field="current_maturity",
                message=f"Capability '{cap.name}' has invalid current maturity: {cap.current_maturity}",
            ))
        if cap.target_maturity not in levels:
            errors.append(ValidationError(
                field="target_maturity",
                message=f"Capability '{cap.name}' has invalid target maturity: {cap.target_maturity}",
            ))
        try:
            if levels.index(cap.current_maturity) > levels.index(cap.target_maturity):
                errors.append(ValidationError(
                    field="target_maturity",
                    message=f"Capability '{cap.name}' target maturity is below current maturity",
                    severity="warning",
                ))
        except ValueError:
            logger.warning(
                "Invalid maturity level in capability '%s': current=%s, target=%s",
                cap.name, cap.current_maturity, cap.target_maturity,
                exc_info=True,
            )
    return errors


def validate_roadmap_consistency(registry: CapabilityRegistry) -> list[ValidationError]:
    """Check roadmap consistency."""
    errors: list[ValidationError] = []
    for cap in registry.list_all():
        if cap.status == CapabilityStatus.COMPLETE and cap.current_maturity.value < CapabilityMaturity.IMPLEMENTED.value:
            errors.append(ValidationError(
                field="status",
                message=f"Capability '{cap.name}' is COMPLETE but maturity is {cap.current_maturity.name}",
                severity="warning",
            ))
        if cap.status == CapabilityStatus.IN_PROGRESS and cap.current_maturity == CapabilityMaturity.CONCEPT:
            errors.append(ValidationError(
                field="status",
                message=f"Capability '{cap.name}' is IN_PROGRESS but maturity is CONCEPT",
                severity="warning",
            ))
    return errors


def validate_all(registry: CapabilityRegistry) -> ValidationResult:
    """Run all validators and return combined result."""
    all_errors: list[ValidationError] = []
    all_errors.extend(validate_duplicate_ids(registry))
    all_errors.extend(validate_dependency_cycles(registry))
    all_errors.extend(validate_missing_owners(registry))
    all_errors.extend(validate_invalid_maturity(registry))
    all_errors.extend(validate_roadmap_consistency(registry))
    is_valid = all(e.severity == "warning" for e in all_errors) or len(all_errors) == 0
    return ValidationResult(is_valid=is_valid, errors=tuple(all_errors))
