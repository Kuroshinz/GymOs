import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../domain/workout_state.dart';

final exerciseCatalogProvider = Provider<List<WorkoutExercise>>((ref) {
  return const [
    WorkoutExercise(
      id: 'ex-1',
      name: 'Incline Barbell Bench Press',
      targetMuscle: 'Upper Chest',
      category: 'Compound',
      previousPerformance: '80 kg x 8 reps, 3 sets',
    ),
    WorkoutExercise(
      id: 'ex-2',
      name: 'Weighted Pull-Up',
      targetMuscle: 'Lats & Back',
      category: 'Compound',
      previousPerformance: 'Bodyweight + 15 kg x 6 reps, 4 sets',
    ),
    WorkoutExercise(
      id: 'ex-3',
      name: 'Bulgarian Split Squat',
      targetMuscle: 'Quads & Glutes',
      category: 'Unilateral',
      previousPerformance: '24 kg DBs x 10 reps, 3 sets',
    ),
    WorkoutExercise(
      id: 'ex-4',
      name: 'Dumbbell Lateral Raise',
      targetMuscle: 'Lateral Delts',
      category: 'Isolation',
      previousPerformance: '15 kg DBs x 12 reps, 4 sets',
    ),
    WorkoutExercise(
      id: 'ex-5',
      name: 'Incline Dumbbell Curl',
      targetMuscle: 'Biceps',
      category: 'Isolation',
      previousPerformance: '14 kg DBs x 10 reps, 3 sets',
    ),
  ];
});

class ActiveWorkoutNotifier extends StateNotifier<ActiveWorkoutState> {
  Timer? _ticker;

  ActiveWorkoutNotifier() : super(const ActiveWorkoutState(exercises: []));

  void startWorkout(String title) {
    state = ActiveWorkoutState(
      workoutTitle: title,
      exercises: [],
      elapsedSeconds: 0,
      restTimeRemaining: 0,
      isRestTimerActive: false,
    );
    _startTicker();
  }

  void endWorkout() {
    _ticker?.cancel();
    state = state.copyWith(clearWorkout: true);
  }

  void addExercise(WorkoutExercise exercise) {
    final activeEx = ActiveExerciseState(
      exercise: exercise,
      sets: [
        ActiveSet(
          id: 'set-${DateTime.now().millisecondsSinceEpoch}-1',
          setNumber: 1,
          weight: 0.0,
          reps: 0,
          rir: 2,
          isCompleted: false,
        )
      ],
    );
    state = state.copyWith(
      exercises: [...state.exercises, activeEx],
    );
  }

  void removeExercise(String exerciseId) {
    state = state.copyWith(
      exercises: state.exercises.where((e) => e.exercise.id != exerciseId).toList(),
    );
  }

  void addSet(String exerciseId) {
    state = state.copyWith(
      exercises: state.exercises.map((e) {
        if (e.exercise.id != exerciseId) return e;
        final nextSetNum = e.sets.length + 1;
        final lastSet = e.sets.isNotEmpty ? e.sets.last : null;
        final newSet = ActiveSet(
          id: 'set-${DateTime.now().millisecondsSinceEpoch}-$nextSetNum',
          setNumber: nextSetNum,
          weight: lastSet?.weight ?? 0.0,
          reps: lastSet?.reps ?? 0,
          rir: lastSet?.rir ?? 2,
          isCompleted: false,
        );
        return e.copyWith(sets: [...e.sets, newSet]);
      }).toList(),
    );
  }

  void removeSet(String exerciseId, String setId) {
    state = state.copyWith(
      exercises: state.exercises.map((e) {
        if (e.exercise.id != exerciseId) return e;
        final filtered = e.sets.where((s) => s.id != setId).toList();
        // Re-number sets
        final renumbered = List<ActiveSet>.generate(filtered.length, (index) {
          return filtered[index].copyWith(setNumber: index + 1);
        });
        return e.copyWith(sets: renumbered);
      }).toList(),
    );
  }

  void updateSetMetrics(
    String exerciseId,
    String setId, {
    double? weight,
    int? reps,
    int? rir,
  }) {
    state = state.copyWith(
      exercises: state.exercises.map((e) {
        if (e.exercise.id != exerciseId) return e;
        return e.copyWith(
          sets: e.sets.map((s) {
            if (s.id != setId) return s;
            return s.copyWith(
              weight: weight,
              reps: reps,
              rir: rir,
            );
          }).toList(),
        );
      }).toList(),
    );
  }

  void toggleSetComplete(String exerciseId, String setId) {
    state = state.copyWith(
      exercises: state.exercises.map((e) {
        if (e.exercise.id != exerciseId) return e;
        return e.copyWith(
          sets: e.sets.map((s) {
            if (s.id != setId) return s;
            final nextState = !s.isCompleted;
            if (nextState) {
              // Trigger rest timer
              startRestTimer(state.targetRestSeconds);
            }
            return s.copyWith(isCompleted: nextState);
          }).toList(),
        );
      }).toList(),
    );
  }

  void startRestTimer(int durationSeconds) {
    state = state.copyWith(
      restTimeRemaining: durationSeconds,
      isRestTimerActive: true,
      targetRestSeconds: durationSeconds,
    );
  }

  void skipRestTimer() {
    state = state.copyWith(
      restTimeRemaining: 0,
      isRestTimerActive: false,
    );
  }

  void adjustRestTimer(int deltaSeconds) {
    final nextVal = (state.restTimeRemaining + deltaSeconds).clamp(0, 999);
    state = state.copyWith(
      restTimeRemaining: nextVal,
      isRestTimerActive: nextVal > 0,
    );
  }

  void _startTicker() {
    _ticker?.cancel();
    _ticker = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (state.workoutTitle == null) {
        timer.cancel();
        return;
      }
      
      int nextElapsed = state.elapsedSeconds + 1;
      int nextRest = state.restTimeRemaining;
      bool restActive = state.isRestTimerActive;

      if (restActive && nextRest > 0) {
        nextRest -= 1;
        if (nextRest == 0) {
          restActive = false;
        }
      }

      state = state.copyWith(
        elapsedSeconds: nextElapsed,
        restTimeRemaining: nextRest,
        isRestTimerActive: restActive,
      );
    });
  }

  @override
  void dispose() {
    _ticker?.cancel();
    super.dispose();
  }
}

final activeWorkoutProvider = StateNotifierProvider<ActiveWorkoutNotifier, ActiveWorkoutState>((ref) {
  return ActiveWorkoutNotifier();
});
