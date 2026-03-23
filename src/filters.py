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
    return (offer.price - props.diff.value) >= props.min_price.value


def max_price_filter(offer: OfferPreview, props: DempingOfferNode) -> bool:
    return (offer.price - props.diff.value) <= props.max_price.value


def rating_filter(offer: OfferPreview, props: DempingOfferNode) -> bool:
    return offer.seller.rating >= props.from_rating.value


def review_filter(offer: OfferPreview, props: DempingOfferNode) -> bool:
    return offer.seller.reviews_amount >= props.from_reviews_amount.value


def keywords_filter(offer: OfferPreview, props: DempingOfferNode) -> bool:
    if not props.keywords.value:
        return True

    if not offer.title:
        return False

    return any(i in offer.title for i in props.keywords.value)


FILTERS = [
    friend_filter,
    min_price_filter,
    max_price_filter,
    rating_filter,
    review_filter,
]


def filter_offers(offers: list[OfferPreview], props: DempingOfferNode) -> list[OfferPreview]:
    return [i for i in offers if all(filt(i, props) for filt in FILTERS)]
