from __future__ import annotations
from typing import TYPE_CHECKING, Any

from funpayhub.app.dispatching.events.base import HubEvent

if TYPE_CHECKING:
    from funpaybotengine.types import OfferPreview


class DempingPluginEvent(HubEvent, event_name='__demping_plugin_event__'): ...


class OffersListFetch(DempingPluginEvent, event_name='offers_list_fetch'):
    def __init__(self, subcategory_id: int, offers_list: list[OfferPreview]) -> None:
        super().__init__()
        self._offers_list = offers_list
        self._subcategory_id = subcategory_id

    @property
    def offers_list(self) -> list[OfferPreview]:
        return self._offers_list

    @property
    def subcategory_id(self) -> int:
        return self._subcategory_id

    @property
    def event_context_injection(self) -> dict[str, Any]:
        return {
            'offers_list': self.offers_list,
            'subcategory_id': self.subcategory_id,
        }