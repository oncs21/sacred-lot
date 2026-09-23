import httpx

from app.core.exceptions import APIException
from app.schemas.property import ParcelDataSchema


async def fetch_parcel_information(lat: float, long: float) -> ParcelDataSchema:
    url = "https://gis.colorado.gov/public/rest/services/Address_and_Parcel/Colorado_Public_Parcels/FeatureServer/0/query"
    params = {
        "geometry": f"{long},{lat}",
        "geometryType": "esriGeometryPoint",
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
        features = data.get("features", [])

        if not features:
            raise APIException(
                status_code=404,
                error_code="PARCEL_NOT_FOUND",
                message=f"No spatial match for coordinates: lat={lat}, lon={long}",
                user_message="No official parcel record was found for this specific location."
            )

        feature = features[0]
        attrs = feature.get("attributes", {})
        geometry = feature.get("geometry", {})

        acres = attrs.get("landAcres") or 0.0
        sqft = attrs.get("landSqft")

        if sqft is None or sqft == 0:
            sqft = acres * 43560.00

        return ParcelDataSchema(
            object_id=attrs.get("OBJECTID"),
            parcel_id=attrs.get("parcel_id", "UNKNOWN"),
            county_name=attrs.get("countyName", "Unknown County"),
            address=attrs.get("situsAdd", "Unmapped Address"),
            city=attrs.get("sitAddCty", "Unknown City"),
            owner=attrs.get("owner", "Private Owner"),
            land_acres=round(acres, 3),
            calculated_sqft=round(sqft, 2),
            zoning_code=attrs.get("zoningCode") or "MU-3",
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