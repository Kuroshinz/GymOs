# GymOS AI Analytics Stabilization Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix runtime import bugs, security configuration gaps, and logical threshold edge cases in the GymOS AI analytics workflows module.

**Architecture:** Address the startup import failures, secure API endpoints against stack trace leaks, correct hypertrophy MAV boundary conditions, and annotate/align thresholds with our Fitness Engine Standard.

**Tech Stack:** Python, FastAPI, Pydantic, pytest

---

### Task 1: Fix typing imports in `modules/ai/workflows/models.py`

**Files:**
- Modify: [models.py](file:///d:/Personal/NexusOs/modules/ai/workflows/models.py)

**Step 1: Write the failing test**
Run `python -c "import modules.ai.workflows.models"` to verify it crashes.
Expected: `ImportError: cannot import name 'list' from 'typing'`

**Step 2: Write minimal implementation**
Replace `from typing import list, dict` with `from typing import List, Dict` in [models.py](file:///d:/Personal/NexusOs/modules/ai/workflows/models.py#L2).

**Step 3: Verify it passes**
Run: `python -c "import modules.ai.workflows.models"`
Expected: Exit code 0 (no output).

---

### Task 2: Standardize and Annotate Volume Landmarks in `modules/ai/rules/volume_landmarks.py`

**Files:**
- Modify: [volume_landmarks.py](file:///d:/Personal/NexusOs/modules/ai/rules/volume_landmarks.py)

**Step 1: Write minimal implementation**
Annotate the hardcoded `landmarks` dictionary with `# HARDCODED_FALLBACK` comments to satisfy the [FITNESS_ENGINE_STANDARD.md](file:///d:/Personal/NexusOs/.ai/FITNESS_ENGINE_STANDARD.md#L85-L87) requirement.

**Step 2: Verify it passes**
Review [volume_landmarks.py](file:///d:/Personal/NexusOs/modules/ai/rules/volume_landmarks.py) to confirm comments are correctly annotated.

---

### Task 3: Fix MAV boundary check in `modules/ai/rules/volume_landmarks.py`

**Files:**
- Modify: [volume_landmarks.py](file:///d:/Personal/NexusOs/modules/ai/rules/volume_landmarks.py)
- Test: [test_ai_analytics.py](file:///d:/Personal/NexusOs/tests/unit/test_ai_analytics.py)

**Step 1: Write the failing test**
Add a test case in [test_ai_analytics.py](file:///d:/Personal/NexusOs/tests/unit/test_ai_analytics.py) to check volume values between MEV and MAV_min (e.g. 11 sets for chest).

```python
def test_volume_landmarks_boundary():
    # Chest MEV is 10, MAV_min is 12. 11 sets is above MEV but below MAV_min.
    res = calculate_volume_landmarks("chest", 11)
    assert "Within MAV" not in res["status"]
    assert "Below MAV" in res["status"]
```

**Step 2: Run test to verify it fails**
Run: `pytest tests/unit/test_ai_analytics.py::test_volume_landmarks_boundary`
Expected: FAIL due to incorrect status string assignment.

**Step 3: Write minimal implementation**
Modify [volume_landmarks.py](file:///d:/Personal/NexusOs/modules/ai/rules/volume_landmarks.py#L18-L25) boundary checks:
```python
    if weekly_sets < mev:
        status = "Below MEV (Maintenance/Under-training)"
    elif weekly_sets < data["MAV_min"]:
        status = "Above MEV (Below MAV Optimal Range)"
    elif weekly_sets <= data["MAV_max"]:
        status = "Within MAV (Optimal Hypertrophy)"
    elif weekly_sets < mrv:
        status = "Near MRV (High Volume)"
    else:
        status = "Above MRV (Overreaching/Over-training)"
```

**Step 4: Run test to verify it passes**
Run: `pytest tests/unit/test_ai_analytics.py`
Expected: PASS

---

### Task 4: Fix router exception handling in `modules/ai/workflows/routes.py`

**Files:**
- Modify: [routes.py](file:///d:/Personal/NexusOs/modules/ai/workflows/routes.py)

**Step 1: Write minimal implementation**
Sanitize error messages returned from API endpoints instead of forwarding raw exception details directly in the response body.

**Step 2: Verify it passes**
Run: `pytest`
Expected: All tests pass.
