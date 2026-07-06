# Reason Tree

## Overview

The Reason Tree represents complete reasoning chains from user intent through to the final recommendation. Every node is immutable and traceable, providing full transparency into how decisions are made.

## ReasonNodeType Chain

```
INTENT → KNOWLEDGE → RECOVERY → PREDICTION → DECISION → RECOMMENDATION
```

## ReasonNode

```python
@dataclass
class ReasonNode:
    node_id: str
    node_type: ReasonNodeType
    label: str
    description: str = ""
    confidence: float = 0.0
    evidence_ids: list[str] = field(default_factory=list)
    parent_id: str | None = None
    children_ids: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=utc_now)
    metadata: dict = field(default_factory=dict)
```

## ReasonChain

```python
@dataclass
class ReasonChain:
    chain_id: str
    nodes: list[ReasonNode]
```

### Properties

| Property | Returns |
|---|---|
| `length` | Number of nodes in chain |
| `is_complete` | True if >= 2 nodes |
| `overall_confidence` | Average confidence across all nodes |
| `node_types` | Ordered list of node types in chain |

## ReasonTree API

| Method | Description |
|---|---|
| `add_node(node)` | Add a node to the tree |
| `get_node(id)` | Lookup node by ID |
| `get_nodes_by_type(type)` | All nodes of a given type |
| `build_chain(recommendation_id)` | Walk parent_id chain from recommendation back to root |
| `get_chain(id)` | Get a previously built chain |
| `find_chains_for_node(id)` | All chains containing a specific node |
| `query(type, min_confidence)` | Filtered node query |
| `clear()` | Remove all nodes and chains |
| `to_dict()` | Serialize to dict |

### Properties

| Property | Returns |
|---|---|
| `node_count` | Total nodes |
| `chain_count` | Total built chains |

## Building Chains

The `build_chain` method walks the `parent_id` chain from a recommendation node backwards to the root:

```python
chain = tree.build_chain("rec-001")
# Chain nodes sorted by type order: INTENT, KNOWLEDGE, RECOVERY, PREDICTION, DECISION, RECOMMENDATION
```

Chains are sorted by the canonical type order regardless of insertion order. Circular references are handled by tracking visited nodes.
