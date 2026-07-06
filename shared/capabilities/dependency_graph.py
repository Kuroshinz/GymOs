"""Dependency Graph — analyzes capability relationships.

Stateless functions operating on capability registry data.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from shared.capabilities.registry import CapabilityRegistry


@dataclass(frozen=True)
class DependencyEdge:
    """A directed dependency between two capabilities."""
    source_id: str
    target_id: str
    is_blocking: bool = False


@dataclass(frozen=True)
class DependencyGraphResult:
    """Complete dependency analysis."""
    edges: tuple[DependencyEdge, ...] = field(default_factory=tuple)
    levels: tuple[tuple[str, ...], ...] = field(default_factory=tuple)
    circular_dependencies: tuple[tuple[str, ...], ...] = field(default_factory=tuple)
    orphan_capabilities: tuple[str, ...] = field(default_factory=tuple)


def build_dependency_graph(registry: CapabilityRegistry) -> DependencyGraphResult:
    """Analyze all capabilities and their dependencies."""
    capabilities = {cap.capability_id: cap for cap in registry.list_all()}
    edges: list[DependencyEdge] = []
    all_ids = set(capabilities.keys())

    for cap in capabilities.values():
        for dep_id in cap.dependencies:
            is_blocking = dep_id in cap.blocked_by
            edges.append(DependencyEdge(
                source_id=cap.capability_id,
                target_id=dep_id,
                is_blocking=is_blocking,
            ))

    # Topological sort attempt (simple Kahn's algorithm)
    in_degree: dict[str, int] = {cid: 0 for cid in all_ids}
    adj: dict[str, list[str]] = {cid: [] for cid in all_ids}
    for edge in edges:
        if edge.target_id in adj and edge.source_id in adj:
            adj[edge.target_id].append(edge.source_id)
            in_degree[edge.source_id] = in_degree.get(edge.source_id, 0) + 1

    queue = [cid for cid, deg in in_degree.items() if deg == 0]
    levels: list[list[str]] = []
    visited: set[str] = set()

    while queue:
        current_level: list[str] = []
        for _ in range(len(queue)):
            node = queue.pop(0)
            if node in visited:
                continue
            visited.add(node)
            current_level.append(node)
            for neighbor in adj.get(node, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        if current_level:
            levels.append(tuple(current_level))

    circular: list[tuple[str, ...]] = []
    remaining = all_ids - visited
    if remaining:
        circular.append(tuple(remaining))

    orphans = tuple(
        cid for cid in all_ids
        if cid in capabilities
        and not capabilities[cid].dependencies
        and not any(cid == edge.target_id for edge in edges)
    )

    return DependencyGraphResult(
        edges=tuple(edges),
        levels=tuple(levels),
        circular_dependencies=tuple(circular),
        orphan_capabilities=orphans,
    )
