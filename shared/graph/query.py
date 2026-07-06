"""Product Knowledge Graph — Query API.

Supports all graph analysis queries:
- get_dependencies / get_dependents
- find_path (shortest path between nodes)
- find_roots / find_leaves (topological)
- find_cycles
- find_orphans
- find_bottlenecks
"""

from __future__ import annotations

from collections import deque

from shared.graph.edge import Edge, EdgeType
from shared.graph.graph import KnowledgeGraph
from shared.graph.node import Node


class GraphQuery:
    """Query engine for the Product Knowledge Graph.

    Provides all analysis queries required by RFC-018.7.
    All methods are pure — they read the graph without modifying it.
    """

    def __init__(self, graph: KnowledgeGraph) -> None:
        self._graph = graph

    # ── Dependency Queries ───────────────────────────────────────────────────

    def get_dependencies(self, node_id: str) -> list[Node]:
        """Nodes that this node depends on.

        Edge(A, B, DEPENDS_ON) means A depends on B.
        So dependencies of A = targets of outgoing edges from A.
        """
        dep_ids: set[str] = set()
        for edge in self._graph.get_outgoing(node_id):
            if edge.edge_type in (EdgeType.DEPENDS_ON, EdgeType.USES):
                dep_ids.add(edge.target_id)
        return [n for n in self._get_nodes(dep_ids) if n is not None]

    def get_dependents(self, node_id: str) -> list[Node]:
        """Nodes that depend on this node.

        Edge(A, B, DEPENDS_ON) means A depends on B.
        So dependents of B = sources of incoming edges to B.
        """
        dep_ids: set[str] = set()
        for edge in self._graph.get_incoming(node_id):
            if edge.edge_type in (EdgeType.DEPENDS_ON, EdgeType.USES):
                dep_ids.add(edge.source_id)
        return [n for n in self._get_nodes(dep_ids) if n is not None]

    def get_transitive_dependencies(self, node_id: str) -> list[Node]:
        """All transitive dependencies (BFS traversal following outgoing DEPENDS_ON edges)."""
        visited: set[str] = set()
        queue: deque[str] = deque()
        queue.append(node_id)
        visited.add(node_id)

        while queue:
            current = queue.popleft()
            for edge in self._graph.get_outgoing(current):
                if edge.edge_type in (EdgeType.DEPENDS_ON, EdgeType.USES):
                    target = edge.target_id
                    if target not in visited:
                        visited.add(target)
                        queue.append(target)

        visited.discard(node_id)
        return [n for n in self._get_nodes(visited) if n is not None]

    def get_all_dependency_edges(self) -> list[Edge]:
        """Return all DEPENDS_ON and USES edges in the graph."""
        return [
            edge for edge in self._graph.edges()
            if edge.edge_type in (EdgeType.DEPENDS_ON, EdgeType.USES)
        ]

    # ── Path Queries ─────────────────────────────────────────────────────────

    def find_path(self, source_id: str, target_id: str) -> list[str] | None:
        """Find the shortest directed path from source to target using BFS.

        Returns a list of node IDs forming the path, or None if no path exists.
        """
        if source_id == target_id:
            return [source_id]

        visited: set[str] = {source_id}
        queue: deque[list[str]] = deque()
        queue.append([source_id])

        while queue:
            path = queue.popleft()
            current = path[-1]

            for edge in self._graph.get_outgoing(current):
                neighbor = edge.target_id
                if neighbor == target_id:
                    return path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])

        return None

    def find_all_paths(self, source_id: str, target_id: str, max_depth: int = 6) -> list[list[str]]:
        """Find all directed paths from source to target, up to max_depth."""
        paths: list[list[str]] = []

        def _dfs(current: str, target: str, visited: set[str], path: list[str]) -> None:
            if len(path) > max_depth:
                return
            if current == target:
                paths.append(list(path))
                return
            for edge in self._graph.get_outgoing(current):
                neighbor = edge.target_id
                if neighbor not in visited:
                    visited.add(neighbor)
                    path.append(neighbor)
                    _dfs(neighbor, target, visited, path)
                    path.pop()
                    visited.discard(neighbor)

        _dfs(source_id, target_id, {source_id}, [source_id])
        return paths

    # ── Topological Queries ──────────────────────────────────────────────────

    def find_roots(self) -> list[Node]:
        """Nodes with no incoming DEPENDS_ON or USES edges.

        These are the foundational nodes that nothing depends on.
        """
        all_dep_targets: set[str] = set()
        for edge in self._graph.edges():
            if edge.edge_type in (EdgeType.DEPENDS_ON, EdgeType.USES):
                all_dep_targets.add(edge.target_id)

        roots: list[Node] = []
        for node in self._graph.nodes():
            if node.node_id not in all_dep_targets:
                roots.append(node)
        return roots

    def find_leaves(self) -> list[Node]:
        """Nodes with no outgoing DEPENDS_ON or USES edges.

        These are the leaf nodes that nothing depends on them.
        """
        all_dep_sources: set[str] = set()
        for edge in self._graph.edges():
            if edge.edge_type in (EdgeType.DEPENDS_ON, EdgeType.USES):
                all_dep_sources.add(edge.source_id)

        leaves: list[Node] = []
        for node in self._graph.nodes():
            if node.node_id not in all_dep_sources:
                leaves.append(node)
        return leaves

    # ── Cycle Detection ──────────────────────────────────────────────────────

    def find_cycles(self) -> list[list[str]]:
        """Detect all cycles in the dependency graph using DFS.

        Returns a list of cycles, where each cycle is a list of node IDs.
        """
        dep_graph: dict[str, list[str]] = {}
        for edge in self._graph.edges():
            if edge.edge_type in (EdgeType.DEPENDS_ON, EdgeType.USES):
                if edge.source_id not in dep_graph:
                    dep_graph[edge.source_id] = []
                dep_graph[edge.source_id].append(edge.target_id)

        cycles: list[list[str]] = []
        visited: set[str] = set()
        rec_stack: set[str] = set()

        def _dfs(node_id: str, path: list[str]) -> None:
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)

            for neighbor in dep_graph.get(node_id, []):
                if neighbor not in visited:
                    _dfs(neighbor, path)
                elif neighbor in rec_stack:
                    # Found a cycle — extract it
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    # Avoid duplicate cycles by checking if the same cycle was already found
                    if not any(self._same_cycle(cycle, c) for c in cycles):
                        cycles.append(cycle)

            path.pop()
            rec_stack.discard(node_id)

        for node_id in dep_graph:
            if node_id not in visited:
                _dfs(node_id, [])

        return cycles

    # ── Orphan Detection ─────────────────────────────────────────────────────

    def find_orphans(self) -> list[Node]:
        """Nodes with no edges at all — isolated from the graph.

        These are nodes that have no incoming or outgoing edges.
        """
        connected: set[str] = set()
        for edge in self._graph.edges():
            connected.add(edge.source_id)
            connected.add(edge.target_id)

        return [
            node for node in self._graph.nodes()
            if node.node_id not in connected
        ]

    # ── Bottleneck Detection ─────────────────────────────────────────────────

    def find_bottlenecks(self, min_dependents: int = 3) -> list[tuple[Node, int]]:
        """Nodes with the highest number of direct dependents.

        Bottlenecks are nodes where many other nodes depend on them.
        A high dependent count means this node is critical — if it breaks,
        many capabilities/modules are affected.

        Returns sorted list of (node, dependent_count), highest first.
        """
        counts: dict[str, int] = {}
        for edge in self._graph.edges():
            if edge.edge_type in (EdgeType.DEPENDS_ON, EdgeType.USES):
                target = edge.target_id
                counts[target] = counts.get(target, 0) + 1

        bottlenecks = sorted(
            [(self._graph.get_node(nid), count) for nid, count in counts.items()],
            key=lambda x: x[1],
            reverse=True,
        )
        return [(n, c) for n, c in bottlenecks if n is not None and c >= min_dependents]

    def find_critical_path(self) -> list[str]:
        """Find the longest dependency chain in the graph.

        This represents the most complex dependency path, where a break
        at any node would affect the most downstream nodes.
        """
        dep_graph: dict[str, list[str]] = {}
        all_nodes: set[str] = set()
        for edge in self._graph.edges():
            if edge.edge_type in (EdgeType.DEPENDS_ON, EdgeType.USES):
                if edge.source_id not in dep_graph:
                    dep_graph[edge.source_id] = []
                dep_graph[edge.source_id].append(edge.target_id)
                all_nodes.add(edge.source_id)
                all_nodes.add(edge.target_id)

        # Find root nodes (no incoming edges)
        all_targets: set[str] = set()
        for targets in dep_graph.values():
            all_targets.update(targets)
        roots = all_nodes - all_targets

        def _longest_path_from(node_id: str, memo: dict[str, list[str]]) -> list[str]:
            if node_id in memo:
                return memo[node_id]
            if node_id not in dep_graph or not dep_graph[node_id]:
                memo[node_id] = [node_id]
                return [node_id]
            longest: list[str] = []
            for neighbor in dep_graph[node_id]:
                path = _longest_path_from(neighbor, memo)
                if len(path) > len(longest):
                    longest = path
            result = [node_id] + longest
            memo[node_id] = result
            return result

        memo: dict[str, list[str]] = {}
        longest_path: list[str] = []
        for root in roots:
            path = _longest_path_from(root, memo)
            if len(path) > len(longest_path):
                longest_path = path
        return longest_path

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _get_nodes(self, node_ids: set[str]) -> list[Node | None]:
        return [self._graph.get_node(nid) for nid in node_ids]

    @staticmethod
    def _same_cycle(a: list[str], b: list[str]) -> bool:
        """Check if two cycles are the same, regardless of starting point."""
        if len(a) != len(b):
            return False
        # Try all rotations of b to match a
        doubled = b + b
        return any(
            all(a[i] == doubled[start + i] for i in range(len(a)))
            for start in range(len(b))
        )
