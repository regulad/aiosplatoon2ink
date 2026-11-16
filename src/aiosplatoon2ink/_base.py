"""The pieces every splatoon2.ink model shares."""

from datetime import datetime
from typing import Any

from pydantic import AwareDatetime, BaseModel, ConfigDict, model_validator

IMAGE_BASE_URL = "https://splatoon2.ink/assets/splatnet"
"""Where splatoon2.ink serves its copies of SplatNet 2's images: an image's URL is this followed by its path."""


class Splatoon2InkModel(BaseModel):
    """Base of every model: immutable, and read from the feeds' keys, which are SplatNet 2's and already snake_case.

    Fields the models don't declare are ignored, so splatoon2.ink can add fields without breaking anything. Models can
    also be built by their Python field names, as tests that make their own data do.
    """

    model_config = ConfigDict(frozen=True, validate_by_name=True)


class Image(Splatoon2InkModel):
    """An image from SplatNet 2, which splatoon2.ink serves a copy of.

    splatoon2.ink copies the pictures in every feed but the Splatfest rankings, whose pictures it has only where another
    feed showed the same thing. It copies none of SplatNet 2's thumbnails, nor the second pictures of sub and special
    weapons, so the models leave those out.
    """

    path: str
    """The image's path on SplatNet 2, as the feeds give it, such as ``/images/stage/<hash>.png``."""

    @model_validator(mode="before")
    @classmethod
    def _from_path(cls, value: Any) -> Any:
        # The feeds give each image as its bare path.
        if isinstance(value, str):
            return {"path": value}
        return value

    @property
    def url(self) -> str:
        """Where splatoon2.ink serves the image."""
        return IMAGE_BASE_URL + self.path


class Color(Splatoon2InkModel):
    """A colour, with each channel from 0 to 1."""

    r: float
    g: float
    b: float
    a: float = 1.0
    css_rgb: str
    """The colour in CSS, in percentages, such as ``rgb(80%,12%,12%)``."""

    @property
    def rgb(self) -> tuple[int, int, int]:
        """The red, green and blue channels, each from 0 to 255."""
        return round(self.r * 255), round(self.g * 255), round(self.b * 255)


class TimePeriod(Splatoon2InkModel):
    """A span of time, from its start up to its end. The feeds give times in Unix seconds, read as UTC."""

    start_time: AwareDatetime
    end_time: AwareDatetime

    def is_active(self, now: datetime) -> bool:
        """Whether this period has started and not yet ended at ``now``, an aware datetime."""
        return self.start_time <= now < self.end_time


__all__ = ["IMAGE_BASE_URL", "Color", "Image", "Splatoon2InkModel", "TimePeriod"]
