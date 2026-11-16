"""An asyncio client for the Splatoon 2 data that splatoon2.ink publishes, with typed models of each feed.

>>> async with Splatoon2InkClient("MyBot/1.0 (+https://github.com/me/mybot)") as client:
...     schedules = await client.schedules()

The models live in :mod:`aiosplatoon2ink.schedules`, :mod:`aiosplatoon2ink.salmon_run`, :mod:`aiosplatoon2ink.gear`,
:mod:`aiosplatoon2ink.festivals`, :mod:`aiosplatoon2ink.timeline` and :mod:`aiosplatoon2ink.weapons`.
"""

from aiosplatoon2ink._base import IMAGE_BASE_URL, Color, Image, TimePeriod
from aiosplatoon2ink._client import DEFAULT_BASE_URL, Splatoon2InkClient
from aiosplatoon2ink.festivals import FestivalRankings, Festivals, Region, Team
from aiosplatoon2ink.gear import Merchandise
from aiosplatoon2ink.salmon_run import CoopSchedules
from aiosplatoon2ink.schedules import Schedules
from aiosplatoon2ink.timeline import Timeline

__all__ = [
    "DEFAULT_BASE_URL",
    "IMAGE_BASE_URL",
    "Color",
    "CoopSchedules",
    "FestivalRankings",
    "Festivals",
    "Image",
    "Merchandise",
    "Region",
    "Schedules",
    "Splatoon2InkClient",
    "Team",
    "TimePeriod",
    "Timeline",
]
