from datetime import UTC, datetime
from typing import Any

import pytest
from conftest import fixture
from pydantic import ValidationError

from aiosplatoon2ink.salmon_run import CoopScheduleDetail, CoopSchedules, RandomWeapon, SuppliedWeapon


def salmon_run(name: str) -> CoopSchedules:
    return CoopSchedules.model_validate_json(fixture(name))


def rotation_with(*weapons: Any) -> CoopScheduleDetail:
    return CoopScheduleDetail.model_validate(
        {
            "start_time": 1794830400,
            "end_time": 1794960000,
            "stage": {
                "name": "Lost Outpost",
                "image": "/images/coop_stage/6d68f5baa75f3a94e5e9bfb89b82e7377e3ecd2c.png",
            },
            "weapons": list(weapons),
        }
    )


def test_rotations_with_named_weapons() -> None:
    feed = salmon_run("coop-schedules.json")

    assert len(feed.schedules) == 5
    assert len(feed.details) == 2
    rotation = feed.details[0]
    assert rotation.start_time == datetime(2026, 11, 16, 12, tzinfo=UTC)
    assert rotation.end_time == datetime(2026, 11, 18, tzinfo=UTC)
    assert rotation.stage.name == "Lost Outpost"
    assert rotation.stage.image.url.endswith("/images/coop_stage/6d68f5baa75f3a94e5e9bfb89b82e7377e3ecd2c.png")
    assert all(isinstance(weapon, SuppliedWeapon) for weapon in rotation.weapons)
    assert [weapon.weapon.name for weapon in rotation.weapons if isinstance(weapon, SuppliedWeapon)] == [
        "Splash-o-matic",
        "Slosher",
        "Splat Brella",
        "Bamboozler 14 Mk I",
    ]


def test_details_belong_to_the_first_rotations() -> None:
    feed = salmon_run("coop-schedules.json")

    assert [feed.detail(rotation) for rotation in feed.schedules] == [*feed.details, None, None, None]


def test_a_random_weapon_among_named_ones() -> None:
    weapons = salmon_run("coop-schedules-random-weapon.json").details[0].weapons

    assert [type(weapon) for weapon in weapons] == [SuppliedWeapon, SuppliedWeapon, SuppliedWeapon, RandomWeapon]
    random = weapons[3]
    assert isinstance(random, RandomWeapon)
    assert random.id == "-1"
    assert not random.is_golden
    assert random.coop_special_weapon is not None
    assert random.coop_special_weapon.name == "Random"


def test_a_rotation_of_random_weapons() -> None:
    feed = salmon_run("coop-schedules-all-random.json")

    assert all(isinstance(weapon, SuppliedWeapon) for weapon in feed.details[0].weapons)
    assert all(isinstance(weapon, RandomWeapon) and weapon.id == "-1" for weapon in feed.details[1].weapons)


def test_a_golden_random_weapon() -> None:
    # No snapshot has one; SplatNet 2 gives it the ID -2, and splatoon2.ink serves its picture.
    golden = {
        "id": "-2",
        "coop_special_weapon": {
            "name": "Random",
            "image": "/images/coop_weapons/7076c8181ab5c49d2ac91e43a2d945a46a99c17d.png",
        },
    }

    (weapon,) = rotation_with(golden).weapons
    assert isinstance(weapon, RandomWeapon)
    assert weapon.is_golden


def test_a_random_weapon_without_a_picture() -> None:
    nameless, null = rotation_with({"id": "-1"}, None).weapons

    assert nameless == RandomWeapon(id="-1")
    assert null == RandomWeapon()


def test_rejects_a_slot_of_another_shape() -> None:
    # splatoon2.ink's feed of January 2018 listed each weapon itself, not a slot holding it.
    weapon = {
        "id": "20",
        "name": "Splash-o-matic",
        "image": "/images/weapon/e5a97d52f12a83a037526588363021f2c1f718b0.png",
    }

    with pytest.raises(ValidationError):
        rotation_with(weapon)
