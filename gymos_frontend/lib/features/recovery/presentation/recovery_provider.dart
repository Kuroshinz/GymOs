import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../domain/recovery_state.dart';

class RecoveryNotifier extends StateNotifier<RecoveryState> {
  RecoveryNotifier()
      : super(
          const RecoveryState(
            score: 88,
            hrvMs: 78,
            hrvTargetMs: 75,
            sleepScore: 92,
            sleepDurationMinutes: 475, // 7h 55m
            sleepTargetMinutes: 480, // 8h
            stressScore: 18,
            readiness: ReadinessLevel.optimal,
            coachAdvice: 'Excellent recovery profile. Heart rate variability is resting above baseline targets. High neural readiness indicates your body can safely handle peak training stress today.',
            trendHistory: [
              RecoveryTrendPoint(dayName: 'Mon', score: 65),
              RecoveryTrendPoint(dayName: 'Tue', score: 72),
              RecoveryTrendPoint(dayName: 'Wed', score: 85),
              RecoveryTrendPoint(dayName: 'Thu', score: 45),
              RecoveryTrendPoint(dayName: 'Fri', score: 90),
              RecoveryTrendPoint(dayName: 'Sat', score: 88),
              RecoveryTrendPoint(dayName: 'Sun', score: 82),
            ],
          ),
        );
}

final recoveryProvider = StateNotifierProvider<RecoveryNotifier, RecoveryState>((ref) {
  return RecoveryNotifier();
});
