import asyncio

import httpx
import pytest

from app.core.config import Settings
from app.integrations import geocoding
from app.main import app
from app.routers import search as search_router

HTTPClient = httpx.AsyncClient


def feature(name="Grace Commons Church", longitude=-105.278, latitude=40.019):
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [longitude, latitude]},
        "properties": {
            "name": name,
            "housenumber": "1820",
            "street": "15th Street",
            "city": "Boulder",
            "state": "Colorado",
            "postcode": "80302",
        },
    }


@pytest.fixture
def photon(monkeypatch):
    monkeypatch.setattr(
        search_router, "fetch_address_suggestions", geocoding.fetch_address_suggestions
    )
    state = {
        "response": httpx.Response(200, json={"features": [feature()]}),
        "requests": [],
    }

    def handler(request):
        state["requests"].append(request)
        response = state["response"]
        if isinstance(response, Exception):
            raise response
        return response

    monkeypatch.setattr(
        geocoding.httpx,
        "AsyncClient",
        lambda **kwargs: HTTPClient(
            transport=httpx.MockTransport(handler),
            **kwargs,
        ),
    )
    monkeypatch.setattr(
        geocoding,
        "get_settings",
        lambda: Settings(
            geocoding_bbox="-109.06,36.99,-102.04,41.00",
        ),
    )
    return state


def get_suggestions(params):
    async def request():
        async with HTTPClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            return await client.get("/search/addresses", params=params)

    return asyncio.run(request())


def test_returns_formatted_addresses_and_coordinates(photon):
    photon["response"] = httpx.Response(
        200, json={"features": [feature(), feature("Another church")]}
    )
    response = get_suggestions({"address": "  15th & Walnut #2  "})
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0] == {
        "address": "Grace Commons Church, 1820 15th Street, Boulder, Colorado, 80302",
        "latitude": 40.019,
        "longitude": -105.278,
    }
    request = photon["requests"][0]
    assert request.url.scheme == "https"
    assert request.url.params["q"] == "15th & Walnut #2"
    assert request.url.params["limit"] == "5"
    assert request.url.params["bbox"] == "-109.06,36.99,-102.04,41.00"


@pytest.mark.parametrize(
    "params",
    [
        {},
        {"address": "ab"},
        {"address": "   "},
        {"address": "x" * 201},
        {"address": "Boulder", "limit": 0},
        {"address": "Boulder", "limit": 11},
        {"address": "Boulder", "limit": "abc"},
    ],
)
def test_rejects_invalid_queries_without_contacting_photon(photon, params):
    assert get_suggestions(params).status_code == 422
    assert photon["requests"] == []


def test_returns_empty_list_when_no_matches(photon):
    photon["response"] = httpx.Response(200, json={"features": []})
    response = get_suggestions({"address": "Unknown"})
    assert response.status_code == 200
    assert response.json() == []


def test_filters_outside_area_deduplicates_and_caps_results(photon):
    photon["response"] = httpx.Response(
        200,
        json={
            "features": [
                feature("Outside", longitude=-120),
                feature(),
                feature(),
                feature("Second"),
                feature("Third"),
            ]
        },
    )
    response = get_suggestions({"address": "church", "limit": 2})
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[1]["address"].startswith("Second,")
    assert photon["requests"][0].url.params["limit"] == "2"


def test_supports_partial_address_properties(photon):
    item = feature()
    item["properties"] = {"street": "15th Street", "city": "Boulder"}
    photon["response"] = httpx.Response(200, json={"features": [item]})
    assert (
        get_suggestions({"address": "15th"}).json()[0]["address"]
        == "15th Street, Boulder"
    )


@pytest.mark.parametrize(
    "upstream,status,code",
    [
        (httpx.Response(429), 503, "GEOCODING_SERVICE_DOWN"),
        (httpx.ReadTimeout("timeout"), 503, "GEOCODING_SERVICE_DOWN"),
        (httpx.Response(200, text="not JSON"), 502, "INVALID_GEOCODING_RESPONSE"),
        (
            httpx.Response(200, json={"features": None}),
            502,
            "INVALID_GEOCODING_RESPONSE",
        ),
        (
            httpx.Response(200, json={"features": [feature(latitude=100)]}),
            502,
            "INVALID_GEOCODING_RESPONSE",
        ),
    ],
)
def test_returns_structured_upstream_errors(photon, upstream, status, code):
    photon["response"] = upstream
    response = get_suggestions({"address": "Boulder"})
    assert response.status_code == status
    assert response.json()["detail"]["error_code"] == code
