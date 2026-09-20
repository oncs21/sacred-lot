import 'package:flutter/material.dart';

import '../../core/tokens.dart';

class StatusBadge extends StatelessWidget {
  const StatusBadge({
    super.key,
    required this.label,
    this.icon = Icons.info_outline,
    this.warning = false,
  });

  final String label;
  final IconData icon;
  final bool warning;

  @override
  Widget build(BuildContext context) {
    final color = warning ? SacredTokens.amberText : SacredTokens.accent;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: color.withValues(alpha: .10),
        borderRadius: BorderRadius.circular(100),
        border: Border.all(color: color.withValues(alpha: .13)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 13, color: color),
          const SizedBox(width: 5),
          Flexible(
            child: Text(
              label,
              style: TextStyle(
                fontSize: 11,
                height: 1.3,
                fontWeight: FontWeight.w600,
                color: color,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
