import 'package:flutter/material.dart';
import '../../../core/theme/theme_tokens.dart';
import '../../../core/widgets/glass_card.dart';
import '../../../core/extensions/context_extensions.dart';

class CoachPage extends StatelessWidget {
  const CoachPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: context.theme.scaffoldBackgroundColor,
      appBar: AppBar(
        title: const Text('AI Coach'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(GymOSTokens.space16),
        child: Column(
          children: [
            GymOSGlassCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Coach Advice',
                    style: context.textTheme.headlineMedium,
                  ),
                  const SizedBox(height: GymOSTokens.space8),
                  Text(
                    'Get tailored recovery and workout recommendations based on your historical training session metrics.',
                    style: context.textTheme.bodyMedium,
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
