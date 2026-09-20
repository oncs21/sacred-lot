import 'package:flutter/material.dart';

import 'tokens.dart';

abstract final class SacredTheme {
  static const metric = TextStyle(
    fontFamily: 'Menlo',
    fontFamilyFallback: ['Courier New', 'monospace'],
    fontFeatures: [FontFeature.tabularFigures()],
    color: SacredTokens.textPrimary,
    fontWeight: FontWeight.w500,
    letterSpacing: -2,
    height: 1.05,
  );

  static ThemeData get dark => ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    scaffoldBackgroundColor: SacredTokens.background,
    colorScheme: ColorScheme.fromSeed(
      seedColor: SacredTokens.accent,
      brightness: Brightness.dark,
      onPrimary: SacredTokens.background,
      primary: SacredTokens.accent,
      surface: SacredTokens.background,
      onSurface: SacredTokens.textPrimary,
    ),
    textTheme: const TextTheme(
      headlineLarge: TextStyle(
        fontSize: 34,
        height: 1.12,
        letterSpacing: -1.3,
        fontWeight: FontWeight.w700,
        color: SacredTokens.textPrimary,
      ),
      headlineSmall: TextStyle(
        fontSize: 23,
        height: 1.2,
        letterSpacing: -.6,
        fontWeight: FontWeight.w600,
        color: SacredTokens.textPrimary,
      ),
      titleMedium: TextStyle(
        fontSize: 15,
        height: 1.3,
        fontWeight: FontWeight.w600,
        color: SacredTokens.textPrimary,
      ),
      bodyLarge: TextStyle(
        fontSize: 16,
        height: 1.5,
        color: SacredTokens.textSecondary,
      ),
      bodyMedium: TextStyle(
        fontSize: 14,
        height: 1.5,
        color: SacredTokens.textSecondary,
      ),
      bodySmall: TextStyle(
        fontSize: 12,
        height: 1.45,
        color: SacredTokens.textSecondary,
      ),
      labelSmall: TextStyle(
        fontSize: 10,
        height: 1.4,
        letterSpacing: 1.4,
        fontWeight: FontWeight.w700,
        color: SacredTokens.textSecondary,
      ),
    ),
    dividerTheme: const DividerThemeData(color: SacredTokens.divider, space: 1),
    sliderTheme: const SliderThemeData(
      activeTrackColor: SacredTokens.accent,
      inactiveTrackColor: SacredTokens.divider,
      thumbColor: SacredTokens.accent,
      trackHeight: 6,
      showValueIndicator: ShowValueIndicator.never,
    ),
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(
        foregroundColor: SacredTokens.accent,
        minimumSize: const Size(48, 48),
        textStyle: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
      ),
    ),
  );
}
