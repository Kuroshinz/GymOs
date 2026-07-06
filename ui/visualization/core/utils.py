from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtGui import QColor


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * clamp(t)


def interpolate_color(c1: str, c2: str, t: float) -> str:
    a = QColor(c1)
    b = QColor(c2)
    t = clamp(t)
    r = int(a.red() + (b.red() - a.red()) * t)
    g = int(a.green() + (b.green() - a.green()) * t)
    bl = int(a.blue() + (b.blue() - a.blue()) * t)
    return f"#{r:02x}{g:02x}{bl:02x}"


def value_to_color(
    value: float,
    colors: Sequence[str] = ("#F87171", "#FBBF24", "#4ADE80"),
    thresholds: Sequence[float] = (0.3, 0.6),
) -> str:
    """Map a 0.0-1.0 value to a color using threshold-based segments."""
    if value <= thresholds[0] or len(colors) < 2:
        return colors[0]
    if value >= thresholds[-1] or len(colors) < 3:
        return colors[-1]
    for i in range(len(thresholds)):
        if value <= thresholds[i]:
            seg_lo = thresholds[i - 1] if i > 0 else 0.0
            seg_hi = thresholds[i]
            t = (value - seg_lo) / (seg_hi - seg_lo) if seg_hi > seg_lo else 0.0
            return interpolate_color(colors[i - 1], colors[i], t)
    return colors[-1]
