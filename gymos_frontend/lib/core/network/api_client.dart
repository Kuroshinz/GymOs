import 'package:dio/dio.dart';
import '../../features/ai_analytics/domain/ai_prediction_models.dart';
import '../../features/workout/domain/workout_log_models.dart';
import '../../features/dashboard/domain/gymos_state_model.dart';

class ApiClient {
  final Dio _dio = Dio(
    BaseOptions(
      baseUrl: "https://gymos-m37k.onrender.com/api",
      connectTimeout: const Duration(seconds: 5),
      receiveTimeout: const Duration(seconds: 5),
      headers: {
        'Content-Type': 'application/json',
      },
    ),
  );

  Future<Map<String, dynamic>> postWorkoutLog({
    required String exerciseName,
    required double weightKg,
    required int reps,
    required int rir,
  }) async {
    try {
      final response = await _dio.post(
        '/workout/log',
        data: {
          'exercise_name': exerciseName,
          'weight_kg': weightKg,
          'reps': reps,
          'rir': rir,
        },
      );
      return response.data as Map<String, dynamic>;
    } catch (e) {
      throw Exception('Failed to log workout: $e');
    }
  }

  Future<Map<String, dynamic>> getRecoveryData() async {
    try {
      final response = await _dio.get('/analytics/recovery');
      return response.data as Map<String, dynamic>;
    } catch (e) {
      throw Exception('Failed to load recovery data: $e');
    }
  }

  Future<Map<String, dynamic>> getPredictionData() async {
    try {
      final response = await _dio.get('/analytics/predictions');
      return response.data as Map<String, dynamic>;
    } catch (e) {
      throw Exception('Failed to load prediction data: $e');
    }
  }

  Future<Map<String, dynamic>> getAiData() async {
    try {
      final response = await _dio.get('/ai');
      return response.data as Map<String, dynamic>;
    } catch (e) {
      throw Exception('Failed to load AI data: $e');
    }
  }

  Future<AiPredictionResponse> getAiPrediction(AiPredictionRequest request) async {
    try {
      final response = await _dio.post(
        '/ai/forecast-recovery',
        data: request.toJson(),
      );
      return AiPredictionResponse.fromJson(response.data as Map<String, dynamic>);
    } catch (e) {
      return const AiPredictionResponse(
        readinessScore: 75.0,
        insightText: 'Connection offline. Local prediction fallback active.',
        efficiencyData: <String, dynamic>{},
      );
    }
  }

  Future<List<Map<String, dynamic>>> fetchExercises() async {
    try {
      final response = await _dio.get('/exercises');
      final data = response.data as List<dynamic>;
      return data.map((e) => e as Map<String, dynamic>).toList();
    } catch (e) {
      throw Exception('Failed to fetch exercises: $e');
    }
  }

  Future<List<Map<String, dynamic>>> fetchMuscles() async {
    try {
      final response = await _dio.get('/muscles');
      final data = response.data as List<dynamic>;
      return data.map((e) => e as Map<String, dynamic>).toList();
    } catch (e) {
      throw Exception('Failed to fetch muscles: $e');
    }
  }

  Future<bool> saveWorkoutSession(WorkoutSessionLog session) async {
    try {
      final response = await _dio.post(
        '/workout/session',
        data: session.toJson(),
      );
      return response.statusCode == 200 || response.statusCode == 201;
    } catch (e) {
      throw Exception('Failed to save workout session: $e');
    }
  }

  Future<Map<String, dynamic>> fetchWorkoutSessions() async {
    try {
      final response = await _dio.get('/workout/sessions');
      return response.data as Map<String, dynamic>;
    } catch (e) {
      throw Exception('Failed to fetch workout sessions: $e');
    }
  }

  Future<Map<String, dynamic>> getUnifiedDashboardState() async {
    try {
      final response = await _dio.get('/dashboard/state');
      return response.data as Map<String, dynamic>;
    } catch (e) {
      throw Exception('Failed to load unified dashboard state: $e');
    }
  }

  Future<GymAppState> fetchUnifiedDashboardState() async {
    try {
      final response = await _dio.get('/dashboard/state');
      return GymAppState.fromJson(response.data as Map<String, dynamic>);
    } catch (e) {
      return GymAppState(
        recoveryScore: 88,
        recoveryColorHex: '#38BDF8',
        activeProgramName: 'PPL-UL Master v6 (Offline)',
        muscleStatus: {
          'Chest': MuscleStatus(fatigue: 45.0, statusText: 'Recovering', colorHex: '#FBBF24'),
          'Triceps': MuscleStatus(fatigue: 15.0, statusText: 'Fresh', colorHex: '#34D399'),
          'Front_Delts': MuscleStatus(fatigue: 85.0, statusText: 'Overloaded', colorHex: '#FB7185'),
        },
        nutritionSummary: NutritionSummary(
          caloriesPct: 50.0,
          caloriesDisplay: '1250 / 2500 kcal',
          proteinPct: 62.5,
          proteinDisplay: '100 / 160 g',
          carbsPct: 42.8,
          carbsDisplay: '120 / 280 g',
          fatPct: 57.1,
          fatDisplay: '40 / 70 g',
        ),
        workoutRecommender: WorkoutRecommender(
          suggestedExercise: 'Lat Pulldown (Offline)',
          aiCoachedTarget: '3 sets x 10 reps @ RIR 2 (Offline)',
        ),
      );
    }
  }

  Future<bool> postNutritionLog({
    required String name,
    required double calories,
    required double proteinG,
    required double carbsG,
    required double fatG,
  }) async {
    try {
      final response = await _dio.post(
        '/nutrition/log',
        data: {
          'name': name,
          'calories': calories,
          'protein_g': proteinG,
          'carbs_g': carbsG,
          'fat_g': fatG,
        },
      );
      return response.statusCode == 200 || response.statusCode == 201;
    } catch (e) {
      throw Exception('Failed to log meal: $e');
    }
  }
}
