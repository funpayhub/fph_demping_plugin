from __future__ import annotations

from typing import TYPE_CHECKING, Any

from aiogram import Router as TGRouter

from funpayhub.lib.telegram.ui import MenuBuilder, MenuModification

from funpayhub.app.plugin import Plugin
from funpayhub.app.dispatching import Router as HubRouter

from .events import OffersListFetch
from .updater import FetchersManager
from .handlers import router as INTERNAL_ROUTER
from .telegram import (
    MENUS,
    ROUTERS as TELEGRAM_ROUTERS,
    MENU_MODIFICATIONS,
)
from .hub_router import router as HUB_ROUTER
from .properties import DumperProperties


if TYPE_CHECKING:
    from funpaybotengine.types import OfferPreview

    from funpayhub.lib.properties import Properties


class DumpingPlugin(Plugin):
    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.fetchers_manager = FetchersManager(on_fetch=self.on_fetch_callback)
        self.props: DumperProperties | None = None

    async def properties(self) -> Properties:
        self.props = DumperProperties()
        return self.props

    async def telegram_routers(self) -> TGRouter | list[TGRouter]:
        return TELEGRAM_ROUTERS

    async def hub_routers(self) -> HubRouter | list[HubRouter]:
        return [HUB_ROUTER, INTERNAL_ROUTER]

    async def menus(self) -> type[MenuBuilder] | list[type[MenuBuilder]]:
        return MENUS

    async def menu_modifications(
        self,
    ) -> dict[str, type[MenuModification] | list[type[MenuModification]]]:
        return MENU_MODIFICATIONS

    async def post_setup(self) -> None:
        self.hub.workflow_data.update(
            {
                'fetchers_manager': self.fetchers_manager,
                'dumper_properties': self.props,
                'dumper_props': self.props,
            },
        )

    async def on_fetch_callback(self, subcategory_id: int, offers: list[OfferPreview]) -> None:
        offers = [i for i in offers if i.seller.id != self.hub.funpay.bot.userid]

        event = OffersListFetch(subcategory_id, offers)
        print('emiting event')
        await self.hub.dispatcher.event_entry(event)
