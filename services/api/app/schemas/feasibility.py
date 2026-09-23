from pydantic import BaseModel, Field
from typing import List, Optional

class FeasibilityResponseSchema(BaseModel):
    parcel_id: str
    owner: str
    address: str
    total_acres: float
    total_sqft: float
    units_yield: int = Field(..., description="Estimated micro-housing units yielded")
    retained_parking_pct: int = Field(..., description="Percentage of parking surface preserved")
    geojson_rings: List[List[List[float]]] = Field(..., description="Boundary ring polygon coordinates for 2D/3D map rendering")

    class Config:
        json_schema_extra = {
            "example": {
                "parcel_id": "146330300005",
                "owner": "GRACE COMMONS CHURCH",
                "address": "1711 15TH ST, BOULDER, CO",
                "total_acres": 0.174,
                "total_sqft": 7579.44,
                "units_yield": 2,
                "retained_parking_pct": 70,
                "geojson_rings": [[[-105.2749, 40.0151], [-105.2749, 40.0150], [-105.2754, 40.0148]]]
            }
        }