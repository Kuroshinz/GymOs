from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from shared.explainability.domain import ReasonNodeType

logger = logging.getLogger("explainability.reason_tree")

_CHAIN_ORDER: dict[ReasonNodeType, int] = {
    ReasonNodeType.INTENT: 0,
    ReasonNodeType.KNOWLEDGE: 1,
    ReasonNodeType.RECOVERY: 2,
    ReasonNodeType.PREDICTION: 3,
    ReasonNodeType.DECISION: 4,
    ReasonNodeType.RECOMMENDATION: 5,
}


@dataclass
class ReasonNode:
    node_id: str
    node_type: ReasonNodeType
    label: str
    description: str = ""
    confidence: float = 0.0
    evidence_ids: list[str] = field(default_factory=list)
    parent_id: str | None = None
    children_ids: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    metadata: dict = field(default_factory=dict)


@dataclass
class ReasonChain:
    chain_id: str
    nodes: list[ReasonNode] = field(default_factory=list)

    @property
    def length(self) -> int:
        return len(self.nodes)

    @property
    def is_complete(self) -> bool:
        return len(self.nodes) >= 2

    @property
    def overall_confidence(self) -> float:
        if not self.nodes:
            return 0.0
        return sum(n.confidence for n in self.nodes) / len(self.nodes)

    @property
    def node_types(self) -> list[ReasonNodeType]:
        return [n.node_type for n in self.nodes]

    def to_dict(self) -> dict[str, Any]:
        return {
            "chain_id": self.chain_id,
            "length": self.length,
            "is_complete": self.is_complete,
            "overall_confidence": self.overall_confidence,
            "nodes": [
                {
                    "node_id": n.node_id,
                    "node_type": n.node_type.value,
                    "label": n.label,
                    "description": n.description,
                    "confidence": n.confidence,
                    "evidence_ids": n.evidence_ids,
                    "parent_id": n.parent_id,
                    "children_ids": n.children_ids,
                    "timestamp": n.timestamp,
                }
                for n in self.nodes
            ],
        }


class ReasonTree:
    def __init__(self) -> None:
        self._nodes: dict[str, ReasonNode] = {}
        self._chains: dict[str, ReasonChain] = {}
        self._type_index: dict[ReasonNodeType, list[str]] = {}

    def add_node(self, node: ReasonNode) -> None:
        self._nodes[node.node_id] = node
        self._type_index.setdefault(node.node_type, []).append(node.node_id)

    def get_node(self, node_id: str) -> ReasonNode | None:
        return self._nodes.get(node_id)

    def get_nodes_by_type(self, node_type: ReasonNodeType) -> list[ReasonNode]:
        node_ids = self._type_index.get(node_type, [])
        return [self._nodes[nid] for nid in node_ids if nid in self._nodes]

    def build_chain(self, recommendation_id: str) -> ReasonChain | None:
        if recommendation_id not in self._nodes:
            return None
        chain = ReasonChain(chain_id=uuid.uuid4().hex[:12])
        visited: set[str] = set()
        current_id: str | None = recommendation_id

        while current_id is not None and current_id not in visited:
            visited.add(current_id)
            node = self._nodes.get(current_id)
            if node is None:
                break
            chain.nodes.append(node)
            current_id = node.parent_id

        chain.nodes.sort(key=lambda n: _CHAIN_ORDER.get(n.node_type, 99))
        self._chains[chain.chain_id] = chain
        return chain

    def get_chain(self, chain_id: str) -> ReasonChain | None:
        return self._chains.get(chain_id)

    def find_chains_for_node(self, node_id: str) -> list[ReasonChain]:
        return [c for c in self._chains.values() if any(n.node_id == node_id for n in c.nodes)]

    def query(
        self,
        node_type: ReasonNodeType | None = None,
        min_confidence: float = 0.0,
    ) -> list[ReasonNode]:
        result = list(self._nodes.values())
        if node_type is not None:
            result = [n for n in result if n.node_type == node_type]
        if min_confidence > 0.0:
            result = [n for n in result if n.confidence >= min_confidence]
        return result

    def get_all_nodes(self) -> list[ReasonNode]:
        return list(self._nodes.values())

    def get_all_chains(self) -> list[ReasonChain]:
        return list(self._chains.values())

    def clear(self) -> None:
        self._nodes.clear()
        self._chains.clear()
        self._type_index.clear()

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    @property
    def chain_count(self) -> int:
        return len(self._chains)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_count": self.node_count,
            "chain_count": self.chain_count,
            "nodes": [
                {
                    "node_id": n.node_id,
                    "node_type": n.node_type.value,
                    "label": n.label,
                    "description": n.description,
                    "confidence": n.confidence,
                    "evidence_ids": n.evidence_ids,
                    "parent_id": n.parent_id,
                    "children_ids": n.children_ids,
                    "timestamp": n.timestamp,
                }
                for n in self._nodes.values()
            ],
            "chains": [c.to_dict() for c in self._chains.values()],
        }
