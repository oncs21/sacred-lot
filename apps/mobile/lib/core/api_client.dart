import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../features/property_search/models/property.dart';
import 'config.dart';

class ApiException implements Exception {
  const ApiException(this.message);
  final String message;
}

class ParcelSelectionRequired implements Exception {
  const ParcelSelectionRequired(this.candidates);
  final List<ParcelCandidate> candidates;
}

class ApiClient {
  ApiClient({http.Client? client, String baseUrl = AppConfig.apiBaseUrl})
    : _client = client ?? http.Client(),
      _baseUrl = Uri.parse(baseUrl);

  final http.Client _client;
  final Uri _baseUrl;

  Future<dynamic> _get(String path, Map<String, String> query) async {
    try {
      final response = await _client
          .get(_baseUrl.resolve(path).replace(queryParameters: query))
          .timeout(const Duration(seconds: 30));
      if (response.statusCode != 200) {
        String message = 'Could not complete the search. Please try again.';
        try {
          final body = jsonDecode(response.body);
          if (body is Map && body['detail'] is Map) {
            final detail = body['detail'] as Map;
            if (response.statusCode == 409 &&
                detail['error_code'] == 'AMBIGUOUS_PARCEL' &&
                detail['candidates'] is List) {
              throw ParcelSelectionRequired(
                (detail['candidates'] as List)
                    .map(
                      (item) => ParcelCandidate.fromJson(
                        item as Map<String, dynamic>,
                      ),
                    )
                    .toList(),
              );
            }
            if (detail['user_message'] is String) {
              message = detail['user_message'] as String;
            }
          }
        } on FormatException {
          message = 'The server is unavailable. Please try again.';
        }
        throw ApiException(message);
      }
      return jsonDecode(response.body);
    } on TimeoutException {
      throw const ApiException('The search timed out. Please try again.');
    } on http.ClientException {
      throw const ApiException(
        'Cannot reach the server. Check your connection and try again.',
      );
    } on FormatException {
      throw const ApiException('The server returned an unreadable response.');
    }
  }

  Future<List<AddressSuggestion>> suggestions(String address) async {
    final body = await _get('/search/addresses', {
      'address': address,
      'limit': '5',
    });
    return (body as List)
        .map((item) => AddressSuggestion.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<ParcelDetails> parcel(
    String address, {
    required double density,
    AddressSuggestion? selection,
    int? objectId,
  }) async {
    final body = await _get('/search/parcel-details', {
      'address': address,
      'density': '$density',
      if (objectId != null) 'object_id': '$objectId',
      if (selection != null) ...{
        'latitude': '${selection.latitude}',
        'longitude': '${selection.longitude}',
      },
    });
    return ParcelDetails.fromJson(body as Map<String, dynamic>);
  }

  void close() => _client.close();
}
