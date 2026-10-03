import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:sacred_lot/app_shell.dart';
import 'package:sacred_lot/core/api_client.dart';
import 'package:sacred_lot/core/theme.dart';

void main() {
  Future<void> openExplore(WidgetTester tester, ApiClient api) async {
    await tester.pumpWidget(
      MaterialApp(
        theme: SacredTheme.dark,
        home: AppShell(api: api),
      ),
    );
    await tester.tap(find.text('Explore').last);
    await tester.pumpAndSettle();
  }

  testWidgets(
    'Autocomplete selection, density, details, and back preserve search',
    (tester) async {
      final requests = <Uri>[];
      final api = ApiClient(
        client: MockClient((request) async {
          requests.add(request.url);
          if (request.url.path.endsWith('/addresses')) {
            return http.Response(
              jsonEncode([
                {
                  'address': '1820 15TH ST BOULDER',
                  'latitude': 40.01738,
                  'longitude': -105.27489,
                },
              ]),
              200,
            );
          }
          return http.Response(
            jsonEncode({
              'address': '1820 15TH ST BOULDER',
              'parcel_id': '12345',
              'owner': 'Sample owner',
              'total_acres': 1.2,
              'total_sqft': 52272,
            }),
            200,
          );
        }),
      );
      addTearDown(api.close);
      await openExplore(tester, api);
      await tester.enterText(find.byType(TextField), '18');
      await tester.pump(const Duration(milliseconds: 300));
      expect(requests, isEmpty);
      await tester.enterText(find.byType(TextField), '182');
      await tester.pump(const Duration(milliseconds: 100));
      await tester.enterText(find.byType(TextField), '1820');
      await tester.pump(const Duration(milliseconds: 300));
      await tester.pumpAndSettle();
      expect(requests.single.queryParameters['address'], '1820');
      await tester.tap(find.text('1820 15TH ST BOULDER'));
      await tester.pumpAndSettle();
      tester.widget<Slider>(find.byType(Slider)).onChanged!(.5);
      await tester.pump();
      await tester.tap(find.byTooltip('Search property'));
      await tester.pumpAndSettle();
      expect(requests.last.queryParameters['density'], '0.5');
      expect(requests.last.queryParameters['latitude'], '40.01738');
      expect(requests.last.queryParameters['longitude'], '-105.27489');
      expect(find.text('Sample owner'), findsOneWidget);
      expect(find.byType(NavigationBar), findsOneWidget);
      await tester.tap(find.text('Back to search'));
      await tester.pumpAndSettle();
      expect(
        tester.widget<TextField>(find.byType(TextField)).controller!.text,
        '1820 15TH ST BOULDER',
      );
      expect(tester.widget<Slider>(find.byType(Slider)).value, .5);
      await tester.enterText(find.byType(TextField), '123 New Street');
      await tester.pump();
      await tester.tap(find.byTooltip('Search property'));
      await tester.pumpAndSettle();
      expect(requests.last.queryParameters.containsKey('latitude'), isFalse);
      expect(requests.last.queryParameters.containsKey('longitude'), isFalse);
    },
  );

  testWidgets('Late suggestions cannot replace a newer query', (tester) async {
    final oldResponse = Completer<http.Response>();
    final api = ApiClient(
      client: MockClient((request) async {
        if (request.url.queryParameters['address'] == '182') {
          return oldResponse.future;
        }
        return http.Response(
          '[{"address":"New address","latitude":40.0,"longitude":-105.0}]',
          200,
        );
      }),
    );
    addTearDown(api.close);
    await openExplore(tester, api);
    await tester.enterText(find.byType(TextField), '182');
    await tester.pump(const Duration(milliseconds: 300));
    await tester.enterText(find.byType(TextField), '1820');
    await tester.pump(const Duration(milliseconds: 300));
    await tester.pumpAndSettle();
    oldResponse.complete(
      http.Response(
        '[{"address":"Old address","latitude":40.1,"longitude":-105.1}]',
        200,
      ),
    );
    await tester.pumpAndSettle();
    expect(find.text('New address'), findsOneWidget);
    expect(find.text('Old address'), findsNothing);
  });

  testWidgets('Manual address search displays a server error and can retry', (
    tester,
  ) async {
    var attempts = 0;
    final api = ApiClient(
      client: MockClient((request) async {
        attempts++;
        return http.Response(
          '{"detail":{"user_message":"No parcel found."}}',
          404,
        );
      }),
    );
    addTearDown(api.close);
    await openExplore(tester, api);
    await tester.enterText(find.byType(TextField), '123 Main Street');
    await tester.pump();
    await tester.tap(find.byTooltip('Search property'));
    await tester.pumpAndSettle();
    expect(find.text('No parcel found.'), findsOneWidget);
    await tester.tap(find.text('Try again'));
    await tester.pumpAndSettle();
    expect(attempts, 2);
  });
}
