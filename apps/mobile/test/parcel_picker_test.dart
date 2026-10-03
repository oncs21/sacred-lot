import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:sacred_lot/core/api_client.dart';
import 'package:sacred_lot/features/property_search/parcel_screen.dart';

void main() {
  testWidgets('Choose unit A, display unavailable area, and change parcel', (
    tester,
  ) async {
    final api = ApiClient(
      client: MockClient((request) async {
        if (request.url.queryParameters['object_id'] == null) {
          return http.Response(
            jsonEncode({
              'detail': {
                'error_code': 'AMBIGUOUS_PARCEL',
                'candidates': [
                  {
                    'object_id': 1,
                    'parcel_id': 'A',
                    'address': '550 MCCASLIN UNIT A',
                    'owner': 'Owner A',
                  },
                  {
                    'object_id': 2,
                    'parcel_id': 'B',
                    'address': '550 MCCASLIN UNIT B',
                    'owner': 'Owner B',
                  },
                ],
              },
            }),
            409,
          );
        }
        expect(request.url.queryParameters['object_id'], '1');
        return http.Response(
          jsonEncode({
            'parcel_id': 'A',
            'address': '550 MCCASLIN UNIT A',
            'owner': 'Owner A',
            'zoning': {
              'status': 'matched',
              'districts': [
                {'code': 'RE', 'description': 'Residential-Estate'},
              ],
            },
            'total_acres': null,
            'total_sqft': null,
          }),
          200,
        );
      }),
    );
    addTearDown(api.close);
    await tester.pumpWidget(
      MaterialApp(
        home: ParcelScreen(api: api, address: '550 McCaslin', density: .3),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.text('Choose a parcel'), findsOneWidget);
    await tester.tap(find.text('550 MCCASLIN UNIT A'));
    await tester.pumpAndSettle();
    expect(find.text('Area unavailable'), findsNWidgets(2));
    expect(find.text('RE — Residential-Estate'), findsOneWidget);
    expect(find.text('Owner A'), findsOneWidget);
    await tester.tap(find.text('Choose another parcel'));
    await tester.pumpAndSettle();
    expect(find.text('550 MCCASLIN UNIT B'), findsOneWidget);
  });
}
