from app.integrations.geocoding import fetch_coordinates
from app.integrations.parcels import fetch_parcel_information

DEFAULT_PARKING_SURFACE_RATIO = 0.65
DEFAULT_GROSS_UNIT_SQFT = 600

async def run_property_feasibility(
        address: str, 
        density: float = 0.3,
        parking_ratio: float = DEFAULT_PARKING_SURFACE_RATIO,
        unit_size_sqft: int = DEFAULT_GROSS_UNIT_SQFT
    ):
    lat, long = await fetch_coordinates(address)
    parcel = await fetch_parcel_information(lat, long)

    usable_sqft = parcel.calculated_sqft * parking_ratio
    allocated_sqft = usable_sqft * density
    estimated_units = int(allocated_sqft // unit_size_sqft)

    return {
        "parcel_id": parcel.parcel_id,
        "owner": parcel.owner,
        "address": f"{parcel.address}, {parcel.city}, CO",
        "total_acres": parcel.land_acres,
        "total_sqft": parcel.calculated_sqft,
        "units_yield": estimated_units,
        "retained_parking_pct": int((1.0 - density) * 100),
        "geojson_rings": parcel.geometry_rings
    }