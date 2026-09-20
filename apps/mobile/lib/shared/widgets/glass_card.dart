import 'dart:ui';

import 'package:flutter/material.dart';

import '../../core/tokens.dart';

class GlassCard extends StatelessWidget {
  const GlassCard({super.key, required this.child, this.tint});

  final Widget child;
  final Color? tint;

  @override
  Widget build(BuildContext context) {
    final highContrast = MediaQuery.highContrastOf(context);
    return DecoratedBox(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(SacredTokens.cardRadius),
        boxShadow: const [
          BoxShadow(
            color: Color(0x26000000),
            blurRadius: 24,
            offset: Offset(0, 8),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(SacredTokens.cardRadius),
        child: BackdropFilter.grouped(
          enabled: !highContrast,
          filter: ImageFilter.blur(
            sigmaX: SacredTokens.blurSigma,
            sigmaY: SacredTokens.blurSigma,
          ),
          child: DecoratedBox(
            decoration: BoxDecoration(
              color: highContrast
                  ? SacredTokens.background
                  : tint ?? SacredTokens.cardGlassBg,
              gradient: highContrast
                  ? null
                  : LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        Colors.white.withValues(alpha: .08),
                        Colors.white.withValues(alpha: .03),
                      ],
                    ),
              borderRadius: BorderRadius.circular(SacredTokens.cardRadius),
              border: Border.all(
                color: highContrast
                    ? SacredTokens.textSecondary
                    : SacredTokens.cardBorder,
              ),
            ),
            child: Padding(padding: const EdgeInsets.all(22), child: child),
          ),
        ),
      ),
    );
  }
}
