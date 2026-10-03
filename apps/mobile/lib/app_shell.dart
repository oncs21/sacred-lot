import 'package:flutter/material.dart';

import 'core/api_client.dart';
import 'features/feasibility/feasibility_screen.dart';
import 'features/property_search/explore_screen.dart';

class AppShell extends StatefulWidget {
  const AppShell({super.key, this.api});

  final ApiClient? api;

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  final _exploreNavigator = GlobalKey<NavigatorState>();
  late final ApiClient _api = widget.api ?? ApiClient();
  int _selected = 0;

  @override
  void dispose() {
    if (widget.api == null) _api.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    body: IndexedStack(
      index: _selected,
      children: [
        const FeasibilityScreen(),
        Navigator(
          key: _exploreNavigator,
          onGenerateRoute: (_) =>
              MaterialPageRoute<void>(builder: (_) => ExploreScreen(api: _api)),
        ),
      ],
    ),
    bottomNavigationBar: NavigationBar(
      selectedIndex: _selected,
      onDestinationSelected: (index) => setState(() => _selected = index),
      destinations: const [
        NavigationDestination(
          icon: Icon(Icons.dashboard_outlined),
          selectedIcon: Icon(Icons.dashboard),
          label: 'Dashboard',
        ),
        NavigationDestination(icon: Icon(Icons.search), label: 'Explore'),
      ],
    ),
  );
}
