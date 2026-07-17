import 'package:flutter/material.dart';

enum ReadinessLevel {
  optimal('Optimal', Color(0xFF10B981)),
  moderate('Moderate', Color(0xFFF59E0B)),
  strained('Strained', Color(0xFFEF4444));

  final String label;
  final Color color;
  const ReadinessLevel(this.label, this.color);
}

@immutable
class RecoveryTrendPoint {
  final String dayName;
  final int score;

  const RecoveryTrendPoint({
    required this.dayName,
    required this.score,
  });
}

@immutable
class RecoveryState {
  final int score;
  final int hrvMs;
  final int hrvTargetMs;
  final int sleepScore;
  final int sleepDurationMinutes;
  final int sleepTargetMinutes;
  final int stressScore; // 0-100 (lower is better)
  final ReadinessLevel readiness;
  final String coachAdvice;
  final List<RecoveryTrendPoint> trendHistory;

  const RecoveryState({
    required this.score,
    required this.hrvMs,
    required this.hrvTargetMs,
    required this.sleepScore,
    required this.sleepDurationMinutes,
    required this.sleepTargetMinutes,
    required this.stressScore,
    required this.readiness,
    required this.coachAdvice,
    required this.trendHistory,
  });
}
