from copy import deepcopy

from app.integrations.parcels import consolidate_parcel_records
from app.core.address_search import normalize


def record(object_id=1, owner="Owner A"):
    return {
        "attributes": {
            "OBJECTID": object_id, "parcel_id": "157509403020",
            "countyName": "Boulder", "situsAdd": "1926 CENTAUR CIR",
            "owner": owner, "landAcres": 0.1,
        },
        "geometry": {"rings": [[[0, 0], [0, 1], [1, 0], [0, 0]]]},
    }


def test_combines_same_parcel_and_preserves_owner_entries():
    records = [record(), record(2, "Owner B"), record(3, "Owner A")]
    original = deepcopy(records)
    result = consolidate_parcel_records(records)
    assert len(result) == 1
    assert result[0]["attributes"]["owner"] == "Owner A; Owner B"
    assert result[0]["geometry"] == records[0]["geometry"]
    assert records == original


def test_distinct_parcels_remain_ambiguous():
    other = record(2)
    other["attributes"]["parcel_id"] = "different"
    assert len(consolidate_parcel_records([record(), other])) == 2


def test_conflicting_geometry_or_area_is_not_combined():
    for field in ("geometry", "area"):
        other = record(2)
        if field == "geometry":
            other["geometry"] = {"rings": []}
        else:
            other["attributes"]["landAcres"] = 2
        assert len(consolidate_parcel_records([record(), other])) == 2


def test_missing_parcel_identity_is_not_combined():
    item = record()
    item["attributes"]["parcel_id"] = None
    assert len(consolidate_parcel_records([item, deepcopy(item)])) == 2


def test_circle_matches_abbreviated_street_type():
    assert normalize("1926 Centaur Circle Lafayette") == normalize("1926 Centaur CIR Lafayette")


def test_picker_candidates_and_selected_parcel(monkeypatch):
    import asyncio
    import httpx
    import pytest
    from app.core.exceptions import APIException
    from app.integrations import parcels
    from app.services import analysis

    first = record()
    second = record(2, 'Owner B')
    second['attributes']['parcel_id'] = 'second'
    second['attributes']['landAcres'] = 0
    second['attributes']['situsAdd'] = '550 MCCASLIN B'
    client_type = httpx.AsyncClient
    monkeypatch.setattr(parcels.httpx, 'AsyncClient', lambda **kwargs: client_type(
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json={'features': [first, second]})), **kwargs,
    ))
    with pytest.raises(APIException) as error:
        asyncio.run(parcels.fetch_parcel_information(40, -105))
    assert [c['object_id'] for c in error.value.detail['candidates']] == [1, 2]
    result = asyncio.run(analysis.run_property_feasibility('550', latitude=40, longitude=-105, object_id=2))
    assert result['parcel_id'] == 'second'
    assert result['total_acres'] is None
    assert result['total_sqft'] is None
    assert result['units_yield'] is None
    with pytest.raises(APIException) as error:
        asyncio.run(parcels.fetch_parcel_information(40, -105, object_id=999))
    assert error.value.status_code == 404
