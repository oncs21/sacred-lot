import 'package:flutter/material.dart';

import '../../../core/theme.dart';
import '../../../shared/widgets/glass_card.dart';
import '../../../shared/widgets/status_badge.dart';
import '../models/dashboard_scenario.dart';
import 'card_heading.dart';

class DensityCard extends StatelessWidget {
  const DensityCard({
    super.key,
    required this.scenario,
    required this.onUnitsChanged,
  });

  final DashboardScenario scenario;
  final ValueChanged<int> onUnitsChanged;

  @override
  Widget build(BuildContext context) => GlassCard(
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const CardHeading(
          icon: Icons.tune_rounded,
          title: 'Explore density',
          index: '03',
        ),
        const SizedBox(height: 22),
        Wrap(
          spacing: 16,
          runSpacing: 12,
          crossAxisAlignment: WrapCrossAlignment.center,
          children: [
            Text(
              '${scenario.units}',
              style: SacredTheme.metric.copyWith(fontSize: 38),
            ),
            Text('target homes', style: Theme.of(context).textTheme.bodyMedium),
            const StatusBadge(
              label: 'Interactive Model',
              icon: Icons.tune_rounded,
            ),
          ],
        ),
        const SizedBox(height: 12),
        Slider(
          value: scenario.units.toDouble(),
          min: 10,
          max: 45,
          divisions: 35,
          onChanged: (value) => onUnitsChanged(value.round()),
          semanticFormatterCallback: (value) => '${value.round()} target homes',
        ),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Expanded(
              child: Text(
                '10 homes',
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                '45 homes',
                textAlign: TextAlign.end,
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ),
          ],
        ),
        const SizedBox(height: 18),
        Text(
          'Drag to explore the trade-off between housing and retained parking surface.',
          style: Theme.of(context).textTheme.bodySmall,
        ),
      ],
    ),
  );
}
