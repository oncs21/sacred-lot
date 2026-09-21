from functools import lru_cache
from math import isfinite

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SACRED_LOT_", frozen=True)

    geocoding_bbox: str = "-109.06,36.99,-102.04,41.00"

    @field_validator("geocoding_bbox")
    @classmethod
    def validate_bbox(cls, value: str) -> str:
        coordinates = tuple(float(part.strip()) for part in value.split(","))
        if len(coordinates) != 4 or not all(isfinite(item) for item in coordinates):
            raise ValueError("Bounding box requires four finite coordinates")
        west, south, east, north = coordinates
        if not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
            raise ValueError(
                "Bounding box must contain ordered longitude/latitude bounds"
            )
        return ",".join(part.strip() for part in value.split(","))

    def contains(self, latitude: float, longitude: float) -> bool:
        west, south, east, north = map(float, self.geocoding_bbox.split(","))
        return west <= longitude <= east and south <= latitude <= north


@lru_cache
def get_settings() -> Settings:
    return Settings()
