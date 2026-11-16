"""Models for https://splatoon2.ink/data/schedules.json: the Regular, Ranked and League Battle rotations.

The feed is SplatNet 2's ``/api/schedules`` response, as splatoon2.ink republishes it. Each rotation's ``id`` is left
out: the feed gives every rotation the same one.
"""

from enum import StrEnum

from aiosplatoon2ink._base import Image, Splatoon2InkModel, TimePeriod


class GameMode(StrEnum):
    """A battle mode, as SplatNet 2 names it internally."""

    REGULAR = "regular"
    RANKED = "gachi"
    LEAGUE = "league"


class Rule(StrEnum):
    """The rule of a battle, as SplatNet 2 names it internally."""

    TURF_WAR = "turf_war"
    SPLAT_ZONES = "splat_zones"
    TOWER_CONTROL = "tower_control"
    RAINMAKER = "rainmaker"
    CLAM_BLITZ = "clam_blitz"


class GameModeInfo(Splatoon2InkModel):
    """A battle mode, with its name."""

    key: GameMode
    name: str
    """The mode's name in English, such as "Ranked Battle"."""


class RuleInfo(Splatoon2InkModel):
    """The rule of a battle, with its name."""

    key: Rule
    name: str
    """The rule's name in English, such as "Tower Control"."""
    multiline_name: str
    """The name broken over lines, as the game shows it in narrow spaces, such as ``"Tower\\nControl"``."""


class Stage(Splatoon2InkModel):
    """A battle stage."""

    id: str
    name: str
    image: Image


class Rotation(TimePeriod):
    """One rotation of a battle mode: two hours of one rule on two stages."""

    game_mode: GameModeInfo
    rule: RuleInfo
    stage_a: Stage
    stage_b: Stage

    @property
    def stages(self) -> tuple[Stage, Stage]:
        """Both stages, in the order SplatNet 2 lists them."""
        return self.stage_a, self.stage_b


class Schedules(Splatoon2InkModel):
    """The rotations of each battle mode, in order.

    Each list runs from the current rotation, which may already have ended if the feed is up to an hour old, to about a
    day ahead.
    """

    regular: tuple[Rotation, ...]
    """Regular Battle rotations."""
    gachi: tuple[Rotation, ...]
    """Ranked Battle rotations."""
    league: tuple[Rotation, ...]
    """League Battle rotations."""

    def in_mode(self, mode: GameMode) -> tuple[Rotation, ...]:
        """The rotations of one battle mode."""
        match mode:
            case GameMode.REGULAR:
                return self.regular
            case GameMode.RANKED:
                return self.gachi
            case GameMode.LEAGUE:
                return self.league


__all__ = ["GameMode", "GameModeInfo", "Rotation", "Rule", "RuleInfo", "Schedules", "Stage"]
