import 'package:flutter/material.dart';
import '../../../../core/theme/theme_tokens.dart';
import '../../../../core/widgets/glass_card.dart';
import '../../../../core/extensions/context_extensions.dart';

class GymOSCoachInsightCard extends StatelessWidget {
  final String recommendation;
  final String description;

  const GymOSCoachInsightCard({
    super.key,
    required this.recommendation,
    required this.description,
  });

  @override
  Widget build(BuildContext context) {
    return GymOSGlassCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.psychology, color: Color(0xFF10B981), size: 22),
              const SizedBox(width: GymOSTokens.space8),
              Text(
                'AI Coach Insight',
                style: context.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
            ],
          ),
          const SizedBox(height: GymOSTokens.space12),
          Text(
            recommendation,
            style: context.textTheme.titleMedium?.copyWith(
              color: const Color(0xFF10B981),
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: GymOSTokens.space8),
          Text(
            description,
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
