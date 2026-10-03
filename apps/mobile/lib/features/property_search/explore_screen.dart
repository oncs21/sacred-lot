import 'dart:async';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

import '../../core/api_client.dart';
import '../../shared/widgets/dashboard_background.dart';
import '../../shared/widgets/glass_card.dart';
import 'models/property.dart';
import 'parcel_screen.dart';

class ExploreScreen extends StatefulWidget {
  const ExploreScreen({super.key, required this.api});

  final ApiClient api;

  @override
  State<ExploreScreen> createState() => _ExploreScreenState();
}

class _ExploreScreenState extends State<ExploreScreen> {
  final _address = TextEditingController();
  Timer? _debounce;
  int _revision = 0;
  List<AddressSuggestion> _suggestions = [];
  bool _loading = false;
  bool _searched = false;
  String? _error;
  double _density = .3;
  AddressSuggestion? _selection;

  @override
  void dispose() {
    _debounce?.cancel();
    _address.dispose();
    super.dispose();
  }

  void _changed(String value) {
    _selection = null;
    _debounce?.cancel();
    final revision = ++_revision;
    final query = value.trim();
    setState(() {
      _suggestions = [];
      _error = null;
      _searched = false;
      _loading = query.length >= 3;
    });
    if (query.length < 3) return;
    _debounce = Timer(const Duration(milliseconds: 250), () async {
      try {
        final results = await widget.api.suggestions(query);
        if (!mounted || revision != _revision) return;
        setState(() {
          _suggestions = results;
          _loading = false;
          _searched = true;
        });
      } catch (error) {
        if (!mounted || revision != _revision) return;
        setState(() {
          _loading = false;
          _error = error is ApiException
              ? error.message
              : 'Could not load suggestions. You can still search an address.';
        });
      }
    });
  }

  void _select(AddressSuggestion suggestion) {
    _selection = suggestion;
    _debounce?.cancel();
    _revision++;
    _address.text = suggestion.address;
    _address.selection = TextSelection.collapsed(offset: _address.text.length);
    setState(() {
      _suggestions = [];
      _loading = false;
      _searched = false;
      _error = null;
    });
    FocusScope.of(context).unfocus();
  }

  void _search() {
    final address = _address.text.trim();
    if (address.length < 3) return;
    _debounce?.cancel();
    _revision++;
    setState(() => _loading = false);
    FocusScope.of(context).unfocus();
    Navigator.of(context).push(
      CupertinoPageRoute<void>(
        builder: (_) => ParcelScreen(
          api: widget.api,
          address: address,
          density: _density,
          selection: _selection,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    body: DashboardBackground(
      child: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 720),
            child: ListView(
              padding: const EdgeInsets.all(20),
              children: [
                const SizedBox(height: 24),
                Text(
                  'Explore',
                  style: Theme.of(context).textTheme.headlineLarge,
                ),
                const SizedBox(height: 12),
                const Text('Search by street address.'),
                const SizedBox(height: 28),
                GlassCard(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      TextField(
                        controller: _address,
                        maxLength: 200,
                        textInputAction: TextInputAction.search,
                        onChanged: _changed,
                        onSubmitted: (_) => _search(),
                        decoration: InputDecoration(
                          labelText: 'Property address',
                          hintText: 'Street address, city',
                          counterText: '',
                          border: const OutlineInputBorder(),
                          suffixIcon: IconButton(
                            tooltip: 'Search property',
                            onPressed: _address.text.trim().length >= 3
                                ? _search
                                : null,
                            icon: const Icon(Icons.search),
                          ),
                        ),
                      ),
                      const SizedBox(height: 12),
                      if (_loading) const LinearProgressIndicator(),
                      if (_address.text.trim().length < 3)
                        const Text(
                          'Enter 3 or more characters to see suggestions.',
                        ),
                      if (_error != null) Text(_error!, semanticsLabel: _error),
                      if (_searched && _suggestions.isEmpty)
                        const Text(
                          'No suggestions. Search with the address entered.',
                        ),
                      for (final suggestion in _suggestions)
                        Material(
                          type: MaterialType.transparency,
                          child: ListTile(
                            contentPadding: EdgeInsets.zero,
                            leading: const Icon(Icons.location_on_outlined),
                            title: Text(suggestion.address),
                            trailing: const Icon(Icons.north_west, size: 18),
                            onTap: () => _select(suggestion),
                          ),
                        ),
                    ],
                  ),
                ),
                const SizedBox(height: 20),
                GlassCard(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Housing allocation',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        '${(_density * 100).round()}% of assumed parking area',
                      ),
                      Slider(
                        value: _density,
                        min: .1,
                        max: 1,
                        divisions: 18,
                        semanticFormatterCallback: (value) =>
                            '${(value * 100).round()} percent of assumed parking area',
                        onChanged: (value) => setState(() => _density = value),
                      ),
                      const Text(
                        'Assumes parking covers 65% of the parcel. Actual usable area needs verification.',
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    ),
  );
}
