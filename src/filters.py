from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from funpaybotengine.types import OfferPreview
    from demping.src.properties import DempingOfferNode



def friend_filter(offer: OfferPreview, props: DempingOfferNode) -> bool:
    if not props.ignore_friends:
        return True

    return not (offer.seller.id in props.parent.friends_list.value)


def min_price_filter(offer: OfferPreview, props: DempingOfferNode) -> bool:
    return offer.price - props.diff.value < props.min_price.value
