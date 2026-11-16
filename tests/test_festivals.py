import json
from datetime import UTC, datetime

from conftest import fixture

from aiosplatoon2ink.festivals import FestivalRankings, Festivals, Region, Team, TeamRates, _RankingsFeed
from aiosplatoon2ink.gear import GearKind


def festivals() -> Festivals:
    return Festivals.model_validate_json(fixture("festivals.json"))


def rankings() -> FestivalRankings:
    return _RankingsFeed.model_validate_json(fixture("festivals/na-4064-rankings.json")).rankings


def test_every_region_lists_every_splatfest_newest_first() -> None:
    feed = festivals()

    for region in Region:
        fests = feed.in_region(region)
        assert len(fests) == 30
        assert [fest.times.start for fest in fests] == sorted((fest.times.start for fest in fests), reverse=True)
        assert fests[0].festival_id == 4064
        assert fests[0].times.start == datetime(2021, 1, 15, 22, tzinfo=UTC)
        assert all(fest.result is not None and fest.result.festival_id == fest.festival_id for fest in fests)
    assert feed.in_region(Region.NA)[0].names.alpha_short == "Super Mushroom"
    assert feed.in_region(Region.JP)[0].names.alpha_short == "スーパーキノコ"


def test_results_since_version_4() -> None:
    fest = festivals().in_region(Region.NA)[0]

    result = fest.result
    assert result is not None
    assert result.festival_version == 2
    assert fest.winner is Team.ALPHA
    assert fest.names.short(Team.ALPHA) == "Super Mushroom"
    assert result.summary.vote is Team.BRAVO
    assert result.rates.vote == TeamRates(alpha=3180, bravo=6820)
    assert result.rates.regular is not None and result.rates.challenge is not None
    assert result.rates.solo is None and result.rates.team is None
    assert result.contribution_alpha is not None and result.contribution_bravo is not None


def test_results_before_version_4() -> None:
    fest = festivals().in_region(Region.NA)[-1]

    result = fest.result
    assert result is not None
    assert fest.festival_id == 2050
    assert fest.names.long(Team.BRAVO) == "Ketchup is better than Mayo!"
    assert fest.times.result == datetime(2017, 8, 6, 6, tzinfo=UTC)
    assert result.festival_version == 1
    assert fest.winner is Team.ALPHA
    assert result.summary.solo is Team.ALPHA and result.summary.regular is None
    assert result.rates.solo == TeamRates(alpha=5183, bravo=4817)
    assert result.rates.regular is None
    assert result.contribution_alpha is None


def test_splatfest_colours_and_pictures() -> None:
    fest = festivals().in_region(Region.NA)[0]

    assert fest.colors.alpha.rgb == (204, 31, 31)
    assert fest.colors.alpha.css_rgb == "rgb(80%,12%,12%)"
    assert fest.special_stage.name == "Shifty Station"
    assert (
        fest.images.panel.url
        == "https://splatoon2.ink/assets/splatnet/images/festival/15195d4abf17afbc6bc1c22cbff56012.png"
    )


def test_a_splatfest_before_its_results() -> None:
    data = json.loads(fixture("festivals.json"))
    data["na"]["results"] = []

    fest = Festivals.model_validate(data).in_region(Region.NA)[0]
    assert fest.result is None
    assert fest.winner is None


def test_rankings() -> None:
    feed = rankings()

    for team in Team:
        places = feed.for_team(team)
        assert [place.order for place in places] == list(range(1, 101))
        assert [place.score for place in places] == sorted((place.score for place in places), reverse=True)
    first = feed.alpha[0]
    assert first.score == 2666
    assert first.principal_id == "0000000000000001"
    assert first.info.nickname == "Player Alpha 1"
    assert not first.cheater
    assert first.updated_time == datetime(2021, 1, 17, 13, 0, 29, tzinfo=UTC)
    assert first.info.weapon.name == "L-3 Nozzlenose"
    assert first.info.weapon.sub.name == "Curling Bomb"
    assert first.info.weapon.special.name == "Baller"
    assert first.info.head.kind is GearKind.HEAD
    assert first.info.clothes.kind is GearKind.CLOTHING
    assert first.info.shoes.kind is GearKind.SHOES
    assert any(place.info.head.brand.frequent_skill is None for place in feed.alpha)
