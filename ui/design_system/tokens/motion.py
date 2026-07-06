from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MotionCurves:
    linear: str = "0, 0, 1, 1"
    ease: str = "0.25, 0.1, 0.25, 1"
    ease_in: str = "0.42, 0, 1, 1"
    ease_out: str = "0, 0, 0.58, 1"
    ease_in_out: str = "0.42, 0, 0.58, 1"

    spring_standard: str = "0.34, 1.56, 0.64, 1"
    spring_gentle: str = "0.2, 0, 0.4, 1"

    emphasize: str = "0.05, 0, 0, 1"


@dataclass(frozen=True)
class MotionTokens:
    instant: str = "0ms"
    fast: str = "100ms"
    normal: str = "200ms"
    slow: str = "300ms"
    slower: str = "500ms"
    slowest: str = "700ms"

    duration_fast: str = "100ms"
    duration_normal: str = "200ms"
    duration_slow: str = "300ms"
    duration_slower: str = "500ms"
    duration_slowest: str = "700ms"

    delay_none: str = "0ms"
    delay_short: str = "50ms"
    delay_medium: str = "100ms"
    delay_long: str = "200ms"

    curve_linear: str = "cubic-bezier(0, 0, 1, 1)"
    curve_ease: str = "cubic-bezier(0.25, 0.1, 0.25, 1)"
    curve_ease_in: str = "cubic-bezier(0.42, 0, 1, 1)"
    curve_ease_out: str = "cubic-bezier(0, 0, 0.58, 1)"
    curve_ease_in_out: str = "cubic-bezier(0.42, 0, 0.58, 1)"
    curve_spring_standard: str = "cubic-bezier(0.34, 1.56, 0.64, 1)"
    curve_emphasize: str = "cubic-bezier(0.05, 0, 0, 1)"

    _curves: MotionCurves = MotionCurves()


def easing_style(
    duration: str = "200ms",
    curve: str = "cubic-bezier(0.25, 0.1, 0.25, 1)",
    delay: str = "0ms",
    property: str = "all",
) -> str:
    return f"{property} {duration} {curve} {delay}"
