"""Graph Reports — generates reports from the Product Knowledge Graph.

Report types:
- Architecture Graph — full architectural overview
- Capability Graph — capability relationships
- RFC Graph — RFC evolution
- Impact Report — change impact analysis
- Dependency Report — dependency analysis
- Health Report — graph health
"""

from __future__ import annotations

from shared.graph.edge import EdgeType
from shared.graph.graph import KnowledgeGraph
from shared.graph.health import GraphHealthAnalyzer
from shared.graph.impact import ImpactAnalyzer
from shared.graph.node import NodeType
from shared.graph.query import GraphQuery


def generate_architecture_report(graph: KnowledgeGraph) -> str:
    """Generate a Markdown report of the full architecture graph."""
    query = GraphQuery(graph)
    lines: list[str] = []
    lines.append("# Architecture Graph Report")
    lines.append("")
    lines.append(f"**Total Nodes:** {graph.node_count} | **Total Edges:** {graph.edge_count}")
    lines.append("")

    # Nodes by type
    lines.append("## Nodes by Type")
    lines.append("")
    lines.append("| Node Type | Count |")
    lines.append("|-----------|-------|")
    for ntype in NodeType:
        count = len(graph.nodes_by_type(ntype))
        if count > 0:
            lines.append(f"| {ntype.name} | {count} |")
    lines.append("")

    # Edges by type
    lines.append("## Edges by Type")
    lines.append("")
    lines.append("| Edge Type | Count |")
    lines.append("|-----------|-------|")
    for etype in EdgeType:
        count = len(graph.edges_by_type(etype))
        if count > 0:
            lines.append(f"| {etype.name} | {count} |")
    lines.append("")

    # All capabilities
    lines.append("## Capabilities")
    lines.append("")
    for cap in graph.nodes_by_type(NodeType.CAPABILITY):
        deps = query.get_dependencies(cap.node_id)
        dependents = query.get_dependents(cap.node_id)
        lines.append(f"### {cap.name}")
        lines.append(f"- **ID:** `{cap.node_id}`")
        lines.append(f"- **Status:** {cap.metadata.status}")
        lines.append(f"- **Health:** {cap.metadata.health_score}/100")
        lines.append(f"- **Dependencies:** {len(deps)}")
        for d in deps:
            lines.append(f"  - {d.name} (`{d.node_id}`)")
        lines.append(f"- **Dependents:** {len(dependents)}")
        for d in dependents:
            lines.append(f"  - {d.name} (`{d.node_id}`)")
        lines.append("")

    # All versions
    lines.append("## Versions")
    lines.append("")
    lines.append("| Version | Description | Status |")
    lines.append("|---------|-------------|--------|")
    for version in graph.nodes_by_type(NodeType.VERSION):
        lines.append(f"| {version.name} | {version.metadata.description} | {version.metadata.status} |")
    lines.append("")

    return "\n".join(lines)


def generate_capability_report(graph: KnowledgeGraph) -> str:
    """Generate a Markdown report focused on capabilities and their relationships."""
    query = GraphQuery(graph)
    lines: list[str] = []
    lines.append("# Capability Graph Report")
    lines.append("")

    for cap in sorted(graph.nodes_by_type(NodeType.CAPABILITY), key=lambda n: n.metadata.health_score):
        deps = query.get_dependencies(cap.node_id)
        dependents = query.get_dependents(cap.node_id)
        trans_deps = query.get_transitive_dependencies(cap.node_id)
        edges = graph.get_outgoing(cap.node_id)

        lines.append(f"## {cap.name} (`{cap.node_id}`)")
        lines.append(f"- **Health:** {cap.metadata.health_score}/100")
        lines.append(f"- **Risk:** {cap.metadata.risk_score}/100")
        lines.append(f"- **Status:** {cap.metadata.status}")
        lines.append(f"- **Introduced:** v{cap.metadata.version_introduced}")
        lines.append("")

        if deps:
            lines.append(f"**Dependencies ({len(deps)}):**")
            for d in deps:
                lines.append(f"- {d.name}")
            lines.append("")

        if trans_deps:
            lines.append(f"**Transitive Dependencies ({len(trans_deps)}):**")
            for d in sorted(trans_deps, key=lambda n: n.name):
                if d.node_id != cap.node_id:
                    lines.append(f"- {d.name}")
            lines.append("")

        if dependents:
            lines.append(f"**Dependents ({len(dependents)}):**")
            for d in dependents:
                lines.append(f"- {d.name}")
            lines.append("")

        # Features and modules
        impl_by = [e for e in edges if e.edge_type in (EdgeType.IMPLEMENTS, EdgeType.OWNS)]
        if impl_by:
            lines.append("**Implemented/Owned By:**")
            for e in impl_by:
                target = graph.get_node(e.target_id)
                if target:
                    lines.append(f"- {target.name}")
            lines.append("")

    return "\n".join(lines)


def generate_rfc_report(graph: KnowledgeGraph) -> str:
    """Generate a Markdown report of RFCs and their evolution."""
    lines: list[str] = []
    lines.append("# RFC Graph Report")
    lines.append("")

    rfcs = graph.nodes_by_type(NodeType.RFC)
    if not rfcs:
        lines.append("No RFC nodes found in the graph.")
        return "\n".join(lines)

    lines.append(f"**Total RFCs:** {len(rfcs)}")
    lines.append("")

    for rfc in sorted(rfcs, key=lambda n: n.name):
        lines.append(f"## {rfc.name}")
        lines.append(f"- **Description:** {rfc.metadata.description}")
        lines.append(f"- **Status:** {rfc.metadata.status}")
        lines.append("")

        # Find what this RFC evolves into
        outgoing = graph.get_outgoing(rfc.node_id)
        evolves = [e for e in outgoing if e.edge_type == EdgeType.EVOLVES_TO]
        if evolves:
            lines.append("**Evolves into:**")
            for e in evolves:
                target = graph.get_node(e.target_id)
                if target:
                    lines.append(f"- {target.name} (`{target.node_id}`)")
            lines.append("")

    return "\n".join(lines)


def generate_impact_report(graph: KnowledgeGraph, target_node_id: str | None = None) -> str:
    """Generate a change impact report for one or all nodes."""
    analyzer = ImpactAnalyzer(graph)
    lines: list[str] = []
    lines.append("# Impact Report")
    lines.append("")

    if target_node_id:
        result = analyzer.analyze(target_node_id)
        lines.append(result.breakage_analysis)
        lines.append("")
        lines.append(f"**Risk Score:** {result.risk_score}/100")
        lines.append(f"**Dependency Depth:** {result.dependency_depth}")
        lines.append(f"**Total Affected Nodes:** {result.total_affected_nodes}")
    else:
        # Report on all capability nodes
        lines.append("## All Capabilities Impact Summary")
        lines.append("")
        lines.append("| Capability | Risk | Affected Nodes | Depth |")
        lines.append("|------------|------|----------------|-------|")
        for cap in graph.nodes_by_type(NodeType.CAPABILITY):
            result = analyzer.analyze(cap.node_id)
            lines.append(f"| {cap.name} | {result.risk_score} | {result.total_affected_nodes} | {result.dependency_depth} |")
        lines.append("")

    return "\n".join(lines)


def generate_dependency_report(graph: KnowledgeGraph) -> str:
    """Generate a detailed dependency analysis report."""
    query = GraphQuery(graph)
    lines: list[str] = []
    lines.append("# Dependency Report")
    lines.append("")

    # Bottlenecks
    bottlenecks = query.find_bottlenecks(min_dependents=1)
    if bottlenecks:
        lines.append("## Top Bottlenecks (Most Dependents)")
        lines.append("")
        lines.append("| Node | Type | Dependents |")
        lines.append("|------|------|------------|")
        for node, count in bottlenecks[:10]:
            lines.append(f"| {node.name} | {node.node_type.name} | {count} |")
        lines.append("")

    # Critical path
    critical_path = query.find_critical_path()
    if critical_path:
        lines.append("## Critical Dependency Path")
        lines.append("")
        lines.append("The longest dependency chain in the graph:")
        lines.append("")
        for i, nid in enumerate(critical_path):
            node = graph.get_node(nid)
            name = node.name if node else nid
            arrow = " → " if i < len(critical_path) - 1 else ""
            lines.append(f"- **{name}**{arrow}")
        lines.append("")

    # Cycles
    cycles = query.find_cycles()
    if cycles:
        lines.append(f"## Dependency Cycles ({len(cycles)} found)")
        lines.append("")
        for cycle in cycles:
            cycle_names = []
            for nid in cycle:
                node = graph.get_node(nid)
                cycle_names.append(node.name if node else nid)
            lines.append(f"- {' → '.join(cycle_names)}")
        lines.append("")

    # Roots and leaves
    roots = query.find_roots()
    leaves = query.find_leaves()
    lines.append(f"## Roots (No Dependencies): {len(roots)}")
    lines.append(f"## Leaves (No Dependents): {len(leaves)}")
    lines.append("")

    # All dependency edges
    dep_edges = query.get_all_dependency_edges()
    if dep_edges:
        lines.append(f"## All Dependency Edges ({len(dep_edges)})")
        lines.append("")
        lines.append("| Source | → | Target | Type |")
        lines.append("|--------|---|--------|------|")
        for edge in sorted(dep_edges, key=lambda e: (e.source_id, e.target_id)):
            lines.append(f"| {edge.source_id} | → | {edge.target_id} | {edge.edge_type.name} |")
        lines.append("")

    return "\n".join(lines)


def generate_health_report(graph: KnowledgeGraph) -> str:
    """Generate a health report for the Quality Graph itself."""
    analyzer = GraphHealthAnalyzer(graph)
    score = analyzer.analyze()

    lines: list[str] = []
    lines.append("# Product Knowledge Graph — Health Report")
    lines.append("")
    lines.append(f"**Rating:** {score.rating.upper()}")
    lines.append(f"**Overall:** {score.overall}/100")
    lines.append("")

    # Dimensions
    lines.append("## Health Dimensions")
    lines.append("")
    lines.append("| Dimension | Score | Description |")
    lines.append("|-----------|-------|-------------|")
    lines.append(f"| Completeness | {score.completeness}/100 | % of expected node types present |")
    lines.append(f"| Connectivity | {score.connectivity}/100 | % of nodes with edges |")
    lines.append(f"| Cycle Health | {score.cycle_health}/100 | 100 = no cycles |")
    lines.append(f"| Orphan Health | {score.orphan_health}/100 | 100 = no orphans |")
    lines.append(f"| Depth Health | {score.depth_health}/100 | Reasonable dependency depth |")
    lines.append("")

    # Stats
    lines.append("## Statistics")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Total Nodes | {score.node_count} |")
    lines.append(f"| Total Edges | {score.edge_count} |")
    lines.append(f"| Avg Edges/Node | {score.avg_edges_per_node} |")
    lines.append(f"| Cycles | {score.cycle_count} |")
    lines.append(f"| Orphans | {score.orphan_count} |")
    lines.append(f"| Max Depth | {score.max_depth} |")
    lines.append("")

    # Recommendations
    lines.append("## Recommendations")
    lines.append("")
    if score.cycle_count > 0:
        lines.append(f"- ⚠️  Resolve {score.cycle_count} dependency cycle(s)")
    if score.orphan_count > 0:
        lines.append(f"- ⚠️  Connect {score.orphan_count} orphan node(s)")
    if score.completeness < 80:
        lines.append("- ⚠️  Add missing node types to improve completeness")
    if score.connectivity < 80:
        lines.append("- ⚠️  Add edges to improve connectivity score")
    lines.append("")

    return "\n".join(lines)
