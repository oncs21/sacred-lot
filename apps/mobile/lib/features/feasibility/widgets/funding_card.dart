import 'package:flutter/material.dart';

import '../../../core/theme.dart';
import '../../../core/tokens.dart';
import '../../../shared/widgets/glass_card.dart';
import '../models/dashboard_scenario.dart';
import 'card_heading.dart';

class FundingCard extends StatelessWidget {
  const FundingCard({super.key, required this.scenario});

  final DashboardScenario scenario;

  static const _colors = [
    SacredTokens.accent,
    SacredTokens.chartIndigo,
    SacredTokens.chartMint,
  ];

  @override
  Widget build(BuildContext context) => GlassCard(
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const CardHeading(
          icon: Icons.account_balance_outlined,
          title: 'Faith-capital mix',
          index: '04',
        ),
        const SizedBox(height: 22),
        Text(
          'A shared investment.',
          style: Theme.of(context).textTheme.headlineSmall,
        ),
        const SizedBox(height: 6),
        const Text('60 / 30 / 10 · Fixed scenario mix.'),
        const SizedBox(height: 22),
        ExcludeSemantics(
          child: ClipRRect(
            borderRadius: BorderRadius.circular(6),
            child: SizedBox(
              height: 18,
              child: Row(
                children: [
                  for (var i = 0; i < scenario.funding.length; i++) ...[
                    if (i > 0) const SizedBox(width: 3),
                    Expanded(
                      flex: scenario.funding[i].percent,
                      child: ColoredBox(
                        color: _colors[i % _colors.length],
                        child: const SizedBox.expand(),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ),
        const SizedBox(height: 16),
        for (var i = 0; i < scenario.funding.length; i++)
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 5),
            child: Row(
              children: [
                Container(
                  width: 8,
                  height: 8,
                  decoration: BoxDecoration(
                    color: _colors[i % _colors.length],
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    scenario.funding[i].label,
                    style: Theme.of(context).textTheme.bodyMedium
                        ?.copyWith(color: SacredTokens.textPrimary),
                  ),
                ),
                const SizedBox(width: 12),
                Text(
                  '${scenario.funding[i].percent}%',
                  style: SacredTheme.metric.copyWith(
                    fontSize: 14,
                    letterSpacing: -.3,
                  ),
                ),
              ],
            ),
          ),
        const SizedBox(height: 14),
        Text(
          'LIHTC = Low-Income Housing Tax Credit. Eligibility and funding have not been assessed.',
          style: Theme.of(context).textTheme.bodySmall,
        ),
      ],
    ),
  );
}
