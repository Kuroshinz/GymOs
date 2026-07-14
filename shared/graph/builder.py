"""Graph Builder — automatically constructs the Product Knowledge Graph.

Reads from three canonical sources without duplicating data:
1. Capability Platform (shared/capabilities/) — 12 registered capabilities
2. Kernel (shared/kernel/) — product identity, RFCs, releases, snapshots
3. Evolution Engine (shared/evolution/) — RFCs, milestones, versions, forecasts
"""

from __future__ import annotations

from shared.capabilities import registry as _cap_registry
from shared.evolution.milestone_graph import build_milestone_progress
from shared.evolution.timeline import build_evolution_chain
from shared.graph.edge import Edge, EdgeType
from shared.graph.graph import KnowledgeGraph
from shared.graph.node import Node, NodeMetadata, NodeType
from shared.kernel.kernel_state import create_default_state


class GraphBuilder:
    """Constructs the Product Knowledge Graph from canonical data sources.

    The builder is stateless — every call to build() reconstructs the graph
    from the current state of the Capability Platform, Kernel, and Evolution Engine.
    This ensures the graph is always up-to-date with the source data.
    """

    def build(self) -> KnowledgeGraph:
        """Build and return the complete Product Knowledge Graph."""
        graph = KnowledgeGraph()
        self._add_vision_nodes(graph)
        self._add_roadmap_nodes(graph)
        self._add_capability_nodes(graph)
        self._add_rfc_nodes(graph)
        self._add_module_nodes(graph)
        self._add_engine_nodes(graph)
        self._add_feature_nodes(graph)
        self._add_version_nodes(graph)
        self._add_milestone_nodes(graph)
        self._add_document_nodes(graph)
        self._add_evolution_chain(graph)
        return graph

    # ── Vision ───────────────────────────────────────────────────────────────

    def _add_vision_nodes(self, graph: KnowledgeGraph) -> None:
        """Add vision/document nodes from the Kernel."""
        vision = Node(
            node_id="vision:gymos",
            node_type=NodeType.VISION,
            name="GymOS — Personal Hypertrophy Operating System",
            metadata=NodeMetadata(
                description="Build the best possible physique through data-driven training, nutrition, and recovery intelligence.",
                status="active",
                source="kernel",
                tags=("hypertrophy", "personal-os", "fitness"),
            ),
        )
        graph.add_node(vision)

        pillars = Node(
            node_id="vision:seven-pillars",
            node_type=NodeType.VISION,
            name="Seven Pillars: Training, Nutrition, Recovery, Consistency, Intelligence, Automation, Knowledge",
            metadata=NodeMetadata(
                description="Every feature belongs to one of seven product pillars.",
                status="active",
                source="kernel",
                tags=("pillars", "architecture"),
            ),
        )
        graph.add_node(pillars)
        graph.add_edge(Edge("vision:seven-pillars", "vision:gymos", EdgeType.BELONGS_TO))

    # ── Roadmap ──────────────────────────────────────────────────────────────

    def _add_roadmap_nodes(self, graph: KnowledgeGraph) -> None:
        """Add roadmap stages as nodes, linked to milestones and versions."""
        roadmap_stages = {
            "v0.5": "Platform Maturity — Architecture hardening, standards, Nutrition Intelligence",
            "v0.6": "Recovery Intelligence — Sleep, HRV, deload, nutrition UI",
            "v0.7": "Prediction Engine — Forecasting, trends, smart recommendations",
            "v0.8": "AI Coach — Natural language, adaptive guidance",
            "v0.9": "Adaptive Programming — Self-tuning auto-adjustments",
            "v1.0": "Full Autopilot — Complete hypertrophy operating system",
        }

        for version, description in roadmap_stages.items():
            node = Node(
                node_id=f"roadmap:{version}",
                node_type=NodeType.ROADMAP,
                name=f"Version {version} — {description.split(' — ')[0]}",
                metadata=NodeMetadata(
                    description=description,
                    status="reached" if version == "v0.5" else "planned",
                    source="evolution",
                    tags=("roadmap", version),
                ),
            )
            graph.add_node(node)
            graph.add_edge(Edge(node.node_id, "vision:gymos", EdgeType.BELONGS_TO))

    # ── Capabilities ─────────────────────────────────────────────────────────

    def _add_capability_nodes(self, graph: KnowledgeGraph) -> None:
        """Add all 12 registered capabilities as nodes with metadata."""
        for cap in _cap_registry.list_all():
            node = Node(
                node_id=f"capability:{cap.capability_id}",
                node_type=NodeType.CAPABILITY,
                name=cap.name,
                metadata=NodeMetadata(
                    version_introduced=cap.version_introduced,
                    status=cap.status.name.lower(),
                    health_score=cap.health.overall,
                    risk_score=cap.risk_level.value * 25,
                    tags=(cap.category, cap.priority.name.lower()),
                    source="capabilities",
                    description=cap.description,
                ),
            )
            graph.add_node(node)

            # Connect capability to its category/vision
            vision_id = "vision:gymos"
            graph.add_edge(Edge(node.node_id, vision_id, EdgeType.BELONGS_TO))

            # Add dependency edges between capabilities
            for dep_id in cap.dependencies:
                dep_node_id = f"capability:{dep_id}"
                if graph.has_node(dep_node_id):
                    edge_type = EdgeType.DEPENDS_ON
                    graph.add_edge(Edge(node.node_id, dep_node_id, edge_type))

    # ── RFCs ─────────────────────────────────────────────────────────────────

    def _add_rfc_nodes(self, graph: KnowledgeGraph) -> None:
        """Add all RFCs as nodes, linked to capabilities they affect."""
        state = create_default_state()
        for rfc_id, rfc in state.rfcs.items():
            node = Node(
                node_id=f"rfc:{rfc_id}",
                node_type=NodeType.RFC,
                name=f"{rfc_id}: {rfc.title}",
                metadata=NodeMetadata(
                    description=rfc.description,
                    status=rfc.status.name.lower(),
                    source="kernel",
                    tags=("rfc",),
                ),
            )
            graph.add_node(node)
            graph.add_edge(Edge(node.node_id, "vision:gymos", EdgeType.BELONGS_TO))

            # RFC → Capability evolution edges
            rfc_cap_map = _get_rfc_capability_mapping()
            for cap_id in rfc_cap_map.get(rfc_id, []):
                cap_node_id = f"capability:{cap_id}"
                if graph.has_node(cap_node_id):
                    graph.add_edge(Edge(node.node_id, cap_node_id, EdgeType.EVOLVES_TO))

    # ── Modules ──────────────────────────────────────────────────────────────

    def _add_module_nodes(self, graph: KnowledgeGraph) -> None:
        """Add Python modules as nodes, linked to capabilities they implement."""
        module_capability_map = {
            "workout": "training-intelligence",
            "nutrition": "nutrition-intelligence",
            "recovery": "recovery-intelligence",
            "brain": "decision-intelligence",
            "settings": "experience-platform",
        }

        for module_name, cap_id in module_capability_map.items():
            node = Node(
                node_id=f"module:{module_name}",
                node_type=NodeType.MODULE,
                name=f"{module_name.capitalize()} Module",
                metadata=NodeMetadata(
                    status="active" if cap_id != "experience-platform" else "draft",
                    source="capabilities",
                    tags=("module", module_name),
                    description=f"The {module_name} module implements {module_name} intelligence.",
                ),
            )
            graph.add_node(node)

            cap_node_id = f"capability:{cap_id}"
            if graph.has_node(cap_node_id):
                graph.add_edge(Edge(node.node_id, cap_node_id, EdgeType.IMPLEMENTS))

    # ── Engines ──────────────────────────────────────────────────────────────

    def _add_engine_nodes(self, graph: KnowledgeGraph) -> None:
        """Add engines as nodes, linked to capabilities and modules."""
        engines = {
            "engine:event-bus": ("Event Bus", "event-platform", "Platform event-driven communication."),
            "engine:di-container": ("DI Container", "capability-platform", "Dependency injection container."),
            "engine:gymbrain": ("GymBrain", "decision-intelligence", "Deterministic rule engine."),
            "engine:evolution": ("Evolution Engine", "product-intelligence", "Product evolution analysis."),
            "engine:kerner": ("Kernel", "product-intelligence", "Product operating system runtime."),
        }

        for engine_id, (name, cap_id, description) in engines.items():
            node = Node(
                node_id=engine_id,
                node_type=NodeType.ENGINE,
                name=name,
                metadata=NodeMetadata(
                    description=description,
                    status="active",
                    source="kernel",
                    tags=("engine",),
                ),
            )
            graph.add_node(node)

            cap_node_id = f"capability:{cap_id}"
            if graph.has_node(cap_node_id):
                graph.add_edge(Edge(node.node_id, cap_node_id, EdgeType.IMPLEMENTS))

    # ── Features ─────────────────────────────────────────────────────────────

    def _add_feature_nodes(self, graph: KnowledgeGraph) -> None:
        """Add key features linked to their capabilities."""
        features: list[tuple[str, str, str, str]] = [
            ("feature:workout-logging", "Workout Logging", "training-intelligence", "Set/rep tracking with RIR."),
            ("feature:pr-detection", "PR Detection", "training-intelligence", "Auto-detect weight/rep/volume/e1RM PRs."),
            ("feature:double-progression", "Double Progression", "capability-platform", "Reps-first progression method."),
            ("feature:volume-analytics", "Volume Analytics", "capability-platform", "Weekly volume by muscle group."),
            ("feature:fatigue-analysis", "Fatigue Analysis", "decision-intelligence", "5-factor fatigue detection."),
            ("feature:plateau-detection", "Plateau Detection", "decision-intelligence", "6 plateau type detection."),
            ("feature:lean-bulk", "Lean Bulk Analysis", "nutrition-intelligence", "Quality score, protein deficit."),
            ("feature:macro-tracking", "Macro Tracking", "nutrition-intelligence", "Daily macro vs target."),
            ("feature:knowledge-loader", "Knowledge Loader", "knowledge-platform", "Single source of truth for knowledge."),
            ("feature:event-platform", "Event Platform", "event-platform", "14 typed domain events."),
            ("feature:capability-registry", "Capability Registry", "capability-platform", "12 registered capabilities."),
        ]

        for feature_id, name, cap_id, description in features:
            node = Node(
                node_id=feature_id,
                node_type=NodeType.FEATURE,
                name=name,
                metadata=NodeMetadata(
                    description=description,
                    status="active",
                    source="capabilities",
                    tags=("feature",),
                ),
            )
            graph.add_node(node)

            cap_node_id = f"capability:{cap_id}"
            if graph.has_node(cap_node_id):
                graph.add_edge(Edge(node.node_id, cap_node_id, EdgeType.OWNS))

    # ── Versions ─────────────────────────────────────────────────────────────

    def _add_version_nodes(self, graph: KnowledgeGraph) -> None:
        """Add versions as nodes, linked to roadmap and milestones."""
        versions = {
            "0.1.0": "Foundation — Core architecture, workout tracking",
            "0.2.0": "AI Development Kit — Knowledge layer, coaching",
            "0.3.0": "GymBrain Intelligence — 15 rules, analysis engines",
            "0.4.0": "Nutrition Architecture — Domain models, analysis",
            "0.5.0": "Platform Maturity — ADRs, Constitution, Standards",
        }

        for version, description in versions.items():
            node = Node(
                node_id=f"version:{version}",
                node_type=NodeType.VERSION,
                name=f"v{version}",
                metadata=NodeMetadata(
                    description=description,
                    status="released",
                    source="kernel",
                    tags=("version", version),
                ),
            )
            graph.add_node(node)
            graph.add_edge(Edge(node.node_id, "vision:gymos", EdgeType.BELONGS_TO))

    # ── Milestones ───────────────────────────────────────────────────────────

    def _add_milestone_nodes(self, graph: KnowledgeGraph) -> None:
        """Add milestones as nodes from the Evolution Engine."""
        milestones = build_milestone_progress()

        for milestone in milestones:
            node = Node(
                node_id=f"milestone:{milestone.label.lower().replace(' ', '-')}",
                node_type=NodeType.MILESTONE,
                name=milestone.label,
                metadata=NodeMetadata(
                    version_introduced=f"v{milestone.target_version}",
                    description=milestone.description,
                    status="reached" if milestone.is_reached else "in_progress",
                    health_score=milestone.completion_percent,
                    source="evolution",
                    tags=("milestone", f"v{milestone.target_version}"),
                ),
            )
            graph.add_node(node)
            graph.add_edge(Edge(node.node_id, "vision:gymos", EdgeType.BELONGS_TO))

            # Milestone contains capabilities
            roadmap_id = f"roadmap:v{milestone.target_version}"
            if graph.has_node(roadmap_id):
                graph.add_edge(Edge(node.node_id, roadmap_id, EdgeType.BELONGS_TO))

    # ── Documents ────────────────────────────────────────────────────────────

    def _add_document_nodes(self, graph: KnowledgeGraph) -> None:
        """Add documents as nodes, linked to what they document."""
        documents: list[tuple[str, str, str]] = [
            ("PRODUCT_STRATEGY", "Product Strategy", "vision:gymos"),
            ("ARCHITECTURE_OVERVIEW", "Architecture Overview", "vision:gymos"),
            ("PRODUCT_REQUIREMENTS", "Product Requirements", "vision:seven-pillars"),
            ("EVOLUTION_REPORT", "Evolution Report", "vision:gymos"),
        ]

        for doc_id, title, target_id in documents:
            node = Node(
                node_id=f"document:{doc_id.lower()}",
                node_type=NodeType.DOCUMENT,
                name=title,
                metadata=NodeMetadata(
                    description=f"Documentation: {title}",
                    status="active",
                    source="kernel",
                    tags=("document",),
                ),
            )
            graph.add_node(node)
            if graph.has_node(target_id):
                graph.add_edge(Edge(node.node_id, target_id, EdgeType.DOCUMENTS))

    # ── Evolution Chain ──────────────────────────────────────────────────────

    def _add_evolution_chain(self, graph: KnowledgeGraph) -> None:
        """Add evolution chain links: RFC → Capability → Milestone → Version."""
        chain = build_evolution_chain()
        for link in chain.links:
            rfc_id = f"rfc:{link.rfc_id}"
            cap_id = f"capability:{link.capability_id}"
            milestone_id = f"milestone:{link.milestone_label.lower().replace(' ', '-')}"
            version_id = f"version:{link.milestone_version}"

            # Link RFC → Milestone (via capability)
            if graph.has_node(rfc_id) and graph.has_node(milestone_id) and not graph.has_edge(rfc_id, milestone_id):
                graph.add_edge(Edge(rfc_id, milestone_id, EdgeType.EVOLVES_TO,
                                    metadata=f"Evolution chain: {link.rfc_id} → {link.milestone_label}"))

            # Link Capability → Milestone
            if graph.has_node(cap_id) and graph.has_node(milestone_id) and not graph.has_edge(cap_id, milestone_id):
                graph.add_edge(Edge(cap_id, milestone_id, EdgeType.CONTAINS))

            # Link Milestone → Version
            if graph.has_node(milestone_id) and graph.has_node(version_id) and not graph.has_edge(milestone_id, version_id):
                graph.add_edge(Edge(milestone_id, version_id, EdgeType.EVOLVES_TO))


def build_graph() -> KnowledgeGraph:
    """Convenience function to build the complete graph."""
    return GraphBuilder().build()


# ── Helper: RFC → Capability mapping ──────────────────────────────────────

def _get_rfc_capability_mapping() -> dict[str, list[str]]:
    """Central mapping of RFC IDs to affected capability IDs.

    Must stay in sync with shared/evolution/rfc_history.py.
    """
    return {
        "RFC-018": ["capability-platform", "product-intelligence"],
        "RFC-018.5": [
            "capability-platform", "product-intelligence",
            "training-intelligence", "nutrition-intelligence",
            "knowledge-platform", "event-platform",
        ],
        "RFC-018.7": ["capability-platform", "product-intelligence"],
        "RFC-019": ["recovery-intelligence"],
        "RFC-020": ["experience-platform"],
    }
