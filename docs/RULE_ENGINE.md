# Rule Engine

## Architecture

The `RuleEngine` (`modules/gymbrain/rules/engine.py`) evaluates registered rules against current training data and returns sorted, deduplicated recommendations.

### Key Design Decisions

1. **Rules are stateless** — each `BaseRule.evaluate()` takes a `DataProvider` and optional context dict. No mutable state is stored on the rule.

2. **Rules return RuleResult** — never modify external state. A `RuleResult` has:
   - `triggered: bool` — whether the condition was met
   - `recommendation: Recommendation | None` — the structured output
   - `evidence: list[str]` — data points that triggered the rule
   - `confidence: float` — how certain the rule is
   - `reason: str` — human-readable explanation

3. **Deduplication** — rules producing the same `(category, title)` pair are merged (first registered wins).

4. **Max limit** — configurable cap on total recommendations returned (default 20).

## BaseRule Interface

```python
class BaseRule(ABC):
    def __init__(self, name: str, description: str = "", priority: int = 50)
    
    @abstractmethod
    def evaluate(self, provider: DataProvider, context: dict | None = None) -> RuleResult
```

## Rule Catalog

### Volume Rules (`volume_rules.py`)

- **VolumeRule**: If a priority muscle's weekly volume is below MEV, recommend increasing volume (confidence: 0.85)
- **VolumeExcessRule**: If a muscle's weekly volume exceeds MRV, recommend reducing volume (confidence: 0.80)
- **FrequencyRule**: If a priority muscle is trained less than recommended frequency, suggest increasing (confidence: 0.75)

### Progression Rules (`progression_rules.py`)

- **ProgressionRule**: If target reps are reached with adequate RIR ≥ 2, recommend increasing load (confidence: 0.95) — implements Double Progression
- **DeloadRule**: If recovery flags indicate deload is needed, recommend deload week (confidence: 0.60-0.90)

### Plateau Rules (`plateau_rules.py`)

- **WeightPlateauRule**: If bodyweight unchanged for 14+ days with high adherence, recommend increasing calories (confidence: 0.75)
- **StrengthPlateauRule**: If e1rm hasn't increased for 3+ weeks on compound lift, recommend programming change (confidence: 0.80)
- **RepPlateauRule**: If reps haven't increased within target range for 3+ weeks, recommend adjustment (confidence: 0.70)

### Fatigue Rules (`fatigue_rules.py`)

- **FatigueRule**: If fatigue level is HIGH or VERY_HIGH, recommend recovery-focused actions (confidence: 0.90)
- **TechniqueRule**: If fatigue/recovery flags indicate technique degradation, recommend technique review (confidence: 0.65)
- **RestRule**: If RIR is consistently 0 across sessions, recommend increased rest (confidence: 0.75)

### Recovery Rules (`recovery_rules.py`)

- **RecoveryRule**: If recovery score is low/declining, recommend recovery interventions (confidence: 0.70-0.90)
- **ConsistencyRule**: If sessions have been missed, recommend consistency improvements (confidence: 0.80)

### Nutrition Rules (`nutrition_rules.py`)

- **NutritionRule**: If bodyweight trend is decreasing/stable/too fast during bulk, adjust calories (confidence: 0.70-0.85)
- **BodyweightStallRule**: If bodyweight hasn't moved in 14+ days, recommend increasing calories (confidence: 0.80)

## Adding a New Rule

```python
from modules.gymbrain.rules.base import BaseRule, RuleResult

class MyNewRule(BaseRule):
    def __init__(self):
        super().__init__(
            name="my_new_rule",
            description="What this rule does",
            priority=70,
        )
    
    def evaluate(self, provider, context=None):
        # Check conditions
        if condition:
            return RuleResult(
                triggered=True,
                recommendation=Recommendation(...),
                evidence=["data point 1", "data point 2"],
                confidence=0.85,
                reason="Why this was triggered",
            )
        return RuleResult()

# Register with the engine
engine.register(MyNewRule())
```
