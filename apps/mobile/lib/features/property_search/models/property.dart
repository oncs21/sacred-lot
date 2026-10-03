class AddressSuggestion {
  const AddressSuggestion({
    required this.address,
    required this.latitude,
    required this.longitude,
  });

  factory AddressSuggestion.fromJson(Map<String, dynamic> json) =>
      AddressSuggestion(
        address: json['address'] as String,
        latitude: (json['latitude'] as num).toDouble(),
        longitude: (json['longitude'] as num).toDouble(),
      );

  final String address;
  final double latitude;
  final double longitude;
}

class ParcelDetails {
  const ParcelDetails({
    required this.address,
    required this.parcelId,
    required this.owner,
    required this.acres,
    required this.squareFeet,
    this.zoning = const ZoningDetails(),
  });

  factory ParcelDetails.fromJson(Map<String, dynamic> json) => ParcelDetails(
    zoning: ZoningDetails.fromJson(json['zoning'] as Map<String, dynamic>?),
    address: json['address'] as String,
    parcelId: json['parcel_id'] as String,
    owner: json['owner'] as String,
    acres: (json['total_acres'] as num?)?.toDouble(),
    squareFeet: (json['total_sqft'] as num?)?.toDouble(),
  );

  final String address;
  final String parcelId;
  final String owner;
  final double? acres;
  final double? squareFeet;
  final ZoningDetails zoning;
}

class ParcelCandidate {
  const ParcelCandidate({
    required this.objectId,
    required this.parcelId,
    required this.address,
    required this.owner,
  });
  factory ParcelCandidate.fromJson(Map<String, dynamic> json) =>
      ParcelCandidate(
        objectId: json['object_id'] as int,
        parcelId: json['parcel_id'] as String,
        address: json['address'] as String,
        owner: json['owner'] as String,
      );
  final int objectId;
  final String parcelId;
  final String address;
  final String owner;
}

class ZoningDetails {
  const ZoningDetails({this.status = 'unavailable', this.districts = const []});
  factory ZoningDetails.fromJson(Map<String, dynamic>? json) => ZoningDetails(
    status: json?['status'] as String? ?? 'unavailable',
    districts: (json?['districts'] as List? ?? []).map((item) {
      final code = item['code'] as String;
      final description = item['description'] as String?;
      return description == null ? code : '$code — $description';
    }).toList(),
  );
  final String status;
  final List<String> districts;
  String get label => switch (status) {
    'matched' => districts.join('\n'),
    'partial' =>
      '${districts.join('\n')}\nOnly part of the parcel has mapped zoning.',
    'no_match' => 'No match in the City of Boulder dataset',
    _ => 'Zoning information unavailable',
  };
}
