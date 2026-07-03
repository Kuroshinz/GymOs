# Fitness Engine Standard

*Effective: Sprint 3.2.5*

## 1. Purpose

This standard governs all fitness intelligence code in GymOS: rules, analyzers, engines, and recommendation logic. Fitness engines are the core differentiator of GymOS — they must be correct, explainable, and evidence-based.

## 2. Engine Classification

### 2.1 Analysis Engine
Analyzes data and produces structured results. Does NOT produce recommendations.

- Examples: `PlateauDetector`, `FatigueAnalyzer`, `MuscleAnalyzer`, `MacroAnalyzer`
- Output: typed dataclass (e.g., `PlateauResult`, `FatigueResult`)
- Pure function of input data (stateless, deterministic)

### 2.2 Rule Engine
Evaluates conditions against current state and produces recommendations when triggered.

- Examples: `VolumeRule`, `ProteinDeficitRule`, `DeloadRule`
- Extends: `BaseRule` (ABC)
- Methods: `evaluate(provider, context) -> RuleResult`
- Stateless — all state comes from DataProvider

### 2.3 Decision Engine
Orchestrates multiple analysis engines and rule engines. Single entry point for application code.

- Examples: `DecisionEngine`
- Wires: DataProvider + Analyzers + RuleEngine
- Public API: `get_today_recommendations()`, `get_weekly_review()`

### 2.4 Provider Engine
Abstracts data access behind a typed interface. Never contains business logic.

- Examples: `DataProvider`, `NutritionProvider`, `ProductionNutritionProvider`
- Implements: Protocol from `shared/interfaces/`
- Null-safe: returns `None` or empty collections for missing data

## 3. Rule Requirements

Every rule MUST document:
- **Condition**: When does this rule trigger? (precise mathematical/logical condition)
- **Evidence**: What data supports the conclusion?
- **Confidence**: How confident is this rule? (0.0-1.0, based on data quality/completeness)
- **Priority**: How important is this rule relative to others? (1-100, higher = more important)
- **Source**: What scientific evidence supports this rule?

### Rule Template

```python
class DeloadRule(BaseRule):
    """Recommend deload when weekly volume exceeds sustainable threshold for 3+ weeks.

    Evidence: Systematic review by Schoenfeld (2017) found that
    accumulated fatigue beyond 8 weeks of high-volume training
    reduces hypertrophy gains. Deload weeks restore muscle sensitivity.

    Source: Schoenfeld BJ, et al. "Effects of different volume-equated
    resistance training loading strategies..." JSCR, 2017.
    """

    def __init__(self) -> None:
        super().__init__(name="deload_rule", description="Deload week recommendation", priority=80)

    def evaluate(self, provider: DataProvider, context: dict[str, Any] | None = None) -> RuleResult:
        # Logic here
        ...
```

## 4. Threshold Standards

### 4.1 Scientific Thresholds
All scientific thresholds (e.g., "protein target = 1.6-2.2 g/kg", "deload after 8 weeks") MUST be:
1. Defined in `knowledge/` as structured data (YAML/JSON/Markdown with version field)
2. Consumed through the Knowledge Pipeline (KnowledgeLoader → KnowledgeService)
3. Never hard-coded in Python code

### 4.2 User-Adjustable Thresholds
Thresholds that users may want to adjust (e.g., "acceptable RIR range", "min session duration") SHOULD be:
1. Configurable through the Settings module (future)
2. Sourced from `knowledge/user/` defaults if not configured
3. Overridable at runtime via the UserProfile

### 4.3 Fallback Defaults
When knowledge-backed thresholds are unavailable (no knowledge file, broken pipeline), rules MUST fall back to reasonable hard-coded defaults. These defaults MUST be documented with a `# HARDCODED_FALLBACK` comment.

## 5. Evidence & Attribution

- Every rule with scientific backing MUST cite its source(s)
- Citations use APA format
- Sources live in `knowledge/research/` as structured markdown files
- The `references` field in exercise/muscle definitions links to research

## 6. Testing Standards for Engines

### 6.1 Analysis Engine Tests
- Test with empty data (returns defaults/empty)
- Test with boundary values (threshold edges)
- Test with known inputs → verify known outputs
- Test determinism (same input → same output)

### 6.2 Rule Tests
- Test NOT triggered condition
- Test triggered condition with minimal evidence
- Test priority ordering when multiple rules trigger
- Test that rules don't modify provider state

### 6.3 Decision Engine Tests
- Test with all providers returning None (graceful degradation)
- Test with partial data (nutrition only, training only)
- Test that rules are registered in correct order
- Test that evaluate_rules returns typed Recommendation objects

## 7. Prohibited Patterns

- ❌ Non-deterministic rule evaluation (random, time-based triggers)
- ❌ Rules accessing databases or repositories directly
- ❌ Rules modifying provider state during evaluation
- ❌ Business logic in UI code (widgets, controllers)
- ❌ Scientific thresholds hard-coded without fallback annotation
- ❌ Silent failure (unhandled exceptions in rule evaluation)
