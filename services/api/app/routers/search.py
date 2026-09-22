from typing import Annotated

from fastapi import APIRouter, Query
from pydantic import StringConstraints

from app.integrations.geocoding import fetch_address_suggestions
from app.schemas.address import AddressSuggestion
from app.schemas.feasibility import FeasibilityResponseSchema
from app.services.analysis import run_property_feasibility

router = APIRouter(prefix="/search", tags=["Search & Feasibility"])


@router.get("/parcel-details", response_model=FeasibilityResponseSchema)
async def fetch_parcel_details(address: str, density: float):
    return await run_property_feasibility(address=address, density=density)


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
