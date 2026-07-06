"""Graph Serializer — serializes the Product Knowledge Graph to/from dict and JSON.

Supports:
- Full graph serialization (nodes + edges)
- Partial serialization (subgraph, node list)
- Deserialization
"""

from __future__ import annotations

import json
from typing import Any

from shared.graph.edge import EDGE_TYPE_MAP, Edge, EdgeType
from shared.graph.graph import KnowledgeGraph
from shared.graph.node import NODE_TYPE_MAP, Node, NodeMetadata, NodeType


def graph_to_dict(graph: KnowledgeGraph) -> dict[str, Any]:
    """Serialize the complete Knowledge Graph to a dictionary."""
    return {
        "node_count": graph.node_count,
        "edge_count": graph.edge_count,
        "nodes": [node_to_dict(node) for node in graph.nodes()],
        "edges": [edge_to_dict(edge) for edge in graph.edges()],
    }


def graph_to_json(graph: KnowledgeGraph, indent: int = 2) -> str:
    """Serialize the complete Knowledge Graph to a JSON string."""
    return json.dumps(graph_to_dict(graph), indent=indent)


def graph_from_dict(data: dict[str, Any]) -> KnowledgeGraph:
    """Deserialize a Knowledge Graph from a dictionary."""
    graph = KnowledgeGraph()
    for node_data in data.get("nodes", []):
        graph.add_node(node_from_dict(node_data))
    for edge_data in data.get("edges", []):
        graph.add_edge(edge_from_dict(edge_data))
    return graph


def graph_from_json(json_str: str) -> KnowledgeGraph:
    """Deserialize a Knowledge Graph from a JSON string."""
    return graph_from_dict(json.loads(json_str))


# ── Node serialization ───────────────────────────────────────────────────

def node_to_dict(node: Node) -> dict[str, Any]:
    """Serialize a single Node to a dictionary."""
    return {
        "node_id": node.node_id,
        "node_type": node.node_type.name.lower(),
        "name": node.name,
        "metadata": {
            "version_introduced": node.metadata.version_introduced,
            "version_deprecated": node.metadata.version_deprecated,
            "status": node.metadata.status,
            "health_score": node.metadata.health_score,
            "risk_score": node.metadata.risk_score,
            "tags": list(node.metadata.tags),
            "source": node.metadata.source,
            "description": node.metadata.description,
            "url": node.metadata.url,
        },
    }


def node_from_dict(data: dict[str, Any]) -> Node:
    """Deserialize a Node from a dictionary."""
    node_type_name = data.get("node_type", "feature").upper()
    node_type = NODE_TYPE_MAP.get(node_type_name.lower(), NodeType.FEATURE)
    meta = data.get("metadata", {})
    metadata = NodeMetadata(
        version_introduced=meta.get("version_introduced", ""),
        version_deprecated=meta.get("version_deprecated", ""),
        status=meta.get("status", ""),
        health_score=meta.get("health_score", 0.0),
        risk_score=meta.get("risk_score", 0.0),
        tags=tuple(meta.get("tags", [])),
        source=meta.get("source", ""),
        description=meta.get("description", ""),
        url=meta.get("url", ""),
    )
    return Node(
        node_id=data.get("node_id", ""),
        node_type=node_type,
        name=data.get("name", ""),
        metadata=metadata,
    )


# ── Edge serialization ───────────────────────────────────────────────────

def edge_to_dict(edge: Edge) -> dict[str, Any]:
    """Serialize a single Edge to a dictionary."""
    return {
        "source_id": edge.source_id,
        "target_id": edge.target_id,
        "edge_type": edge.edge_type.name.lower(),
        "weight": edge.weight,
        "metadata": edge.metadata,
    }


def edge_from_dict(data: dict[str, Any]) -> Edge:
    """Deserialize an Edge from a dictionary."""
    edge_type_name = data.get("edge_type", "depends_on").upper()
    edge_type = EDGE_TYPE_MAP.get(edge_type_name.lower(), EdgeType.DEPENDS_ON)
    return Edge(
        source_id=data.get("source_id", ""),
        target_id=data.get("target_id", ""),
        edge_type=edge_type,
        weight=data.get("weight", 1.0),
        metadata=data.get("metadata", ""),
    )


# ── Subgraph extraction ───────────────────────────────────────────────────

def extract_subgraph(graph: KnowledgeGraph, center_node_id: str, depth: int = 1) -> KnowledgeGraph:
    """Extract a subgraph centered on a node, up to 'depth' hops away.

    Useful for visualizing the immediate neighborhood of a node.
    """
    subgraph = KnowledgeGraph()
    center = graph.get_node(center_node_id)
    if center is None:
        return subgraph

    subgraph.add_node(center)

    # BFS to find nodes within depth
    visited: set[str] = {center_node_id}
    current_ring: set[str] = {center_node_id}

    for _ in range(depth):
        next_ring: set[str] = set()
        for nid in current_ring:
            for edge in graph.get_outgoing(nid):
                if edge.target_id not in visited:
                    visited.add(edge.target_id)
                    next_ring.add(edge.target_id)
                    target_node = graph.get_node(edge.target_id)
                    if target_node:
                        subgraph.add_node(target_node)
                    subgraph.add_edge(edge)
            for edge in graph.get_incoming(nid):
                if edge.source_id not in visited:
                    visited.add(edge.source_id)
                    next_ring.add(edge.source_id)
                    source_node = graph.get_node(edge.source_id)
                    if source_node:
                        subgraph.add_node(source_node)
                    subgraph.add_edge(edge)
        current_ring = next_ring

    return subgraph
