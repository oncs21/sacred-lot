import asyncio
import runpy
import sqlite3
from pathlib import Path

import httpx
import pytest

from app.core.config import Settings
from app.integrations import addresses
from app.main import app

IMPORTER = runpy.run_path(
    str(Path(__file__).resolve().parents[3] / "scripts/import_addresses.py")
)


@pytest.fixture
def database(tmp_path, monkeypatch):
    output = tmp_path / "addresses.sqlite"
    IMPORTER["import_records"](
        [
            {
                "AddrFull": street,
                "PlaceName": "BOULDER",
                "Zipcode": "80302",
                "Latitude": 40.017,
                "Longitude": -105.275,
                "ParcelID": "fixture",
            }
            for street in ["1820 15TH ST", "1820 15TH ST UNIT 2"]
        ],
        output,
        "synthetic fixture",
    )
    monkeypatch.setattr(
        addresses, "get_settings", lambda: Settings(address_database=output)
    )

    def reject_network(*args, **kwargs):
        raise AssertionError("Local search must not use the network")

    monkeypatch.setattr(
        httpx.AsyncHTTPTransport, "handle_async_request", reject_network
    )
    return output


def request(params):
    async def get():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            return await client.get("/search/addresses", params=params)

    return asyncio.run(get())


def test_contract_and_limit(database):
    response = request({"address": " 1820 15th street Boulder ", "limit": 1})
    assert response.status_code == 200
    assert response.json() == [
        {
            "address": "1820 15TH ST, BOULDER, CO, 80302",
            "latitude": 40.017,
            "longitude": -105.275,
        }
    ]
    assert len(request({"address": "1820 15"}).json()) == 2


@pytest.mark.parametrize("query", ["unknown avenue", "***", '" OR --'])
def test_empty_results(database, query):
    response = request({"address": query})
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize(
    "params",
    [
        {},
        {"address": "  "},
        {"address": "ab"},
        {"address": "x" * 201},
        {"address": "Boulder", "limit": 11},
    ],
)
def test_validation(database, params):
    assert request(params).status_code == 422


def test_bounds(database, monkeypatch):
    monkeypatch.setattr(
        addresses,
        "get_settings",
        lambda: Settings(address_database=database, geocoding_bbox="-125,32,-114,42"),
    )
    assert request({"address": "1820"}).json() == []


@pytest.mark.parametrize("state", ["missing", "corrupt", "wrong-version"])
def test_database_failure(database, state):
    if state == "missing":
        database.unlink()
    elif state == "corrupt":
        database.write_bytes(b"not sqlite")
    else:
        with sqlite3.connect(database) as connection:
            connection.execute(
                "UPDATE metadata SET value = '2' WHERE key = 'schema_version'"
            )
    response = request({"address": "1820"})
    assert response.status_code == 503
    assert response.json()["detail"]["error_code"] == "ADDRESS_DATABASE_UNAVAILABLE"
    if state == "missing":
        assert not database.exists()
