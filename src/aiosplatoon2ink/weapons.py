"""Weapons, as the Salmon Run schedules, the timeline and the Splatfest rankings list them."""

from aiosplatoon2ink._base import Image, Splatoon2InkModel


class Weapon(Splatoon2InkModel):
    """A main weapon."""

    id: str
    name: str
    image: Image


class SubWeapon(Splatoon2InkModel):
    """A sub weapon."""

    id: str
    name: str
    image_a: Image
    """The sub weapon's picture. SplatNet 2's second picture of it, ``image_b``, isn't served by splatoon2.ink."""


class SpecialWeapon(Splatoon2InkModel):
    """A special weapon."""

    id: str
    name: str
    image_a: Image
    """The special weapon's picture. SplatNet 2's second picture of it, ``image_b``, isn't served by splatoon2.ink."""


class WeaponKit(Weapon):
    """A main weapon, with the sub weapon and special weapon it comes with."""

    sub: SubWeapon
    special: SpecialWeapon


__all__ = ["SpecialWeapon", "SubWeapon", "Weapon", "WeaponKit"]
