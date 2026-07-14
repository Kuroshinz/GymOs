"""Graph Health — assesses the health and quality of the Product Knowledge Graph itself.

Measures:
- Completeness (do all canonical elements have nodes?)
- Connectivity (are nodes properly connected?)
- Cycle health (are there dependency cycles?)
- Orphan health (are there isolated nodes?)
- Depth health (are dependency chains reasonable?)
"""

from __future__ import annotations

from dataclasses import dataclass

from shared.graph.edge import EdgeType
from shared.graph.graph import KnowledgeGraph
from shared.graph.node import NodeType
from shared.graph.query import GraphQuery


@dataclass(frozen=True)
class GraphHealthScore:
    """Multi-dimensional health score for the Product Knowledge Graph."""

    overall: float = 0.0  # 0-100
    completeness: float = 0.0  # % of expected nodes present
    connectivity: float = 0.0  # % of nodes with edges
    cycle_health: float = 0.0  # 100 if no cycles
    orphan_health: float = 0.0  # 100 if no orphans
    depth_health: float = 0.0  # based on max dependency depth
    node_count: int = 0
    edge_count: int = 0
    cycle_count: int = 0
    orphan_count: int = 0
    max_depth: int = 0
    avg_edges_per_node: float = 0.0
    rating: str = "unknown"


class GraphHealthAnalyzer:
    """Analyzes the health and quality of the Product Knowledge Graph."""

    # Expected node types and their minimum counts
    EXPECTED_NODE_TYPES: dict[NodeType, tuple[int, str]] = {
        NodeType.VISION: (1, "Product vision"),
        NodeType.ROADMAP: (3, "Roadmap stages"),
        NodeType.RFC: (3, "RFCs"),
        NodeType.CAPABILITY: (8, "Capabilities"),
        NodeType.MODULE: (3, "Modules"),
        NodeType.ENGINE: (3, "Engines"),
        NodeType.FEATURE: (5, "Features"),
        NodeType.VERSION: (3, "Versions"),
        NodeType.MILESTONE: (3, "Milestones"),
        NodeType.DOCUMENT: (1, "Documents"),
    }

    # Maximum reasonable dependency depth before we flag it
    MAX_REASONABLE_DEPTH = 6

    def __init__(self, graph: KnowledgeGraph) -> None:
        self._graph = graph
        self._query = GraphQuery(graph)

    def analyze(self) -> GraphHealthScore:
        """Compute all health dimensions and return a composite score."""
        completeness = self._score_completeness()
        connectivity = self._score_connectivity()
        cycle_health = self._score_cycles()
        orphan_health = self._score_orphans()
        depth_health = self._score_depth()

        # Composite: weighted average
        overall = (
            completeness * 0.30 +
            connectivity * 0.25 +
            cycle_health * 0.20 +
            orphan_health * 0.15 +
            depth_health * 0.10
        )

        # Count stats
        cycles = self._query.find_cycles()
        orphans = self._query.find_orphans()
        max_depth = self._compute_max_depth()
        avg_edges = (self._graph.edge_count / max(self._graph.node_count, 1))

        rating = self._compute_rating(overall)

        return GraphHealthScore(
            overall=round(overall, 1),
            completeness=round(completeness, 1),
            connectivity=round(connectivity, 1),
            cycle_health=round(cycle_health, 1),
            orphan_health=round(orphan_health, 1),
            depth_health=round(depth_health, 1),
            node_count=self._graph.node_count,
            edge_count=self._graph.edge_count,
            cycle_count=len(cycles),
            orphan_count=len(orphans),
            max_depth=max_depth,
            avg_edges_per_node=round(avg_edges, 2),
            rating=rating,
        )

    def _score_completeness(self) -> float:
        """Score how complete the graph is: does it cover all expected node types?"""
        type_counts: dict[NodeType, int] = {}
        for node in self._graph.nodes():
            type_counts[node.node_type] = type_counts.get(node.node_type, 0) + 1

        if not self.EXPECTED_NODE_TYPES:
            return 100.0

        max_score = len(self.EXPECTED_NODE_TYPES)
        score = 0.0
        for node_type, (min_count, _label) in self.EXPECTED_NODE_TYPES.items():
            count = type_counts.get(node_type, 0)
            if count >= min_count:
                score += 1.0
            else:
                # Partial credit
                score += count / max(min_count, 1)

        return (score / max_score) * 100.0

    def _score_connectivity(self) -> float:
        """Score how well connected the graph is."""
        if self._graph.node_count == 0:
            return 0.0

        connected = 0
        for node in self._graph.nodes():
            outgoing = self._graph.get_outgoing(node.node_id)
            incoming = self._graph.get_incoming(node.node_id)
            if outgoing or incoming:
                connected += 1

        return (connected / self._graph.node_count) * 100.0

    def _score_cycles(self) -> float:
        """Score the cycle health: 100 if no cycles, decreasing with cycles."""
        cycles = self._query.find_cycles()
        if not cycles:
            return 100.0
        # Penalty: each cycle reduces score by 20 points, minimum 0
        return max(0.0, 100.0 - (len(cycles) * 20.0))

    def _score_orphans(self) -> float:
        """Score the orphan health: 100 if no orphans, decreasing otherwise."""
        orphans = self._query.find_orphans()
        if not orphans:
            return 100.0
        if self._graph.node_count == 0:
            return 0.0
        orphan_ratio = len(orphans) / self._graph.node_count
        return max(0.0, 100.0 - (orphan_ratio * 200.0))

    def _score_depth(self) -> float:
        """Score based on dependency chain depth.

        Shorter chains are healthier. Depth > MAX_REASONABLE_DEPTH is concerning.
        """
        max_depth = self._compute_max_depth()
        if max_depth <= 2:
            return 100.0
        if max_depth <= self.MAX_REASONABLE_DEPTH:
            return 80.0 + ((self.MAX_REASONABLE_DEPTH - max_depth) / self.MAX_REASONABLE_DEPTH) * 20.0
        # Too deep
        over = max_depth - self.MAX_REASONABLE_DEPTH
        return max(0.0, 80.0 - (over * 15.0))

    def _compute_max_depth(self) -> int:
        """Find the maximum dependency depth across all nodes."""
        all_nodes = list(self._graph.nodes())
        if not all_nodes:
            return 0
        max_depth = 0
        for node in all_nodes:
            # Compute depth for this node
            depth = self._node_depth(node.node_id)
            max_depth = max(max_depth, depth)
        return max_depth

    def _node_depth(self, node_id: str) -> int:
        """Compute the maximum transitive dependency depth from a node."""
        visited: set[str] = set()
        max_depth = [0]

        def _dfs(current: str, depth: int) -> None:
            visited.add(current)
            max_depth[0] = max(max_depth[0], depth)
            for edge in self._graph.get_outgoing(current):
                if edge.edge_type in (EdgeType.DEPENDS_ON, EdgeType.USES) and edge.target_id not in visited:
                    _dfs(edge.target_id, depth + 1)

        _dfs(node_id, 0)
        return max_depth[0]

    @staticmethod
    def _compute_rating(overall: float) -> str:
        if overall >= 90.0:
            return "excellent"
        if overall >= 70.0:
            return "good"
        if overall >= 50.0:
            return "fair"
        if overall >= 30.0:
            return "poor"
        return "critical"
