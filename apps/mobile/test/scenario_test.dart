import 'package:flutter_test/flutter_test.dart';
import 'package:sacred_lot/features/feasibility/models/dashboard_scenario.dart';

void main() {
  test(
    'Density uses the supplied baseline without accumulating rounding errors',
    () {
      const baseline = DashboardScenario.sample;
      expect(baseline.withUnits(24).parkingRetained, closeTo(.7, .000001));
      expect(baseline.withUnits(10).parkingRetained, closeTo(.875, .000001));
      final dense = baseline.withUnits(45);
      expect(dense.parkingRetained, closeTo(.4375, .000001));
      expect(dense.withUnits(24).parkingRetained, closeTo(.7, .000001));
      expect(dense.acres, baseline.acres);
      expect(dense.funding, baseline.funding);
      expect(dense.funding.map((share) => share.percent), [60, 30, 10]);
    },
  );

  test('Density rejects values outside the supported range', () {
    expect(() => DashboardScenario.sample.withUnits(9), throwsRangeError);
    expect(() => DashboardScenario.sample.withUnits(46), throwsRangeError);
  });
}
