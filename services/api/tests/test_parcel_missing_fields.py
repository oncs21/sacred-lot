import asyncio

import httpx
import pytest

from app.integrations import parcels
from app.schemas.feasibility import FeasibilityResponseSchema
from app.services.analysis import run_property_feasibility


@pytest.fixture
def attributes(monkeypatch):
    attributes = {
        "OBJECTID": 1,
        "parcel_id": "123",
        "countyName": "Boulder",
        "situsAdd": "123 Main St",
        "sitAddCty": "Boulder",
        "owner": "Recorded owner",
        "landAcres": 1,
    }
    client_type = httpx.AsyncClient

    def respond(request):
        return httpx.Response(200, json={"features": [{
            "attributes": attributes, "geometry": {"rings": []},
        }]})

    monkeypatch.setattr(
        parcels.httpx, "AsyncClient",
        lambda **kwargs: client_type(transport=httpx.MockTransport(respond), **kwargs),
    )
    return attributes


@pytest.mark.parametrize("value", [None, "", "missing"])
def test_missing_parcel_fields_do_not_break_response(attributes, value):
    for field in ("parcel_id", "countyName", "owner", "situsAdd", "sitAddCty"):
        if value == "missing":
            attributes.pop(field)
        else:
            attributes[field] = value
    parcel = asyncio.run(parcels.fetch_parcel_information(40, -105))
    assert parcel.parcel_id == "Unavailable"
    assert parcel.county_name == "County unavailable"
    assert parcel.owner == "Owner unavailable"
    result = asyncio.run(run_property_feasibility("123 Main St", latitude=40, longitude=-105))
    response = FeasibilityResponseSchema.model_validate(result)
    assert response.owner == "Owner unavailable"
    assert response.parcel_id == "Unavailable"


@pytest.mark.parametrize("value", [None, "", "missing", "RE"])
def test_zoning_only_comes_from_source(attributes, value):
    if value != "missing":
        attributes["zoningCode"] = value
    parcel = asyncio.run(parcels.fetch_parcel_information(40, -105))
    assert parcel.zoning_code == ("RE" if value == "RE" else None)
