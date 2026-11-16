import json
from datetime import UTC, datetime

from conftest import fixture

from aiosplatoon2ink.gear import GearKind, _MerchandisesFeed
from aiosplatoon2ink.salmon_run import RandomWeapon
from aiosplatoon2ink.timeline import Timeline


def test_gear_on_sale() -> None:
    merchandises = _MerchandisesFeed.model_validate_json(fixture("merchandises.json")).merchandises

    assert len(merchandises) == 6
    assert [item.gear.kind for item in merchandises].count(GearKind.CLOTHING) == 5
    first = merchandises[0]
    assert first.gear.name == "Canary Trainers"
    assert first.gear.kind is GearKind.SHOES
    assert first.gear.rarity == 0
    assert first.gear.brand.name == "Tentatek"
    assert first.gear.brand.frequent_skill is not None
    assert first.gear.brand.frequent_skill.name == "Ink Recovery Up"
    assert first.skill.name == "Drop Roller"
    assert first.price == 2250
    assert first.end_time == datetime(2026, 11, 16, 12, tzinfo=UTC)
    assert first.original_gear is not None
    assert first.original_gear.price == 900
    assert first.original_gear.skill.name == "Quick Super Jump"


def test_salmon_run_reward_gear() -> None:
    timeline = Timeline.model_validate_json(fixture("timeline.json"))

    assert timeline.coop is not None
    gear = timeline.coop.reward_gear.gear
    assert gear.name == "North-Country Parka"
    assert gear.kind is GearKind.CLOTHING
    assert gear.brand.name == "Grizzco"
    assert gear.brand.frequent_skill is None
    assert timeline.coop.reward_gear.available_time == datetime(2026, 11, 14, 12, tzinfo=UTC)
    assert timeline.coop.schedule.stage.name == "Lost Outpost"
    assert timeline.weapon_availability is None


def test_random_weapons_given_as_null() -> None:
    timeline = Timeline.model_validate_json(fixture("timeline-2018.json"))

    assert timeline.coop is not None
    assert timeline.coop.reward_gear.gear.name == "Oceanic Hard Hat"
    assert timeline.coop.schedule.weapons == (RandomWeapon(),) * 4


def test_new_weapons() -> None:
    # No snapshot has a new weapon, so this lists one from the rankings, whose weapons have the same shape.
    weapon = json.loads(fixture("festivals/na-4064-rankings.json"))["rankings"]["alpha"][0]["info"]["weapon"]
    timeline = Timeline.model_validate(
        {"coop": None, "weapon_availability": {"availabilities": [{"weapon": weapon, "release_time": 1610748000}]}}
    )

    assert timeline.coop is None
    assert timeline.weapon_availability is not None
    (availability,) = timeline.weapon_availability.availabilities
    assert availability.weapon.name == "L-3 Nozzlenose"
    assert availability.weapon.sub.image_a.url.startswith("https://splatoon2.ink/assets/splatnet/images/sub/")
    assert availability.release_time == datetime(2021, 1, 15, 22, tzinfo=UTC)
