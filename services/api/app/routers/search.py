from fastapi import APIRouter
import httpx


router = APIRouter()

@router.get("/parcel-details")
async def fetch_parcel_details(
    address: str,
    density: float
):
    raise NotImplementedError