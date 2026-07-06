"""Product Knowledge Graph — GymOS Architecture Intelligence.

The Product Knowledge Graph is the canonical representation of GymOS architecture.
Every architectural element — vision, roadmap, RFC, capability, module, engine,
feature, version, milestone, document — is a node connected by typed relationships.

Usage:
    from shared.graph import build_graph, GraphQuery, ImpactAnalyzer

    graph = build_graph()
    query = GraphQuery(graph)
    deps = query.get_dependencies("capability:training-intelligence")
    bottlenecks = query.find_bottlenecks()
    impact = ImpactAnalyzer(graph).analyze("capability:training-intelligence")
    health = GraphHealthAnalyzer(graph).analyze()
"""

from shared.graph.builder import GraphBuilder, build_graph
from shared.graph.edge import Edge, EdgeType
from shared.graph.graph import KnowledgeGraph
from shared.graph.health import GraphHealthAnalyzer, GraphHealthScore
from shared.graph.impact import ImpactAnalyzer, ImpactResult
from shared.graph.node import Node, NodeMetadata, NodeType
from shared.graph.query import GraphQuery
from shared.graph.reports import (
    generate_architecture_report,
    generate_capability_report,
    generate_dependency_report,
    generate_health_report,
    generate_impact_report,
    generate_rfc_report,
)
from shared.graph.serializer import (
    edge_from_dict,
    edge_to_dict,
    extract_subgraph,
    graph_from_dict,
    graph_from_json,
    graph_to_dict,
    graph_to_json,
    node_from_dict,
    node_to_dict,
)

__all__ = (
    # Graph
    "KnowledgeGraph",
    "build_graph",
    "GraphBuilder",
    # Node
    "Node",
    "NodeMetadata",
    "NodeType",
    # Edge
    "Edge",
    "EdgeType",
    # Query
    "GraphQuery",
    # Impact
    "ImpactAnalyzer",
    "ImpactResult",
    # Health
    "GraphHealthAnalyzer",
    "GraphHealthScore",
    # Serializer
    "graph_to_dict",
    "graph_to_json",
    "graph_from_dict",
    "graph_from_json",
    "node_to_dict",
    "node_from_dict",
    "edge_to_dict",
    "edge_from_dict",
    "extract_subgraph",
    # Reports
    "generate_architecture_report",
    "generate_capability_report",
    "generate_rfc_report",
    "generate_impact_report",
    "generate_dependency_report",
    "generate_health_report",
)
