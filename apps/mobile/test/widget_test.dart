import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sacred_lot/app.dart';
import 'package:sacred_lot/features/feasibility/widgets/density_card.dart';
import 'package:sacred_lot/features/feasibility/widgets/funding_card.dart';
import 'package:sacred_lot/features/feasibility/widgets/parcel_card.dart';
import 'package:sacred_lot/features/feasibility/widgets/yield_card.dart';

void main() {
  for (final size in const [
    Size(320, 700),
    Size(402, 874),
    Size(1024, 768),
    Size(1440, 900),
  ]) {
    for (final scale in [1.0, 2.0]) {
      testWidgets('Dashboard fits ${size.width} wide at $scale text scale', (
        tester,
      ) async {
        tester.view.physicalSize = size;
        tester.view.devicePixelRatio = 1;
        tester.platformDispatcher.textScaleFactorTestValue = scale;
        addTearDown(tester.view.resetPhysicalSize);
        addTearDown(tester.view.resetDevicePixelRatio);
        addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
        await tester.pumpWidget(const SacredLotApp());
        await tester.pumpAndSettle();
        expect(find.byType(YieldCard), findsOneWidget);
        expect(find.byType(ParcelCard), findsOneWidget);
        expect(find.byType(DensityCard), findsOneWidget);
        expect(find.byType(FundingCard), findsOneWidget);
        await tester.ensureVisible(find.text('Local philanthropy'));
        await tester.pumpAndSettle();
        expect(tester.takeException(), isNull);
      });
    }
  }

  testWidgets(
    'Slider updates housing and parking without claiming zoning approval',
    (tester) async {
      await tester.pumpWidget(const SacredLotApp());
      expect(find.text('Scenario estimate'), findsOneWidget);
      expect(find.text('Illustrative data'), findsOneWidget);
      expect(find.text('Compliant'), findsNothing);
      expect(find.text('Variance Required'), findsNothing);
      await tester.ensureVisible(find.byType(Slider));
      final slider = tester.widget<Slider>(find.byType(Slider));
      expect(slider.onChanged, isNotNull);
      expect(slider.value, 24);
      expect(slider.min, 10);
      expect(slider.max, 45);
      await tester.drag(find.byType(Slider), const Offset(400, 0));
      await tester.pumpAndSettle();
      expect(
        tester.widget<YieldCard>(find.byType(YieldCard)).scenario.units,
        45,
      );
      expect(find.text('44% parking surface retained'), findsOneWidget);
      expect(find.text('60%'), findsOneWidget);
      expect(find.text('30%'), findsOneWidget);
      expect(find.text('10%'), findsOneWidget);
      await tester.drag(find.byType(Slider), const Offset(-400, 0));
      await tester.pumpAndSettle();
      expect(
        tester.widget<YieldCard>(find.byType(YieldCard)).scenario.units,
        10,
      );
      expect(find.text('88% parking surface retained'), findsOneWidget);
    },
  );

  testWidgets('Wide dashboard arranges cards in two aligned rows', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(1200, 1200);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(const SacredLotApp());
    final yieldRect = tester.getRect(find.byType(YieldCard));
    final parcelRect = tester.getRect(find.byType(ParcelCard));
    final densityRect = tester.getRect(find.byType(DensityCard));
    final fundingRect = tester.getRect(find.byType(FundingCard));
    expect(yieldRect.top, parcelRect.top);
    expect(yieldRect.width, parcelRect.width);
    expect(yieldRect.right, lessThan(parcelRect.left));
    expect(densityRect.top, fundingRect.top);
    expect(densityRect.top, greaterThan(yieldRect.bottom));
  });

  testWidgets('High contrast mode disables glass blur', (tester) async {
    tester.platformDispatcher.accessibilityFeaturesTestValue =
        FakeAccessibilityFeatures(highContrast: true);
    addTearDown(tester.platformDispatcher.clearAccessibilityFeaturesTestValue);
    await tester.pumpWidget(const SacredLotApp());
    for (final filter in tester.widgetList<BackdropFilter>(
      find.byType(BackdropFilter),
    )) {
      expect(filter.enabled, isFalse);
    }
    expect(tester.takeException(), isNull);
  });
}
