import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../workout_provider.dart';
import '../../../../core/theme/theme_tokens.dart';
import '../../../../core/widgets/glass_card.dart';
import '../../../../core/extensions/context_extensions.dart';

class GymOSExerciseListView extends ConsumerWidget {
  const GymOSExerciseListView({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final catalog = ref.watch(exerciseCatalogProvider);
    final activeState = ref.watch(activeWorkoutProvider);
    final activeNotifier = ref.read(activeWorkoutProvider.notifier);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Exercises Catalog',
                  style: context.textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                Text(
                  'Select moves to add to your session',
                  style: context.textTheme.bodyMedium,
                ),
              ],
            ),
            if (!activeState.isActive)
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF6366F1),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(GymOSTokens.radiusM),
                  ),
                ),
                onPressed: () => activeNotifier.startWorkout('Active GymOS Session'),
                icon: const Icon(Icons.play_arrow),
                label: const Text('Start Workout', style: TextStyle(fontWeight: FontWeight.bold)),
              ),
          ],
        ),
        const SizedBox(height: GymOSTokens.space24),
        Expanded(
          child: ListView.builder(
            itemCount: catalog.length,
            itemBuilder: (context, index) {
              final exercise = catalog[index];
              final isAlreadyAdded = activeState.exercises.any((e) => e.exercise.id == exercise.id);

              return Padding(
                padding: const EdgeInsets.only(bottom: GymOSTokens.space12),
                child: GymOSGlassCard(
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Text(
                                  exercise.name,
                                  style: context.textTheme.titleMedium?.copyWith(
                                    fontWeight: FontWeight.bold,
                                    color: Colors.white,
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: const Color(0xFF1F2035),
                                    borderRadius: BorderRadius.circular(GymOSTokens.radiusS),
                                  ),
                                  child: Text(
                                    exercise.category,
                                    style: const TextStyle(fontSize: 10, color: Colors.grey),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: GymOSTokens.space4),
                            Text(
                              'Target: ${exercise.targetMuscle}',
                              style: context.textTheme.bodyMedium?.copyWith(
                                color: context.colorScheme.onSurface.withOpacity(0.5),
                              ),
                            ),
                            const SizedBox(height: GymOSTokens.space8),
                            Row(
                              children: [
                                const Icon(Icons.history, size: 14, color: Colors.grey),
                                const SizedBox(width: 4),
                                Text(
                                  'Prev: ${exercise.previousPerformance}',
                                  style: context.textTheme.bodySmall,
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                      if (activeState.isActive)
                        IconButton(
                          onPressed: isAlreadyAdded
                              ? null
                              : () {
                                  activeNotifier.addExercise(exercise);
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    SnackBar(
                                      content: Text('${exercise.name} added to session.'),
                                      backgroundColor: const Color(0xFF10B981),
                                      duration: const Duration(seconds: 1),
                                    ),
                                  );
                                },
                          icon: Icon(
                            isAlreadyAdded ? Icons.check_circle : Icons.add_circle_outline,
                            color: isAlreadyAdded ? const Color(0xFF10B981) : const Color(0xFF6366F1),
                            size: 28,
                          ),
                        ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }
}
