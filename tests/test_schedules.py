from datetime import UTC, datetime, timedelta

from conftest import fixture

from aiosplatoon2ink import IMAGE_BASE_URL, TimePeriod
from aiosplatoon2ink.schedules import GameMode, Rule, Schedules


def schedules() -> Schedules:
    return Schedules.model_validate_json(fixture("schedules.json"))


def test_each_mode_lists_a_day_of_rotations() -> None:
    feed = schedules()

    for mode in GameMode:
        rotations = feed.in_mode(mode)
        assert len(rotations) == 12
        assert all(rotation.game_mode.key is mode for rotation in rotations)
        assert all(rotation.end_time - rotation.start_time == timedelta(hours=2) for rotation in rotations)
        assert all(before.end_time == after.start_time for before, after in zip(rotations, rotations[1:]))
        assert rotations[0].start_time == datetime(2026, 11, 16, 10, tzinfo=UTC)


def test_ranked_battle() -> None:
    rotation = schedules().in_mode(GameMode.RANKED)[0]

    assert rotation.game_mode.name == "Ranked Battle"
    assert rotation.rule.key is Rule.CLAM_BLITZ
    assert rotation.rule.name == "Clam Blitz"
    assert rotation.rule.multiline_name == "Clam\nBlitz"
    assert [stage.name for stage in rotation.stages] == ["MakoMart", "Skipper Pavilion"]
    assert rotation.stage_a.id == "13"


def test_regular_battle_is_turf_war() -> None:
    feed = schedules()

    assert {rotation.rule.key for rotation in feed.regular} == {Rule.TURF_WAR}
    assert {rotation.rule.key for rotation in feed.league} == set(Rule) - {Rule.TURF_WAR}


def test_stage_pictures_are_served_by_splatoon2ink() -> None:
    stage = schedules().league[0].stage_a

    assert stage.name == "Inkblot Art Academy"
    assert stage.image.path == "/images/stage/5c030a505ee57c889d3e5268a4b10c1f1f37880a.png"
    assert stage.image.url == f"{IMAGE_BASE_URL}/images/stage/5c030a505ee57c889d3e5268a4b10c1f1f37880a.png"
    assert stage.image.url.startswith("https://splatoon2.ink/assets/splatnet/images/")


def test_time_period_is_active() -> None:
    period = TimePeriod.model_validate({"start_time": 1794823200, "end_time": 1794830400})

    assert period.start_time == datetime(2026, 11, 16, 10, tzinfo=UTC)
    assert not period.is_active(datetime(2026, 11, 16, 9, 59, tzinfo=UTC))
    assert period.is_active(datetime(2026, 11, 16, 10, tzinfo=UTC))
    assert not period.is_active(datetime(2026, 11, 16, 12, tzinfo=UTC))
