import 'package:flutter/foundation.dart';

@immutable
class DashboardScenario {
  const DashboardScenario({
    required this.units,
    required this.acres,
    required this.squareFeetLabel,
    required this.parkingRetained,
    required this.funding,
  });

  final int units;
  final double acres;
  final String squareFeetLabel;
  final double parkingRetained;
  final List<FundingShare> funding;

  DashboardScenario withUnits(int value) {
    if (value < 10 || value > 45) {
      throw RangeError.range(value, 10, 45, 'units');
    }
    return DashboardScenario(
      units: value,
      acres: sample.acres,
      squareFeetLabel: sample.squareFeetLabel,
      parkingRetained: 1 - value / sample.units * (1 - sample.parkingRetained),
      funding: sample.funding,
    );
  }

  static const sample = DashboardScenario(
    units: 24,
    acres: 1.2,
    squareFeetLabel: '52,272',
    parkingRetained: .7,
    funding: [
      FundingShare(label: 'LIHTC', percent: 60),
      FundingShare(label: 'Faith grants', percent: 30),
      FundingShare(label: 'Local philanthropy', percent: 10),
    ],
  );
}

@immutable
class FundingShare {
  const FundingShare({required this.label, required this.percent});

  final String label;
  final int percent;
}
