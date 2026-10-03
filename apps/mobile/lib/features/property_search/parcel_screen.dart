import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

import '../../core/api_client.dart';
import '../../shared/widgets/dashboard_background.dart';
import '../../shared/widgets/glass_card.dart';
import 'models/property.dart';

class ParcelScreen extends StatefulWidget {
  const ParcelScreen({
    super.key,
    required this.api,
    required this.address,
    required this.density,
    this.selection,
  });

  final ApiClient api;
  final String address;
  final double density;
  final AddressSuggestion? selection;

  @override
  State<ParcelScreen> createState() => _ParcelScreenState();
}

class _ParcelScreenState extends State<ParcelScreen> {
  ParcelDetails? _parcel;
  Object? _error;
  bool _loading = true;
  List<ParcelCandidate> _candidates = [];
  int? _objectId;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final parcel = await widget.api.parcel(
        widget.address,
        density: widget.density,
        selection: widget.selection,
        objectId: _objectId,
      );
      if (!mounted) return;
      setState(() {
        _parcel = parcel;
        _loading = false;
      });
    } on ParcelSelectionRequired catch (error) {
      if (!mounted) return;
      setState(() {
        _candidates = error.candidates;
        _loading = false;
        _objectId = null;
      });
    } catch (error) {
      if (!mounted) return;
      setState(() {
        _error = error;
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(
      automaticallyImplyLeading: false,
      title: TextButton.icon(
        onPressed: () => Navigator.of(context).pop(),
        icon: const Icon(CupertinoIcons.back),
        label: const Text('Back to search'),
      ),
    ),
    body: DashboardBackground(
      child: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 720),
            child: ListView(
              padding: const EdgeInsets.all(20),
              children: [
                Text(
                  'Property details',
                  style: Theme.of(context).textTheme.headlineLarge,
                ),
                const SizedBox(height: 12),
                Text(widget.address),
                const SizedBox(height: 24),
                _buildDetails(context),
              ],
            ),
          ),
        ),
      ),
    ),
  );

  Widget _buildDetails(BuildContext context) {
    if (_loading) {
      return const Column(
        children: [
          CircularProgressIndicator(),
          SizedBox(height: 16),
          Text('Loading parcel details…'),
        ],
      );
    }
    if (_error != null) {
      final error = _error;
      return GlassCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              error is ApiException
                  ? error.message
                  : 'Could not load this property. Please try again.',
            ),
            TextButton(onPressed: _load, child: const Text('Try again')),
          ],
        ),
      );
    }
    if (_candidates.isNotEmpty && _objectId == null) {
      return GlassCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Choose a parcel',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 12),
            const Text('Multiple parcels found. Choose an address or unit.'),
            const SizedBox(height: 16),
            for (final candidate in _candidates)
              Material(
                type: MaterialType.transparency,
                child: ListTile(
                  contentPadding: EdgeInsets.zero,
                  title: Text(candidate.address),
                  subtitle: Text(
                    'Parcel ${candidate.parcelId}\n${candidate.owner}',
                  ),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () {
                    _objectId = candidate.objectId;
                    _load();
                  },
                ),
              ),
          ],
        ),
      );
    }
    final parcel = _parcel!;
    return GlassCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (_candidates.isNotEmpty)
            TextButton(
              onPressed: () => setState(() {
                _objectId = null;
                _parcel = null;
              }),
              child: const Text('Choose another parcel'),
            ),
          for (final field in [
            ('Parcel record address', parcel.address),
            ('Parcel ID', parcel.parcelId),
            ('Zoning · City of Boulder dataset', parcel.zoning.label),
            ('Owner', parcel.owner),
            (
              'Parcel area',
              parcel.acres == null
                  ? 'Area unavailable'
                  : '${parcel.acres!.toStringAsFixed(2)} acres',
            ),
            (
              'Square feet',
              parcel.squareFeet?.toStringAsFixed(0) ?? 'Area unavailable',
            ),
            (
              'Housing allocation',
              '${(widget.density * 100).round()}% of assumed parking area',
            ),
          ]) ...[
            Text(field.$1, style: Theme.of(context).textTheme.bodySmall),
            const SizedBox(height: 4),
            SelectableText(
              field.$2,
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 20),
          ],
        ],
      ),
    );
  }
}
