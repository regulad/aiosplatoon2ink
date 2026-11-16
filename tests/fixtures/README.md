# Fixtures

Feeds exactly as splatoon2.ink served them, chosen so the tests cover each shape the feeds take. The data comes from
SplatNet 2 through [splatoon2.ink](https://splatoon2.ink/).

| File | Served | Shows |
| --- | --- | --- |
| `schedules.json` | 2026-11-16, live | Regular, Ranked and League Battle rotations |
| `coop-schedules.json` | 2026-11-16, live | Salmon Run rotations, each weapon named |
| `coop-schedules-random-weapon.json` | 2020-03-21 08:14 UTC, [Wayback Machine](https://web.archive.org/web/20200321081412/https://splatoon2.ink/data/coop-schedules.json) | A green "?" among named weapons |
| `coop-schedules-all-random.json` | 2023-05-27 11:16 UTC, [Wayback Machine](https://web.archive.org/web/20230527111655/https://splatoon2.ink/data/coop-schedules.json) | A rotation of four green "?"s |
| `merchandises.json` | 2026-11-16, live | SplatNet 2's shop |
| `festivals.json` | 2026-11-16, live | Every Splatfest in every region, from the first in August 2017 to the last in January 2021 |
| `festivals/na-4064-rankings.json` | 2026-11-16, live, with each player's nickname and IDs replaced | The rankings of the last Splatfest in North America |
| `timeline.json` | 2026-11-16, live | Salmon Run's reward gear and current rotation; no new weapons |
| `timeline-2018.json` | 2018-04-29 17:22 UTC, [Wayback Machine](https://web.archive.org/web/20180429172244/https://splatoon2.ink/data/timeline.json) | A rotation of four "?"s, each given as `null` |

No snapshot shows new weapons in the timeline: the Wayback Machine has none from the days after a release, and
Splatoon 2's last new weapons came out in 2019. The tests build that case from a weapon in the rankings instead.

The live tests (`pytest -m live`) check the models against the feeds as they are now.
