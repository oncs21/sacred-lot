from pydantic import BaseModel, ConfigDict, Field


class AddressSuggestion(BaseModel):
    model_config = ConfigDict(frozen=True)

    address: str = Field(min_length=1)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
