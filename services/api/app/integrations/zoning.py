import json
import logging
from functools import lru_cache
from pathlib import Path

from shapely import STRtree, make_valid
from shapely.geometry import Polygon, shape
from shapely.ops import unary_union
from starlette.concurrency import run_in_threadpool

from app.core.config import get_settings
from app.schemas.zoning import ZoningDistrict, ZoningResult

logger = logging.getLogger(__name__)


@lru_cache(maxsize=2)
def _load(path: Path, modified: int):
    data = json.loads(path.read_text(encoding="utf-8"))
    metadata = data["metadata"]
    if metadata["coordinate_system"] != "EPSG:4326":
        raise ValueError("Zoning geometry must use EPSG:4326")
    geometries = []
    districts = []
    for feature in data["features"]:
        geometry = shape(feature["geometry"])
        if not geometry.is_valid:
            repaired = make_valid(geometry)
            if abs(repaired.area - geometry.area) > max(abs(geometry.area) * 1e-9, 1e-18):
                raise ValueError("Geometry repair changes zoning area")
            if repaired.geom_type == "GeometryCollection":
                repaired = unary_union([part for part in repaired.geoms if part.geom_type in {"Polygon", "MultiPolygon"}])
            geometry = repaired
        if geometry.geom_type not in {"Polygon", "MultiPolygon"} or geometry.is_empty or not geometry.is_valid:
            raise ValueError("Invalid zoning polygon")
        attributes = feature["properties"]
        districts.append(ZoningDistrict(code=attributes["ZONING"], description=attributes.get("ZNDESC")))
        geometries.append(geometry)
    if not geometries:
        raise ValueError("Empty zoning dataset")
    return STRtree(geometries), geometries, districts, metadata


def _lookup(rings: list) -> ZoningResult:
    try:
        if not rings:
            return ZoningResult(status="unavailable")
        parcel = Polygon()
        for ring in rings:
            if len(ring) < 4 or ring[0] != ring[-1]:
                raise ValueError("Parcel rings must be closed")
            polygon = Polygon(ring)
            if not polygon.is_valid or polygon.is_empty:
                raise ValueError("Invalid parcel geometry")
            parcel = parcel.symmetric_difference(polygon)
        if parcel.is_empty or parcel.area <= 0:
            raise ValueError("Empty parcel geometry")
        path = get_settings().zoning_dataset.expanduser().resolve()
        tree, geometries, districts, metadata = _load(path, path.stat().st_mtime_ns)
        intersections = []
        matches = {}
        for index in tree.query(parcel, predicate="intersects"):
            intersection = parcel.intersection(geometries[index])
            if intersection.area > 0:
                district = districts[index]
                matches[district.code] = district
                intersections.append(intersection)
        status = "no_match"
        if matches:
            covered = unary_union(intersections).area / parcel.area
            status = "matched" if covered >= .999999 else "partial"
        return ZoningResult(
            status=status,
            jurisdiction="City of Boulder" if matches else None,
            districts=[matches[code] for code in sorted(matches)],
            source_url=metadata["source_url"],
            retrieved_at=metadata["retrieved_at"],
        )
    except Exception:
        logger.exception("Zoning lookup unavailable")
        return ZoningResult(status="unavailable")


async def fetch_zoning(rings: list) -> ZoningResult:
    return await run_in_threadpool(_lookup, rings)
