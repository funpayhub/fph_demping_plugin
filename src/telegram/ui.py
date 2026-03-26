from __future__ import annotations

__all__ = ['AddOfferButtonModification', 'AddDumpingMenuBuilder']


from typing import TYPE_CHECKING

from funpayparsers.types import SubcategoryType

from funpayhub.lib.base_app.telegram.app.ui.ui_finalizers import StripAndNavigationFinalizer
from funpayhub.lib.telegram.ui import MenuModification, MenuBuilder, MenuContext
from funpayhub.lib.translater import translater
from funpayhub.lib.telegram.ui import Menu
from dumping.src.properties import DumpingOfferNode
from funpayhub.lib.base_app.telegram.app.ui.callbacks import OpenMenu
from . import callbacks as cbs

if TYPE_CHECKING:
    from funpayhub.lib.base_app.telegram.app.properties.ui import NodeMenuContext
    from dumping.src.properties import DumperProperties
    from funpayhub.app.properties import FunPayHubProperties as FPHProps
    from funpayhub.app.main import FunPayHub as FPH


ru = translater.translate


class AddDumpingMenuBuilder(MenuBuilder, menu_id='dumper:add_dumping', context_type=MenuContext):
    async def build(self, ctx: MenuContext, hub: FPH, props: FPHProps) -> Menu:
        menu = Menu(finalizer=StripAndNavigationFinalizer())
        if not hub.funpay.authenticated:
            menu.main_text = ru(
                '<b>❌ FunPay Hub не удалось авторизироваться в аккаунт FunPay. '
                'Добавление демпинг лотов невозможно.</b>'
            )
            return menu

        menu.main_text = ru('<b>📋 Выберите лот, которому хотите настроить демпинг.</b>')

        profile = await hub.funpay.profile()
        props: DumperProperties = props.plugin_properties.get_properties(
            ['com_github_qvvonk_funpayhub_dumping_plugin']
        )
        for subcategory_id, offers in profile.offers.get(SubcategoryType.OFFERS, {}).items():
            for offer in offers:
                node_id = DumpingOfferNode.get_id_for(offer.id)
                if node_id in props.entries:
                    continue

                menu.main_keyboard.add_callback_button(
                    button_id=f'add_dumping:{offer.id}',
                    text=f'[{offer.id}] {offer.title}',
                    callback_data=cbs.BindOffer(
                        offer_id=offer.id,
                        subcategory_id=subcategory_id,
                        ui_history=ctx.as_ui_history()
                    ).pack()
                )
        return menu


class AddOfferButtonModification(MenuModification, modification_id='dumper:add_offer_button'):
    async def filter(self, ctx: NodeMenuContext, menu: Menu, props: FPHProps):
        plugin_props = props.plugin_properties.get_properties(
            ['com_github_qvvonk_funpayhub_dumping_plugin']
        )
        return ctx.entry_path == plugin_props.path

    async def modify(self, ctx: NodeMenuContext, menu: Menu):
        menu.footer_keyboard.add_callback_button(
            button_id='bind_to_offer',
            text=ru('➕ Добавть лот'),
            callback_data=OpenMenu(
                menu_id='dumper:add_dumping', ui_history=ctx.as_ui_history()
            ).pack()
        )
        return menu


OFFERS_CACHE: dict[int, str] = {}


class RenamePropertiesModification(MenuModification, modification_id='dumper:rename_props'):
    async def filter(self, ctx: NodeMenuContext, menu: Menu, props: FPHProps, hub: FPH):
        plugin_props = props.plugin_properties.get_properties(
            ['com_github_qvvonk_funpayhub_dumping_plugin']
        )
        return hub.funpay.authenticated and ctx.entry_path == plugin_props.path

    async def modify(self, ctx: NodeMenuContext, menu: Menu, hub: FPH):
        profile = await hub.funpay.profile()
        offers = profile.offers.get(SubcategoryType.OFFERS, {})
        offers = {i.id: i for l in offers.values() for i in l}

        for line in menu.main_keyboard:
            for button in line:
                if not button.button_id.startswith('param_change:'):
                    continue

                node_id = button.button_id.split(':')[1].split('.')[-1]
                if not DumpingOfferNode.is_offer_node(node_id):
                    continue

                offer_id = int(DumpingOfferNode.extract_offer_id(node_id))
                if offer := (offers.get(offer_id)):
                    button.obj.text = f'[{offer.id}] {offer.title}'
                    OFFERS_CACHE[offer.id] = offer.title
                elif name := OFFERS_CACHE.get(offer_id):
                    button.text = f'[{offer_id}] {name}'

        return menu
