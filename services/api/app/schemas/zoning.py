from typing import Literal

from pydantic import BaseModel, Field


class ZoningDistrict(BaseModel):
    code: str
    description: str | None = None


class ZoningResult(BaseModel):
    status: Literal["matched", "partial", "no_match", "unavailable"]
    jurisdiction: str | None = None
    districts: list[ZoningDistrict] = Field(default_factory=list)
    source_url: str | None = None
    retrieved_at: str | None = None
