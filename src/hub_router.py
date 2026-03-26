from __future__ import annotations

from typing import TYPE_CHECKING

from funpayhub.app.dispatching import Router, FunPayStartEvent
from dumping.src.properties import DumpingOfferNode
from dumping.src.logger import logger
from typing import Any

if TYPE_CHECKING:
    from dumping.src.updater import FetchersManager
    from dumping.src.properties import DumperProperties as DumperProps
    from funpayhub.lib.properties import Parameter

router = Router(name='dumper')


@router.on_funpay_start()
async def start_tasks(
    event: FunPayStartEvent,
    fetchers_manager: FetchersManager,
    dumper_props: DumperProps,
):
    if event.error:
        return

    for i in dumper_props.offer_properties:
        fetchers_manager.subscribe_to(i.subcategory_id.value)


@router.on_parameter_value_changed()
async def update_offer_state(
    parameter: Parameter[Any],
    dumper_props: DumperProps,
    dumper_offers_states: dict[int, bool]
) -> None:
    if not parameter.is_child(dumper_props):
        return

    node_id_to_check = parameter.path[len(dumper_props.path)]

    if not DumpingOfferNode.is_offer_node(node_id_to_check):
        return

    offer_id = int(DumpingOfferNode.extract_offer_id(node_id_to_check))
    logger.info('Состояние лота %s установлено на %s (изменение параметра).', offer_id, True)
    dumper_offers_states[offer_id] = True
