from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from pydantic import StringConstraints

from app.integrations.addresses import fetch_address_suggestions
from app.schemas.address import AddressSuggestion
from app.schemas.feasibility import FeasibilityResponseSchema
from app.services.analysis import run_property_feasibility

router = APIRouter(prefix="/search", tags=["Search & Feasibility"])


@router.get("/parcel-details", response_model=FeasibilityResponseSchema)
async def fetch_parcel_details(
    address: str,
    density: Annotated[float, Query(ge=0, le=1)],
    latitude: Annotated[float | None, Query(ge=-90, le=90)] = None,
    longitude: Annotated[float | None, Query(ge=-180, le=180)] = None,
    object_id: Annotated[int | None, Query(gt=0)] = None,
):
    if (latitude is None) != (longitude is None):
        raise HTTPException(status_code=422, detail="Latitude and longitude must be supplied together")
    return await run_property_feasibility(
        address=address, density=density, latitude=latitude, longitude=longitude, object_id=object_id,
    )


@router.get("/addresses", response_model=list[AddressSuggestion])
async def suggest_addresses(
    address: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=3, max_length=200),
        Query(description="Partial street address or place name"),
    ],
    limit: Annotated[int, Query(ge=1, le=10)] = 5,
) -> list[AddressSuggestion]:
    return await fetch_address_suggestions(address, limit)
