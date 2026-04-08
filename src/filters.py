from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from funpaybotengine.types import OfferPreview
    from dumping.src.properties import DumpingOfferNode


def min_price_filter(offer: OfferPreview, props: DumpingOfferNode) -> bool:
    return (offer.price.value - props.diff.value) >= props.min_price.value


def max_price_filter(offer: OfferPreview, props: DumpingOfferNode) -> bool:
    return (offer.price.value - props.diff.value) <= props.max_price.value


def rating_filter(offer: OfferPreview, props: DumpingOfferNode) -> bool:
    return offer.seller.rating >= props.from_rating.value


def review_filter(offer: OfferPreview, props: DumpingOfferNode) -> bool:
    return offer.seller.reviews_amount >= props.from_reviews_amount.value


def keywords_filter(offer: OfferPreview, props: DumpingOfferNode) -> bool:
    if not props.keywords.value:
        return True

    if not offer.title:
        return False

    return any(i in offer.title for i in props.keywords.value)


def online_filter(offer: OfferPreview, props: DumpingOfferNode) -> bool:
    if not props.ignore_offline.value:
        return True

    return not offer.auto_delivery and not offer.seller.online


def users_list_filter(offer: OfferPreview, props: DumpingOfferNode) -> bool:
    users_list, list_type = props.users_list.value, props.list_type.real_value
    if not users_list or list_type == 'ignore':
        return True

    seller_in_list = offer.seller.id in users_list or offer.seller.username in users_list
    if list_type == 'friends':
        return not seller_in_list
    elif list_type == 'competitors':
        return seller_in_list
    return True


FILTERS = [
    min_price_filter,
    max_price_filter,
    rating_filter,
    review_filter,
    online_filter,
    users_list_filter,
]


def filter_offers(offers: list[OfferPreview], props: DumpingOfferNode) -> list[OfferPreview]:
    return [i for i in offers if all(filt(i, props) for filt in FILTERS)]
