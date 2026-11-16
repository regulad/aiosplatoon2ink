"""Models for https://splatoon2.ink/data/festivals.json, every Splatfest in each of SplatNet 2's three regions, and
https://splatoon2.ink/data/festivals/<region>-<festival_id>-rankings.json, the top players of each Splatfest.

Each region's list is SplatNet 2's ``/api/festivals/active`` and ``/api/festivals/pasts`` responses, combined by
splatoon2.ink. The rankings are SplatNet 2's ``/api/festivals/<festival_id>/rankings`` response for that region.
"""

from enum import IntEnum, StrEnum
from typing import Annotated, Any

from pydantic import AwareDatetime, BeforeValidator

from aiosplatoon2ink._base import Color, Image, Splatoon2InkModel
from aiosplatoon2ink.gear import Gear
from aiosplatoon2ink.schedules import Stage
from aiosplatoon2ink.weapons import WeaponKit


class Region(StrEnum):
    """A region of SplatNet 2's that holds its own Splatfests."""

    NA = "na"
    """The Americas, Australia and New Zealand."""
    EU = "eu"
    """Europe."""
    JP = "jp"
    """Japan."""


class Team(IntEnum):
    """One of a Splatfest's two teams. SplatNet 2 names them alpha and bravo; the game shows them by their names."""

    ALPHA = 0
    BRAVO = 1


class FestivalTimes(Splatoon2InkModel):
    """When a Splatfest is announced, held and decided."""

    announce: AwareDatetime
    start: AwareDatetime
    end: AwareDatetime
    result: AwareDatetime
    """When the results are announced."""


class FestivalNames(Splatoon2InkModel):
    """The names of a Splatfest's teams, in the region's language."""

    alpha_short: str
    """Team Alpha's name, such as "Mayo"."""
    alpha_long: str
    """Team Alpha's side in full, such as "Mayo is better than Ketchup!". It can span lines."""
    bravo_short: str
    bravo_long: str

    def short(self, team: Team) -> str:
        """A team's name."""
        return self.alpha_short if team is Team.ALPHA else self.bravo_short

    def long(self, team: Team) -> str:
        """A team's name in full."""
        return self.alpha_long if team is Team.ALPHA else self.bravo_long


class FestivalImages(Splatoon2InkModel):
    """A Splatfest's pictures."""

    alpha: Image
    """Team Alpha's picture."""
    bravo: Image
    """Team Bravo's picture."""
    panel: Image
    """The Splatfest's announcement, with both teams."""


class FestivalColors(Splatoon2InkModel):
    """A Splatfest's colours."""

    alpha: Color
    """Team Alpha's ink colour."""
    bravo: Color
    """Team Bravo's ink colour."""
    middle: Color
    """A colour for the Splatfest itself, which splatoon2.ink shows behind its dates."""


class TeamRates(Splatoon2InkModel):
    """Each team's share of one category of a Splatfest's results, in hundredths of a percent: 5302 is 53.02%."""

    alpha: int
    bravo: int


class FestivalRates(Splatoon2InkModel):
    """Each team's share of each category of a Splatfest's results.

    Splatfests held before version 4.0, in September 2018, counted Solo and Team battles; later ones count Normal and
    Pro. SplatNet 2 calls Splatfest Battle (Normal) ``regular`` and Splatfest Battle (Pro) ``challenge``.
    """

    vote: TeamRates
    """Popularity: each team's share of the votes."""
    solo: TeamRates | None = None
    """Each team's win rate in Splatfest Battle (Solo), before version 4.0."""
    team: TeamRates | None = None
    """Each team's win rate in Splatfest Battle (Team), before version 4.0."""
    regular: TeamRates | None = None
    """Each team's share of the clout in Splatfest Battle (Normal), from version 4.0."""
    challenge: TeamRates | None = None
    """Each team's share of the clout in Splatfest Battle (Pro), from version 4.0."""


class FestivalSummary(Splatoon2InkModel):
    """The team that won each category of a Splatfest's results, and the Splatfest itself."""

    total: Team
    """The team that won the Splatfest."""
    vote: Team
    solo: Team | None = None
    team: Team | None = None
    regular: Team | None = None
    challenge: Team | None = None


class Contribution(Splatoon2InkModel):
    """A team's average clout in each kind of Splatfest Battle, from version 4.0."""

    regular: float
    """In Splatfest Battle (Normal)."""
    challenge: float
    """In Splatfest Battle (Pro)."""


class FestivalResult(Splatoon2InkModel):
    """A Splatfest's results."""

    festival_id: int
    festival_version: int
    """2 for Splatfests held under version 4.0's rules, which count Normal and Pro battles, or 1 for those before,
    which count Solo and Team battles."""
    summary: FestivalSummary
    rates: FestivalRates
    contribution_alpha: Contribution | None = None
    """Team Alpha's average clout, from version 4.0."""
    contribution_bravo: Contribution | None = None
    """Team Bravo's average clout, from version 4.0."""


class Festival(Splatoon2InkModel):
    """A Splatfest, as one region holds it."""

    festival_id: int
    """SplatNet 2's ID for the Splatfest, shared by every region that held it."""
    times: FestivalTimes
    names: FestivalNames
    images: FestivalImages
    colors: FestivalColors
    special_stage: Stage
    """The stage played only during the Splatfest, such as Shifty Station."""
    result: FestivalResult | None = None
    """The results, once announced. The feed lists them apart from the Splatfests; this joins them by ID."""

    @property
    def winner(self) -> Team | None:
        """The team that won, once the results are announced."""
        return self.result.summary.total if self.result is not None else None


def _festival_id(value: Any) -> int | None:
    # Anything but an int is left for pydantic to reject, rather than raising here.
    festival_id = value.get("festival_id") if isinstance(value, dict) else None
    return festival_id if isinstance(festival_id, int) else None


def _join_results(value: Any) -> Any:
    # Each region lists its Splatfests and their results apart: {"festivals": [...], "results": [...]}.
    if isinstance(value, dict) and isinstance(value.get("festivals"), list) and isinstance(value.get("results"), list):
        results = {_festival_id(result): result for result in value["results"]}
        return [
            (
                {**festival, "result": results.get(festival_id)}
                if (festival_id := _festival_id(festival)) is not None
                else festival
            )
            for festival in value["festivals"]
        ]
    return value


type _RegionFestivals = Annotated[tuple[Festival, ...], BeforeValidator(_join_results)]


class Festivals(Splatoon2InkModel):
    """Every Splatfest, newest first, for each region. Names are in the region's language."""

    na: _RegionFestivals
    eu: _RegionFestivals
    jp: _RegionFestivals

    def in_region(self, region: Region) -> tuple[Festival, ...]:
        """Every Splatfest held in a region, newest first."""
        match region:
            case Region.NA:
                return self.na
            case Region.EU:
                return self.eu
            case Region.JP:
                return self.jp


class RankedPlayer(Splatoon2InkModel):
    """A player in a Splatfest's rankings, and what they wore and played with.

    splatoon2.ink doesn't copy the rankings' pictures, so some of these images' URLs answer 404.
    """

    nickname: str
    weapon: WeaponKit
    head: Gear
    clothes: Gear
    shoes: Gear


class FestivalRanking(Splatoon2InkModel):
    """A player's place in a team's rankings."""

    order: int
    """The player's place, from 1."""
    score: int
    """The player's Splatfest Power."""
    principal_id: str
    """SplatNet 2's ID for the player."""
    cheater: bool
    """Whether SplatNet 2 marked the player as a cheater."""
    updated_time: AwareDatetime
    """When the player's score was last updated."""
    info: RankedPlayer


class FestivalRankings(Splatoon2InkModel):
    """The top 100 players of each team in a Splatfest, by Splatfest Power."""

    alpha: tuple[FestivalRanking, ...]
    bravo: tuple[FestivalRanking, ...]

    def for_team(self, team: Team) -> tuple[FestivalRanking, ...]:
        """A team's rankings, from first place."""
        return self.alpha if team is Team.ALPHA else self.bravo


class _RankingsFeed(Splatoon2InkModel):
    rankings: FestivalRankings


__all__ = [
    "Contribution",
    "Festival",
    "FestivalColors",
    "FestivalImages",
    "FestivalNames",
    "FestivalRanking",
    "FestivalRankings",
    "FestivalRates",
    "FestivalResult",
    "FestivalSummary",
    "FestivalTimes",
    "Festivals",
    "RankedPlayer",
    "Region",
    "Team",
    "TeamRates",
]
