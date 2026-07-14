"""Application icon as embedded SVG.

Provides QIcon at multiple sizes without requiring external files.
"""

from __future__ import annotations

from PySide6.QtCore import QByteArray
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

_ICON_SVG = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <defs>
    <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#818CF8"/>
      <stop offset="100%" stop-color="#6366F1"/>
    </linearGradient>
  </defs>
  <!-- Background rounded square -->
  <rect x="16" y="16" width="480" height="480" rx="96" fill="url(#g)"/>
  <!-- Dumbbell icon -->
  <g fill="none" stroke="#FFFFFF" stroke-width="32" stroke-linecap="round" stroke-linejoin="round">
    <!-- Left weight plates -->
    <rect x="88" y="160" width="48" height="192" rx="16" fill="#FFFFFF"/>
    <rect x="56" y="144" width="40" height="224" rx="12" fill="#FFFFFF"/>
    <!-- Right weight plates -->
    <rect x="376" y="160" width="48" height="192" rx="16" fill="#FFFFFF"/>
    <rect x="416" y="144" width="40" height="224" rx="12" fill="#FFFFFF"/>
    <!-- Bar -->
    <line x1="160" y1="256" x2="352" y2="256" stroke-width="40"/>
  </g>
  <!-- G letter overlay -->
  <text x="256" y="364" font-family="Inter,Helvetica,sans-serif"
        font-size="120" font-weight="800" fill="#FFFFFF" text-anchor="middle"
        style="letter-spacing:-4px;">G</text>
</svg>"""


def create_app_icon() -> QIcon:
    """Create the application icon from embedded SVG.

    Returns a QIcon suitable for setWindowIcon() and taskbar.
    """
    icon = QIcon()

    data = QByteArray(_ICON_SVG.encode("utf-8"))
    renderer = QSvgRenderer(data)

    for size in (16, 32, 48, 64, 96, 128, 256):
        pixmap = QPixmap(size, size)
        pixmap.fill(0)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        icon.addPixmap(pixmap)

    return icon
