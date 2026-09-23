import runpy
import sqlite3
from pathlib import Path

import pytest

from app.core.address_search import search

IMPORTER = runpy.run_path(
    str(Path(__file__).resolve().parents[3] / "scripts/import_addresses.py")
)


def record(address="1820 15TH ST", **changes):
    return {
        "AddrFull": address,
        "PlaceName": "BOULDER",
        "Zipcode": "80302",
        "Latitude": 40.017,
        "Longitude": -105.275,
        "ParcelID": "test-parcel",
        **changes,
    }


def test_import_and_prefix_search_preserve_units_and_missing_parcels(tmp_path):
    output = tmp_path / "addresses.sqlite"
    counts = IMPORTER["import_records"](
        [
            record(),
            record(),
            record("1820 15TH ST UNIT 2", ParcelID=None),
            record(""),
            record(Latitude=float("nan")),
            record(Longitude=0),
        ],
        output,
        "synthetic fixture",
    )
    assert counts == {
        "read": 6,
        "imported": 2,
        "duplicates": 1,
        "missing_address": 1,
        "invalid_coordinates": 2,
        "missing_parcel_id": 1,
    }
    with sqlite3.connect(output) as connection:
        results = search(connection, "1820 15th street Boulder")
        assert len(results) == 2
        assert any("UNIT 2" in result[0] and result[3] == "" for result in results)
        assert len(search(connection, "1820 15", 1)) == 1
        assert search(connection, '" OR * --') == []
        assert search(connection, "") == []


def test_failure_does_not_publish_database(tmp_path):
    def broken_records():
        yield record()
        raise RuntimeError("read failed")

    output = tmp_path / "addresses.sqlite"
    with pytest.raises(RuntimeError):
        IMPORTER["import_records"](broken_records(), output, "fixture")
    assert list(tmp_path.iterdir()) == []


def test_existing_database_is_not_overwritten(tmp_path):
    output = tmp_path / "addresses.sqlite"
    output.write_bytes(b"existing data")
    with pytest.raises(FileExistsError):
        IMPORTER["import_records"]([], output, "fixture")
    assert output.read_bytes() == b"existing data"


def test_statewide_import_preserves_distinct_cities_and_records_coverage(tmp_path):
    import json

    output = tmp_path / "statewide.sqlite"
    IMPORTER["import_records"](
        [
            record(County="Boulder"),
            record(
                PlaceName="DENVER", County="Denver", Latitude=39.74, Longitude=-104.99
            ),
        ],
        output,
        "fixture",
    )
    with sqlite3.connect(output) as connection:
        assert len(search(connection, "1820 15th")) == 2
        assert "DENVER" in search(connection, "1820 15th Denver")[0][0]
        metadata = dict(connection.execute("SELECT key,value FROM metadata"))
        assert metadata["layer"] == "Colorado_Public_Address_Composite"
        assert json.loads(metadata["county_counts"]) == {"BOULDER": 1, "DENVER": 1}
