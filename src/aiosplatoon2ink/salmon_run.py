"""Models for https://splatoon2.ink/data/coop-schedules.json: Salmon Run rotations, with the stage and weapons of the next
two.

The feed is SplatNet 2's ``/api/coop_schedules`` response, as splatoon2.ink republishes it.
"""

from typing import Annotated, Any

from pydantic import Discriminator, Tag, model_validator

from aiosplatoon2ink._base import Image, Splatoon2InkModel, TimePeriod
from aiosplatoon2ink.weapons import Weapon


class CoopStage(Splatoon2InkModel):
    """A Salmon Run stage. SplatNet 2 gives it no ID."""

    name: str
    image: Image


class SuppliedWeapon(Splatoon2InkModel):
    """A weapon Grizzco supplies in a rotation."""

    id: str
    """The weapon's ID, the same as :attr:`Weapon.id`."""
    weapon: Weapon


class CoopSpecialWeapon(Splatoon2InkModel):
    """The picture SplatNet 2 shows for a "?" among a rotation's weapons."""

    name: str
    """Always "Random", in English."""
    image: Image


class RandomWeapon(Splatoon2InkModel):
    """A "?" among a rotation's weapons: a weapon handed out at random.

    A green "?" has the ID ``"-1"``. A golden one, ``"-2"``, can hand out Grizzco's rare weapons.
    """

    id: str | None = None
    """``"-1"`` for a green "?" or ``"-2"`` for a golden one. None where splatoon2.ink's feeds of early 2018 gave the
    slot as ``null``."""
    coop_special_weapon: CoopSpecialWeapon | None = None
    """The "?" picture, which the feeds of early 2018 didn't have."""

    @model_validator(mode="before")
    @classmethod
    def _from_null(cls, value: Any) -> Any:
        # Early in 2018, splatoon2.ink's timeline gave each "?" as null.
        if value is None:
            return {}
        return value

    @property
    def is_golden(self) -> bool:
        """Whether this is a golden "?", which can hand out Grizzco's rare weapons."""
        return self.id == "-2"


def _weapon_slot_kind(value: Any) -> str | None:
    if isinstance(value, SuppliedWeapon):
        return "supplied"
    if value is None or isinstance(value, RandomWeapon):
        return "random"
    if isinstance(value, dict):
        if value.get("weapon") is not None:
            return "supplied"
        if "coop_special_weapon" in value or value.keys() <= {"id", "weapon"}:
            return "random"
    return None  # Not a weapon slot, which pydantic reports as a validation error.


type CoopWeapon = Annotated[
    Annotated[SuppliedWeapon, Tag("supplied")] | Annotated[RandomWeapon, Tag("random")],
    Discriminator(_weapon_slot_kind),
]
"""One of a rotation's four weapons: either a weapon SplatNet 2 names, or a "?"."""


class CoopScheduleDetail(TimePeriod):
    """A Salmon Run rotation, with its stage and the weapons Grizzco supplies."""

    stage: CoopStage
    weapons: tuple[CoopWeapon, ...]


class CoopSchedules(Splatoon2InkModel):
    """Salmon Run rotations, from the current or next one onwards."""

    details: tuple[CoopScheduleDetail, ...]
    """The first two rotations of :attr:`schedules`, with their stages and weapons."""
    schedules: tuple[TimePeriod, ...]
    """Every rotation SplatNet 2 lists, by time alone: usually five, including those in :attr:`details`."""

    def detail(self, rotation: TimePeriod) -> CoopScheduleDetail | None:
        """The stage and weapons of a rotation from :attr:`schedules`, if SplatNet 2 lists them yet."""
        return next((detail for detail in self.details if detail.start_time == rotation.start_time), None)


__all__ = [
    "CoopScheduleDetail",
    "CoopSchedules",
    "CoopSpecialWeapon",
    "CoopStage",
    "CoopWeapon",
    "RandomWeapon",
    "SuppliedWeapon",
]
