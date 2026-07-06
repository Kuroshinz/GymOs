"""Product Knowledge Graph — Node definitions.

Every GymOS architectural element becomes a typed node in the knowledge graph.
Node types capture the full taxonomy: Vision → Roadmap → RFC → Capability → Module → Engine → Feature.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto


class NodeType(Enum):
    """Canonical node types in the Product Knowledge Graph."""

    VISION = auto()
    ROADMAP = auto()
    RFC = auto()
    CAPABILITY = auto()
    MODULE = auto()
    ENGINE = auto()
    FEATURE = auto()
    VERSION = auto()
    MILESTONE = auto()
    DOCUMENT = auto()


# Map of node type names (lowercased) to enum values for string-based lookups
NODE_TYPE_MAP: dict[str, NodeType] = {
    "vision": NodeType.VISION,
    "roadmap": NodeType.ROADMAP,
    "rfc": NodeType.RFC,
    "capability": NodeType.CAPABILITY,
    "module": NodeType.MODULE,
    "engine": NodeType.ENGINE,
    "feature": NodeType.FEATURE,
    "version": NodeType.VERSION,
    "milestone": NodeType.MILESTONE,
    "document": NodeType.DOCUMENT,
}


@dataclass(frozen=True)
class NodeMetadata:
    """Additional metadata attached to a graph node."""

    version_introduced: str = ""
    version_deprecated: str = ""
    status: str = ""  # active, deprecated, planned, draft, complete
    health_score: float = 0.0  # 0-100
    risk_score: float = 0.0  # 0-100
    tags: tuple[str, ...] = field(default_factory=tuple)
    source: str = ""  # which subsystem created this node (capabilities, kernel, evolution)
    description: str = ""
    url: str = ""


@dataclass(frozen=True)
class Node:
    """A single node in the Product Knowledge Graph.

    Every architectural element (capability, RFC, module, engine, feature,
    milestone, version, vision, document) is a node identified by a unique ID.
    """

    node_id: str  # unique identifier, e.g. "capability:training-intelligence"
    node_type: NodeType
    name: str
    metadata: NodeMetadata = field(default_factory=NodeMetadata)

    @property
    def is_active(self) -> bool:
        """A node is active if its status is 'active' or empty."""
        return self.metadata.status in ("active", "", "complete")

    @property
    def short_id(self) -> str:
        """Return the ID without the type prefix, if present."""
        if ":" in self.node_id:
            return self.node_id.split(":", 1)[1]
        return self.node_id

    def __repr__(self) -> str:
        return f"Node({self.node_id}, {self.node_type.name}, {self.name})"
