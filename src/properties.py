from __future__ import annotations
from typing import Any, TYPE_CHECKING

from funpayhub.lib.base_app.properties_flags import TelegramUIEmojiFlag
from funpayhub.lib.exceptions import PropertiesError, ValidationError
from funpayhub.lib.properties import Properties, ListParameter, ToggleParameter, IntParameter, \
    FloatParameter


class DemperProperties(Properties):
    def __init__(self):
        super().__init__(
            id='demper',
            name='Настройки демпера',
            description='Настройки демпера.',
            file='config/demping.toml'
        )

        self.friends_list = self.attach_node(
            ListParameter(
                id='friends',
                name='Друзья',
                description='Друзья.',
                flags=[TelegramUIEmojiFlag('🤝')]
            )
        )

    async def add_for_offer(self, offer_id: str, save: bool = True) -> DempingOfferNode:
        node_id = DempingOfferNode.get_id_for(offer_id)
        if node_id in self._nodes:
            raise PropertiesError('Offer ID %s already exists', offer_id)

        node = DempingOfferNode(offer_id)
        self.attach_node(node)
        if save:
            await self.save()
        return node

    async def load_from_dict(self, properties_dict: dict[str, Any]) -> None:
        await super().load_from_dict(properties_dict)
        for node_id, node_dict in properties_dict.items():
            if not node_id.startswith('__offer__'):
                continue

            node = await self.add_for_offer(node_id.lstrip('__offer__'), save=False)
            await node.load_from_dict(node_dict)


async def positive_validator(v: float) -> None:
    if v <= 0.01:
        raise ValidationError('Значение должнобыть больше или равно 0.01.')


class DempingOfferNode(Properties):
    if TYPE_CHECKING:
        parent: DemperProperties

    def __init__(self, offer_id: str):
        super().__init__(
            id=self.get_id_for(offer_id),
            name=offer_id,
            description=f'Настройки демпинга лота.'
        )

        self.enabled = self.attach_node(
            ToggleParameter(
                id='enabled',
                name='Включить',
                description='Включить',
                default_value=True,
            )
        )

        self.min_price = self.attach_node(
            FloatParameter(
                id='min_price',
                name='Минимальная цена',
                description='Минимальная цена, ниже которой плагин не будет демпить лот.',
                default_value=99999.0,
            )
        )

        self.max_price = self.attach_node(
            FloatParameter(
                id='max_price',
                name='Максимальная цена',
                description='Максимальная цена лота.',
                default_value=999999.0,

            )
        )

        self.diff = self.attach_node(
            FloatParameter(
                id='diff',
                name='Разница',
                description='Разница',
                default_value=0.01,
                validator=positive_validator,
            )
        )

        self.from_rating = self.attach_node(
            IntParameter(
                id='from_rating',
                name='Порог рейтинга',
                description='При демпинге будут учитываться только те лоты, '
                            'у продавцов которых рейтинг такой же или выше указанного.',
                default_value=4
            )
        )

        self.from_reviews_amount = self.attach_node(
            IntParameter(
                id='from_reviews_amount',
                name='Порог отзывов',
                description='При демпинге будут учитываться только те лоты, у продавцов которых '
                            'кол-во отзывов равно или больше указанного.',
                default_value=0
            )
        )

        self.keywords: ListParameter[str] = self.attach_node(
            ListParameter(
                id='keywords',
                name='Ключевые слова',
                description='При демпинге будут учитываться только те лоты, '
                            'в которых есть указанные ключевые слова'
            )
        )

        self.ignore_friends = self.attach_node(
            ToggleParameter(
                id='ignore_friends',
                name='Игнорировать друзей',
                description='Игнорировать друзей',
                default_value=False
            )
        )

    @classmethod
    def get_id_for(cls, offer_id: str) -> str:
        return f'__offer__{offer_id}'