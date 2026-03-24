from funpayhub.lib.telegram.callback_data import CallbackData


class OpenBindOfferMenu(CallbackData, identifier='deumper.bind_offer_dumper'):
    ...


class BindOffer(CallbackData, identifier='dumper.bind_offer'):
    offer_id: int
