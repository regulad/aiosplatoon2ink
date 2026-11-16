"""Check the models against the feeds splatoon2.ink serves now. Run with ``pytest -m live``."""

import pytest

from aiosplatoon2ink import Region, Splatoon2InkClient
from aiosplatoon2ink.schedules import GameMode

pytestmark = pytest.mark.live

USER_AGENT = "aiosplatoon2ink-tests/1.0 (+https://github.com/regulad/aiosplatoon2ink)"


async def test_every_feed_parses() -> None:
    async with Splatoon2InkClient(USER_AGENT) as client:
        schedules = await client.schedules()
        salmon_run = await client.salmon_run()
        gear = await client.gear()
        festivals = await client.festivals()
        newest = festivals.in_region(Region.NA)[0]
        rankings = await client.festival_rankings(Region.NA, newest.festival_id)
        timeline = await client.timeline()

    assert all(schedules.in_mode(mode) for mode in GameMode)
    assert salmon_run.schedules and salmon_run.details
    assert gear
    assert all(festivals.in_region(region) for region in Region)
    assert rankings.alpha and rankings.bravo
    assert timeline.coop is None or timeline.coop.reward_gear.gear.name
