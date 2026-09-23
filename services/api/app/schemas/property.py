from typing import List, Optional
from pydantic import BaseModel, Field

class ParcelDataSchema(BaseModel):
    object_id: int
    parcel_id: str
    county_name: str
    address: str
    city: str
    owner: str
    land_acres: float
    calculated_sqft: float
    zoning_code: Optional[str] = "UNKNOWN"
    zoning_desc: Optional[str] = None
    geometry_rings: List[List[List[float]]] = Field(..., description="Polygon boundary ring coordinates")

    class Config:
        frozen = True