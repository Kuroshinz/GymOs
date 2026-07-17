import 'package:flutter/material.dart';
import '../../domain/dashboard_state.dart';
import '../../../../core/theme/theme_tokens.dart';
import '../../../../core/widgets/glass_card.dart';
import '../../../../core/extensions/context_extensions.dart';

class GymOSWeeklyProgressChart extends StatelessWidget {
  final List<ProgressDataPoint> data;

  const GymOSWeeklyProgressChart({
    super.key,
    required this.data,
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
                'Weekly Volume Consistency',
                style: context.textTheme.titleMedium?.copyWith(
                  color: context.colorScheme.onSurface.withOpacity(0.6),
                ),
              ),
              const Icon(Icons.bar_chart, color: Color(0xFF6366F1), size: 20),
            ],
          ),
          const SizedBox(height: GymOSTokens.space24),
          SizedBox(
            height: 120,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              crossAxisAlignment: CrossAxisAlignment.end,
              children: data.map((point) {
                return _buildChartBar(context, point);
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildChartBar(BuildContext context, ProgressDataPoint point) {
    final heightFactor = point.volumePercent.clamp(0.05, 1.0);
    final hasWorkout = point.volumePercent > 0.0;

    return Expanded(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          Expanded(
            child: FractionallySizedBox(
              heightFactor: heightFactor,
              widthFactor: 0.45,
              child: Container(
                decoration: BoxDecoration(
                  gradient: hasWorkout
                      ? GymOSTokens.primaryGradient
                      : null,
                  color: hasWorkout ? null : const Color(0xFF1F2035),
                  borderRadius: BorderRadius.circular(GymOSTokens.radiusS),
                ),
              ),
            ),
          ),
          const SizedBox(height: GymOSTokens.space8),
          Text(
            point.dayName,
            style: context.textTheme.bodySmall?.copyWith(
              color: hasWorkout ? Colors.white : context.colorScheme.onSurface.withOpacity(0.4),
              fontWeight: hasWorkout ? FontWeight.bold : FontWeight.normal,
            ),
          ),
        ],
      ),
    );
  }
}
