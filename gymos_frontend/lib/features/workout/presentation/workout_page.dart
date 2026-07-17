import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'workout_provider.dart';
import 'widgets/exercise_list_view.dart';
import 'widgets/active_workout_tracker.dart';
import 'widgets/rest_timer_banner.dart';
import '../../../core/theme/theme_tokens.dart';
import '../../../core/extensions/context_extensions.dart';

class WorkoutPage extends ConsumerWidget {
  const WorkoutPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final activeState = ref.watch(activeWorkoutProvider);
    final activeNotifier = ref.read(activeWorkoutProvider.notifier);

    return Scaffold(
      backgroundColor: context.theme.scaffoldBackgroundColor,
      body: SafeArea(
        child: Stack(
          children: [
            Padding(
              padding: const EdgeInsets.only(
                left: GymOSTokens.space16,
                right: GymOSTokens.space16,
                top: GymOSTokens.space16,
                bottom: GymOSTokens.space48,
              ),
              child: activeState.isActive
                  ? DefaultTabController(
                      length: 2,
                      child: Column(
                        children: [
                          TabBar(
                            indicatorColor: const Color(0xFF6366F1),
                            labelColor: Colors.white,
                            unselectedLabelColor: Colors.grey,
                            indicatorSize: TabBarIndicatorSize.tab,
                            dividerColor: Colors.transparent,
                            tabs: const [
                              Tab(
                                icon: Icon(Icons.edit_note),
                                child: Text('Track Session', style: TextStyle(fontWeight: FontWeight.bold)),
                              ),
                              Tab(
                                icon: Icon(Icons.add_circle_outline),
                                child: Text('Add Exercises', style: TextStyle(fontWeight: FontWeight.bold)),
                              ),
                            ],
                          ),
                          const SizedBox(height: GymOSTokens.space16),
                          const Expanded(
                            child: TabBarView(
                              children: [
                                GymOSActiveWorkoutTracker(),
                                GymOSExerciseListView(),
                              ],
                            ),
                          ),
                        ],
                      ),
                    )
                  : Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Training Session',
                                  style: context.textTheme.headlineMedium?.copyWith(
                                    fontWeight: FontWeight.bold,
                                    color: Colors.white,
                                  ),
                                ),
                                Text(
                                  'Ready to hit a new personal record?',
                                  style: context.textTheme.bodyMedium,
                                ),
                              ],
                            ),
                            ElevatedButton.icon(
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color(0xFF6366F1),
                                foregroundColor: Colors.white,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(GymOSTokens.radiusM),
                                ),
                              ),
                              onPressed: () => activeNotifier.startWorkout('Hypertrophy Vol. A'),
                              icon: const Icon(Icons.play_arrow),
                              label: const Text('Quick Start', style: TextStyle(fontWeight: FontWeight.bold)),
                            ),
                          ],
                        ),
                        const SizedBox(height: GymOSTokens.space24),
                        const Expanded(
                          child: GymOSExerciseListView(),
                        ),
                      ],
                    ),
            ),
            
            // Floating Rest Timer
            const GymOSRestTimerBanner(),
          ],
        ),
      ),
    );
  }
}
