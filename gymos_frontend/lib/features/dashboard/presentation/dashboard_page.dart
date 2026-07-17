import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'dashboard_provider.dart';
import 'widgets/greeting_widget.dart';
import 'widgets/recovery_card.dart';
import 'widgets/today_workout_card.dart';
import 'widgets/nutrition_summary_card.dart';
import 'widgets/coach_insight_card.dart';
import 'widgets/weekly_progress_chart.dart';
import '../../../core/theme/theme_tokens.dart';
import '../../../core/extensions/context_extensions.dart';

class DashboardPage extends ConsumerWidget {
  const DashboardPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(dashboardProvider);

    return Scaffold(
      backgroundColor: context.theme.scaffoldBackgroundColor,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(GymOSTokens.space24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              GymOSGreetingWidget(
                athleteName: state.athleteName,
                athleteLevel: state.athleteLevel,
                streakDays: state.workoutStreakDays,
              ),
              const SizedBox(height: GymOSTokens.space24),
              
              // Responsive Layout Grid
              if (context.isMobile)
                Column(
                  children: [
                    GymOSRecoveryCard(
                      score: state.recovery.score,
                      hrvMs: state.recovery.hrvMs,
                      rhrBpm: state.recovery.restingHeartRateBpm,
                      sleepDurationMinutes: state.recovery.sleepDurationMinutes,
                      statusText: state.recovery.statusText,
                      color: state.recovery.color,
                    ),
                    const SizedBox(height: GymOSTokens.space16),
                    GymOSTodayWorkoutCard(
                      title: state.todayWorkout.title,
                      subTitle: state.todayWorkout.subTitle,
                      totalSets: state.todayWorkout.totalSets,
                      estimatedMinutes: state.todayWorkout.estimatedMinutes,
                      muscleFocus: state.todayWorkout.muscleFocus,
                    ),
                    const SizedBox(height: GymOSTokens.space16),
                    GymOSNutritionSummaryCard(
                      caloriesConsumed: state.nutrition.caloriesConsumed,
                      caloriesTarget: state.nutrition.caloriesTarget,
                      proteinG: state.nutrition.proteinG,
                      proteinTargetG: state.nutrition.proteinTargetG,
                      carbsG: state.nutrition.carbsG,
                      carbsTargetG: state.nutrition.carbsTargetG,
                      fatG: state.nutrition.fatG,
                      fatTargetG: state.nutrition.fatTargetG,
                    ),
                    const SizedBox(height: GymOSTokens.space16),
                    GymOSCoachInsightCard(
                      recommendation: state.coachInsight.recommendation,
                      description: state.coachInsight.description,
                    ),
                    const SizedBox(height: GymOSTokens.space16),
                    GymOSWeeklyProgressChart(
                      data: state.weeklyProgress,
                    ),
                  ],
                )
              else
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Left Column (Workout progress, charts and state)
                    Expanded(
                      flex: 6,
                      child: Column(
                        children: [
                          GymOSRecoveryCard(
                            score: state.recovery.score,
                            hrvMs: state.recovery.hrvMs,
                            rhrBpm: state.recovery.restingHeartRateBpm,
                            sleepDurationMinutes: state.recovery.sleepDurationMinutes,
                            statusText: state.recovery.statusText,
                            color: state.recovery.color,
                          ),
                          const SizedBox(height: GymOSTokens.space16),
                          GymOSTodayWorkoutCard(
                            title: state.todayWorkout.title,
                            subTitle: state.todayWorkout.subTitle,
                            totalSets: state.todayWorkout.totalSets,
                            estimatedMinutes: state.todayWorkout.estimatedMinutes,
                            muscleFocus: state.todayWorkout.muscleFocus,
                          ),
                          const SizedBox(height: GymOSTokens.space16),
                          GymOSWeeklyProgressChart(
                            data: state.weeklyProgress,
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: GymOSTokens.space24),
                    // Right Column (AI Insights and Nutrition)
                    Expanded(
                      flex: 5,
                      child: Column(
                        children: [
                          GymOSNutritionSummaryCard(
                            caloriesConsumed: state.nutrition.caloriesConsumed,
                            caloriesTarget: state.nutrition.caloriesTarget,
                            proteinG: state.nutrition.proteinG,
                            proteinTargetG: state.nutrition.proteinTargetG,
                            carbsG: state.nutrition.carbsG,
                            carbsTargetG: state.nutrition.carbsTargetG,
                            fatG: state.nutrition.fatG,
                            fatTargetG: state.nutrition.fatTargetG,
                          ),
                          const SizedBox(height: GymOSTokens.space16),
                          GymOSCoachInsightCard(
                            recommendation: state.coachInsight.recommendation,
                            description: state.coachInsight.description,
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
            ],
          ),
        ),
      ),
    );
  }
}
