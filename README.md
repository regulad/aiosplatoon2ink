# aiosplatoon2ink

An asyncio client for the Splatoon 2 data that [splatoon2.ink](https://splatoon2.ink/) publishes, with typed,
immutable [pydantic](https://docs.pydantic.dev/) models of each feed. It's the Splatoon 2 sibling of
[aiosplatoon3ink](https://github.com/regulad/aiosplatoon3ink).

```python
from datetime import UTC, datetime

from aiosplatoon2ink import Splatoon2InkClient
from aiosplatoon2ink.schedules import GameMode

async with Splatoon2InkClient("MyBot/1.0 (+https://github.com/me/mybot)") as client:
    schedules = await client.schedules()

now = datetime.now(UTC)
rotation = next(rotation for rotation in schedules.in_mode(GameMode.RANKED) if rotation.is_active(now))
print(rotation.rule.name, [stage.name for stage in rotation.stages], rotation.stage_a.image.url)
```

## Feeds

| Method | Feed | Returns |
| --- | --- | --- |
| `schedules()` | [`schedules.json`](https://splatoon2.ink/data/schedules.json) | Every Regular, Ranked and League Battle rotation for about a day |
| `salmon_run()` | [`coop-schedules.json`](https://splatoon2.ink/data/coop-schedules.json) | Salmon Run rotations, with the stage and weapons of the next two |
| `gear()` | [`merchandises.json`](https://splatoon2.ink/data/merchandises.json) | Gear on sale at SplatNet 2's shop |
| `festivals()` | [`festivals.json`](https://splatoon2.ink/data/festivals.json) | Every Splatfest and its results, in each of the three regions |
| `festival_rankings(region, festival_id)` | [`festivals/<region>-<festival_id>-rankings.json`](https://splatoon2.ink/data/festivals/na-4064-rankings.json) | The top 100 players of each team in a Splatfest |
| `timeline()` | [`timeline.json`](https://splatoon2.ink/data/timeline.json) | The month's Salmon Run reward gear, and weapons released in the last few days |

The models keep SplatNet 2's field names, which are already snake_case. Where SplatNet's internal names differ from
the game's, the enums use the game's: `GameMode.RANKED` is `"gachi"`, and `GearKind.CLOTHING` is `"clothes"`. Each
image is an `Image`, whose `url` is splatoon2.ink's copy of it. Fields the models don't know are ignored. Each method
raises `aiohttp.ClientError` when a request fails, and `pydantic.ValidationError` when a feed has a shape the models
don't expect.

The translations under `data/locale/` aren't modelled yet.

## Using splatoon2.ink's data

splatoon2.ink's [terms](https://github.com/misenhower/splatoon2.ink/wiki/Data-access-policy) ask that you:

- credit splatoon2.ink wherever you show its data;
- cache the feeds rather than fetch them more often than once an hour, since that's how often they update;
- send a User-Agent that says how to reach you, which the client requires;
- avoid hotlinking its images and data from a very busy site;
- keep whatever you build free of charge.

## Installing

It isn't on PyPI. Install it from git, pinned to a commit:

```sh
poetry add "git+https://github.com/regulad/aiosplatoon2ink.git#<commit>"
```

## Developing

```sh
poetry install --with type
poetry run pytest              # against the snapshots in tests/fixtures
poetry run pytest -m live      # against splatoon2.ink's feeds as they are now
poetry run mypy src tests
poetry run pre-commit run --all-files
```

## License

AGPL-3.0. The data belongs to Nintendo, and reaches you through SplatNet 2 and splatoon2.ink.
