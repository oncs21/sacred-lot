import 'package:flutter/material.dart';

import '../../core/tokens.dart';

class DashboardBackground extends StatelessWidget {
  const DashboardBackground({super.key, required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) => DecoratedBox(
    decoration: const BoxDecoration(
      color: SacredTokens.background,
      gradient: RadialGradient(
        center: Alignment(.9, -.75),
        radius: 1.25,
        colors: [Color(0xFF36523D), Color(0xFF294A3D), SacredTokens.background],
        stops: [0, .48, 1],
      ),
    ),
    child: child,
  );
}
