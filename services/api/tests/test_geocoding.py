import asyncio
from unittest.mock import AsyncMock

import httpx
import pytest

from app.core.exceptions import APIException
from app.integrations import geocoding


@pytest.fixture
def client(monkeypatch):
    mock = AsyncMock(spec=httpx.AsyncClient)
    mock.__aenter__.return_value = mock
    monkeypatch.setattr(geocoding.httpx, "AsyncClient", lambda: mock)
    return mock


def feature(longitude=-105.278, latitude=40.019):
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [longitude, latitude]},
        "properties": {},
    }


def test_returns_latitude_then_longitude_from_first_match(client):
    client.get.return_value = httpx.Response(
        200, json={"features": [feature(), feature(-104.99, 39.74)]}
    )

    coordinates = asyncio.run(geocoding.fetch_coordinates("Boulder, CO"))

    assert coordinates == (40.019, -105.278)
    client.get.assert_awaited_once()


def test_uses_https_and_encodes_address_as_query_parameter(client):
    address = "1820 15th St & Walnut, Boulder, CO #2"
    client.get.return_value = httpx.Response(200, json={"features": [feature()]})

    asyncio.run(geocoding.fetch_coordinates(address))

    args, kwargs = client.get.call_args
    endpoint = httpx.URL(args[0])
    assert endpoint.scheme == "https"
    assert endpoint.host == "photon.komoot.io"
    assert endpoint.path.rstrip("/") == "/api"
    assert not endpoint.query
    request = httpx.Request("GET", endpoint, params=kwargs["params"])
    assert request.url.params.get_list("q") == [address]
    assert request.url.params["limit"] == "1"


def test_reports_address_not_found(client):
    client.get.return_value = httpx.Response(200, json={"features": []})

    with pytest.raises(APIException) as error:
        asyncio.run(geocoding.fetch_coordinates("Unknown address"))

    assert error.value.status_code == 404
    assert error.value.error_code == "ADDRESS_NOT_FOUND"
    assert error.value.user_message


@pytest.mark.parametrize("status_code", [403, 429, 500, 503])
def test_maps_unsuccessful_upstream_status_to_service_unavailable(client, status_code):
    client.get.return_value = httpx.Response(status_code, text="Upstream unavailable")

    with pytest.raises(APIException) as error:
        asyncio.run(geocoding.fetch_coordinates("Boulder, CO"))

    assert error.value.status_code == 503
    assert error.value.error_code == "GEOCODING_SERVICE_DOWN"
    assert str(status_code) in error.value.message


@pytest.mark.parametrize("error_type", [httpx.ConnectError, httpx.ReadTimeout])
def test_maps_transport_failure_to_application_error(client, error_type):
    client.get.side_effect = error_type("Connection failed")

    with pytest.raises(APIException) as error:
        asyncio.run(geocoding.fetch_coordinates("Boulder, CO"))

    assert error.value.status_code == 500
    assert error.value.error_code == "NETWORK_ERROR"
    client.__aexit__.assert_awaited_once()


@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(200, text="not JSON"),
        httpx.Response(
            200,
            json={
                "features": [
                    feature() | {"geometry": {"type": "Point", "coordinates": []}}
                ]
            },
        ),
        httpx.Response(200, json={}),
        httpx.Response(200, json=[]),
        httpx.Response(200, json={"features": None}),
        httpx.Response(200, json={"features": [None]}),
        httpx.Response(200, json={"features": [feature("invalid", 40)]}), # pyright: ignore[reportArgumentType]
        httpx.Response(200, json={"features": [feature(True, 40)]}), # pyright: ignore[reportArgumentType]
        httpx.Response(200, json={"features": [feature(-181, 40)]}),
        httpx.Response(200, json={"features": [feature(-105, 91)]}),
    ],
    ids=[
        "invalid-json",
        "missing-coordinate-pair",
        "missing-features",
        "invalid-root",
        "null-features",
        "invalid-feature",
        "string-coordinate",
        "boolean-coordinate",
        "invalid-longitude",
        "invalid-latitude",
    ],
)
def test_maps_malformed_upstream_payload_to_application_error(client, response):
    client.get.return_value = response

    with pytest.raises(APIException) as error:
        asyncio.run(geocoding.fetch_coordinates("Boulder, CO"))

    assert error.value.status_code == 502
    assert error.value.error_code == "INVALID_GEOCODING_RESPONSE"
    assert error.value.user_message
