import pymel.core as pm
from Luna import Logger
from Luna import external
from Luna.static import Directories
from functools import partial
from Luna.core.config import Config
try:
    from Luna.interface.menu.commands import main_cmds
    from Luna.interface.menu.commands import help_cmds
except Exception as e:
    Logger.exception("Failed to import modules", exc_info=e)

if Logger.get_level() == 10:
    try:
        reload(main_cmds)
        reload(help_cmds)
        Logger.debug("Reloaded command modules")
    except ImportError:
        Logger.exception("Failed to reload command modules")


def _null_command(*args):
    pass


class MenuUtil:
    @staticmethod
    def addMenuItem(parent=None,
                    label="",
                    command=_null_command,
                    icon="",
                    divider=False,
                    option_box=False,
                    check_box=False,
                    use_maya_icons=False,
                    var_name=None,
                    default_value=False):

        if icon and not use_maya_icons:
            icon = Directories.ICONS_PATH + icon

        if divider:
            return pm.menuItem(p=parent, dl=label, i=icon, d=divider)

        elif option_box:
            return pm.menuItem(p=parent, l=label, i=icon, ob=option_box, c=command)

        elif check_box:
            if not var_name:
                Logger.error("Menuitem: {0}::{1} is not connected to config!".format(parent, label))
                return

            checkBox_value = Config.get(var_name, default_value)
            checkBox = pm.menuItem(p=parent, l=label, i=icon, cb=checkBox_value, c=partial(Config.set, var_name))
            return checkBox

        else:
            return pm.menuItem(p=parent, l=label, i=icon, c=command)

    @staticmethod
    def addSubMenu(parent, label, tear_off=False, icon=None, use_maya_icons=False):
        '''Adds a sub menu item with the specified label and icon to the specified parent popup menu.'''
        if icon and not use_maya_icons:
            icon = Directories.ICONS_PATH + icon

        return pm.menuItem(p=parent, l=label, i=icon, subMenu=True, to=tear_off)


class LunaMenu:
    MAIN_WINDOW = pm.melGlobals["gMainWindow"]
    MENU_OBJECT = "LunaMainMenu"
    MENU_LABEL = "Luna"

    @classmethod
    def _delete_old(cls):
        if pm.menu(cls.MENU_OBJECT, label=cls.MENU_LABEL, exists=1, parent=cls.MAIN_WINDOW):
            pm.deleteUI(pm.menu(cls.MENU_OBJECT, e=1, deleteAllItems=1))
            Logger.debug("Deleted existing {} object".format(cls.MENU_OBJECT))

    @classmethod
    def create(cls):
        cls._delete_old()
        Logger.info("Building {0} menu...".format(cls.MENU_LABEL))
        main_menu = pm.menu(cls.MENU_OBJECT, label=cls.MENU_LABEL, parent=cls.MAIN_WINDOW, tearOff=1)
        # Add items
        MenuUtil.addMenuItem(main_menu, label="Build manager", command=main_cmds.build_manager)

        # Tools menu
        tools_menu = MenuUtil.addSubMenu(main_menu, label="Tools", tear_off=1)
        MenuUtil.addMenuItem(tools_menu, divider=1, label="External")
        if "dsRenamingTool" in pm.moduleInfo(lm=1):
            MenuUtil.addMenuItem(tools_menu, "Renaming tool", command=external.tools.renaming_tool, icon="rename.png", use_maya_icons=1)
            Logger.info("dsRenamingTool detected. Shortcut was added to Tools section")

        # Help and config section
        MenuUtil.addMenuItem(main_menu, divider=1)
        help_menu = MenuUtil.addSubMenu(main_menu, label="Help", tear_off=1)
        MenuUtil.addMenuItem(help_menu, "About", command=help_cmds.show_about_dialog)
        MenuUtil.addMenuItem(help_menu, "Documentation", icon="help.png", command=help_cmds.open_docs, use_maya_icons=1)

        MenuUtil.addMenuItem(main_menu, label="Configuration", command=main_cmds.config_manager)
        Logger.info("Successfully added menu: {0}".format(cls.MENU_LABEL))


if __name__ == "__main__":
    LunaMenu.create()
