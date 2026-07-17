import 'package:flutter/material.dart';
import '../../domain/recovery_state.dart';
import '../../../../core/theme/theme_tokens.dart';
import '../../../../core/widgets/glass_card.dart';
import '../../../../core/extensions/context_extensions.dart';

class GymOSRecoveryTrendChart extends StatelessWidget {
  final List<RecoveryTrendPoint> trendHistory;

  const GymOSRecoveryTrendChart({
    super.key,
    required this.trendHistory,
  });

  @override
  Widget build(BuildContext context) {
    return GymOSGlassCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                '7-Day Recovery Trend',
                style: context.textTheme.titleMedium?.copyWith(
                  color: context.colorScheme.onSurface.withOpacity(0.6),
                ),
              ),
              const Icon(Icons.show_chart, color: Color(0xFF6366F1), size: 20),
            ],
          ),
          const SizedBox(height: GymOSTokens.space24),
          SizedBox(
            height: 140,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              crossAxisAlignment: CrossAxisAlignment.end,
              children: trendHistory.map((point) {
                final heightFactor = (point.score / 100.0).clamp(0.1, 1.0);
                
                // Color mapping: green for high, amber for mod, red for low recovery
                Color barColor = const Color(0xFFEF4444);
                if (point.score >= 67) {
                  barColor = const Color(0xFF10B981);
                } else if (point.score >= 34) {
                  barColor = const Color(0xFFF59E0B);
                }

                return Expanded(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      Expanded(
                        child: TweenAnimationBuilder<double>(
                          tween: Tween<double>(begin: 0.0, end: heightFactor),
                          duration: GymOSTokens.durationSlow,
                          curve: Curves.easeOutCubic,
                          builder: (context, value, child) {
                            return FractionallySizedBox(
                              heightFactor: value,
                              widthFactor: 0.4,
                              child: Container(
                                decoration: BoxDecoration(
                                  color: barColor,
                                  borderRadius: BorderRadius.circular(GymOSTokens.radiusS),
                                  boxShadow: [
                                    BoxShadow(
                                      color: barColor.withOpacity(0.2),
                                      blurRadius: 6,
                                      offset: const Offset(0, 2),
                                    ),
                                  ],
                                ),
                              ),
                            );
                          },
                        ),
                      ),
                      const SizedBox(height: GymOSTokens.space8),
                      Text(
                        point.dayName,
                        style: context.textTheme.bodySmall?.copyWith(
                          color: context.colorScheme.onSurface.withOpacity(0.5),
                        ),
                      ),
                    ],
                  ),
                );
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }
}
