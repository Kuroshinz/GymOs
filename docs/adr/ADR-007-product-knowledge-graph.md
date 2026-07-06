# ADR-007: Product Knowledge Graph

**Status:** Accepted

## Context

GymOS has grown into a complex platform with 12 capabilities, 3+ RFCs, 5+ versions,
multiple modules, engines, features, and documents. Understanding the relationship
between these elements — "What breaks if Recovery disappears?", "Which RFC created
this capability?", "Which module depends on which capability?" — requires a
structured, queryable representation of the entire architecture.

Previously, this knowledge was implicit in the code structure, documentation, and
team memory. There was no single source of truth for architectural relationships.

The RFC requires a graph capable of answering:
- Which capabilities depend on Recovery?
- Which RFC created this capability?
- Which version introduced this engine?
- Which modules consume this knowledge?
- What breaks if this node disappears?
- Which capability is the biggest bottleneck?

## Decision

Build a Product Knowledge Graph as a directed, typed property graph in
`shared/graph/`. The graph is:

- **Self-constructing**: reads from three canonical sources (Capability Platform,
  Kernel, Evolution Engine) — no manual data entry required.
- **Typed**: 10 node types (Vision, Roadmap, RFC, Capability, Module, Engine,
  Feature, Version, Milestone, Document) and 10 edge types (depends_on,
  implements, owns, contains, evolves_to, documents, uses, publishes, subscribes,
  belongs_to).
- **Queryable**: full query API including dependency analysis, path finding,
  topological analysis, cycle detection, orphan detection, and bottleneck analysis.
- **Safe**: pure read operations — the builder constructs from canonical sources
  without modifying them.
- **Reportable**: 6 report formats (Architecture, Capability, RFC, Impact,
  Dependency, Health).

## Rationale

1. **Never duplicate data**: The graph builder reads from existing canonical
   sources. When the capability registry changes, the graph reflects it
   automatically.

2. **Clean Architecture compliance**: The graph lives in `shared/` — it's a
   shared service that any module can query. Business logic stays in modules.

3. **No UI required**: The graph is accessed through a programmatic API. Reports
   are generated as Markdown.

4. **Proven approach**: Property graphs are the industry standard for dependency
   analysis (used by GitHub's dependency graph, AWS infrastructure analysis, etc.).

5. **Testable**: Pure data structure with stateless queries. No I/O, no
   side effects. The builder reads from already-loaded registries.

## Consequences

**Positive:**
- Architectural knowledge is now queryable, not implicit
- Impact analysis is automated — no more manual "what if this breaks?"
- Bottleneck detection helps prioritize architectural improvements
- 6 report types provide different architectural views
- 140+ tests verify correctness

**Negative:**
- Builds on top of existing systems — if Capability Platform schema changes,
  the graph builder must be updated
- Graph is in-memory only (not persisted to database)
- Serialization/deserialization available for persistence needs

## Technical Details

### Node Types

| Type | Description | Example |
|------|-------------|---------|
| VISION | Product vision/philosophy | vision:gymos |
| ROADMAP | Version roadmap stage | roadmap:v0.5 |
| RFC | RFC document | rfc:RFC-018 |
| CAPABILITY | Registered capability | capability:training-intelligence |
| MODULE | Python module | module:workout |
| ENGINE | Engine service | engine:event-bus |
| FEATURE | Specific feature | feature:pr-detection |
| VERSION | Product version | version:0.5.0 |
| MILESTONE | Milestone | milestone:platform-maturity |
| DOCUMENT | Documentation | document:product-strategy |

### Edge Types

| Type | Meaning |
|------|---------|
| DEPENDS_ON | A depends on B |
| IMPLEMENTS | A implements B |
| OWNS | A owns B |
| CONTAINS | A contains B |
| EVOLVES_TO | A evolves into B |
| DOCUMENTS | A documents B |
| USES | A uses B |
| PUBLISHES | A publishes events consumed by B |
| SUBSCRIBES | A subscribes to events from B |
| BELONGS_TO | A belongs to B |

### Query API

```python
query = GraphQuery(graph)
deps = query.get_dependencies(node_id)
dependents = query.get_dependents(node_id)
path = query.find_path(source_id, target_id)
cycles = query.find_cycles()
orphans = query.find_orphans()
bottlenecks = query.find_bottlenecks(min_dependents=3)
roots = query.find_roots()
leaves = query.find_leaves()
```

### Impact Analysis

```python
analyzer = ImpactAnalyzer(graph)
result = analyzer.analyze("capability:training-intelligence")
# result.affected_capabilities, result.risk_score, result.dependency_depth
```

### Graph Health

```python
analyzer = GraphHealthAnalyzer(graph)
score = analyzer.analyze()
# score.completeness, score.connectivity, score.cycle_health, score.orphan_health
```

### Reports

```python
from shared.graph.reports import (
    generate_architecture_report,   # Architecture Graph
    generate_capability_report,     # Capability Graph
    generate_rfc_report,            # RFC Graph
    generate_impact_report,         # Impact Report
    generate_dependency_report,     # Dependency Report
    generate_health_report,         # Health Report
)
```
