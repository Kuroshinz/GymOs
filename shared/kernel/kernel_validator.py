"""Kernel Validator — validates kernel state, debt items, and readiness.

Stateless validation functions.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from shared.kernel.kernel import (
    DebtRegistryItem,
    KernelSnapshot,
    Release,
    ReleaseReadinessResult,
    RfcRecord,
)


@dataclass(frozen=True)
class KernelValidationError:
    """A single kernel validation error."""
    field: str
    message: str
    severity: str = "error"  # error, warning


@dataclass(frozen=True)
class KernelValidationResult:
    """Complete kernel validation result."""
    is_valid: bool
    errors: tuple[KernelValidationError, ...] = field(default_factory=tuple)


def validate_rfc(rfc: RfcRecord) -> list[KernelValidationError]:
    errors: list[KernelValidationError] = []
    if not rfc.rfc_id:
        errors.append(KernelValidationError(field="rfc_id", message="RFC ID is required"))
    if not rfc.title:
        errors.append(KernelValidationError(field="title", message="RFC title is required"))
    return errors


def validate_release(release: Release) -> list[KernelValidationError]:
    errors: list[KernelValidationError] = []
    if not release.version:
        errors.append(KernelValidationError(field="version", message="Release version is required"))
    return errors


def validate_debt_item(item: DebtRegistryItem) -> list[KernelValidationError]:
    errors: list[KernelValidationError] = []
    if not item.debt_id:
        errors.append(KernelValidationError(field="debt_id", message="Debt item ID is required"))
    if not item.title:
        errors.append(KernelValidationError(field="title", message="Debt item title is required"))
    if not item.owner:
        errors.append(KernelValidationError(field="owner", message="Debt item owner is required"))
    if item.severity not in ("critical", "high", "medium", "low"):
        errors.append(KernelValidationError(field="severity", message=f"Invalid severity: {item.severity}"))
    return errors


def validate_snapshot(snapshot: KernelSnapshot) -> list[KernelValidationError]:
    errors: list[KernelValidationError] = []
    if not snapshot.timestamp:
        errors.append(KernelValidationError(field="timestamp", message="Snapshot timestamp is required"))
    return errors


def validate_release_readiness(result: ReleaseReadinessResult) -> list[KernelValidationError]:
    errors: list[KernelValidationError] = []
    if result.score < 0 or result.score > 100:
        errors.append(KernelValidationError(field="score", message=f"Release score out of range: {result.score}"))
    if result.blocker_count < 0:
        errors.append(KernelValidationError(field="blocker_count", message="Blocker count cannot be negative"))
    return errors


def validate_all_debt_items(items: list[DebtRegistryItem]) -> KernelValidationResult:
    all_errors: list[KernelValidationError] = []
    for item in items:
        all_errors.extend(validate_debt_item(item))
    return KernelValidationResult(
        is_valid=len(all_errors) == 0,
        errors=tuple(all_errors),
    )
