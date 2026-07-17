import 'package:flutter/material.dart';
import '../../../core/theme/theme_tokens.dart';
import '../../../core/widgets/glass_card.dart';
import '../../../core/extensions/context_extensions.dart';

class ProfilePage extends StatelessWidget {
  const ProfilePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: context.theme.scaffoldBackgroundColor,
      appBar: AppBar(
        title: const Text('Athlete Profile'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(GymOSTokens.space16),
        child: Column(
          children: [
            GymOSGlassCard(
              child: Row(
                children: [
                  CircleAvatar(
                    radius: 30,
                    backgroundColor: context.colorScheme.primary,
                    child: const Text('N', style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold)),
                  ),
                  const SizedBox(width: GymOSTokens.space16),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Nguyễn Thiện Nhân', style: context.textTheme.titleLarge),
                      const SizedBox(height: GymOSTokens.space4),
                      Text('Level 28 • Elite Athlete', style: context.textTheme.bodyMedium),
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
