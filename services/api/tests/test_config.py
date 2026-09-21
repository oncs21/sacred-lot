import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_bounding_box_can_be_configured_through_environment(monkeypatch):
    monkeypatch.setenv("SACRED_LOT_GEOCODING_BBOX", "-125,32,-114,42")
    settings = Settings()
    assert settings.geocoding_bbox == "-125,32,-114,42"
    assert settings.contains(37, -122)
    assert not settings.contains(40, -105)


@pytest.mark.parametrize(
    "bbox",
    [
        "",
        "1,2,3",
        "a,b,c,d",
        "-102,37,-109,41",
        "-109,41,-102,37",
        "-181,37,-102,41",
        "-109,37,-102,91",
        "nan,37,-102,41",
    ],
)
def test_invalid_bounding_box_is_rejected(bbox):
    with pytest.raises(ValidationError):
        Settings(geocoding_bbox=bbox)
