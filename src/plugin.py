from __future__ import annotations
from typing import TYPE_CHECKING

from funpayhub.app.plugin import Plugin
from funpayhub.lib.telegram.ui import MenuModification
from .properties import DumperProperties
from .telegram import MENU_MODIFICATIONS

if TYPE_CHECKING:
    from funpayhub.lib.properties import Properties


class DumpingPlugin(Plugin):
    async def properties(self) -> Properties:
        props = DumperProperties()
        return props

    async def menu_modifications(
        self,
    ) -> dict[str, type[MenuModification] | list[type[MenuModification]]]:
        return MENU_MODIFICATIONS
