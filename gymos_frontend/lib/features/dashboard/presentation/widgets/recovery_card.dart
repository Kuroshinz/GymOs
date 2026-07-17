import 'package:flutter/material.dart';
import '../../../../core/theme/theme_tokens.dart';
import '../../../../core/widgets/glass_card.dart';
import '../../../../core/extensions/context_extensions.dart';

class GymOSRecoveryCard extends StatelessWidget {
  final int score;
  final int hrvMs;
  final int rhrBpm;
  final int sleepDurationMinutes;
  final String statusText;
  final Color color;

  const GymOSRecoveryCard({
    super.key,
    required this.score,
    required this.hrvMs,
    required this.rhrBpm,
    required this.sleepDurationMinutes,
    required this.statusText,
    required this.color,
  });

  String _formatSleep(int mins) {
    final hours = mins ~/ 60;
    final remainingMins = mins % 60;
    return '${hours}h ${remainingMins}m';
  }

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
                'Recovery Score',
                style: context.textTheme.titleMedium?.copyWith(
                  color: context.colorScheme.onSurface.withOpacity(0.6),
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(GymOSTokens.radiusS),
                ),
                child: Text(
                  statusText,
                  style: context.textTheme.bodySmall?.copyWith(
                    color: color,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: GymOSTokens.space16),
          Row(
            children: [
              Stack(
                alignment: Alignment.center,
                children: [
                  SizedBox(
                    width: 80,
                    height: 80,
                    child: CircularProgressIndicator(
                      value: score / 100.0,
                      strokeWidth: 8,
                      backgroundColor: const Color(0xFF1F2035),
                      valueColor: AlwaysStoppedAnimation<Color>(color),
                    ),
                  ),
                  Text(
                    '$score%',
                    style: context.textTheme.headlineMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                ],
              ),
              const SizedBox(width: GymOSTokens.space24),
              Expanded(
                child: Column(
                  children: [
                    _buildMetricRow(context, 'HRV (Rmssd)', '$hrvMs ms', Icons.favorite_border),
                    const Divider(color: Color(0xFF1F2035), height: 12),
                    _buildMetricRow(context, 'Resting HR', '$rhrBpm bpm', Icons.bolt),
                    const Divider(color: Color(0xFF1F2035), height: 12),
                    _buildMetricRow(context, 'Sleep Log', _formatSleep(sleepDurationMinutes), Icons.bedtime_outlined),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMetricRow(BuildContext context, String label, String value, IconData icon) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Row(
          children: [
            Icon(icon, size: 16, color: context.colorScheme.onSurface.withOpacity(0.4)),
            const SizedBox(width: 8),
            Text(label, style: context.textTheme.bodyMedium),
          ],
        ),
        Text(
          value,
          style: context.textTheme.bodyLarge?.copyWith(
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
      ],
    );
  }
}
