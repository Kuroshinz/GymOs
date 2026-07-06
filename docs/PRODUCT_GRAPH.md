# Product Knowledge Graph

The Product Knowledge Graph is the canonical representation of GymOS architecture.
Every architectural element is a node connected by typed relationships.

## Purpose

The graph exists to answer architectural questions:

- **Which capabilities depend on Recovery?** → `get_dependents("capability:recovery-intelligence")`
- **Which RFC created this capability?** → `get_incoming("capability:training-intelligence")` with EVOLVES_TO edges
- **Which version introduced this engine?** → Node metadata `version_introduced`
- **Which modules consume this knowledge?** → `get_dependents("capability:knowledge-platform")`
- **What breaks if this node disappears?** → `ImpactAnalyzer.analyze(node_id)`
- **Which capability is the biggest bottleneck?** → `find_bottlenecks()`

## Node Types

| Type | Prefix | Description | Example |
|------|--------|-------------|---------|
| Vision | `vision:` | Product vision, goals, philosophy | `vision:gymos` |
| Roadmap | `roadmap:` | Version roadmap stages | `roadmap:v0.5` |
| RFC | `rfc:` | RFC documents | `rfc:RFC-018` |
| Capability | `capability:` | Registered capabilities | `capability:training-intelligence` |
| Module | `module:` | Python code modules | `module:workout` |
| Engine | `engine:` | Engine services | `engine:event-bus` |
| Feature | `feature:` | Specific features | `feature:pr-detection` |
| Version | `version:` | Product versions | `version:0.5.0` |
| Milestone | `milestone:` | Milestones | `milestone:platform-maturity` |
| Document | `document:` | Documentation | `document:product-strategy` |

## Edge Types

| Type | Meaning | Usage |
|------|---------|-------|
| `depends_on` | A depends on B | Capability → Capability |
| `implements` | A implements B | Module → Capability, Engine → Capability |
| `owns` | A owns B | Feature → Capability (inverse: belongs_to) |
| `contains` | A contains B | Capability → Milestone |
| `evolves_to` | A evolves into B | RFC → Capability, Milestone → Version |
| `documents` | A documents B | Document → Node |
| `uses` | A uses B (weaker than depends_on) | Module → Module |
| `publishes` | A publishes events to B | Module → Module |
| `subscribes` | A subscribes to events from B | Module → Module |
| `belongs_to` | A belongs to B | General containment |

## Data Sources

The graph is constructed automatically from three canonical sources:

1. **Capability Platform** (`shared/capabilities/`) — 12 registered capabilities with health, dependencies, and metadata
2. **Kernel** (`shared/kernel/`) — product identity, RFCs, releases, snapshots
3. **Evolution Engine** (`shared/evolution/`) — RFCs, milestones, versions, forecasts, evolution chain

The builder never duplicates data — it reads directly from these sources at build time.

## Architecture

```
shared/graph/
├── __init__.py     # Public API
├── graph.py        # KnowledgeGraph data structure (nodes + edges)
├── node.py         # Node, NodeMetadata, NodeType
├── edge.py         # Edge, EdgeType
├── builder.py      # GraphBuilder — constructs from canonical sources
├── query.py        # GraphQuery — all analysis queries
├── impact.py       # ImpactAnalyzer — blast radius analysis
├── health.py       # GraphHealthAnalyzer — graph quality scoring
├── serializer.py   # JSON/dict serialization
└── reports.py      # 6 report generators
```

## Usage

```python
from shared.graph import build_graph, GraphQuery, ImpactAnalyzer, GraphHealthAnalyzer

# Build the graph
graph = build_graph()
print(f"Graph: {graph.node_count} nodes, {graph.edge_count} edges")

# Query dependencies
query = GraphQuery(graph)
deps = query.get_dependencies("capability:recovery-intelligence")
print(f"Recovery depends on: {[d.name for d in deps]}")

# Find bottlenecks
bottlenecks = query.find_bottlenecks()
print(f"Top bottleneck: {bottlenecks[0][0].name} ({bottlenecks[0][1]} dependents)")

# Impact analysis
impact = ImpactAnalyzer(graph).analyze("capability:training-intelligence")
print(f"Breakage: {impact.total_affected_nodes} nodes affected, risk={impact.risk_score}")

# Graph health
health = GraphHealthAnalyzer(graph).analyze()
print(f"Graph health: {health.overall}/100 ({health.rating})")
```
