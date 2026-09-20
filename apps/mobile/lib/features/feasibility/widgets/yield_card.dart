import 'package:flutter/material.dart';

import '../../../core/theme.dart';
import '../../../core/tokens.dart';
import '../../../shared/widgets/glass_card.dart';
import '../../../shared/widgets/status_badge.dart';
import '../models/dashboard_scenario.dart';
import 'card_heading.dart';

class YieldCard extends StatelessWidget {
  const YieldCard({super.key, required this.scenario});

  final DashboardScenario scenario;

  @override
  Widget build(BuildContext context) => GlassCard(
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const CardHeading(
          icon: Icons.holiday_village_outlined,
          title: 'Housing potential',
          index: '01',
        ),
        const SizedBox(height: 22),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
          decoration: BoxDecoration(
            color: SacredTokens.accent.withValues(alpha: .12),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: SacredTokens.accent.withValues(alpha: .22),
            ),
          ),
          child: Wrap(
            crossAxisAlignment: WrapCrossAlignment.end,
            spacing: 12,
            runSpacing: 8,
            children: [
              Text(
                '${scenario.units}',
                style: SacredTheme.metric.copyWith(
                  fontSize: 82,
                  letterSpacing: -5,
                  color: SacredTokens.accent,
                ),
              ),
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Text(
                  'homes',
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),
        const StatusBadge(
          label: 'Scenario estimate',
          icon: Icons.rule_outlined,
        ),
        const SizedBox(height: 24),
        const Divider(),
        const SizedBox(height: 16),
        Text(
          'A vision of what could be.',
          style: Theme.of(context).textTheme.titleMedium
              ?.copyWith(color: SacredTokens.accent),
        ),
        const SizedBox(height: 6),
        const Text('Explore how your land could make room for new neighbors.'),
      ],
    ),
  );
}
