from __future__ import annotations
from typing import TYPE_CHECKING


from funpayhub.lib.telegram.ui import MenuModification
from funpayhub.lib.translater import translater

if TYPE_CHECKING:
    from funpayhub.lib.base_app.telegram.app.properties.ui import NodeMenuContext
    from funpayhub.lib.telegram.ui import Menu
    from dumping.src.properties import DumperProperties
    from funpayhub.app.properties import FunPayHubProperties as FPHProps


ru = translater.translate


class AddOfferButtonModification(MenuModification, modification_id='dumper:add_offer_button'):
    async def filter(self, ctx: NodeMenuContext, menu: Menu, props: FPHProps):
        plugin_props = props.plugin_properties.get_properties(
            ['com_github_qvvonk_funpayhub_dumping_plugin']
        )
        return ctx.entry_path == plugin_props.path

    async def modify(self, ctx: NodeMenuContext, menu: Menu):
        menu.footer_keyboard.add_callback_button(
            button_id='bind_to_offer',
            text=ru('➕ Добавть лот'),
            callback_data='dummy'
        )
        return menu
