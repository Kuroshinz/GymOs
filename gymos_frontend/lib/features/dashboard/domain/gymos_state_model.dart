import 'package:flutter/material.dart';

class GymAppState {
  final int recoveryScore;
  final String recoveryColorHex;
  final String activeProgramName;
  final Map<String, MuscleStatus> muscleStatus;
  final NutritionSummary nutritionSummary;
  final WorkoutRecommender workoutRecommender;

  GymAppState({
    required this.recoveryScore,
    required this.recoveryColorHex,
    required this.activeProgramName,
    required this.muscleStatus,
    required this.nutritionSummary,
    required this.workoutRecommender,
  });

  factory GymAppState.fromJson(Map<String, dynamic> json) {
    final Map<String, dynamic> muscleMap = json['muscle_status'] as Map<String, dynamic>? ?? {};
    final status = muscleMap.map((key, value) => MapEntry(
      key,
      MuscleStatus.fromJson(value as Map<String, dynamic>),
    ));

    return GymAppState(
      recoveryScore: (json['recovery_score'] as num?)?.toInt() ?? 85,
      recoveryColorHex: json['recovery_color_hex'] as String? ?? '#34D399',
      activeProgramName: json['active_program_name'] as String? ?? 'PPL-UL Master v6',
      muscleStatus: status,
      nutritionSummary: NutritionSummary.fromJson(json['nutrition_summary'] as Map<String, dynamic>? ?? {}),
      workoutRecommender: WorkoutRecommender.fromJson(json['workout_recommender'] as Map<String, dynamic>? ?? {}),
    );
  }

  Color get recoveryColor => parseHexColor(recoveryColorHex);

  static Color parseHexColor(String hexString) {
    final cleanHex = hexString.replaceAll('#', '');
    if (cleanHex.length == 6) {
      return Color(int.parse('FF$cleanHex', radix: 16));
    } else if (cleanHex.length == 8) {
      return Color(int.parse(cleanHex, radix: 16));
    }
    return const Color(0xFF6366F1); // fallback indigo
  }
}

class MuscleStatus {
  final double fatigue;
  final String statusText;
  final String colorHex;

  MuscleStatus({
    required this.fatigue,
    required this.statusText,
    required this.colorHex,
  });

  factory MuscleStatus.fromJson(Map<String, dynamic> json) {
    return MuscleStatus(
      fatigue: (json['fatigue'] as num?)?.toDouble() ?? 0.0,
      statusText: json['status_text'] as String? ?? 'Fresh',
      colorHex: json['color'] as String? ?? '#34D399',
    );
  }

  Color get color => GymAppState.parseHexColor(colorHex);
}

class NutritionSummary {
  final double caloriesPct;
  final String caloriesDisplay;
  final double proteinPct;
  final String proteinDisplay;
  final double carbsPct;
  final String carbsDisplay;
  final double fatPct;
  final String fatDisplay;

  NutritionSummary({
    required this.caloriesPct,
    required this.caloriesDisplay,
    required this.proteinPct,
    required this.proteinDisplay,
    required this.carbsPct,
    required this.carbsDisplay,
    required this.fatPct,
    required this.fatDisplay,
  });

  factory NutritionSummary.fromJson(Map<String, dynamic> json) {
    return NutritionSummary(
      caloriesPct: (json['calories_pct'] as num?)?.toDouble() ?? 0.0,
      caloriesDisplay: json['calories_display'] as String? ?? '0 / 2500 kcal',
      proteinPct: (json['protein_pct'] as num?)?.toDouble() ?? 0.0,
      proteinDisplay: json['protein_display'] as String? ?? '0 / 160 g',
      carbsPct: (json['carbs_pct'] as num?)?.toDouble() ?? 0.0,
      carbsDisplay: json['carbs_display'] as String? ?? '0 / 280 g',
      fatPct: (json['fat_pct'] as num?)?.toDouble() ?? 0.0,
      fatDisplay: json['fat_display'] as String? ?? '0 / 70 g',
    );
  }
}

class WorkoutRecommender {
  final String suggestedExercise;
  final String aiCoachedTarget;

  WorkoutRecommender({
    required this.suggestedExercise,
    required this.aiCoachedTarget,
  });

  factory WorkoutRecommender.fromJson(Map<String, dynamic> json) {
    return WorkoutRecommender(
      suggestedExercise: json['suggested_exercise'] as String? ?? 'Lat Pulldown',
      aiCoachedTarget: json['ai_coached_target'] as String? ?? '3 sets x 10 reps @ RIR 2',
    );
  }
}
