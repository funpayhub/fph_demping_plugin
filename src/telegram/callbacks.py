from __future__ import annotations

from funpayhub.lib.telegram.callback_data import CallbackData


class BindOffer(CallbackData, identifier='dumper.bind_offer'):
    offer_id: int
    subcategory_id: int


class UnbindOffer(CallbackData, identifier='dumper.unbind_offer'):
    offer_id: int
