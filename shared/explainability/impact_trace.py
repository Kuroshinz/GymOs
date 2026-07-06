from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from shared.explainability.domain import TraceNodeType

logger = logging.getLogger("explainability.impact")


@dataclass
class TraceNode:
    node_id: str
    node_type: TraceNodeType
    label: str
    description: str = ""
    parent_id: str | None = None
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ImpactTrace:
    trace_id: str
    nodes: list[TraceNode] = field(default_factory=list)

    @property
    def path(self) -> list[TraceNode]:
        return list(self.nodes)

    @property
    def root(self) -> TraceNode | None:
        return self.nodes[0] if self.nodes else None

    @property
    def leaf(self) -> TraceNode | None:
        return self.nodes[-1] if self.nodes else None

    @property
    def length(self) -> int:
        return len(self.nodes)

    @property
    def node_types(self) -> list[TraceNodeType]:
        return [n.node_type for n in self.nodes]

    def add_node(self, node: TraceNode) -> None:
        if self.nodes:
            node.parent_id = self.nodes[-1].node_id
        self.nodes.append(node)

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "length": self.length,
            "nodes": [
                {
                    "node_id": n.node_id,
                    "node_type": n.node_type.value,
                    "label": n.label,
                    "description": n.description,
                    "parent_id": n.parent_id,
                    "timestamp": n.timestamp,
                }
                for n in self.nodes
            ],
        }

    def to_markdown(self) -> str:
        lines = [f"# Impact Trace: {self.trace_id}", ""]
        for i, node in enumerate(self.nodes):
            prefix = "  " * i
            lines.append(f"{prefix}- **{node.node_type.label}**: {node.label}")
            if node.description:
                lines.append(f"{prefix}  {node.description}")
        return "\n".join(lines)


_TYPICAL_PATH: list[TraceNodeType] = [
    TraceNodeType.RFC,
    TraceNodeType.CAPABILITY,
    TraceNodeType.DECISION,
    TraceNodeType.RECOMMENDATION,
    TraceNodeType.UI,
]


class ImpactTraceStore:
    def __init__(self) -> None:
        self._traces: dict[str, ImpactTrace] = {}
        self._rfc_index: dict[str, list[str]] = {}
        self._capability_index: dict[str, list[str]] = {}

    def create_trace(
        self,
        rfc_label: str = "",
        capability_label: str = "",
        decision_label: str = "",
        recommendation_label: str = "",
        ui_label: str = "",
    ) -> ImpactTrace:
        trace = ImpactTrace(trace_id=uuid.uuid4().hex[:12])
        parent_id: str | None = None

        pairs = [
            (TraceNodeType.RFC, rfc_label),
            (TraceNodeType.CAPABILITY, capability_label),
            (TraceNodeType.DECISION, decision_label),
            (TraceNodeType.RECOMMENDATION, recommendation_label),
            (TraceNodeType.UI, ui_label),
        ]

        for node_type, label in pairs:
            if not label:
                continue
            node_id = uuid.uuid4().hex[:12]
            node = TraceNode(
                node_id=node_id,
                node_type=node_type,
                label=label,
                parent_id=parent_id,
            )
            trace.nodes.append(node)
            parent_id = node_id

        self._traces[trace.trace_id] = trace
        self._index_trace(trace)
        return trace

    def _index_trace(self, trace: ImpactTrace) -> None:
        for node in trace.nodes:
            if node.node_type == TraceNodeType.RFC:
                self._rfc_index.setdefault(node.label, []).append(trace.trace_id)
            elif node.node_type == TraceNodeType.CAPABILITY:
                self._capability_index.setdefault(node.label, []).append(trace.trace_id)

    def add_trace(self, trace: ImpactTrace) -> None:
        self._traces[trace.trace_id] = trace
        self._index_trace(trace)

    def get_trace(self, trace_id: str) -> ImpactTrace | None:
        return self._traces.get(trace_id)

    def query_by_rfc(self, rfc_label: str) -> list[ImpactTrace]:
        trace_ids = self._rfc_index.get(rfc_label, [])
        return [self._traces[tid] for tid in trace_ids if tid in self._traces]

    def query_by_capability(self, capability_label: str) -> list[ImpactTrace]:
        trace_ids = self._capability_index.get(capability_label, [])
        return [self._traces[tid] for tid in trace_ids if tid in self._traces]

    def query_by_type(self, node_type: TraceNodeType) -> list[ImpactTrace]:
        return [
            t for t in self._traces.values()
            if any(n.node_type == node_type for n in t.nodes)
        ]

    def get_all(self) -> list[ImpactTrace]:
        return list(self._traces.values())

    def clear(self) -> None:
        self._traces.clear()
        self._rfc_index.clear()
        self._capability_index.clear()

    @property
    def count(self) -> int:
        return len(self._traces)

    def to_dict(self) -> dict[str, Any]:
        return {
            "count": self.count,
            "traces": [t.to_dict() for t in self._traces.values()],
        }
