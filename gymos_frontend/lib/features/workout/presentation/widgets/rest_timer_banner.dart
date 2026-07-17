import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../workout_provider.dart';
import '../../../../core/theme/theme_tokens.dart';
import '../../../../core/widgets/glass_card.dart';
import '../../../../core/extensions/context_extensions.dart';

class GymOSRestTimerBanner extends ConsumerWidget {
  const GymOSRestTimerBanner({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(activeWorkoutProvider);
    final notifier = ref.read(activeWorkoutProvider.notifier);

    if (!state.isRestTimerActive || state.restTimeRemaining <= 0) {
      return const SizedBox.shrink();
    }

    final minutes = state.restTimeRemaining ~/ 60;
    final seconds = state.restTimeRemaining % 60;
    final progress = (state.restTimeRemaining / state.targetRestSeconds).clamp(0.0, 1.0);

    return Align(
      alignment: Alignment.bottomCenter,
      child: Padding(
        padding: const EdgeInsets.all(GymOSTokens.space16),
        child: GymOSGlassCard(
          borderRadius: BorderRadius.circular(GymOSTokens.radiusXL),
          border: Border.all(
            color: const Color(0xFF10B981).withOpacity(0.4),
            width: 1.5,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.notifications_active, color: Color(0xFF10B981), size: 20),
                      const SizedBox(width: 8),
                      Text(
                        'Rest Timer Active',
                        style: context.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                    ],
                  ),
                  Text(
                    '${minutes.toString().padLeft(2, '0')}:${seconds.toString().padLeft(2, '0')}',
                    style: context.textTheme.headlineMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      fontFamily: 'monospace',
                      color: const Color(0xFF10B981),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: GymOSTokens.space12),
              ClipRRect(
                borderRadius: BorderRadius.circular(GymOSTokens.radiusS),
                child: LinearProgressIndicator(
                  value: progress,
                  minHeight: 4,
                  backgroundColor: const Color(0xFF1F2035),
                  color: const Color(0xFF10B981),
                ),
              ),
              const SizedBox(height: GymOSTokens.space12),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      TextButton(
                        onPressed: () => notifier.adjustRestTimer(-10),
                        child: const Text('-10s', style: TextStyle(color: Colors.grey)),
                      ),
                      TextButton(
                        onPressed: () => notifier.adjustRestTimer(10),
                        child: const Text('+10s', style: TextStyle(color: Colors.grey)),
                      ),
                    ],
                  ),
                  ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF1F2035),
                      foregroundColor: Colors.white,
                      elevation: 0,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(GymOSTokens.radiusM),
                      ),
                    ),
                    onPressed: () => notifier.skipRestTimer(),
                    child: const Text('Skip Rest', style: TextStyle(fontWeight: FontWeight.bold)),
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
