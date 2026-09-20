import 'package:flutter/material.dart';

import '../../core/tokens.dart';
import '../../shared/widgets/dashboard_background.dart';
import '../../shared/widgets/status_badge.dart';
import 'models/dashboard_scenario.dart';
import 'widgets/density_card.dart';
import 'widgets/funding_card.dart';
import 'widgets/parcel_card.dart';
import 'widgets/yield_card.dart';

class FeasibilityScreen extends StatelessWidget {
  const FeasibilityScreen({super.key});

  @override
  Widget build(BuildContext context) => Scaffold(
    body: DashboardBackground(
      child: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(20, 16, 20, 28),
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 1040),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const _BrandHeader(),
                  const SizedBox(height: 32),
                  Text(
                    'PROPERTY WORKSPACE',
                    style: Theme.of(context).textTheme.labelSmall,
                  ),
                  const SizedBox(height: 10),
                  Text(
                    'Land with purpose.',
                    style: Theme.of(context).textTheme.headlineLarge,
                  ),
                  const SizedBox(height: 10),
                  const Text(
                    'Explore the possibility of homes,\ncommunity, and a lasting impact.',
                  ),
                  const SizedBox(height: 20),
                  Wrap(
                    spacing: 10,
                    runSpacing: 8,
                    crossAxisAlignment: WrapCrossAlignment.center,
                    children: [
                      const Icon(
                        Icons.location_on_outlined,
                        size: 16,
                        color: SacredTokens.accent,
                      ),
                      Text(
                        'Sample church property',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      const StatusBadge(
                        label: 'Illustrative data',
                        icon: Icons.science_outlined,
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                  BackdropGroup(child: const _BentoGrid()),
                  const SizedBox(height: 24),
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Icon(
                        Icons.verified_user_outlined,
                        size: 18,
                        color: SacredTokens.textSecondary,
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          'A starting point, not an approval. Illustrative local model; no site or zoning assessment has been performed. A planner, architect, and qualified financial advisor must review any real proposal.',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                  const Divider(),
                  const SizedBox(height: 16),
                  Text(
                    'SACRED LOT  /  FEASIBILITY & VISION',
                    style: Theme.of(context).textTheme.labelSmall,
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    ),
  );
}

class _BrandHeader extends StatelessWidget {
  const _BrandHeader();

  @override
  Widget build(BuildContext context) => Wrap(
    spacing: 12,
    runSpacing: 12,
    crossAxisAlignment: WrapCrossAlignment.center,
    children: [
      Container(
        width: 36,
        height: 36,
        decoration: BoxDecoration(
          color: const Color(0x20FFFFFF),
          borderRadius: BorderRadius.circular(11),
        ),
        child: const Icon(
          Icons.holiday_village_outlined,
          size: 21,
          color: Colors.white,
        ),
      ),
      const Text(
        'sacred lot',
        style: TextStyle(
          fontSize: 20,
          fontWeight: FontWeight.w700,
          letterSpacing: -.7,
          color: SacredTokens.textPrimary,
        ),
      ),
      const StatusBadge(
        label: 'Feasibility studio',
        icon: Icons.auto_awesome_outlined,
      ),
    ],
  );
}

class _BentoGrid extends StatefulWidget {
  const _BentoGrid();

  @override
  State<_BentoGrid> createState() => _BentoGridState();
}

class _BentoGridState extends State<_BentoGrid> {
  DashboardScenario _scenario = DashboardScenario.sample;

  void _updateUnits(int units) {
    if (units == _scenario.units) return;
    setState(() => _scenario = _scenario.withUnits(units));
  }

  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (context, constraints) {
      final scenario = _scenario;
      final singleColumn =
          constraints.maxWidth < 720 ||
          MediaQuery.textScalerOf(context).scale(16) > 24;
      if (singleColumn) {
        return Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            YieldCard(scenario: scenario),
            const SizedBox(height: 16),
            ParcelCard(scenario: scenario),
            const SizedBox(height: 16),
            DensityCard(scenario: scenario, onUnitsChanged: _updateUnits),
            const SizedBox(height: 16),
            FundingCard(scenario: scenario),
          ],
        );
      }
      return Column(
        children: [
          IntrinsicHeight(
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Expanded(flex: 1, child: YieldCard(scenario: scenario)),
                const SizedBox(width: 16),
                Expanded(flex: 1, child: ParcelCard(scenario: scenario)),
              ],
            ),
          ),
          const SizedBox(height: 16),
          IntrinsicHeight(
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Expanded(
                  flex: 1,
                  child: DensityCard(
                    scenario: scenario,
                    onUnitsChanged: _updateUnits,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(flex: 1, child: FundingCard(scenario: scenario)),
              ],
            ),
          ),
        ],
      );
    },
  );
}
