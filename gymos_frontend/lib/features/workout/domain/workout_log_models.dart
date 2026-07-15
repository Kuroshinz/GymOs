class WorkoutSessionLog {
  final String id;
  final String programId;
  final DateTime startTime;
  final DateTime? endTime;
  final List<ExerciseLog> exercises;

  const WorkoutSessionLog({
    required this.id,
    required this.programId,
    required this.startTime,
    this.endTime,
    required this.exercises,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'program_id': programId,
      'start_time': startTime.toIso8601String(),
      'end_time': endTime?.toIso8601String(),
      'exercises': exercises.map((e) => e.toJson()).toList(),
    };
  }

  factory WorkoutSessionLog.fromJson(Map<String, dynamic> json) {
    return WorkoutSessionLog(
      id: json['id'] as String,
      programId: json['program_id'] as String,
      startTime: DateTime.parse(json['start_time'] as String),
      endTime: json['end_time'] != null ? DateTime.parse(json['end_time'] as String) : null,
      exercises: (json['exercises'] as List<dynamic>)
          .map((e) => ExerciseLog.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}

class ExerciseLog {
  final String exerciseId;
  final String exerciseName;
  final List<SetLog> sets;

  const ExerciseLog({
    required this.exerciseId,
    required this.exerciseName,
    required this.sets,
  });

  Map<String, dynamic> toJson() {
    return {
      'exercise_id': exerciseId,
      'exercise_name': exerciseName,
      'sets': sets.map((s) => s.toJson()).toList(),
    };
  }

  factory ExerciseLog.fromJson(Map<String, dynamic> json) {
    return ExerciseLog(
      exerciseId: json['exercise_id'] as String,
      exerciseName: json['exercise_name'] as String,
      sets: (json['sets'] as List<dynamic>)
          .map((s) => SetLog.fromJson(s as Map<String, dynamic>))
          .toList(),
    );
  }
}

class SetLog {
  final int setNumber;
  final double weight;
  final int reps;
  final int rir;
  final bool isCompleted;

  const SetLog({
    required this.setNumber,
    required this.weight,
    required this.reps,
    required this.rir,
    required this.isCompleted,
  });

  Map<String, dynamic> toJson() {
    return {
      'set_number': setNumber,
      'weight': weight,
      'reps': reps,
      'rir': rir,
      'is_completed': isCompleted,
    };
  }

  factory SetLog.fromJson(Map<String, dynamic> json) {
    return SetLog(
      setNumber: json['set_number'] as int,
      weight: (json['weight'] as num).toDouble(),
      reps: json['reps'] as int,
      rir: json['rir'] as int,
      isCompleted: json['is_completed'] as bool,
    );
  }
}
