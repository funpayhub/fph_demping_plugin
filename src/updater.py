from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any
from dataclasses import dataclass
from asyncio import Lock
from collections.abc import Callable, Coroutine

from funpaybotengine import Bot
from dumping.src.logger import logger
from funpaybotengine.types.enums import SubcategoryType


if TYPE_CHECKING:
    from funpaybotengine.types import OfferPreview


type OnFetchCallback = Callable[[int, list[OfferPreview]], Coroutine[Any, Any, Any]]


class OffersFetcher:
    def __init__(self, subcategory_id: int, *, on_fetch: OnFetchCallback | None = None):
        self._subcategory_id = subcategory_id
        self.on_fetch = on_fetch

        self._last_hash: int | None = None

        self._running_lock: Lock = Lock()

    async def _iteration(self) -> None:
        bot = Bot()

        for i in range(3):
            try:
                page = await bot.get_subcategory_page(SubcategoryType.OFFERS, self._subcategory_id)
                break
            except Exception as e:
                print(e)
                continue
        else:
            ...
            return

        offers_hash = hash(tuple(i.id for i in (page.offers or [])))
        if offers_hash != self._last_hash:
            self._last_hash = offers_hash
            if self.on_fetch is not None:
                asyncio.create_task(self.on_fetch(self._subcategory_id, list(page.offers or [])))

    async def _start(self) -> None:
        if self._running_lock.locked():
            raise RuntimeError(f'Fetcher for subcategory {self.subcategory_id} already running.')

        logger.info('Цикл получения таблицы лотов подкатегории %s запущен.', self.subcategory_id)
        async with self._running_lock:
            while True:
                await self._iteration()
                await asyncio.sleep(30)

    async def start(self) -> None:
        try:
            await self._start()
        except asyncio.CancelledError:
            logger.info(
                'Цикл получения таблицы лотов подкатегории %s остановлен.',
                self.subcategory_id,
            )
            raise

    @property
    def subcategory_id(self) -> int:
        return self._subcategory_id


@dataclass
class FetcherInfo:
    subcategory_id: int
    fetcher: OffersFetcher
    task: asyncio.Task | None = None
    subscribers: int = 1


class FetchersManager:
    def __init__(self, on_fetch: OnFetchCallback | None = None):
        self._fetchers: dict[int, FetcherInfo] = {}
        self._on_fetch = on_fetch

    def subscribe_to(self, subcategory_id: int) -> None:
        if subcategory_id in self._fetchers:
            self._fetchers[subcategory_id].subscribers += 1
            return

        fetcher = OffersFetcher(subcategory_id, on_fetch=self.on_fetch_callback)
        info = FetcherInfo(subcategory_id, fetcher)
        task = asyncio.create_task(fetcher.start())
        info.task = task
        self._fetchers[subcategory_id] = info

    async def unsubscribe_from(self, subcategory_id: int) -> None:
        if subcategory_id not in self._fetchers:
            return

        info = self._fetchers[subcategory_id]
        info.subscribers -= 1
        if info.subscribers <= 0:
            del self._fetchers[subcategory_id]

            if info.task is not None:
                info.task.cancel()

                try:
                    await info.task
                except asyncio.CancelledError:
                    pass

    @property
    def on_fetch_callback(self) -> OnFetchCallback | None:
        return self._on_fetch

    @on_fetch_callback.setter
    def on_fetch_callback(self, on_fetch: OnFetchCallback | None):
        self._on_fetch = on_fetch
        for i in self._fetchers.values():
            i.on_fetch = on_fetch
