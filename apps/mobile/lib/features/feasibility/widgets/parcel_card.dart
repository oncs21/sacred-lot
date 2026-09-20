import 'package:flutter/material.dart';

import '../../../core/theme.dart';
import '../../../core/tokens.dart';
import '../../../shared/widgets/glass_card.dart';
import '../models/dashboard_scenario.dart';
import 'card_heading.dart';

class ParcelCard extends StatelessWidget {
  const ParcelCard({super.key, required this.scenario});

  final DashboardScenario scenario;

  @override
  Widget build(BuildContext context) => GlassCard(
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const CardHeading(
          icon: Icons.layers_outlined,
          title: 'Parcel impact',
          index: '02',
        ),
        const SizedBox(height: 24),
        Wrap(
          crossAxisAlignment: WrapCrossAlignment.center,
          spacing: 8,
          children: [
            Text(
              '${scenario.acres}',
              style: SacredTheme.metric.copyWith(fontSize: 38),
            ),
            Text('acres', style: Theme.of(context).textTheme.titleMedium),
          ],
        ),
        const SizedBox(height: 4),
        Text(
          '${scenario.squareFeetLabel} sq ft · Sample parking surface',
          style: Theme.of(context).textTheme.bodySmall,
        ),
        const SizedBox(height: 24),
        Row(
          children: [
            const Icon(
              Icons.local_parking_rounded,
              color: SacredTokens.accent,
              size: 24,
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Semantics(
                label: 'Illustrative parking surface retained',
                value: '${(scenario.parkingRetained * 100).round()} percent',
                child: ExcludeSemantics(
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(6),
                    child: SizedBox(
                      height: 20,
                      child: Row(
                        children: [
                          Expanded(
                            flex: (scenario.parkingRetained * 100).round(),
                            child: const ColoredBox(
                              color: SacredTokens.accent,
                              child: SizedBox.expand(),
                            ),
                          ),
                          const SizedBox(width: 3),
                          Expanded(
                            flex: ((1 - scenario.parkingRetained) * 100)
                                .round(),
                            child: const ColoredBox(
                              color: SacredTokens.accentLight,
                              child: SizedBox.expand(),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Text(
          '${(scenario.parkingRetained * 100).round()}% parking surface retained',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 6),
        Text(
          'Illustrative land allocation; not a parking-space count.',
          style: Theme.of(context).textTheme.bodySmall,
        ),
      ],
    ),
  );
}
