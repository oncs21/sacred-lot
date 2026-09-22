import httpx

from app.core.config import get_settings
from app.core.exceptions import APIException
from app.schemas.address import AddressSuggestion

HEADERS = {"User-Agent": "SacredLot/1.0 (open-source-housing-feasibility)"}


async def fetch_coordinates(address: str):
    url = "https://photon.komoot.io/api"
    settings = get_settings()
    params = {"q": address, "limit": 1, "bbox": settings.geocoding_bbox}

    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=6.0) as client:
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
                    user_message="We couldn't find a matching address in the supported area. Please check the street and city name.",
                )

            latitude, longitude = _coordinates(features[0])

            if not settings.contains(latitude, longitude):
                raise APIException(
                    status_code=422,
                    error_code="OUTSIDE_SUPPORTED_AREA",
                    message="Geocoding result lies outside the configured bounding box.",
                    user_message="This location is outside our currently supported area.",
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


def _coordinates(feature: object) -> tuple[float, float]:
    if not isinstance(feature, dict):
        raise TypeError("Expected a GeoJSON feature object")
    geometry = feature["geometry"]
    if not isinstance(geometry, dict):
        raise TypeError("Expected a geometry object")
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
        raise ValueError("Coordinates must be numeric and within geographic bounds")

    return latitude, longitude


async def fetch_address_suggestions(
    address: str, limit: int = 5
) -> list[AddressSuggestion]:
    settings = get_settings()
    params = {"q": address.strip(), "limit": limit, "bbox": settings.geocoding_bbox}
    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=6.0) as client:
            response = await client.get("https://photon.komoot.io/api", params=params)
    except httpx.RequestError as exc:
        raise APIException(
            status_code=503,
            error_code="GEOCODING_SERVICE_DOWN",
            message="Failed to reach Photon API.",
            user_message="Address suggestions are temporarily unavailable. Please try again shortly.",
        ) from exc

    if response.status_code != 200:
        raise APIException(
            status_code=503,
            error_code="GEOCODING_SERVICE_DOWN",
            message=f"Photon API returned status {response.status_code}",
            user_message="Address suggestions are temporarily unavailable. Please try again shortly.",
        )

    try:
        payload = response.json()
        if not isinstance(payload, dict) or not isinstance(
            payload.get("features"), list
        ):
            raise TypeError("Expected a GeoJSON features array")
        suggestions = []
        seen = set()
        for feature in payload["features"]:
            latitude, longitude = _coordinates(feature)
            if not settings.contains(latitude, longitude):
                continue
            properties = feature["properties"]
            if not isinstance(properties, dict):
                raise TypeError("Expected feature properties")
            label = _address_label(properties)
            if not label:
                continue
            key = (label, latitude, longitude)
            if key in seen:
                continue
            seen.add(key)
            suggestions.append(
                AddressSuggestion(
                    address=label,
                    latitude=latitude,
                    longitude=longitude,
                )
            )
            if len(suggestions) == limit:
                break
        return suggestions
    except (ValueError, KeyError, TypeError, IndexError) as exc:
        raise APIException(
            status_code=502,
            error_code="INVALID_GEOCODING_RESPONSE",
            message="Photon returned invalid address suggestions.",
            user_message="Address lookup returned an invalid response. Please try again shortly.",
        ) from exc


def _address_label(properties: dict) -> str:
    def text(key: str) -> str:
        value = properties.get(key)
        return value.strip() if isinstance(value, str) else ""

    street = " ".join(filter(None, [text("housenumber"), text("street")]))
    parts = [
        text("name"),
        street,
        text("city") or text("town") or text("village"),
        text("state"),
        text("postcode"),
        text("country"),
    ]
    return ", ".join(dict.fromkeys(part for part in parts if part))
