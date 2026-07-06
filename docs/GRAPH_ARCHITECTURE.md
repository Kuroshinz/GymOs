# Product Knowledge Graph — Architecture

## Overview

The Product Knowledge Graph (`shared/graph/`) is a typed, directed property graph
that provides a single canonical representation of GymOS architecture.

## Design Principles

### 1. Never Duplicate Data

The `GraphBuilder` reads from existing canonical sources:
- **Capability Platform** (`shared/capabilities/`) — capability registry, health, dependencies
- **Kernel** (`shared/kernel/`) — product identity, RFCs, releases, snapshots
- **Evolution Engine** (`shared/evolution/`) — milestones, versions, evolution chain

When these sources change, the graph reflects those changes on the next `build()` call.
There is no separate data entry.

### 2. Clean Architecture

```
shared/graph/          # Shared service layer
  ├── node.py          # Domain types (Node, NodeType, NodeMetadata)
  ├── edge.py          # Domain types (Edge, EdgeType)
  ├── graph.py         # Domain entity (KnowledgeGraph)
  ├── builder.py       # Application service (constructs graph)
  ├── query.py         # Application service (analysis queries)
  ├── impact.py        # Application service (blast radius)
  ├── health.py        # Application service (graph quality)
  ├── serializer.py    # Infrastructure (JSON/dict I/O)
  └── reports.py       # Presentation (Markdown reports)
```

- Domain types (`node.py`, `edge.py`, `graph.py`) import only stdlib + shared types
- Application services (`builder.py`, `query.py`, `impact.py`, `health.py`) import domain types
- Infrastructure (`serializer.py`) handles serialization
- Presentation (`reports.py`) generates Markdown output

### 3. Pure, Stateless Operations

All query, impact, and health operations are pure functions that read the graph
without modifying it. The graph is immutable once built.

### 4. Composable

The modules are designed to be used independently or together:
- `GraphBuilder.build()` → returns a `KnowledgeGraph`
- `GraphQuery(graph)` → analysis queries on that graph
- `ImpactAnalyzer(graph)` → impact analysis on that graph
- `GraphHealthAnalyzer(graph)` → health assessment on that graph
- Reports → Markdown strings

## Module Dependencies

```
builder.py
  → depends on: node.py, edge.py, graph.py
  → depends on: shared/capabilities/, shared/kernel/, shared/evolution/

query.py
  → depends on: node.py, edge.py, graph.py

impact.py
  → depends on: node.py, edge.py, graph.py, query.py

health.py
  → depends on: node.py, edge.py, graph.py, query.py

serializer.py
  → depends on: node.py, edge.py, graph.py

reports.py
  → depends on: all modules (used for report generation)
```

## Builder Architecture

The `GraphBuilder` constructs the graph in 10 phases:

1. **Vision nodes**: Product vision and 7 pillars
2. **Roadmap nodes**: 6 roadmap stages (v0.5 through v1.0)
3. **Capability nodes**: 12 registered capabilities with dependency edges
4. **RFC nodes**: All RFCs with evolution edges to capabilities
5. **Module nodes**: 5 modules with implements edges to capabilities
6. **Engine nodes**: 5 engines with implements edges to capabilities
7. **Feature nodes**: 11 features with owns edges to capabilities
8. **Version nodes**: 5 released versions
9. **Milestone nodes**: Milestones from Evolution Engine
10. **Document nodes**: Key documentation files
11. **Evolution chain**: RFC → Capability → Milestone → Version links

## Thread Safety

The graph is designed for single-threaded use (consistent with GymOS's async
event loop model). The `KnowledgeGraph` is mutable during construction but should
be treated as read-only after `build()` returns.

## Serialization

The graph supports full serialization/deserialization:

```python
from shared.graph import graph_to_json, graph_from_json

# Serialize
json_str = graph_to_json(graph)

# Write to file
with open("graph_backup.json", "w") as f:
    f.write(json_str)

# Deserialize
graph = graph_from_json(json_str)
```

## Subgraph Extraction

Extract a subgraph centered on a node for focused analysis:

```python
from shared.graph import extract_subgraph

# Get a 2-hop subgraph around Training Intelligence
sub = extract_subgraph(graph, "capability:training-intelligence", depth=2)
print(f"Subgraph: {sub.node_count} nodes, {sub.edge_count} edges")
```
