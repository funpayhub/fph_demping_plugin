from __future__ import annotations
from typing import TYPE_CHECKING

from funpayhub.app.plugin import Plugin
from .properties import DemperProperties

if TYPE_CHECKING:
    from funpayhub.lib.properties import Properties


class DempingPlugin(Plugin):
    async def properties(self) -> Properties:
        props = DemperProperties()
        return props
