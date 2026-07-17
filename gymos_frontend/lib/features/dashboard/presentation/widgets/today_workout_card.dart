import 'package:flutter/material.dart';
import '../../../../core/theme/theme_tokens.dart';
import '../../../../core/widgets/glass_card.dart';
import '../../../../core/extensions/context_extensions.dart';

class GymOSTodayWorkoutCard extends StatelessWidget {
  final String title;
  final String subTitle;
  final int totalSets;
  final int estimatedMinutes;
  final String muscleFocus;

  const GymOSTodayWorkoutCard({
    super.key,
    required this.title,
    required this.subTitle,
    required this.totalSets,
    required this.estimatedMinutes,
    required this.muscleFocus,
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
                "Today's Active Workout",
                style: context.textTheme.titleMedium?.copyWith(
                  color: context.colorScheme.onSurface.withOpacity(0.6),
                ),
              ),
              const Icon(Icons.fitness_center, color: Color(0xFF6366F1), size: 20),
            ],
          ),
          const SizedBox(height: GymOSTokens.space16),
          Text(
            title,
            style: context.textTheme.headlineSmall?.copyWith(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
          Text(
            subTitle,
            style: context.textTheme.bodyMedium?.copyWith(
              color: context.colorScheme.onSurface.withOpacity(0.5),
            ),
          ),
          const SizedBox(height: GymOSTokens.space16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildWorkoutMetric(context, '$totalSets Sets', 'Intensity target'),
              _buildWorkoutMetric(context, '$estimatedMinutes mins', 'Estimated time'),
              _buildWorkoutMetric(context, muscleFocus, 'Primary focus'),
            ],
          ),
          const SizedBox(height: GymOSTokens.space16),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF6366F1),
              foregroundColor: Colors.white,
              elevation: 0,
              minimumSize: const Size(double.infinity, 44),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(GymOSTokens.radiusM),
              ),
            ),
            onPressed: () {},
            child: const Text('Start Training Session', style: TextStyle(fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }

  Widget _buildWorkoutMetric(BuildContext context, String value, String description) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          value,
          style: context.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        Text(
          description,
          style: context.textTheme.bodySmall?.copyWith(
            color: context.colorScheme.onSurface.withOpacity(0.4),
          ),
        ),
      ],
    );
  }
}
