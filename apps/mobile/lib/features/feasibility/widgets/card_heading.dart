import 'package:flutter/material.dart';

import '../../../core/tokens.dart';

class CardHeading extends StatelessWidget {
  const CardHeading({
    super.key,
    required this.icon,
    required this.title,
    required this.index,
  });

  final IconData icon;
  final String title;
  final String index;

  @override
  Widget build(BuildContext context) => Row(
    children: [
      Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: const Color(0x18FFFFFF),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Icon(icon, size: 18, color: SacredTokens.textPrimary),
      ),
      const SizedBox(width: 10),
      Expanded(
        child: Text(title, style: Theme.of(context).textTheme.titleMedium),
      ),
      const SizedBox(width: 8),
      Text(index, style: Theme.of(context).textTheme.labelSmall),
    ],
  );
}
