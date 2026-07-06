"""Product Knowledge Graph — core graph data structure.

The KnowledgeGraph is a directed, typed property graph that holds all
architectural elements (nodes) and their relationships (edges).
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field

from shared.graph.edge import Edge, EdgeType
from shared.graph.node import Node, NodeType


@dataclass
class KnowledgeGraph:
    """The Product Knowledge Graph.

    A directed, typed property graph where:
    - Nodes represent architectural elements (capabilities, RFCs, modules, etc.)
    - Edges represent typed relationships (depends_on, implements, contains, etc.)

    Usage:
        graph = KnowledgeGraph()
        graph.add_node(node)
        graph.add_edge(edge)
        deps = graph.get_dependencies("capability:training-intelligence")
    """

    _nodes: dict[str, Node] = field(default_factory=dict)
    _edges: list[Edge] = field(default_factory=list)

    # Adjacency lists for fast lookups
    _outgoing: dict[str, list[Edge]] = field(default_factory=dict)  # source -> edges
    _incoming: dict[str, list[Edge]] = field(default_factory=dict)  # target -> edges

    # ── Node management ──────────────────────────────────────────────────────

    def add_node(self, node: Node) -> None:
        """Add a node to the graph. Replaces any existing node with the same ID."""
        self._nodes[node.node_id] = node
        if node.node_id not in self._outgoing:
            self._outgoing[node.node_id] = []
        if node.node_id not in self._incoming:
            self._incoming[node.node_id] = []

    def has_node(self, node_id: str) -> bool:
        return node_id in self._nodes

    def get_node(self, node_id: str) -> Node | None:
        return self._nodes.get(node_id)

    def remove_node(self, node_id: str) -> None:
        """Remove a node and all its incident edges."""
        self._nodes.pop(node_id, None)
        # Remove outgoing edges
        for edge in list(self._outgoing.get(node_id, [])):
            self._remove_edge_from_list(edge, self._incoming.get(edge.target_id, []))
        # Remove incoming edges
        for edge in list(self._incoming.get(node_id, [])):
            self._remove_edge_from_list(edge, self._outgoing.get(edge.source_id, []))
        self._outgoing.pop(node_id, None)
        self._incoming.pop(node_id, None)
        self._edges = [e for e in self._edges if e.source_id != node_id and e.target_id != node_id]

    def nodes(self) -> Iterator[Node]:
        return iter(self._nodes.values())

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    def nodes_by_type(self, node_type: NodeType) -> list[Node]:
        return [n for n in self._nodes.values() if n.node_type == node_type]

    # ── Edge management ──────────────────────────────────────────────────────

    def add_edge(self, edge: Edge) -> None:
        """Add a directed edge. Automatically creates adjacency entries."""
        self._edges.append(edge)
        if edge.source_id not in self._outgoing:
            self._outgoing[edge.source_id] = []
        if edge.target_id not in self._incoming:
            self._incoming[edge.target_id] = []
        self._outgoing[edge.source_id].append(edge)
        self._incoming[edge.target_id].append(edge)

    def has_edge(self, source_id: str, target_id: str, edge_type: EdgeType | None = None) -> bool:
        for edge in self._edges:
            if edge.source_id == source_id and edge.target_id == target_id:
                if edge_type is None or edge.edge_type == edge_type:
                    return True
        return False

    def remove_edge(self, source_id: str, target_id: str, edge_type: EdgeType | None = None) -> None:
        """Remove matching edges between source and target."""
        remaining: list[Edge] = []
        for edge in self._edges:
            if edge.source_id == source_id and edge.target_id == target_id:
                if edge_type is None or edge.edge_type == edge_type:
                    self._remove_edge_from_list(edge, self._outgoing.get(source_id, []))
                    self._remove_edge_from_list(edge, self._incoming.get(target_id, []))
                    continue
            remaining.append(edge)
        self._edges = remaining

    def edges(self) -> Iterator[Edge]:
        return iter(self._edges)

    @property
    def edge_count(self) -> int:
        return len(self._edges)

    def edges_by_type(self, edge_type: EdgeType) -> list[Edge]:
        return [e for e in self._edges if e.edge_type == edge_type]

    # ── Traversal ────────────────────────────────────────────────────────────

    def get_outgoing(self, node_id: str) -> list[Edge]:
        """All edges where this node is the source."""
        return list(self._outgoing.get(node_id, []))

    def get_incoming(self, node_id: str) -> list[Edge]:
        """All edges where this node is the target."""
        return list(self._incoming.get(node_id, []))

    def get_neighbors(self, node_id: str) -> list[str]:
        """All nodes directly reachable via outgoing edges."""
        neighbors: set[str] = set()
        for edge in self.get_outgoing(node_id):
            neighbors.add(edge.target_id)
        for edge in self.get_incoming(node_id):
            neighbors.add(edge.source_id)
        return list(neighbors)

    def get_dependencies(self, node_id: str) -> list[Node]:
        """Nodes this node depends on.

        Edge(A, B, DEPENDS_ON) means A depends on B.
        So for node A, outgoing edges to targets = dependencies of A.
        """
        dep_ids: set[str] = set()
        for edge in self.get_outgoing(node_id):
            if edge.edge_type in (EdgeType.DEPENDS_ON, EdgeType.USES):
                dep_ids.add(edge.target_id)
        return [self._nodes[nid] for nid in dep_ids if nid in self._nodes]

    def get_dependents(self, node_id: str) -> list[Node]:
        """Nodes that depend on this node.

        Edge(A, B, DEPENDS_ON) means A depends on B.
        So for node B, incoming edges from sources = dependents of B.
        """
        dep_ids: set[str] = set()
        for edge in self.get_incoming(node_id):
            if edge.edge_type in (EdgeType.DEPENDS_ON, EdgeType.USES):
                dep_ids.add(edge.source_id)
        return [self._nodes[nid] for nid in dep_ids if nid in self._nodes]

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _remove_edge_from_list(self, edge: Edge, lst: list[Edge]) -> None:
        try:
            lst.remove(edge)
        except ValueError:
            pass

    def __contains__(self, node_id: str) -> bool:
        return node_id in self._nodes

    def __len__(self) -> int:
        return len(self._nodes)

    def __repr__(self) -> str:
        return f"KnowledgeGraph({self.node_count} nodes, {self.edge_count} edges)"
