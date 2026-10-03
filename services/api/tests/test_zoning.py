import json
from types import SimpleNamespace

import pytest

from app.integrations import zoning


def ring(x, y, size=1):
    return [[x,y], [x+size,y], [x+size,y+size], [x,y+size], [x,y]]


@pytest.fixture
def dataset(tmp_path, monkeypatch):
    path = tmp_path / 'zoning.geojson'
    path.write_text(json.dumps({
        'metadata': {'coordinate_system': 'EPSG:4326', 'source_url': 'https://example.test/zoning', 'retrieved_at': '2026-09-29'},
        'features': [
            {'properties': {'ZONING': code, 'ZNDESC': code},
             'geometry': {'type': 'Polygon', 'coordinates': [ring(x, 0)]}}
            for x, code in [(0, 'A'), (1, 'B')]
        ],
    }))
    monkeypatch.setattr(zoning, 'get_settings', lambda: SimpleNamespace(zoning_dataset=path))
    return path


def test_single_district_and_boundary_contact(dataset):
    result = zoning._lookup([ring(0, 0)])
    assert result.status == 'matched'
    assert [d.code for d in result.districts] == ['A']
    assert result.source_url == 'https://example.test/zoning'


def test_multiple_districts(dataset):
    result = zoning._lookup([ring(.5, 0)])
    assert result.status == 'matched'
    assert [d.code for d in result.districts] == ['A', 'B']


def test_partial_coverage(dataset):
    assert zoning._lookup([ring(1.5, 0)]).status == 'partial'


def test_no_match_does_not_assert_jurisdiction(dataset):
    result = zoning._lookup([ring(5, 5)])
    assert result.status == 'no_match'
    assert result.jurisdiction is None


def test_holes_are_excluded(dataset):
    result = zoning._lookup([ring(-1, -1, 4), ring(0, 0, 2)])
    assert result.status == 'no_match'


@pytest.mark.parametrize('failure', ['missing', 'invalid'])
def test_unavailable_dataset(dataset, failure):
    if failure == 'missing':
        dataset.unlink()
    else:
        dataset.write_text('not json')
    assert zoning._lookup([ring(0, 0)]).status == 'unavailable'


def test_invalid_parcel_geometry(dataset):
    assert zoning._lookup([]).status == 'unavailable'
    assert zoning._lookup([[[0, 0], [1, 1]]]).status == 'unavailable'


def test_repairs_zero_area_spike_in_source_ring(dataset):
    data = json.loads(dataset.read_text())
    data['features'][0]['geometry']['coordinates'] = [
        [[0,0], [1,0], [1,1], [.5,1], [.5,.5], [.5,1], [0,1], [0,0]]
    ]
    dataset.write_text(json.dumps(data))
    assert zoning._lookup([ring(.1,.1,.2)]).status == 'matched'
