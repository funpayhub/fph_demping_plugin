from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any
from collections.abc import Callable, Coroutine
from asyncio import Lock, Event
from funpaybotengine import Bot
from funpaybotengine.types.enums import SubcategoryType

if TYPE_CHECKING:
    from funpaybotengine.types import OfferPreview


class OffersFetcher:
    def __init__(
        self,
        subcategory_id: int,
        *,
        on_fetch: Callable[[int, list[OfferPreview]], Coroutine[Any, Any, Any]] | None = None
    ):
        self._subcategory_id = subcategory_id
        self.on_fetch = on_fetch

        self._last_hash: int | None = None

        self._running_lock: Lock = Lock()

        self._stopping_lock: Lock = Lock()
        self._stopped_event: Event = Event()

    async def _iteration(self) -> None:
        bot = Bot()

        for i in range(3):
            try:
                page = await bot.get_subcategory_page(SubcategoryType.OFFERS, self._subcategory_id)
                break
            except Exception as e:
                continue
        else:
            ...
            return

        offers_hash = hash(tuple(i.id for i in (page.offers or [])))
        if offers_hash != self._last_hash:
            self._last_hash = offers_hash
            if self.on_fetch is not None:
                asyncio.create_task(self.on_fetch(self._subcategory_id, list(page.offers or [])))


    async def start(self) -> None:
        if self._running_lock.locked():
            raise RuntimeError(f'Fetcher for subcategory {self.subcategory_id} already running.')

        self._stopped_event.clear()
        async with self._running_lock:
            while True:
                if self._stopping_lock.locked():
                    self._stopped_event.set()
                    return
                await self._iteration()

    async def stop(self) -> None:
        if not self._running_lock.locked():
            return

        if self._stopping_lock.locked():
            await self._stopped_event.wait()
            return

        async with self._stopping_lock:
            await self._stopped_event.wait()


    @property
    def subcategory_id(self) -> int:
        return self._subcategory_id