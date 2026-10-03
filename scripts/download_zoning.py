import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

SOURCE = "https://gis.bouldercolorado.gov/ags_svr1/rest/services/plan/ZoningDistricts/MapServer/0"
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "data/processed/boulder_zoning.geojson"


def download(output: Path) -> None:
    params = {
        "where": "1=1",
        "outFields": "OBJECTID,ZONING,ZNDESC,ZONINGDISTPURPOSE",
        "outSR": "4326",
        "f": "geojson",
    }
    with urlopen(Request(f"{SOURCE}/query?{urlencode(params)}", headers={"User-Agent": "SacredLot/0.1"}), timeout=60) as response:
        data = json.load(response)
    with urlopen(Request(f"{SOURCE}/query?where=1%3D1&returnCountOnly=true&f=json", headers={"User-Agent": "SacredLot/0.1"}), timeout=30) as response:
        count = json.load(response)["count"]
    if data.get("type") != "FeatureCollection" or len(data.get("features", [])) != count:
        raise ValueError("Zoning download is incomplete")
    if data.get("exceededTransferLimit") or not count:
        raise ValueError("Zoning download is empty or truncated")
    data["metadata"] = {
        "source_url": SOURCE,
        "jurisdiction": "City of Boulder",
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "coordinate_system": "EPSG:4326",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(".tmp")
    temporary.write_text(json.dumps(data), encoding="utf-8")
    temporary.replace(output)
    print(f"Saved {count} zoning polygons to {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    download(parser.parse_args().output)
