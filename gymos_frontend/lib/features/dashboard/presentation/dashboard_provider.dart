import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../domain/dashboard_state.dart';

class DashboardNotifier extends StateNotifier<DashboardState> {
  DashboardNotifier()
      : super(
          const DashboardState(
            athleteName: 'Nguyễn Thiện Nhân',
            athleteLevel: 28,
            workoutStreakDays: 14,
            recovery: RecoveryScoreState(
              score: 88,
              hrvMs: 78,
              restingHeartRateBpm: 54,
              sleepDurationMinutes: 465, // 7h 45m
              statusText: 'Optimal Readiness',
              color: const Color(0xFF10B981),
            ),
            todayWorkout: WorkoutState(
              title: 'Push A: Hypertrophy Focus',
              subTitle: 'Chest, Shoulders & Triceps',
              totalSets: 24,
              estimatedMinutes: 65,
              muscleFocus: 'Upper Chest & Lateral Delts',
            ),
            nutrition: NutritionState(
              caloriesConsumed: 1650,
              caloriesTarget: 2500,
              proteinG: 125,
              proteinTargetG: 180,
              carbsG: 180,
              carbsTargetG: 250,
              fatG: 48,
              fatTargetG: 75,
            ),
            coachInsight: CoachInsightState(
              recommendation: 'Target Progressive Overload on Incline Press',
              description: 'Your recovery is high at 88% and rest parameters suggest minimal fatigue. Today is the optimal day to target new personal records in chest pressing movements.',
            ),
            weeklyProgress: const [
              ProgressDataPoint(dayName: 'Mon', volumePercent: 0.8),
              ProgressDataPoint(dayName: 'Tue', volumePercent: 0.95),
              ProgressDataPoint(dayName: 'Wed', volumePercent: 0.3),
              ProgressDataPoint(dayName: 'Thu', volumePercent: 0.0),
              ProgressDataPoint(dayName: 'Fri', volumePercent: 0.85),
              ProgressDataPoint(dayName: 'Sat', volumePercent: 0.0),
              ProgressDataPoint(dayName: 'Sun', volumePercent: 0.0),
            ],
          ),
        );
}

final dashboardProvider = StateNotifierProvider<DashboardNotifier, DashboardState>((ref) {
  return DashboardNotifier();
});
