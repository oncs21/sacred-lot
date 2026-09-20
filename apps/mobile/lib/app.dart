import 'package:flutter/material.dart';

import 'core/theme.dart';
import 'features/feasibility/feasibility_screen.dart';

class SacredLotApp extends StatelessWidget {
  const SacredLotApp({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'Sacred Lot',
    debugShowCheckedModeBanner: false,
    theme: SacredTheme.dark,
    home: const FeasibilityScreen(),
  );
}
