from collections.abc import Awaitable, Callable

import pytest
from aiohttp import ClientResponseError, ClientSession, web
from aiohttp.test_utils import TestServer
from conftest import FIXTURES
from pydantic import ValidationError

from aiosplatoon2ink import Region, Splatoon2InkClient

type ServerFactory = Callable[[web.Application], Awaitable[TestServer]]
type Requests = list[tuple[str, str]]

USER_AGENT = "aiosplatoon2ink-tests/1.0"


@pytest.fixture
async def feeds(aiohttp_server: ServerFactory) -> tuple[TestServer, Requests]:
    """Serve the fixtures as splatoon2.ink serves its feeds, recording each request's path and User-Agent."""
    requests: Requests = []

    async def serve(request: web.Request) -> web.StreamResponse:
        requests.append((request.path, request.headers.get("User-Agent", "")))
        if not (FIXTURES / request.match_info["name"]).is_file():
            raise web.HTTPNotFound()
        return web.FileResponse(FIXTURES / request.match_info["name"])

    async def serve_wrong_shape(request: web.Request) -> web.StreamResponse:
        return web.json_response({"regular": "not a list of rotations", "gachi": [], "league": []})

    app = web.Application()
    app.router.add_get("/data/{name:.+}", serve)
    app.router.add_get("/wrong-shape/{name:.+}", serve_wrong_shape)
    return await aiohttp_server(app), requests


async def test_fetches_each_feed_with_the_user_agent(feeds: tuple[TestServer, Requests]) -> None:
    server, requests = feeds

    async with Splatoon2InkClient(USER_AGENT, base_url=server.make_url("/data/")) as client:
        schedules = await client.schedules()
        salmon_run = await client.salmon_run()
        gear = await client.gear()
        festivals = await client.festivals()
        rankings = await client.festival_rankings(Region.NA, 4064)
        timeline = await client.timeline()

    assert schedules.regular
    assert salmon_run.details[0].stage.name == "Lost Outpost"
    assert gear[0].gear.name == "Canary Trainers"
    assert festivals.in_region(Region.EU)
    assert rankings.alpha[0].order == 1
    assert timeline.coop is not None
    assert requests == [
        ("/data/schedules.json", USER_AGENT),
        ("/data/coop-schedules.json", USER_AGENT),
        ("/data/merchandises.json", USER_AGENT),
        ("/data/festivals.json", USER_AGENT),
        ("/data/festivals/na-4064-rankings.json", USER_AGENT),
        ("/data/timeline.json", USER_AGENT),
    ]


async def test_closes_only_its_own_session(feeds: tuple[TestServer, Requests]) -> None:
    server, _ = feeds

    client = Splatoon2InkClient(USER_AGENT, base_url=server.make_url("/data/"))
    await client.timeline()
    session = client._session
    await client.close()
    assert session is not None and session.closed

    async with ClientSession() as shared:
        async with Splatoon2InkClient(USER_AGENT, session=shared, base_url=server.make_url("/data/")) as client:
            await client.timeline()
        assert not shared.closed


async def test_raises_on_http_errors(feeds: tuple[TestServer, Requests]) -> None:
    server, _ = feeds

    async with Splatoon2InkClient(USER_AGENT, base_url=server.make_url("/missing/")) as client:
        with pytest.raises(ClientResponseError) as raised:
            await client.schedules()
    assert raised.value.status == 404

    async with Splatoon2InkClient(USER_AGENT, base_url=server.make_url("/data/")) as client:
        with pytest.raises(ClientResponseError) as raised:
            await client.festival_rankings(Region.EU, 4064)
    assert raised.value.status == 404


async def test_raises_on_a_feed_of_the_wrong_shape(feeds: tuple[TestServer, Requests]) -> None:
    server, _ = feeds

    async with Splatoon2InkClient(USER_AGENT, base_url=server.make_url("/wrong-shape/")) as client:
        with pytest.raises(ValidationError):
            await client.schedules()
