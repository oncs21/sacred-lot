from fastapi import APIRouter
import httpx

from app.services.analysis import run_property_feasibility
from app.schemas.feasibility import FeasibilityResponseSchema

router = APIRouter(prefix="/search", tags=["Search & Feasibility"])

@router.get("/parcel-details", response_model=FeasibilityResponseSchema)
async def fetch_parcel_details(
    address: str,
    density: float
):
    return await run_property_feasibility(address=address, density=density)