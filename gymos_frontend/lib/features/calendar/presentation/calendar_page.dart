import 'package:flutter/material.dart';
import '../../../core/theme/theme_tokens.dart';
import '../../../core/widgets/glass_card.dart';
import '../../../core/extensions/context_extensions.dart';

class CalendarPage extends StatelessWidget {
  const CalendarPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: context.theme.scaffoldBackgroundColor,
      appBar: AppBar(
        title: const Text('Schedule'),
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
                    'Training Calendar',
                    style: context.textTheme.headlineMedium,
                  ),
                  const SizedBox(height: GymOSTokens.space8),
                  Text(
                    'Plan workouts, recovery days, and nutrition budgets.',
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
