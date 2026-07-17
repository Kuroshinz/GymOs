import 'package:flutter/material.dart';

class RecoveryScoreState {
  final int score;
  final int hrvMs;
  final int restingHeartRateBpm;
  final int sleepDurationMinutes;
  final String statusText;
  final Color color;

  const RecoveryScoreState({
    required this.score,
    required this.hrvMs,
    required this.restingHeartRateBpm,
    required this.sleepDurationMinutes,
    required this.statusText,
    required this.color,
  });
}

class WorkoutState {
  final String title;
  final String subTitle;
  final int totalSets;
  final int estimatedMinutes;
  final String muscleFocus;

  const WorkoutState({
    required this.title,
    required this.subTitle,
    required this.totalSets,
    required this.estimatedMinutes,
    required this.muscleFocus,
  });
}

class NutritionState {
  final int caloriesConsumed;
  final int caloriesTarget;
  final int proteinG;
  final int proteinTargetG;
  final int carbsG;
  final int carbsTargetG;
  final int fatG;
  final int fatTargetG;

  const NutritionState({
    required this.caloriesConsumed,
    required this.caloriesTarget,
    required this.proteinG,
    required this.proteinTargetG,
    required this.carbsG,
    required this.carbsTargetG,
    required this.fatG,
    required this.fatTargetG,
  });
}

class CoachInsightState {
  final String recommendation;
  final String description;

  const CoachInsightState({
    required this.recommendation,
    required this.description,
  });
}

class ProgressDataPoint {
  final String dayName;
  final double volumePercent;

  const ProgressDataPoint({
    required this.dayName,
    required this.volumePercent,
  });
}

class DashboardState {
  final String athleteName;
  final int athleteLevel;
  final int workoutStreakDays;
  final RecoveryScoreState recovery;
  final WorkoutState todayWorkout;
  final NutritionState nutrition;
  final CoachInsightState coachInsight;
  final List<ProgressDataPoint> weeklyProgress;

  const DashboardState({
    required this.athleteName,
    required this.athleteLevel,
    required this.workoutStreakDays,
    required this.recovery,
    required this.todayWorkout,
    required this.nutrition,
    required this.coachInsight,
    required this.weeklyProgress,
  });
}
