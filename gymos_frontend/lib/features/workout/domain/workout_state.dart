import 'package:flutter/material.dart';

@immutable
class WorkoutExercise {
  final String id;
  final String name;
  final String targetMuscle;
  final String category;
  final String previousPerformance;

  const WorkoutExercise({
    required this.id,
    required this.name,
    required this.targetMuscle,
    required this.category,
    required this.previousPerformance,
  });
}

@immutable
class ActiveSet {
  final String id;
  final int setNumber;
  final double weight;
  final int reps;
  final int rir;
  final bool isCompleted;

  const ActiveSet({
    required this.id,
    required this.setNumber,
    required this.weight,
    required this.reps,
    required this.rir,
    required this.isCompleted,
  });

  ActiveSet copyWith({
    String? id,
    int? setNumber,
    double? weight,
    int? reps,
    int? rir,
    bool? isCompleted,
  }) {
    return ActiveSet(
      id: id ?? this.id,
      setNumber: setNumber ?? this.setNumber,
      weight: weight ?? this.weight,
      reps: reps ?? this.reps,
      rir: rir ?? this.rir,
      isCompleted: isCompleted ?? this.isCompleted,
    );
  }
}

@immutable
class ActiveExerciseState {
  final WorkoutExercise exercise;
  final List<ActiveSet> sets;

  const ActiveExerciseState({
    required this.exercise,
    required this.sets,
  });

  ActiveExerciseState copyWith({
    WorkoutExercise? exercise,
    List<ActiveSet>? sets,
  }) {
    return ActiveExerciseState(
      exercise: exercise ?? this.exercise,
      sets: sets ?? this.sets,
    );
  }
}

@immutable
class ActiveWorkoutState {
  final String? workoutTitle;
  final List<ActiveExerciseState> exercises;
  final int elapsedSeconds;
  final int restTimeRemaining;
  final bool isRestTimerActive;
  final int targetRestSeconds;

  const ActiveWorkoutState({
    this.workoutTitle,
    required this.exercises,
    this.elapsedSeconds = 0,
    this.restTimeRemaining = 0,
    this.isRestTimerActive = false,
    this.targetRestSeconds = 90,
  });

  bool get isActive => workoutTitle != null;

  ActiveWorkoutState copyWith({
    String? workoutTitle,
    List<ActiveExerciseState>? exercises,
    int? elapsedSeconds,
    int? restTimeRemaining,
    bool? isRestTimerActive,
    int? targetRestSeconds,
    bool clearWorkout = false,
  }) {
    return ActiveWorkoutState(
      workoutTitle: clearWorkout ? null : (workoutTitle ?? this.workoutTitle),
      exercises: clearWorkout ? [] : (exercises ?? this.exercises),
      elapsedSeconds: clearWorkout ? 0 : (elapsedSeconds ?? this.elapsedSeconds),
      restTimeRemaining: clearWorkout ? 0 : (restTimeRemaining ?? this.restTimeRemaining),
      isRestTimerActive: clearWorkout ? false : (isRestTimerActive ?? this.isRestTimerActive),
      targetRestSeconds: clearWorkout ? 90 : (targetRestSeconds ?? this.targetRestSeconds),
    );
  }
}
