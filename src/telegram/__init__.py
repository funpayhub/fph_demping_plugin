from .ui import AddOfferButtonModification, AddDumpingMenuBuilder, RenamePropertiesModification
from funpayhub.app.telegram.ui.ids import MenuIds
from .router import router as router


MENU_MODIFICATIONS = {
    MenuIds.props_node: [AddOfferButtonModification, RenamePropertiesModification]
}

MENUS = [AddDumpingMenuBuilder]

ROUTERS = [router]