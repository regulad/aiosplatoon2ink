from types import TracebackType
from typing import Self

from aiohttp import ClientSession, ClientTimeout
from yarl import URL

from aiosplatoon2ink.festivals import FestivalRankings, Festivals, Region, _RankingsFeed
from aiosplatoon2ink.gear import Merchandise, _MerchandisesFeed
from aiosplatoon2ink.salmon_run import CoopSchedules
from aiosplatoon2ink.schedules import Schedules
from aiosplatoon2ink.timeline import Timeline

DEFAULT_BASE_URL = URL("https://splatoon2.ink/data/")


class Splatoon2InkClient:
    """Reads the data feeds that splatoon2.ink publishes.

    splatoon2.ink updates its feeds once an hour. Its terms ask that clients cache rather than fetch more often than
    that, send a User-Agent that says how to reach them, credit splatoon2.ink wherever the data is shown, and stay free
    of charge: https://github.com/misenhower/splatoon2.ink/wiki/Data-access-policy

    Each method raises :class:`aiohttp.ClientError` when a request fails, and :class:`pydantic.ValidationError` when a
    feed doesn't have the shape the models expect.
    """

    def __init__(
        self,
        user_agent: str,
        *,
        session: ClientSession | None = None,
        base_url: URL | str = DEFAULT_BASE_URL,
    ) -> None:
        """
        :param user_agent: Sent with every request, so splatoon2.ink can tell who to contact if something goes wrong:
            for example, ``"MyBot/1.0 (+https://github.com/me/mybot)"``.
        :param session: A session to make requests with, which the caller keeps and closes. Without one, the client
            opens its own on the first request and closes it in :meth:`close`.
        :param base_url: Where the feeds are served from.
        """
        self.user_agent = user_agent
        self.base_url = URL(base_url)
        self._session = session
        self._owns_session = session is None

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the session the client opened, if it opened one."""
        if self._owns_session and self._session is not None:
            await self._session.close()
            self._session = None

    async def _get(self, path: str) -> bytes:
        if self._session is None:
            self._session = ClientSession(timeout=ClientTimeout(total=30))
        async with self._session.get(self.base_url / path, headers={"User-Agent": self.user_agent}) as response:
            response.raise_for_status()
            return await response.read()

    async def schedules(self) -> Schedules:
        """Fetch the Regular, Ranked and League Battle rotations."""
        return Schedules.model_validate_json(await self._get("schedules.json"))

    async def salmon_run(self) -> CoopSchedules:
        """Fetch the Salmon Run rotations, with the stage and weapons of the next two."""
        return CoopSchedules.model_validate_json(await self._get("coop-schedules.json"))

    async def gear(self) -> tuple[Merchandise, ...]:
        """Fetch the gear on sale at SplatNet 2's shop."""
        return _MerchandisesFeed.model_validate_json(await self._get("merchandises.json")).merchandises

    async def festivals(self) -> Festivals:
        """Fetch every Splatfest and its results, in each region."""
        return Festivals.model_validate_json(await self._get("festivals.json"))

    async def festival_rankings(self, region: Region, festival_id: int) -> FestivalRankings:
        """Fetch the top 100 players of each team in a region's Splatfest.

        splatoon2.ink has them only once a Splatfest's results are out, and answers any other request with a 404, which
        raises :class:`aiohttp.ClientResponseError`.

        :param region: The region that held the Splatfest.
        :param festival_id: The Splatfest's :attr:`~aiosplatoon2ink.festivals.Festival.festival_id`.
        """
        path = f"festivals/{Region(region).value}-{int(festival_id)}-rankings.json"
        return _RankingsFeed.model_validate_json(await self._get(path)).rankings

    async def timeline(self) -> Timeline:
        """Fetch the month's Salmon Run reward gear, and the weapons released in the last few days."""
        return Timeline.model_validate_json(await self._get("timeline.json"))


__all__ = ["DEFAULT_BASE_URL", "Splatoon2InkClient"]
