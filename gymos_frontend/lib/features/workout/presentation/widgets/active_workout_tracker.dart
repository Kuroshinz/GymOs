import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../workout_provider.dart';
import '../../../../core/theme/theme_tokens.dart';
import '../../../../core/widgets/glass_card.dart';
import '../../../../core/extensions/context_extensions.dart';

class GymOSActiveWorkoutTracker extends ConsumerWidget {
  const GymOSActiveWorkoutTracker({super.key});

  String _formatDuration(int totalSeconds) {
    final hours = totalSeconds ~/ 3600;
    final minutes = (totalSeconds % 3600) ~/ 60;
    final seconds = totalSeconds % 60;
    if (hours > 0) {
      return '$hours:${minutes.toString().padLeft(2, '0')}:${seconds.toString().padLeft(2, '0')}';
    }
    return '${minutes.toString().padLeft(2, '0')}:${seconds.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(activeWorkoutProvider);
    final notifier = ref.read(activeWorkoutProvider.notifier);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Workout Header
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  state.workoutTitle ?? 'Active Session',
                  style: context.textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                Row(
                  children: [
                    const Icon(Icons.timer_outlined, size: 14, color: Colors.grey),
                    const SizedBox(width: 4),
                    Text(
                      _formatDuration(state.elapsedSeconds),
                      style: context.textTheme.bodyMedium?.copyWith(
                        fontFamily: 'monospace',
                        color: const Color(0xFF6366F1),
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFFEF4444),
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(GymOSTokens.radiusM),
                ),
              ),
              onPressed: () => notifier.endWorkout(),
              child: const Text('End Session', style: TextStyle(fontWeight: FontWeight.bold)),
            ),
          ],
        ),
        const SizedBox(height: GymOSTokens.space20),
        
        // Active Exercises List
        Expanded(
          child: state.exercises.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.add_task, size: 48, color: context.colorScheme.onSurface.withOpacity(0.2)),
                      const SizedBox(height: 12),
                      const Text(
                        'No exercises added yet.',
                        style: TextStyle(color: Colors.grey),
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        'Tap the "+" icon in the catalog tab below.',
                        style: TextStyle(color: Colors.grey, fontSize: 12),
                      ),
                    ],
                  ),
                )
              : ListView.builder(
                  itemCount: state.exercises.length,
                  itemBuilder: (context, exIndex) {
                    final exState = state.exercises[exIndex];
                    
                    return Dismissible(
                      key: Key(exState.exercise.id),
                      direction: DismissDirection.endToStart,
                      onDismissed: (_) {
                        notifier.removeExercise(exState.exercise.id);
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text('Removed ${exState.exercise.name}'),
                            backgroundColor: const Color(0xFFEF4444),
                            duration: const Duration(seconds: 1),
                          ),
                        );
                      },
                      background: Container(
                        alignment: Alignment.centerRight,
                        padding: const EdgeInsets.only(right: 20),
                        decoration: BoxDecoration(
                          color: const Color(0xFFEF4444).withOpacity(0.15),
                          borderRadius: BorderRadius.circular(GymOSTokens.radiusL),
                        ),
                        child: const Icon(Icons.delete, color: Color(0xFFEF4444)),
                      ),
                      child: Padding(
                        padding: const EdgeInsets.only(bottom: GymOSTokens.space16),
                        child: GymOSGlassCard(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              // Exercise Title
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          exState.exercise.name,
                                          style: context.textTheme.titleMedium?.copyWith(
                                            fontWeight: FontWeight.bold,
                                            color: Colors.white,
                                          ),
                                        ),
                                        Text(
                                          exState.exercise.targetMuscle,
                                          style: const TextStyle(fontSize: 12, color: Colors.grey),
                                        ),
                                      ],
                                    ),
                                  ),
                                  IconButton(
                                    onPressed: () => notifier.addSet(exState.exercise.id),
                                    icon: const Icon(Icons.add_circle, color: Color(0xFF6366F1)),
                                  ),
                                ],
                              ),
                              const SizedBox(height: GymOSTokens.space8),
                              
                              // Table Header
                              const Row(
                                children: [
                                  SizedBox(width: 32, child: Text('SET', style: TextStyle(color: Colors.grey, fontSize: 11, fontWeight: FontWeight.bold))),
                                  Expanded(flex: 3, child: Text('PREV', style: TextStyle(color: Colors.grey, fontSize: 11, fontWeight: FontWeight.bold))),
                                  Expanded(flex: 2, child: Text('KG', style: TextStyle(color: Colors.grey, fontSize: 11, fontWeight: FontWeight.bold))),
                                  Expanded(flex: 2, child: Text('REPS', style: TextStyle(color: Colors.grey, fontSize: 11, fontWeight: FontWeight.bold))),
                                  Expanded(flex: 2, child: Text('RIR', style: TextStyle(color: Colors.grey, fontSize: 11, fontWeight: FontWeight.bold))),
                                  SizedBox(width: 40),
                                ],
                              ),
                              const Divider(color: Color(0xFF1F2035), height: 16),
                              
                              // Sets
                              ...exState.sets.map((set) {
                                return Dismissible(
                                  key: Key(set.id),
                                  direction: DismissDirection.endToStart,
                                  onDismissed: (_) {
                                    notifier.removeSet(exState.exercise.id, set.id);
                                  },
                                  background: Container(
                                    alignment: Alignment.centerRight,
                                    padding: const EdgeInsets.only(right: 12),
                                    color: const Color(0xFFEF4444).withOpacity(0.12),
                                    child: const Icon(Icons.delete, color: Color(0xFFEF4444), size: 18),
                                  ),
                                  child: Container(
                                    height: 48,
                                    padding: const EdgeInsets.symmetric(vertical: 4),
                                    child: Row(
                                      children: [
                                        // Set Number
                                        SizedBox(
                                          width: 32,
                                          child: Text(
                                            '${set.setNumber}',
                                            style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white),
                                          ),
                                        ),
                                        // Previous Performance
                                        Expanded(
                                          flex: 3,
                                          child: Text(
                                            exState.exercise.previousPerformance.split(',').first,
                                            style: const TextStyle(color: Colors.grey, fontSize: 12),
                                            overflow: TextOverflow.ellipsis,
                                          ),
                                        ),
                                        // Weight Input
                                        Expanded(
                                          flex: 2,
                                          child: Padding(
                                            padding: const EdgeInsets.symmetric(horizontal: 4),
                                            child: TextFormField(
                                              initialValue: set.weight > 0 ? '${set.weight}' : '',
                                              keyboardType: TextInputType.number,
                                              style: const TextStyle(color: Colors.white, fontSize: 13),
                                              decoration: InputDecoration(
                                                hintText: '0',
                                                hintStyle: const TextStyle(color: Colors.grey),
                                                isDense: true,
                                                contentPadding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
                                                border: OutlineInputBorder(
                                                  borderRadius: BorderRadius.circular(GymOSTokens.radiusS),
                                                  borderSide: const BorderSide(color: Color(0xFF1F2035)),
                                                ),
                                              ),
                                              onChanged: (val) {
                                                final weight = double.tryParse(val) ?? 0.0;
                                                notifier.updateSetMetrics(exState.exercise.id, set.id, weight: weight);
                                              },
                                            ),
                                          ),
                                        ),
                                        // Reps Input
                                        Expanded(
                                          flex: 2,
                                          child: Padding(
                                            padding: const EdgeInsets.symmetric(horizontal: 4),
                                            child: TextFormField(
                                              initialValue: set.reps > 0 ? '${set.reps}' : '',
                                              keyboardType: TextInputType.number,
                                              style: const TextStyle(color: Colors.white, fontSize: 13),
                                              decoration: InputDecoration(
                                                hintText: '0',
                                                hintStyle: const TextStyle(color: Colors.grey),
                                                isDense: true,
                                                contentPadding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
                                                border: OutlineInputBorder(
                                                  borderRadius: BorderRadius.circular(GymOSTokens.radiusS),
                                                  borderSide: const BorderSide(color: Color(0xFF1F2035)),
                                                ),
                                              ),
                                              onChanged: (val) {
                                                final reps = int.tryParse(val) ?? 0;
                                                notifier.updateSetMetrics(exState.exercise.id, set.id, reps: reps);
                                              },
                                            ),
                                          ),
                                        ),
                                        // RIR Input
                                        Expanded(
                                          flex: 2,
                                          child: Padding(
                                            padding: const EdgeInsets.symmetric(horizontal: 4),
                                            child: TextFormField(
                                              initialValue: '${set.rir}',
                                              keyboardType: TextInputType.number,
                                              style: const TextStyle(color: Colors.white, fontSize: 13),
                                              decoration: InputDecoration(
                                                hintText: '2',
                                                isDense: true,
                                                contentPadding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
                                                border: OutlineInputBorder(
                                                  borderRadius: BorderRadius.circular(GymOSTokens.radiusS),
                                                  borderSide: const BorderSide(color: Color(0xFF1F2035)),
                                                ),
                                              ),
                                              onChanged: (val) {
                                                final rir = int.tryParse(val) ?? 2;
                                                notifier.updateSetMetrics(exState.exercise.id, set.id, rir: rir);
                                              },
                                            ),
                                          ),
                                        ),
                                        // Check Icon
                                        SizedBox(
                                          width: 40,
                                          child: IconButton(
                                            icon: Icon(
                                              set.isCompleted ? Icons.check_box : Icons.check_box_outline_blank,
                                              color: set.isCompleted ? const Color(0xFF10B981) : Colors.grey,
                                              size: 22,
                                            ),
                                            onPressed: () {
                                              notifier.toggleSetComplete(exState.exercise.id, set.id);
                                            },
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                );
                              }),
                            ],
                          ),
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
