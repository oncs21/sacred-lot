import httpx

from app.core.exceptions import APIException


async def fetch_coordinates(address: str):
    url = f"https://photon.komoot.io/api"
    params = {"q": address, "limit": 1}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)

        if response.status_code != 200:
            raise APIException(
                status_code=503,
                error_code="GEOCODING_SERVICE_DOWN",
                message=f"Photon API returned status {response.status_code}",
                user_message="Location lookup is temporarily unavailable. Please try again shortly.",
            )

        try:
            geojson = response.json()
            if not isinstance(geojson, dict):
                raise TypeError("Expected a GeoJSON object")

            features = geojson["features"]
            if not isinstance(features, list):
                raise TypeError("Expected a features array")

            if not features:
                raise APIException(
                    status_code=404,
                    error_code="ADDRESS_NOT_FOUND",
                    message=f"No spatial match for address query: '{address}'",
                    user_message="We couldn't find a matching address. Please check the street and city name.",
                )

            geometry = features[0]["geometry"]
            if geometry["type"] != "Point":
                raise ValueError("Expected Point geometry")

            coords = geometry["coordinates"]
            if not isinstance(coords, list) or len(coords) not in (2, 3):
                raise ValueError("Expected a coordinate pair with optional altitude")

            longitude, latitude = coords[:2]
            if (
                type(longitude) not in (int, float)
                or type(latitude) not in (int, float)
                or not -180 <= longitude <= 180
                or not -90 <= latitude <= 90
            ):
                raise ValueError(
                    "Coordinates must be numeric and within geographic bounds"
                )

            return latitude, longitude
        except (ValueError, KeyError, TypeError, IndexError) as exc:
            raise APIException(
                status_code=502,
                error_code="INVALID_GEOCODING_RESPONSE",
                message="Photon returned an invalid geocoding response.",
                user_message="Location lookup returned an invalid response. Please try again shortly.",
            ) from exc

    except httpx.RequestError as e:
        raise APIException(
            status_code=500,
            error_code="NETWORK_ERROR",
            message=f"Failed to reach Photon API: {e!s}",
            user_message="Network error occurred while fetching address details.",
        )
