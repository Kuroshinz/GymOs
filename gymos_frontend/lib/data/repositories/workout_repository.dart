import '../models/workout_model.dart';

abstract class WorkoutRepository {
  Future<List<WorkoutModel>> getPastWorkouts();
  Future<void> saveWorkout(WorkoutModel workout);
}
