import 'package:flutter/material.dart';
import '../../../../core/theme/theme_tokens.dart';
import '../../../../core/widgets/glass_card.dart';
import '../../../../core/extensions/context_extensions.dart';

class GymOSNutritionSummaryCard extends StatelessWidget {
  final int caloriesConsumed;
  final int caloriesTarget;
  final int proteinG;
  final int proteinTargetG;
  final int carbsG;
  final int carbsTargetG;
  final int fatG;
  final int fatTargetG;

  const GymOSNutritionSummaryCard({
    super.key,
    required this.caloriesConsumed,
    required this.caloriesTarget,
    required this.proteinG,
    required this.proteinTargetG,
    required this.carbsG,
    required this.carbsTargetG,
    required this.fatG,
    required this.fatTargetG,
  });

  @override
  Widget build(BuildContext context) {
    final caloriesRemaining = caloriesTarget - caloriesConsumed;
    final progress = (caloriesConsumed / caloriesTarget).clamp(0.0, 1.0);

    return GymOSGlassCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Nutrition Balance',
                style: context.textTheme.titleMedium?.copyWith(
                  color: context.colorScheme.onSurface.withOpacity(0.6),
                ),
              ),
              const Icon(Icons.restaurant, color: Color(0xFF8B5CF6), size: 20),
            ],
          ),
          const SizedBox(height: GymOSTokens.space16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '$caloriesConsumed kcal',
                    style: context.textTheme.headlineMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  Text(
                    'Consumed of $caloriesTarget target',
                    style: context.textTheme.bodySmall,
                  ),
                ],
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    '$caloriesRemaining kcal',
                    style: context.textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: const Color(0xFF8B5CF6),
                    ),
                  ),
                  const Text(
                    'Remaining budget',
                    style: TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: GymOSTokens.space12),
          ClipRRect(
            borderRadius: BorderRadius.circular(GymOSTokens.radiusS),
            child: LinearProgressIndicator(
              value: progress,
              minHeight: 8,
              backgroundColor: const Color(0xFF1F2035),
              color: const Color(0xFF8B5CF6),
            ),
          ),
          const SizedBox(height: GymOSTokens.space16),
          Row(
            children: [
              Expanded(
                child: _buildMacroProgress(
                  context,
                  'Protein',
                  '$proteinG / $proteinTargetG g',
                  (proteinG / proteinTargetG).clamp(0.0, 1.0),
                  Colors.teal,
                ),
              ),
              const SizedBox(width: GymOSTokens.space12),
              Expanded(
                child: _buildMacroProgress(
                  context,
                  'Carbs',
                  '$carbsG / $carbsTargetG g',
                  (carbsG / carbsTargetG).clamp(0.0, 1.0),
                  Colors.orange,
                ),
              ),
              const SizedBox(width: GymOSTokens.space12),
              Expanded(
                child: _buildMacroProgress(
                  context,
                  'Fat',
                  '$fatG / $fatTargetG g',
                  (fatG / fatTargetG).clamp(0.0, 1.0),
                  const Color(0xFFEF4444),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMacroProgress(
    BuildContext context,
    String name,
    String displayValue,
    double percent,
    Color color,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(name, style: context.textTheme.bodyMedium),
        Text(
          displayValue,
          style: context.textTheme.bodySmall?.copyWith(
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        const SizedBox(height: 6),
        ClipRRect(
          borderRadius: BorderRadius.circular(GymOSTokens.radiusS),
          child: LinearProgressIndicator(
            value: percent,
            minHeight: 4,
            backgroundColor: const Color(0xFF1F2035),
            color: color,
          ),
        ),
      ],
    );
  }
}
