from __future__ import annotations
from typing import TYPE_CHECKING

from aiogram import Router

from funpayhub.app.telegram.ui.ids import MenuIds
from funpayhub.lib.base_app.telegram.app.properties.ui import NodeMenuContext
from . import callbacks as cbs
from dumping.src.properties import DumpingOfferNode
from funpayhub.lib.translater import translater

if TYPE_CHECKING:
    from aiogram.types import CallbackQuery as Query
    from dumping.src.properties import DumperProperties


router = Router(name='dumping')
ru = translater.translate


@router.callback_query(cbs.BindOffer.filter())
async def bind(q: Query, plugin_properties: DumperProperties, cbd: cbs.BindOffer):
    if DumpingOfferNode.get_id_for(cbd.offer_id) in plugin_properties.entries:
        return q.answer(ru('❌ Лот {offer_id} уже добавлен в плагин.'), offer_id=cbd.offer_id)

    node = await plugin_properties.add_for_offer(cbd.offer_id, subcategory_id=cbd.subcategory_id)

    await NodeMenuContext(
        menu_id=MenuIds.props_node,
        trigger=q,
        entry_path=node.path
    ).apply_to()


