from funpayhub.lib.telegram.callback_data import CallbackData


class BindOffer(CallbackData, identifier='dumper.bind_offer'):
    offer_id: int
    subcategory_id: int
