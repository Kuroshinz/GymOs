import 'package:flutter/material.dart';
import '../../../../core/theme/theme_tokens.dart';
import '../../../../core/extensions/context_extensions.dart';

class GymOSRecoveryRadialGauge extends StatelessWidget {
  final int score;
  final Color color;

  const GymOSRecoveryRadialGauge({
    super.key,
    required this.score,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return TweenAnimationBuilder<double>(
      tween: Tween<double>(begin: 0.0, end: score / 100.0),
      duration: GymOSTokens.durationSlow,
      curve: Curves.easeOutCubic,
      builder: (context, value, child) {
        return Stack(
          alignment: Alignment.center,
          children: [
            SizedBox(
              width: 160,
              height: 160,
              child: CircularProgressIndicator(
                value: value,
                strokeWidth: 14,
                backgroundColor: const Color(0xFF1F2035),
                valueColor: AlwaysStoppedAnimation<Color>(color),
              ),
            ),
            Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  '${(value * 100).toInt()}%',
                  style: context.textTheme.headlineLarge?.copyWith(
                    fontSize: 36,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                Text(
                  'RECOVERY',
                  style: context.textTheme.bodySmall?.copyWith(
                    letterSpacing: 1.5,
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
                ),
              ],
            ),
          ],
        );
      },
    );
  }
}
