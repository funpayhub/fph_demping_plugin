from __future__ import annotations
from typing import TYPE_CHECKING
from funpayhub.app.dispatching import Router, FunPayStartEvent

if TYPE_CHECKING:
    from dumping.src.updater import FetchersManager
    from dumping.src.properties import DumperProperties as DumperProps

router = Router(name='dumper')


@router.on_funpay_start()
async def start_tasks(event: FunPayStartEvent, fetchers_manager: FetchersManager, dumper_props: DumperProps):
    if event.error:
        return

    for i in dumper_props.offer_properties:
        fetchers_manager.subscribe_to(i.subcategory_id.value)


