"""Models for https://splatoon2.ink/data/timeline.json: the month's Salmon Run reward gear, and newly released weapons.

The feed is part of SplatNet 2's ``/api/timeline`` response: splatoon2.ink keeps its ``coop`` and
``weapon_availability`` entries, each only while SplatNet 2 has something to show in it.
"""

from pydantic import AwareDatetime

from aiosplatoon2ink._base import Splatoon2InkModel
from aiosplatoon2ink.gear import Gear
from aiosplatoon2ink.salmon_run import CoopScheduleDetail
from aiosplatoon2ink.weapons import WeaponKit


class RewardGear(Splatoon2InkModel):
    """The month's Salmon Run reward gear."""

    gear: Gear
    available_time: AwareDatetime
    """When it became the reward."""


class TimelineCoop(Splatoon2InkModel):
    """Salmon Run, as SplatNet 2's timeline shows it."""

    reward_gear: RewardGear
    schedule: CoopScheduleDetail
    """The current or next rotation."""


class WeaponAvailability(Splatoon2InkModel):
    """A newly released weapon."""

    weapon: WeaponKit
    release_time: AwareDatetime


class NewWeapons(Splatoon2InkModel):
    """The weapons released in the last few days."""

    availabilities: tuple[WeaponAvailability, ...]


class Timeline(Splatoon2InkModel):
    """The month's Salmon Run reward gear, and the weapons released in the last few days."""

    coop: TimelineCoop | None
    """Salmon Run's reward gear and current or next rotation, or None while SplatNet 2's timeline leaves it out."""
    weapon_availability: NewWeapons | None
    """The weapons released in the last few days, for about three days after each release, or None when there are
    none."""


__all__ = ["NewWeapons", "RewardGear", "Timeline", "TimelineCoop", "WeaponAvailability"]
