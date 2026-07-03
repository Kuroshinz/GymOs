"""Today's top recommendation card — single highest-priority GymBrain recommendation.

Click to expand evidence. Dismiss temporarily. Mark as completed.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from .base_card import DashboardCard

PRIORITY_COLORS = {
    "critical": "#F87171",
    "high": "#FBBF24",
    "medium": "#818CF8",
    "low": "#64748B",
}

PRIORITY_LABELS = {
    90: "CRITICAL",
    70: "HIGH",
    50: "MEDIUM",
    30: "LOW",
    10: "INFO",
}

def _priority_label(priority: int) -> str:
    for threshold, label in sorted(PRIORITY_LABELS.items(), reverse=True):
        if priority >= threshold:
            return label
    return "INFO"

def _priority_color(priority: int) -> str:
    label = _priority_label(priority).lower()
    return PRIORITY_COLORS.get(label, "#64748B")


class RecommendationWidget(DashboardCard):
    """Shows the highest-priority recommendation from GymBrain.

    Supports:
      - Expand/collapse evidence summary
      - Mark as completed
      - Dismiss (temporary, hides until next refresh)
    """

    TITLE_STYLE = "color: #F1F5F9; font-size: 20px; font-weight: 700;"
    BADGE_STYLE_TMPL = (
        "background-color: {bg}; color: #0F172A; border-radius: 6px;"
        " padding: 2px 10px; font-size: 11px; font-weight: 700;"
    )
    CONFIDENCE_STYLE = "color: #94A3B8; font-size: 13px;"
    RULE_STYLE = "color: #64748B; font-size: 12px; font-weight: 500;"
    REASON_STYLE = "color: #F1F5F9; font-size: 14px; line-height: 1.4;"
    EVIDENCE_STYLE = (
        "color: #94A3B8; font-size: 12px; font-style: italic;"
        " background-color: #1E293B; border: 1px solid #334155;"
        " border-radius: 8px; padding: 12px;"
    )
    PLACEHOLDER_STYLE = "color: #64748B; font-size: 14px; padding: 24px 0px;"
    BTN_STYLE = (
        "QPushButton {{ background-color: {bg}; color: #F1F5F9;"
        " border: none; border-radius: 8px; padding: 8px 16px;"
        " font-size: 13px; font-weight: 600; }}"
        " QPushButton:hover {{ background-color: {hover}; }}"
    )
    DISMISS_BTN_STYLE = (
        "QPushButton {{ background-color: transparent; color: #64748B;"
        " border: 1px solid #334155; border-radius: 8px; padding: 8px 16px;"
        " font-size: 13px; font-weight: 600; }}"
        " QPushButton:hover {{ background-color: #334155; color: #F1F5F9; }}"
    )

    def __init__(self, parent: QFrame | None = None) -> None:
        super().__init__(title="Recommendation", parent=parent)
        self._expanded = False
        self._dismissed = False
        self._last_recommendation: Any = None

        self._container = QVBoxLayout()
        self._container.setContentsMargins(0, 0, 0, 0)
        self._container.setSpacing(10)

        self._placeholder = QLabel(
            "No recommendations.\nKeep up the great work!"
        )
        self._placeholder.setStyleSheet(self.PLACEHOLDER_STYLE)
        self._placeholder.setAlignment(Qt.AlignCenter)
        self._placeholder.setWordWrap(True)
        self._container.addWidget(self._placeholder)

        self._content = QVBoxLayout()
        self._content.setContentsMargins(0, 0, 0, 0)
        self._content.setSpacing(10)
        self._container.addLayout(self._content)

        self.add_layout(self._container)

    def set_data(self, data: Any) -> None:
        """Update with dashboard data."""
        recs = getattr(data, "recommendations", [])
        self._dismissed = False
        self.setVisible(True)

        if not recs:
            self._placeholder.show()
            self._hide_content()
            return

        # Use the highest-priority recommendation
        top = recs[0]
        self._last_recommendation = top

        self._placeholder.hide()
        self._build_content(top)

    def _hide_content(self) -> None:
        for i in reversed(range(self._content.count())):
            item = self._content.itemAt(i)
            if item:
                w = item.widget()
                if w:
                    w.deleteLater()
                la = item.layout()
                if la:
                    while la.count():
                        c = la.takeAt(0)
                        if c.widget():
                            c.widget().deleteLater()

    def _build_content(self, rec: Any) -> None:
        self._hide_content()

        # Extract fields from Recommendation object
        title = getattr(rec, "title", "") or getattr(rec, "description", "Recommendation")
        priority = getattr(rec, "priority", 50) or 50
        confidence = getattr(rec, "confidence", 0.0) or 0.0
        rule_name = getattr(rec, "rule_name", "") or ""
        reason = getattr(rec, "reason", "") or ""
        evidence = getattr(rec, "evidence", []) or []
        description = getattr(rec, "description", "") or ""

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(self.TITLE_STYLE)
        title_label.setWordWrap(True)
        self._content.addWidget(title_label)

        # Priority badge + confidence
        prio_row = QHBoxLayout()
        prio_row.setContentsMargins(0, 0, 0, 0)
        prio_row.setSpacing(12)

        color = _priority_color(priority)
        badge = QLabel(_priority_label(priority))
        badge.setStyleSheet(self.BADGE_STYLE_TMPL.format(bg=color))
        badge.setFixedHeight(22)
        prio_row.addWidget(badge)

        conf_label = QLabel(f"{confidence:.0%} confidence")
        conf_label.setStyleSheet(self.CONFIDENCE_STYLE)
        prio_row.addWidget(conf_label)
        prio_row.addStretch()
        self._content.addLayout(prio_row)

        # Description / reason
        display_reason = reason or description
        if display_reason:
            reason_label = QLabel(display_reason)
            reason_label.setStyleSheet(self.REASON_STYLE)
            reason_label.setWordWrap(True)
            self._content.addWidget(reason_label)

        # Rule name
        if rule_name:
            rule_label = QLabel(rule_name)
            rule_label.setStyleSheet(self.RULE_STYLE)
            self._content.addWidget(rule_label)

        # Action
        action = getattr(rec, "action", None)
        if action:
            display = getattr(action, "display", "") or ""
            if display:
                action_label = QLabel(f"→ {display}")
                action_label.setStyleSheet("color: #818CF8; font-size: 13px; font-weight: 600;")
                action_label.setWordWrap(True)
                self._content.addWidget(action_label)

        # Evidence (expandable)
        if evidence:
            self._evidence_container = QVBoxLayout()
            self._evidence_container.setContentsMargins(0, 0, 0, 0)
            self._evidence_container.setSpacing(0)
            self._content.addLayout(self._evidence_container)

            toggle_btn = QPushButton("Show evidence")
            toggle_btn.setStyleSheet(
                "QPushButton { background-color: transparent; color: #818CF8;"
                " border: none; font-size: 13px; font-weight: 600; padding: 4px 0px; text-align: left; }"
                " QPushButton:hover { color: #A5B4FC; }"
            )
            toggle_btn.clicked.connect(self._toggle_evidence)
            self._content.addWidget(toggle_btn)

            ev_text = "\n".join(
                [str(e) for e in evidence[:5]]
            )
            self._evidence_label = QLabel(ev_text)
            self._evidence_label.setStyleSheet(self.EVIDENCE_STYLE)
            self._evidence_label.setWordWrap(True)
            self._evidence_label.setVisible(False)
            self._evidence_container.addWidget(self._evidence_label)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 4, 0, 0)
        btn_row.setSpacing(12)

        dismiss_btn = QPushButton("Dismiss")
        dismiss_btn.setStyleSheet(self.DISMISS_BTN_STYLE)
        dismiss_btn.clicked.connect(self._dismiss)
        btn_row.addWidget(dismiss_btn)

        complete_btn = QPushButton("Mark Completed")
        complete_btn.setStyleSheet(self.BTN_STYLE.format(bg="#818CF8", hover="#A5B4FC"))
        complete_btn.clicked.connect(self._mark_completed)
        btn_row.addWidget(complete_btn)

        btn_row.addStretch()
        self._content.addLayout(btn_row)

    def _toggle_evidence(self) -> None:
        self._expanded = not self._expanded
        if hasattr(self, "_evidence_label"):
            self._evidence_label.setVisible(self._expanded)
        for i in range(self._content.count()):
            item = self._content.itemAt(i)
            if item and item.widget():
                btn = item.widget()
                if isinstance(btn, QPushButton) and btn.text() in ("Show evidence", "Hide evidence"):
                    btn.setText("Hide evidence" if self._expanded else "Show evidence")
                    break

    def _dismiss(self) -> None:
        self._dismissed = True
        self.setVisible(False)

    def _mark_completed(self) -> None:
        self._dismissed = True
        self.setVisible(False)
