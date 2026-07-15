# GymOS AI Integration & Flutter-FastAPI Bridge Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Bridge the Flutter `AIAnalyticsPage` with the FastAPI backend using real-time API integrations, while resolving the typing import crash on startup.

**Architecture:** 
1. Fix the `typing` module import crash in Pydantic models.
2. Implement the `fetchAiPrediction` method in the Dart `ApiClient` using Dio.
3. Wire the Flutter `AIAnalyticsPage` to call the `/api/ai/forecast-recovery` endpoint dynamically as sliders change.

**Tech Stack:** Dart, Flutter, Python, FastAPI, Pydantic

---

### Task 1: Fix Startup Crash in `modules/ai/workflows/models.py`

**Files:**
- Modify: [models.py](file:///d:/Personal/NexusOs/modules/ai/workflows/models.py)

**Step 1: Write minimal implementation**
Replace `from typing import list, dict` with `from typing import List, Dict` to ensure compatibility. Update type annotations to uppercase `List` and `Dict`.

**Step 2: Verify it passes**
Run Python command: `python -c "import modules.ai.workflows.models"`
Expected: No errors.

---

### Task 2: Implement Dart API Integration in `api_client.dart`

**Files:**
- Modify: [api_client.dart](file:///d:/Personal/NexusOs/gymos_frontend/lib/core/network/api_client.dart)

**Step 1: Write minimal implementation**
Add `fetchAiPrediction({required double sleep, required int stress, required int soreness})` method to `ApiClient` calling the POST `/ai/forecast-recovery` (or `/api/ai/forecast-recovery`) endpoint:
```dart
  Future<Map<String, dynamic>> fetchAiPrediction({
    required double sleep,
    required int stress,
    required int soreness,
  }) async {
    try {
      final response = await _dio.post(
        '/ai/forecast-recovery',
        data: {
          'sleep_hours': sleep,
          'stress_level': stress,
          'soreness_level': soreness,
          'previous_scores': [80.0, 85.0],
        },
      );
      return response.data as Map<String, dynamic>;
    } catch (e) {
      throw Exception('Failed to fetch prediction: $e');
    }
  }
```

---

### Task 3: Wire Sliders to Dynamic API Queries in `ai_analytics_page.dart`

**Files:**
- Modify: [ai_analytics_page.dart](file:///d:/Personal/NexusOs/gymos_frontend/lib/features/ai_analytics/presentation/ai_analytics_page.dart)

**Step 1: Write minimal implementation**
- Define an async function `_updateSimulatedRecovery()` in state.
- In this function, set a temporary loading indicator, call `_apiClient.fetchAiPrediction(...)`, and update the simulated result panel state with response values (`forecasted_score`, `level`, `description`).
- Attach `_updateSimulatedRecovery()` to Sliders' `onChanged` / `onChangeEnd` callbacks.

**Step 2: Verify it passes**
Run: `flutter analyze`
Expected: PASS
