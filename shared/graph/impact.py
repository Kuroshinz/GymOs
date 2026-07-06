"""Impact Analyzer — calculates the blast radius of any node.

Given any node in the Product Knowledge Graph, returns:
- Affected capabilities
- Affected RFCs
- Affected modules
- Affected engines
- Risk score (0-100)
- Dependency depth (how deep the transitive dependencies go)
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from shared.graph.edge import EdgeType
from shared.graph.graph import KnowledgeGraph
from shared.graph.node import Node, NodeType
from shared.graph.query import GraphQuery


@dataclass(frozen=True)
class ImpactResult:
    """The result of an impact analysis for a single node."""

    target_node_id: str
    target_node_name: str
    target_node_type: str
    affected_capabilities: tuple[str, ...] = field(default_factory=tuple)
    affected_rfcs: tuple[str, ...] = field(default_factory=tuple)
    affected_modules: tuple[str, ...] = field(default_factory=tuple)
    affected_engines: tuple[str, ...] = field(default_factory=tuple)
    total_affected_nodes: int = 0
    risk_score: float = 0.0  # 0-100
    dependency_depth: int = 0  # max transitive depth
    breakage_analysis: str = ""


class ImpactAnalyzer:
    """Analyzes the impact of removing any node from the graph.

    Impact = all nodes that would be affected if this node disappeared.
    This includes direct dependents and transitive dependents.
    """

    def __init__(self, graph: KnowledgeGraph) -> None:
        self._graph = graph
        self._query = GraphQuery(graph)

    def analyze(self, node_id: str) -> ImpactResult:
        """Analyze the full impact of removing a node.

        The analysis covers:
        - All direct and transitive dependents
        - Which capabilities, RFCs, modules, and engines are affected
        - A risk score based on how many dependents exist
        - The maximum depth of the dependency chain
        """
        node = self._graph.get_node(node_id)
        if node is None:
            return ImpactResult(
                target_node_id=node_id,
                target_node_name="Unknown",
                target_node_type="unknown",
                breakage_analysis=f"Node '{node_id}' not found in the graph.",
            )

        # Find all transitively affected nodes (BFS)
        affected = self._find_affected_nodes(node_id)
        affected.discard(node_id)

        # Categorize affected nodes
        capabilities: list[str] = []
        rfcs: list[str] = []
        modules: list[str] = []
        engines: list[str] = []

        for nid in affected:
            n = self._graph.get_node(nid)
            if n is None:
                continue
            if n.node_type == NodeType.CAPABILITY:
                capabilities.append(n.name)
            elif n.node_type == NodeType.RFC:
                rfcs.append(n.name)
            elif n.node_type == NodeType.MODULE:
                modules.append(n.name)
            elif n.node_type == NodeType.ENGINE:
                engines.append(n.name)

        # Calculate risk score
        risk_score = self._calculate_risk_score(node, affected)

        # Dependency depth
        depth = self._max_depth(node_id)

        # Generate analysis text
        breakage = self._generate_breakage_analysis(node, capabilities, rfcs, modules, engines)

        return ImpactResult(
            target_node_id=node_id,
            target_node_name=node.name,
            target_node_type=node.node_type.name,
            affected_capabilities=tuple(sorted(set(capabilities))),
            affected_rfcs=tuple(sorted(set(rfcs))),
            affected_modules=tuple(sorted(set(modules))),
            affected_engines=tuple(sorted(set(engines))),
            total_affected_nodes=len(affected),
            risk_score=risk_score,
            dependency_depth=depth,
            breakage_analysis=breakage,
        )

    def _find_affected_nodes(self, node_id: str) -> set[str]:
        """BFS to find all nodes transitively affected by removing this node.

        Affected nodes are those that depend on this node (directly or transitively).
        Edge(A, B, DEPENDS_ON) means A depends on B.
        So if B is removed, A is affected.
        We follow INCOMING edges: sources of incoming edges = things that depend on us.
        """
        affected: set[str] = set()
        visited: set[str] = set()
        queue: deque[str] = deque()
        queue.append(node_id)
        visited.add(node_id)

        while queue:
            current = queue.popleft()
            affected.add(current)

            # Nodes that depend on the current node (incoming = sources that depend on us)
            for edge in self._graph.get_incoming(current):
                if edge.edge_type in (EdgeType.DEPENDS_ON, EdgeType.USES):
                    source = edge.source_id
                    if source not in visited:
                        visited.add(source)
                        queue.append(source)

            # Also check: if this node implements something, what depends on that?
            for edge in self._graph.get_outgoing(current):
                if edge.edge_type == EdgeType.IMPLEMENTS:
                    # The capability this implements — find what depends on that capability
                    cap_id = edge.target_id
                    if cap_id not in visited:
                        visited.add(cap_id)
                        queue.append(cap_id)

        # Also add nodes that have this node as a dependency
        affected.update(self._find_nodes_depending_on(node_id))

        return affected

    def _find_nodes_depending_on(self, node_id: str) -> set[str]:
        """Find all nodes that directly or transitively depend on this node.

        A depends on B means edge A -> B with DEPENDS_ON or USES type.
        We need to follow the REVERSE direction: find all A where A -> node_id.
        """
        depending: set[str] = set()
        visited: set[str] = set()
        queue: deque[str] = deque()

        # Start with direct dependents
        for edge in self._graph.get_incoming(node_id):
            if edge.edge_type in (EdgeType.DEPENDS_ON, EdgeType.USES):
                source = edge.source_id
                if source not in visited:
                    visited.add(source)
                    queue.append(source)
                    depending.add(source)

        # BFS for transitive dependents
        while queue:
            current = queue.popleft()
            for edge in self._graph.get_incoming(current):
                if edge.edge_type in (EdgeType.DEPENDS_ON, EdgeType.USES):
                    source = edge.source_id
                    if source not in visited:
                        visited.add(source)
                        queue.append(source)
                        depending.add(source)

        return depending

    def _calculate_risk_score(self, node: Node, affected: set[str]) -> float:
        """Calculate risk score (0-100) based on impact.

        Factors:
        - Number of total affected nodes (40%)
        - Number of affected capabilities (30%)
        - Whether RFCs are affected (20%)
        - Node's own risk score from metadata (10%)
        """
        affected.discard(node.node_id)
        if not affected:
            return 0.0

        n_caps = sum(
            1 for nid in affected
            if (n := self._graph.get_node(nid)) and n.node_type == NodeType.CAPABILITY
        )
        n_rfcs = sum(
            1 for nid in affected
            if (n := self._graph.get_node(nid)) and n.node_type == NodeType.RFC
        )

        # Normalize to 0-100
        size_score = min(len(affected) * 8.0, 40.0)
        cap_score = min(n_caps * 10.0, 30.0)
        rfc_score = 20.0 if n_rfcs > 0 else 0.0
        meta_score = node.metadata.risk_score * 0.1

        return round(min(size_score + cap_score + rfc_score + meta_score, 100.0), 1)

    def _max_depth(self, node_id: str) -> int:
        """Calculate the maximum dependent chain depth from this node.

        This measures how deep the transitive dependents go.
        Follows incoming edges (sources = things that depend on current node).
        """
        max_depth = 0
        visited: set[str] = set()

        def _dfs(current: str, depth: int) -> None:
            nonlocal max_depth
            visited.add(current)
            max_depth = max(max_depth, depth)
            for edge in self._graph.get_incoming(current):
                if edge.edge_type in (EdgeType.DEPENDS_ON, EdgeType.USES):
                    source = edge.source_id
                    if source not in visited:
                        _dfs(source, depth + 1)

        _dfs(node_id, 0)
        return max_depth

    def _generate_breakage_analysis(
        self,
        node: Node,
        capabilities: list[str],
        rfcs: list[str],
        modules: list[str],
        engines: list[str],
    ) -> str:
        """Generate a human-readable breakage analysis."""
        parts: list[str] = []
        parts.append(f"## Impact Analysis: {node.name}")
        parts.append("")

        if not capabilities and not rfcs and not modules and not engines:
            parts.append("**No breakage.** This node has no dependents.")
            return "\n".join(parts)

        parts.append(f"Removing **{node.name}** would break or affect:")

        if capabilities:
            parts.append(f"\n### Capabilities ({len(capabilities)})")
            for cap in capabilities:
                parts.append(f"- {cap}")

        if rfcs:
            parts.append(f"\n### RFCs ({len(rfcs)})")
            for rfc in rfcs:
                parts.append(f"- {rfc}")

        if modules:
            parts.append(f"\n### Modules ({len(modules)})")
            for mod in modules:
                parts.append(f"- {mod}")

        if engines:
            parts.append(f"\n### Engines ({len(engines)})")
            for eng in engines:
                parts.append(f"- {eng}")

        return "\n".join(parts)
