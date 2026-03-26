from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import Router
from dumping.src.properties import DumpingOfferNode

from funpayhub.lib.translater import translater
from funpayhub.lib.base_app.telegram.app.properties.ui import NodeMenuContext

from funpayhub.app.telegram.ui.ids import MenuIds

from . import callbacks as cbs


if TYPE_CHECKING:
    from aiogram.types import CallbackQuery as Query
    from dumping.src.updater import FetchersManager
    from dumping.src.properties import DumperProperties

    from funpayhub.lib.telegram.ui import UIRegistry as UI


router = Router(name='dumping')
ru = translater.translate


@router.callback_query(cbs.BindOffer.filter())
async def bind(
    q: Query,
    plugin_properties: DumperProperties,
    cbd: cbs.BindOffer,
    fetchers_manager: FetchersManager,
):
    if DumpingOfferNode.get_id_for(cbd.offer_id) in plugin_properties.entries:
        return q.answer(ru('❌ Лот {offer_id} уже добавлен в плагин.'), offer_id=cbd.offer_id)

    node = await plugin_properties.add_for_offer(cbd.offer_id, subcategory_id=cbd.subcategory_id)
    fetchers_manager.subscribe_to(cbd.subcategory_id)

    await NodeMenuContext(
        menu_id=MenuIds.props_node,
        trigger=q,
        entry_path=node.path,
    ).apply_to()


@router.callback_query(cbs.UnbindOffer.filter())
async def unbind(
    q: Query,
    plugin_properties: DumperProperties,
    cbd: cbs.UnbindOffer,
    fetchers_manager: FetchersManager,
    tg_ui: UI,
):
    node_id = DumpingOfferNode.get_id_for(cbd.offer_id)

    if node_id not in plugin_properties.entries:
        await q.answer(ru('❌ Лот {offer_id} не найден в настройках.'), offer_id=cbd.offer_id)
    else:
        node: DumpingOfferNode = plugin_properties.detach_node(node_id)
        await plugin_properties.save()
        await fetchers_manager.unsubscribe_from(node.subcategory_id.value)

    await tg_ui.context_from_history(cbd.ui_history, trigger=q).apply_to()
