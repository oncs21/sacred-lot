import json

import httpx

from app.core.exceptions import APIException
from app.schemas.property import ParcelDataSchema


def consolidate_parcel_records(features: list[dict]) -> list[dict]:
    parcels = {}
    for feature in features:
        attrs = feature.get("attributes", {})
        if not attrs.get("parcel_id") or not attrs.get("countyName"):
            return features
        identity = json.dumps(
            {
                "attributes": {key: value for key, value in attrs.items()
                               if key not in {"OBJECTID", "owner"}},
                "geometry": feature.get("geometry"),
            },
            sort_keys=True,
        )
        if identity not in parcels:
            parcels[identity] = ({**feature, "attributes": dict(attrs)}, [])
        record, owners = parcels[identity]
        owner = attrs.get("owner")
        if owner and owner not in owners:
            owners.append(owner)
        record["attributes"]["owner"] = "; ".join(owners) or "Owner unavailable"
    return [record for record, _ in parcels.values()]


async def fetch_parcel_information(lat: float, long: float, object_id: int | None = None) -> ParcelDataSchema:
    url = "https://gis.colorado.gov/public/rest/services/Address_and_Parcel/Colorado_Public_Parcels/FeatureServer/0/query"
    params = {
        "geometry": f"{long},{lat}",
        "geometryType": "esriGeometryPoint",
        "inSR": "4326",
        "outSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "*",
        "f": "json"
    }

    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            response = await client.get(
                url=url,
                params=params
            )

        if response.status_code != 200:
            raise APIException(
                status_code=503,
                error_code="STATE_GIS_UNAVAILABLE",
                message=f"Colorado GIS API returned status {response.status_code}",
                user_message="State parcel lookup service is temporarily unreachable."
            )

        data = response.json()
        features = consolidate_parcel_records(data.get("features", []))

        if not features:
            raise APIException(
                status_code=404,
                error_code="PARCEL_NOT_FOUND",
                message=f"No spatial match for coordinates: lat={lat}, lon={long}",
                user_message="No official parcel record was found for this specific location."
            )

        if object_id is not None:
            features = [f for f in features if f.get("attributes", {}).get("OBJECTID") == object_id]
            if not features:
                raise APIException(status_code=404, error_code="PARCEL_SELECTION_NOT_FOUND",
                                   user_message="This parcel is no longer available at this location. Search again.")

        if len(features) > 1:
            error = APIException(
                status_code=409,
                error_code="AMBIGUOUS_PARCEL",
                user_message="Multiple parcels match this location. Please confirm the parcel with the county.",
            )

            error.detail["candidates"] = [
                {"object_id": f["attributes"]["OBJECTID"],
                 "parcel_id": f["attributes"].get("parcel_id") or "Unavailable",
                 "address": f["attributes"].get("situsAdd") or "Address unavailable",
                 "owner": f["attributes"].get("owner") or "Owner unavailable"}
                for f in features
            ]
            raise error

        feature = features[0]
        attrs = feature.get("attributes", {})
        geometry = feature.get("geometry", {})

        acres = attrs.get("landAcres")
        sqft = attrs.get("landSqft")

        acres = acres if acres is not None and acres > 0 else None
        sqft = sqft if sqft is not None and sqft > 0 else None
        if sqft is None and acres is not None:
            sqft = acres * 43560.0
        if acres is None and sqft is not None:
            acres = sqft / 43560.0

        return ParcelDataSchema(
            object_id=attrs.get("OBJECTID"),
            parcel_id=attrs.get("parcel_id") or "Unavailable",
            county_name=attrs.get("countyName") or "County unavailable",
            address=attrs.get("situsAdd") or "Address unavailable",
            city=attrs.get("sitAddCty") or "City unavailable",
            owner=attrs.get("owner") or "Owner unavailable",
            land_acres=round(acres, 3) if acres is not None else None,
            calculated_sqft=round(sqft, 2) if sqft is not None else None,
            zoning_code=attrs.get("zoningCode") or None,
            zoning_desc=attrs.get("zoningDesc"),
            geometry_rings=geometry.get("rings", [])
        )

    except httpx.RequestError as e:
        raise APIException(
            status_code=500,
            error_code="NETWORK_FAILURE",
            message=f"Network exception connecting to Colorado GIS: {str(e)}",
            user_message="Network connectivity error while retrieving parcel boundaries."
        )
