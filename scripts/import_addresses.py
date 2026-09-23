import argparse
import json
import math
import os
import sqlite3
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import pyogrio
from pyogrio.raw import read

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services/api"))

from app.core.address_search import normalize

DEFAULT_LAYER = "Colorado_Public_Address_Composite"

FIELDS = [
    "County",
    "SAUID",
    "AddrFull",
    "PlaceName",
    "Zipcode",
    "Latitude",
    "Longitude",
    "ParcelID",
]


def read_records(source: Path, layer: str = DEFAULT_LAYER):

    info = pyogrio.read_info(source, layer=layer)
    if info["crs"] != "EPSG:4326" or not set(FIELDS).issubset(info["fields"]):
        raise ValueError(
            f"{layer} has an unsupported coordinate system or missing fields"
        )
    for offset in range(0, info["features"], 50000):
        metadata, _, _, arrays = read(
            source,
            layer=layer,
            columns=FIELDS,
            read_geometry=False,
            skip_features=offset,
            max_features=50000,
        )
        for values in zip(*arrays, strict=True):
            yield dict(zip(metadata["fields"], values, strict=True))


def text(value) -> str:
    return value.strip() if isinstance(value, str) else ""


def import_records(
    records, output: Path, source: str, layer: str = DEFAULT_LAYER
) -> dict:
    if output.exists():
        raise FileExistsError(
            f"Output already exists: {output}. Choose a new output path."
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix="addresses-", suffix=".sqlite", dir=output.parent
    )
    os.close(descriptor)
    counts = {
        "read": 0,
        "imported": 0,
        "missing_address": 0,
        "invalid_coordinates": 0,
        "duplicates": 0,
        "missing_parcel_id": 0,
    }
    counties = {}
    try:
        with sqlite3.connect(temporary) as connection:
            connection.executescript("""
                CREATE TABLE addresses (
                    id INTEGER PRIMARY KEY, source_id TEXT, address TEXT NOT NULL,
                    search_text TEXT NOT NULL, city TEXT NOT NULL, zipcode TEXT NOT NULL,
                    latitude REAL NOT NULL, longitude REAL NOT NULL, parcel_id TEXT NOT NULL,
                    UNIQUE(search_text, latitude, longitude, parcel_id)
                );
                CREATE VIRTUAL TABLE addresses_fts USING fts5(
                    search_text, content='addresses', content_rowid='id', prefix='2 3 4'
                );
                CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            """)
            for record in records:
                counts["read"] += 1
                street = text(record.get("AddrFull"))
                if not street or not normalize(street):
                    counts["missing_address"] += 1
                    continue
                try:
                    lat, lon = float(record["Latitude"]), float(record["Longitude"])
                except (ValueError, TypeError, KeyError):
                    counts["invalid_coordinates"] += 1
                    continue
                if not (
                    math.isfinite(lat)
                    and math.isfinite(lon)
                    and 36.99 <= lat <= 41.01
                    and -109.06 <= lon <= -102.04
                ):
                    counts["invalid_coordinates"] += 1
                    continue
                city, zipcode = (
                    text(record.get("PlaceName")),
                    text(record.get("Zipcode")),
                )
                address = ", ".join(
                    part for part in [street, city, "CO", zipcode] if part
                )
                parcel = text(record.get("ParcelID"))
                cursor = connection.execute(
                    "INSERT OR IGNORE INTO addresses "
                    "(source_id,address,search_text,city,zipcode,latitude,longitude,parcel_id) "
                    "VALUES (?,?,?,?,?,?,?,?)",
                    (
                        text(record.get("SAUID")),
                        address,
                        normalize(address),
                        city,
                        zipcode,
                        lat,
                        lon,
                        parcel,
                    ),
                )
                if cursor.rowcount:
                    county = text(record.get("County")).upper() or "UNKNOWN"
                    counties[county] = counties.get(county, 0) + 1
                    counts["imported"] += 1
                    counts["missing_parcel_id"] += not bool(parcel)
                else:
                    counts["duplicates"] += 1
            connection.execute(
                "INSERT INTO addresses_fts(addresses_fts) VALUES ('rebuild')"
            )
            metadata = {
                "source": source,
                "layer": layer,
                "county_counts": json.dumps(counties, sort_keys=True),
                "schema_version": "1",
                "imported_at": datetime.now(UTC).isoformat(),
                "counts": json.dumps(counts),
            }
            connection.executemany(
                "INSERT INTO metadata VALUES (?, ?)", metadata.items()
            )
            if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise ValueError("SQLite integrity check failed")
        connection.close()
        os.link(temporary, output)
        return counts
    finally:
        Path(temporary).unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(
        description="Import Colorado address points into a local search database"
    )
    parser.add_argument(
        "--source", type=Path, default=ROOT / "data/raw/Master_Address_Public.gdb"
    )
    parser.add_argument(
        "--output", type=Path, default=ROOT / "data/processed/addresses.sqlite"
    )
    parser.add_argument("--layer", default=DEFAULT_LAYER)
    args = parser.parse_args()
    counts = import_records(
        read_records(args.source, args.layer), args.output, str(args.source), args.layer
    )
    print(json.dumps(counts, indent=2))
    print(f"Database: {args.output}")


if __name__ == "__main__":
    main()
