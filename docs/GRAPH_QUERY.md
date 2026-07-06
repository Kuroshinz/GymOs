# Product Knowledge Graph — Query API

## Overview

The Query API provides 10 analysis methods for the Product Knowledge Graph.
All methods are pure — they read the graph without modifying it.

## API Reference

### `get_dependencies(node_id) -> list[Node]`

Return nodes that this node directly depends on (via DEPENDS_ON and USES edges).

```python
deps = query.get_dependencies("capability:recovery-intelligence")
# → [Node("capability:training-intelligence"), ...]
```

### `get_dependents(node_id) -> list[Node]`

Return nodes that directly depend on this node.

```python
deps = query.get_dependents("capability:training-intelligence")
# → [Node("capability:nutrition-intelligence"), Node("capability:recovery-intelligence"), ...]
```

### `get_transitive_dependencies(node_id) -> list[Node]`

Return ALL transitive dependencies via BFS traversal.

```python
deps = query.get_transitive_dependencies("capability:ai-coach")
# → [Node("capability:decision-intelligence"), Node("capability:training-intelligence"), ...]
```

### `find_path(source_id, target_id) -> list[str] | None`

Find the shortest directed path between two nodes using BFS.

```python
path = query.find_path("rfc:RFC-018", "version:0.5.0")
# → ["rfc:RFC-018", "capability:capability-platform", "milestone:platform-maturity", "version:0.5.0"]
```

### `find_all_paths(source_id, target_id, max_depth=6) -> list[list[str]]`

Find all directed paths between two nodes up to a maximum depth.

```python
paths = query.find_all_paths("rfc:RFC-018", "milestone:platform-maturity")
# → [["rfc:RFC-018", "capability:capability-platform", "milestone:platform-maturity"], ...]
```

### `find_roots() -> list[Node]`

Nodes with no incoming DEPENDS_ON or USES edges. These are foundational elements.

```python
roots = query.find_roots()
# → [Node("capability:knowledge-platform"), Node("capability:event-platform"), ...]
```

### `find_leaves() -> list[Node]`

Nodes with no outgoing DEPENDS_ON or USES edges.

```python
leaves = query.find_leaves()
# → [Node("version:0.5.0"), Node("document:product-requirements"), ...]
```

### `find_cycles() -> list[list[str]]`

Detect all dependency cycles using DFS. Returns list of cycles, each as a list of node IDs.

```python
cycles = query.find_cycles()
# → []  (no cycles is the expected state)
```

### `find_orphans() -> list[Node]`

Nodes with no edges at all — isolated from the graph.

```python
orphans = query.find_orphans()
# → []  (no orphans is the expected state)
```

### `find_bottlenecks(min_dependents=3) -> list[tuple[Node, int]]`

Nodes with the highest number of direct dependents, sorted by count descending.

```python
bottlenecks = query.find_bottlenecks()
# → [(Node("capability:training-intelligence"), 4), (Node("capability:nutrition-intelligence"), 3)]
```

### `find_critical_path() -> list[str]`

Find the longest dependency chain in the graph. This represents the most complex
dependency path.

```python
path = query.find_critical_path()
# → ["capability:knowledge-platform", "capability:decision-intelligence", ...]
```

### `get_all_dependency_edges() -> list[Edge]`

Return all DEPENDS_ON and USES edges.

```python
edges = query.get_all_dependency_edges()
# → [Edge(capability:nutrition-intelligence -[depends_on]-> capability:training-intelligence), ...]
```

## Impact Analysis

```python
from shared.graph import ImpactAnalyzer

analyzer = ImpactAnalyzer(graph)
result = analyzer.analyze("capability:training-intelligence")

# Result fields:
result.target_node_id        # "capability:training-intelligence"
result.target_node_name      # "Training Intelligence"
result.affected_capabilities # ("Nutrition Intelligence", "Recovery Intelligence", ...)
result.affected_rfcs         # ("RFC-018.5: GymOS Kernel",)
result.affected_modules      # ("Workout Module",)
result.affected_engines      # ()
result.total_affected_nodes  # 5
result.risk_score            # 35.0
result.dependency_depth      # 2
result.breakage_analysis     # Human-readable markdown
```

## Graph Health

```python
from shared.graph import GraphHealthAnalyzer

analyzer = GraphHealthAnalyzer(graph)
score = analyzer.analyze()

# Score fields:
score.overall         # 85.3 (composite health)
score.completeness     # 90.0 (% of expected node types present)
score.connectivity     # 95.0 (% of nodes with edges)
score.cycle_health     # 100.0 (100 = no cycles)
score.orphan_health    # 100.0 (100 = no orphans)
score.depth_health     # 80.0 (based on max depth)
score.node_count       # 42
score.edge_count       # 78
score.cycle_count      # 0
score.orphan_count     # 0
score.max_depth        # 4
score.avg_edges_per_node # 1.86
score.rating           # "good"
```
