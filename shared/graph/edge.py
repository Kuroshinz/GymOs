"""Product Knowledge Graph — Edge definitions.

Typed relationships connect nodes into a directed graph. Each edge type
captures a specific architectural relationship: dependencies, containment,
ownership, evolution, documentation, communication, and membership.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class EdgeType(Enum):
    """Canonical relationship types in the Product Knowledge Graph."""

    DEPENDS_ON = auto()       # A depends on B (B must exist first)
    IMPLEMENTS = auto()       # A implements B (e.g., Module implements Capability)
    OWNS = auto()            # A owns B (e.g., Capability owns Feature)
    CONTAINS = auto()        # A contains B (e.g., Version contains Capabilities)
    EVOLVES_TO = auto()      # A evolves into B (e.g., RFC evolves to Capability)
    DOCUMENTS = auto()       # A documents B (e.g., Doc documents Module)
    USES = auto()            # A uses B (weaker than depends_on)
    PUBLISHES = auto()       # A publishes events consumed by B
    SUBSCRIBES = auto()      # A subscribes to events from B
    BELONGS_TO = auto()      # A belongs to B (inverse of CONTAINS)


# Map of edge type names (lowercased) to enum values
EDGE_TYPE_MAP: dict[str, EdgeType] = {
    "depends_on": EdgeType.DEPENDS_ON,
    "implements": EdgeType.IMPLEMENTS,
    "owns": EdgeType.OWNS,
    "contains": EdgeType.CONTAINS,
    "evolves_to": EdgeType.EVOLVES_TO,
    "documents": EdgeType.DOCUMENTS,
    "uses": EdgeType.USES,
    "publishes": EdgeType.PUBLISHES,
    "subscribes": EdgeType.SUBSCRIBES,
    "belongs_to": EdgeType.BELONGS_TO,
}


@dataclass(frozen=True)
class Edge:
    """A directed, typed relationship between two nodes.

    source_id -> target_id via edge_type.
    """

    source_id: str
    target_id: str
    edge_type: EdgeType
    weight: float = 1.0  # strength/significance of the relationship
    metadata: str = ""   # optional description or context

    @property
    def reversed_type(self) -> EdgeType:
        """Return the logical inverse edge type.

        depends_on  ↔ depends_on (symmetric in meaning, reversed direction)
        contains    ↔ belongs_to
        owns        ↔ belongs_to
        implements  ↔ belongs_to
        documents   ↔ documents (symmetric)
        uses        ↔ uses (symmetric)
        publishes   ↔ subscribes
        evolves_to  ↔ evolves_to (directional, no simple inverse)
        """
        inverse_map: dict[EdgeType, EdgeType] = {
            EdgeType.CONTAINS: EdgeType.BELONGS_TO,
            EdgeType.OWNS: EdgeType.BELONGS_TO,
            EdgeType.IMPLEMENTS: EdgeType.BELONGS_TO,
            EdgeType.PUBLISHES: EdgeType.SUBSCRIBES,
            EdgeType.SUBSCRIBES: EdgeType.PUBLISHES,
        }
        return inverse_map.get(self.edge_type, self.edge_type)

    def __repr__(self) -> str:
        return f"Edge({self.source_id} -[{self.edge_type.name}]-> {self.target_id})"
