from __future__ import annotations

from funpayhub.app.telegram.ui.ids import MenuIds

from .ui import (
    AddRemoveButton,
    AddDumpingMenuBuilder,
    HeaderTextModification,
    AddOfferButtonModification,
    RenamePropertiesModification,
    KeyboardModification
)
from .router import router as router


MENU_MODIFICATIONS = {
    MenuIds.props_node: [
        AddOfferButtonModification,
        RenamePropertiesModification,
        AddRemoveButton,
        HeaderTextModification,
        KeyboardModification,
    ],
}

MENUS = [AddDumpingMenuBuilder]

ROUTERS = [router]
