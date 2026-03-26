from __future__ import annotations

from typing import TYPE_CHECKING

from funpayhub.app.dispatching import Router

from .events import OffersListFetch


if TYPE_CHECKING:
    from funpaybotengine.types import OfferPreview

    from .properties import DumperProperties


router = Router(name='dumping')


@router.on_event(event_filter=OffersListFetch.__event_name__)
async def dump(
    subcategory_id: int,
    offers_list: list[OfferPreview],
    plugin_properties: DumperProperties,
) -> None:
    suitable_offers = []
