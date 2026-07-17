import 'package:flutter/material.dart';
import '../../../../core/theme/theme_tokens.dart';
import '../../../../core/extensions/context_extensions.dart';

class GymOSGreetingWidget extends StatelessWidget {
  final String athleteName;
  final int athleteLevel;
  final int streakDays;

  const GymOSGreetingWidget({
    super.key,
    required this.athleteName,
    required this.athleteLevel,
    required this.streakDays,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Good morning,',
              style: context.textTheme.bodyLarge?.copyWith(
                color: context.colorScheme.onSurface.withOpacity(0.6),
              ),
            ),
            Text(
              athleteName,
              style: context.textTheme.headlineMedium?.copyWith(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        Container(
          padding: const EdgeInsets.symmetric(
            horizontal: GymOSTokens.space12,
            vertical: GymOSTokens.space8,
          ),
          decoration: BoxDecoration(
            color: const Color(0xFF6366F1).withOpacity(0.12),
            borderRadius: BorderRadius.circular(GymOSTokens.radiusM),
            border: Border.all(
              color: const Color(0xFF6366F1).withOpacity(0.3),
            ),
          ),
          child: Row(
            children: [
              const Icon(Icons.local_fire_department, color: Colors.orange, size: 20),
              const SizedBox(width: GymOSTokens.space8),
              Text(
                '$streakDays Day Streak',
                style: context.textTheme.bodyMedium?.copyWith(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
