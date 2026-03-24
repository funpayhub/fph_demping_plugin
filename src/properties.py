from __future__ import annotations
from typing import Any, TYPE_CHECKING

from funpayhub.app.properties.flags import ParameterFlags
from funpayhub.lib.base_app.properties_flags import TelegramUIEmojiFlag
from funpayhub.lib.exceptions import PropertiesError, ValidationError
from funpayhub.lib.properties import Properties, ListParameter, ToggleParameter, IntParameter, \
    FloatParameter


class DumperProperties(Properties):
    def __init__(self):
        super().__init__(
            id='com_github_qvvonk_funpayhub_dumping_plugin',
            name='Настройки демпера',
            description='Настройки демпера.',
            file='config/demping.toml'
        )

        self.friends_list: ListParameter[int] = self.attach_node(
            ListParameter(
                id='friends',
                name='Друзья',
                description='Друзья.',
                flags=[TelegramUIEmojiFlag('🤝')]
            )
        )

    async def add_for_offer(
        self, offer_id: str, save: bool = True, subcategory_id: int | None = None
    ) -> DumpingOfferNode:
        node_id = DumpingOfferNode.get_id_for(offer_id)
        if node_id in self._nodes:
            raise PropertiesError('Offer ID %s already exists', offer_id)

        node = DumpingOfferNode(offer_id, subcategory_id=subcategory_id)
        self.attach_node(node)
        if save:
            await self.save()
        return node

    async def load_from_dict(self, properties_dict: dict[str, Any]) -> None:
        await super().load_from_dict(properties_dict)
        for node_id, node_dict in properties_dict.items():
            if not DumpingOfferNode.is_offer_node(node_id):
                continue

            node = await self.add_for_offer(node_id.lstrip('__offer__'), save=False)
            await node.load_from_dict(node_dict)

    @property
    def offer_properties(self) -> list[DumpingOfferNode]:
        return [i for i in self._nodes.values() if isinstance(i, DumpingOfferNode)]


async def positive_validator(v: float) -> None:
    if v <= 0.01:
        raise ValidationError('Значение должнобыть больше или равно 0.01.')


class DumpingOfferNode(Properties):
    if TYPE_CHECKING:
        parent: DumperProperties

    def __init__(self, offer_id: str, subcategory_id: int | None = None):
        super().__init__(
            id=self.get_id_for(offer_id),
            name=offer_id,
            description=f'Настройки демпинга лота.'
        )

        self.subcategory_id: IntParameter = self.attach_node(
            IntParameter(
                id='subcategory_id',
                name='ID подкатегории',
                description='ID подкатегории лота. Изменяйте только если знаете что делаете.',
                default_value=0,
                flags=[ParameterFlags.HIDE]
            )
        )
        if subcategory_id:
            self.subcategory_id._value = subcategory_id

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

        self.ignore_offline = self.attach_node(
            ToggleParameter(
                id='ignore_offline',
                name='Игнорировать оффлайн',
                description='При демпинге лота не будут учитываться лоты, '
                            'у которых нет автовыдачи и продавцы которых оффлайн.',
                default_value=False,
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

    @classmethod
    def is_offer_node(cls, node_id: str) -> bool:
        return node_id.startswith('__offer__')

    @property
    def offer_id(self) -> int:
        return int(self.id.lstrip('__offer__'))
