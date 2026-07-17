import 'package:flutter/material.dart';
import '../../../core/theme/theme_tokens.dart';
import '../../../core/widgets/glass_card.dart';
import '../../../core/extensions/context_extensions.dart';

class NutritionPage extends StatelessWidget {
  const NutritionPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: context.theme.scaffoldBackgroundColor,
      appBar: AppBar(
        title: const Text('Nutrition Log'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(GymOSTokens.space16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            GymOSGlassCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Daily Balance',
                    style: context.textTheme.headlineMedium,
                  ),
                  const SizedBox(height: GymOSTokens.space8),
                  Text(
                    'Track macros & calorie budget',
                    style: context.textTheme.bodyMedium,
                  ),
                  const SizedBox(height: GymOSTokens.space16),
                  const LinearProgressIndicator(
                    value: 0.65,
                    color: Color(0xFF6366F1),
                    backgroundColor: Color(0xFF1F2035),
                  ),
                  const SizedBox(height: GymOSTokens.space12),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('1,625 / 2,500 kcal', style: context.textTheme.bodyLarge),
                      Text('65% Completed', style: context.textTheme.bodySmall),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
