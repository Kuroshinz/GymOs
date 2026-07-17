import 'dart:ui';
import 'package:flutter/material.dart';
import '../theme/theme_tokens.dart';

class GymOSGlassCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  final double? width;
  final double? height;
  final BorderRadius? borderRadius;
  final Border? border;

  const GymOSGlassCard({
    super.key,
    required this.child,
    this.padding,
    this.width,
    this.height,
    this.borderRadius,
    this.border,
  });

  @override
  Widget build(BuildContext context) {
    final cardBorderRadius = borderRadius ?? BorderRadius.circular(GymOSTokens.radiusL);
    
    return Container(
      width: width,
      height: height,
      decoration: BoxDecoration(
        borderRadius: cardBorderRadius,
        boxShadow: GymOSTokens.premiumShadow,
      ),
      child: ClipRRect(
        borderRadius: cardBorderRadius,
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 12.0, sigmaY: 12.0),
          child: Container(
            padding: padding ?? const EdgeInsets.all(GymOSTokens.space16),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  const Color(0xFF121324).withOpacity(0.7),
                  const Color(0xFF0A0B1E).withOpacity(0.85),
                ],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: cardBorderRadius,
              border: border ?? Border.all(
                color: const Color(0xFF1F2035).withOpacity(0.5),
                width: 1.0,
              ),
            ),
            child: child,
          ),
        ),
      ),
    );
  }
}
