from __future__ import annotations
from typing import TYPE_CHECKING

from aiogram import Router as TGRouter

from funpayhub.app.plugin import Plugin
from funpayhub.lib.telegram.ui import MenuModification, MenuBuilder
from .properties import DumperProperties
from .telegram import MENU_MODIFICATIONS, MENUS, ROUTERS as TELEGRAM_ROUTERS

if TYPE_CHECKING:
    from funpayhub.lib.properties import Properties


class DumpingPlugin(Plugin):
    async def properties(self) -> Properties:
        props = DumperProperties()
        return props

    async def telegram_routers(self) -> TGRouter | list[TGRouter]:
        return TELEGRAM_ROUTERS

    async def menus(self) -> type[MenuBuilder] | list[type[MenuBuilder]]:
        return MENUS

    async def menu_modifications(
        self,
    ) -> dict[str, type[MenuModification] | list[type[MenuModification]]]:
        return MENU_MODIFICATIONS
