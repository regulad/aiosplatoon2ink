"""Models for https://splatoon2.ink/data/merchandises.json: the gear on sale at SplatNet 2's shop, and gear as the other
feeds list it.

The feed is SplatNet 2's ``/api/onlineshop/merchandises`` response, as splatoon2.ink republishes it, with each item's
:attr:`~Merchandise.original_gear` added from Inkipedia's list of gear.
"""

from enum import StrEnum

from pydantic import AwareDatetime

from aiosplatoon2ink._base import Image, Splatoon2InkModel


class GearKind(StrEnum):
    """Where a piece of gear is worn."""

    HEAD = "head"
    CLOTHING = "clothes"
    SHOES = "shoes"


class Skill(Splatoon2InkModel):
    """A gear ability. SplatNet 2 calls abilities skills."""

    id: str
    name: str
    image: Image


class Brand(Splatoon2InkModel):
    """A gear brand."""

    id: str
    name: str
    image: Image
    frequent_skill: Skill | None = None
    """The ability the brand favours in gear's additional slots. Some brands, such as Grizzco, favour none."""


class Gear(Splatoon2InkModel):
    """A piece of gear."""

    id: str
    """SplatNet 2's ID for the gear, which is only unique among gear of the same :attr:`kind`."""
    name: str
    kind: GearKind
    rarity: int
    """The gear's rarity in stars, from 0 to 2. It has one more additional ability slot than its rarity."""
    image: Image
    brand: Brand


class OriginalGear(Splatoon2InkModel):
    """A piece of gear as the game's shops sell it, from Inkipedia's list of gear."""

    name: str
    price: int | None
    """What it costs in the game's shops, or None where Inkipedia lists no price."""
    rarity: int
    skill: Skill
    """The main ability it comes with."""


class Merchandise(Splatoon2InkModel):
    """Gear on sale at SplatNet 2's shop, where it can come with a different main ability than in the game's shops."""

    id: str
    gear: Gear
    skill: Skill
    """The main ability it comes with."""
    price: int
    end_time: AwareDatetime
    """When it leaves the shop."""
    original_gear: OriginalGear | None = None
    """The same gear as the game's shops sell it, if splatoon2.ink found it in Inkipedia's list."""


class _MerchandisesFeed(Splatoon2InkModel):
    merchandises: tuple[Merchandise, ...]


__all__ = ["Brand", "Gear", "GearKind", "Merchandise", "OriginalGear", "Skill"]
