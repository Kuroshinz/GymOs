import 'package:dio/dio.dart';

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
}
