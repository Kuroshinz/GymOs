import 'package:flutter/material.dart';
import '../theme/theme_tokens.dart';
import '../extensions/context_extensions.dart';
import 'glass_card.dart';

class GymOSMetricCard extends StatelessWidget {
  final String title;
  final String value;
  final String unit;
  final IconData icon;
  final Color iconColor;
  final Widget? trailing;
  final Widget? bottomWidget;

  const GymOSMetricCard({
    super.key,
    required this.title,
    required this.value,
    required this.unit,
    required this.icon,
    required this.iconColor,
    this.trailing,
    this.bottomWidget,
  });

  @override
  Widget build(BuildContext context) {
    return GymOSGlassCard(
      padding: const EdgeInsets.all(GymOSTokens.space16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(6),
                    decoration: BoxDecoration(
                      color: iconColor.withOpacity(0.12),
                      borderRadius: BorderRadius.circular(GymOSTokens.radiusS),
                    ),
                    child: Icon(icon, color: iconColor, size: 18),
                  ),
                  const SizedBox(width: GymOSTokens.space8),
                  Text(
                    title,
                    style: context.textTheme.bodyMedium?.copyWith(
                      color: context.colorScheme.onSurface.withOpacity(0.6),
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
              if (trailing != null) trailing!,
            ],
          ),
          const SizedBox(height: GymOSTokens.space12),
          Row(
            crossAxisAlignment: CrossAxisAlignment.baseline,
            textBaseline: TextBaseline.alphabetic,
            children: [
              Text(
                value,
                style: context.textTheme.headlineMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              const SizedBox(width: GymOSTokens.space4),
              Text(
                unit,
                style: context.textTheme.bodyMedium?.copyWith(
                  color: context.colorScheme.onSurface.withOpacity(0.4),
                ),
              ),
            ],
          ),
          if (bottomWidget != null) ...[
            const SizedBox(height: GymOSTokens.space12),
            bottomWidget!,
          ],
        ],
      ),
    );
  }
}
