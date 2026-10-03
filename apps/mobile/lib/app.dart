import 'package:flutter/material.dart';

import 'core/theme.dart';
import 'app_shell.dart';

class SacredLotApp extends StatelessWidget {
  const SacredLotApp({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'Sacred Lot',
    debugShowCheckedModeBanner: false,
    theme: SacredTheme.dark,
    home: const AppShell(),
  );
}
