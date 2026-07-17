import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'recovery_provider.dart';
import 'widgets/recovery_radial_gauge.dart';
import 'widgets/recovery_trend_chart.dart';
import '../../../core/theme/theme_tokens.dart';
import '../../../core/extensions/context_extensions.dart';
import '../../../core/widgets/metric_card.dart';
import '../../../core/widgets/glass_card.dart';

class RecoveryPage extends ConsumerWidget {
  const RecoveryPage({super.key});

  String _formatSleep(int totalMinutes) {
    final hours = totalMinutes ~/ 60;
    final mins = totalMinutes % 60;
    return '${hours}h ${mins}m';
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(recoveryProvider);

    return Scaffold(
      backgroundColor: context.theme.scaffoldBackgroundColor,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(GymOSTokens.space24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Recovery & Readiness',
                    style: context.textTheme.headlineMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  Text(
                    'Monitor nervous system stress and sleep metrics.',
                    style: context.textTheme.bodyMedium,
                  ),
                ],
              ),
              const SizedBox(height: GymOSTokens.space24),

              // Responsive Top Area (Radial Gauge + Coach Advice)
              if (context.isMobile) ...[
                Center(
                  child: GymOSRecoveryRadialGauge(
                    score: state.score,
                    color: state.readiness.color,
                  ),
                ),
                const SizedBox(height: GymOSTokens.space24),
                _buildCoachAdvice(context, state.coachAdvice),
              ] else
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      flex: 4,
                      child: Center(
                        child: GymOSRecoveryRadialGauge(
                          score: state.score,
                          color: state.readiness.color,
                        ),
                      ),
                    ),
                    const SizedBox(width: GymOSTokens.space24),
                    Expanded(
                      flex: 6,
                      child: _buildCoachAdvice(context, state.coachAdvice),
                    ),
                  ],
                ),
              const SizedBox(height: GymOSTokens.space24),

              // Metrics Grid (HRV, Sleep, Stress, Readiness)
              GridView.count(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                crossAxisCount: context.isMobile ? 2 : 4,
                crossAxisSpacing: GymOSTokens.space16,
                mainAxisSpacing: GymOSTokens.space16,
                childAspectRatio: context.isMobile ? 1.25 : 1.35,
                children: [
                  GymOSMetricCard(
                    title: 'HRV',
                    value: '${state.hrvMs}',
                    unit: 'ms',
                    icon: Icons.favorite_border,
                    iconColor: const Color(0xFF6366F1),
                    bottomWidget: Text(
                      'Target: ${state.hrvTargetMs} ms',
                      style: const TextStyle(fontSize: 10, color: Colors.grey),
                    ),
                  ),
                  GymOSMetricCard(
                    title: 'Sleep Log',
                    value: _formatSleep(state.sleepDurationMinutes),
                    unit: 'logged',
                    icon: Icons.bedtime_outlined,
                    iconColor: const Color(0xFF8B5CF6),
                    bottomWidget: Text(
                      'Score: ${state.sleepScore}%',
                      style: const TextStyle(fontSize: 10, color: Colors.grey),
                    ),
                  ),
                  GymOSMetricCard(
                    title: 'Stress Index',
                    value: '${state.stressScore}',
                    unit: '/100',
                    icon: Icons.bolt,
                    iconColor: Colors.orange,
                    bottomWidget: const Text(
                      'Low physiological load',
                      style: TextStyle(fontSize: 10, color: Colors.grey),
                    ),
                  ),
                  GymOSMetricCard(
                    title: 'Readiness State',
                    value: state.readiness.label,
                    unit: 'level',
                    icon: Icons.health_and_safety_outlined,
                    iconColor: state.readiness.color,
                    bottomWidget: ClipRRect(
                      borderRadius: BorderRadius.circular(GymOSTokens.radiusS),
                      child: LinearProgressIndicator(
                        value: state.score / 100.0,
                        minHeight: 4,
                        backgroundColor: const Color(0xFF1F2035),
                        color: state.readiness.color,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: GymOSTokens.space24),

              // Weekly Trend Chart
              GymOSRecoveryTrendChart(trendHistory: state.trendHistory),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildCoachAdvice(BuildContext context, String advice) {
    return GymOSGlassCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.psychology, color: Color(0xFF10B981), size: 22),
              const SizedBox(width: GymOSTokens.space8),
              Text(
                'AI Coach Guidance',
                style: context.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
            ],
          ),
          const SizedBox(height: GymOSTokens.space12),
          Text(
            advice,
            style: context.textTheme.bodyMedium?.copyWith(
              color: context.colorScheme.onSurface.withOpacity(0.7),
              height: 1.4,
            ),
          ),
        ],
      ),
    );
  }
}
