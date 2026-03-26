from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from dumping.src.logger import logger
from dumping.src.filters import filter_offers
from funpayparsers.types import Currency
from dumping.src.properties import DumpingOfferNode

from funpayhub.app.dispatching import Router

from .events import OffersListFetch


if TYPE_CHECKING:
    from funpaybotengine import Bot as FPBot
    from funpaybotengine.types import OfferPreview
    from dumping.src.properties import DumperProperties

    from funpayhub.app.main import FunPayHub as FPH

router = Router('dumping:internal')


fee: dict[int, float] = {}


@router.on_event(event_filter=OffersListFetch.__event_name__)
async def dump_price(
    subcategory_id: int,
    offers_list: list[OfferPreview],
    plugin_properties: DumperProperties,
    hub: FPH,
) -> None:
    offer_ids = {
        int(DumpingOfferNode.extract_offer_id(i.id))
        for i in plugin_properties.offer_properties
        if i.subcategory_id.value == subcategory_id
    }

    if not offer_ids:
        return

    for i in offer_ids:
        try:
            await process_offer(i, offers_list, plugin_properties, hub.funpay.bot)
        except Exception:
            logger.error('Ошибка демпинга цены для лота %d.', i, exc_info=True)


async def process_offer(
    offer_id: int,
    offers_list: list[OfferPreview],
    plugin_properties: DumperProperties,
    bot: FPBot,
) -> None:
    props = plugin_properties.get_for_offer(offer_id)
    if props is None:
        return

    offers = sorted(filter_offers(offers_list, props), key=lambda x: x.price.value)
    target_price = offers[0].price.value - props.diff.value if offers else props.max_price.value

    if props.subcategory_id.value not in fee:
        fee[props.subcategory_id.value] = await get_fee(props.subcategory_id.value, bot)

    real_price = target_price / (1 + fee[props.subcategory_id.value])
    real_price = float(f'{real_price:.4f}')

    try:
        offer_fields = await bot.get_offer_fields(offer_id=offer_id)
    except:
        logger.error('Ошибка получения полей лота %s.', offer_id, exc_info=True)
        return  # todo: delete offer from props if 404

    offer_fields.price = real_price

    try:
        await bot.save_offer_fields(offer_fields)
    except:
        logger.error('Ошибка сохранения полей лота %s.', offer_id, exc_info=True)

    logger.info('Цена лота %d установлена на %f (%f).', offer_id, target_price, real_price)


async def get_fee(subcategory_id: int, bot: FPBot) -> float:
    attempts = 3
    INIT_PRICE = 10000
    while True:
        attempts -= 1
        try:
            result = await bot.calc_lots(subcategory_id, INIT_PRICE)
            minimum = min(
                [i.price for i in result.methods if i.price_money_value.currency is Currency.RUB]
            )
            result = (minimum / (INIT_PRICE / 100) - 100) / 100
            return result
        except Exception:
            if not attempts:
                raise

            await asyncio.sleep(3)
