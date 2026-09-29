from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import analysis


@pytest.mark.parametrize("selected", [True, False])
def test_selected_location_bypasses_geocoding(monkeypatch, selected):
    geocode = AsyncMock(return_value=(39.0, -104.0))
    parcel_lookup = AsyncMock(return_value=SimpleNamespace(
        parcel_id="123", owner="Owner", address="Parcel address", city="Boulder",
        land_acres=1, calculated_sqft=43560, geometry_rings=[],
    ))
    monkeypatch.setattr(analysis, "fetch_coordinates", geocode)
    monkeypatch.setattr(analysis, "fetch_parcel_information", parcel_lookup)
    coordinates = {"latitude": 40.01738, "longitude": -105.27489} if selected else {}
    with TestClient(app) as client:
        response = client.get("/search/parcel-details", params={
            "address": "Selected address", "density": 0.3, **coordinates,
        })
    assert response.status_code == 200
    if selected:
        geocode.assert_not_awaited()
        parcel_lookup.assert_awaited_once_with(40.01738, -105.27489)
    else:
        geocode.assert_awaited_once_with("Selected address")
        parcel_lookup.assert_awaited_once_with(39.0, -104.0)


@pytest.mark.parametrize("coordinates", [
    {"latitude": 40}, {"longitude": -105},
    {"latitude": 91, "longitude": -105},
    {"latitude": 40, "longitude": -181},
    {"latitude": "nan", "longitude": -105},
])
def test_invalid_coordinates_rejected(monkeypatch, coordinates):
    lookup = AsyncMock()
    monkeypatch.setattr(analysis, "fetch_parcel_information", lookup)
    with TestClient(app) as client:
        response = client.get("/search/parcel-details", params={
            "address": "Selected address", "density": 0.3, **coordinates,
        })
    assert response.status_code == 422
    lookup.assert_not_awaited()
