import pymel.core as pm
import luna_rig  # noqa: F401
from luna import Logger
import luna.utils.environFn as environFn
from luna import LunaVars
from luna.core import callbacks
from luna import Config
environFn.store_config(Config.load())
Logger.set_level(Config.get(LunaVars.logging_level, default=10, stored=True))
try:
    from luna.static import directories
    from luna.interface.menu import LunaMenu
    from luna.interface.hud import LunaHUD
except Exception as e:
    Logger.exception("Failed to import modules")
# Store config


def open_port(lang="python"):
    port = Config.get(LunaVars.command_port, default=7221, stored=True)
    if not pm.commandPort("127.0.0.1:{0}".format(port), n=1, q=1):
        try:
            pm.commandPort(name="127.0.0.1:{0}".format(port), stp="python", echoOutput=True)
            Logger.info("Command port opened: Python - {0}".format(port))
        except Exception as e:
            Logger.exception("Failed to open command port", exc_info=e)


def build_luna_menu():
    try:
        LunaMenu.create()
    except Exception as e:
        Logger.exception("Failed to build luna menu", exc_info=e)


def add_luna_callbacks():
    if Config.get(LunaVars.callback_licence, True, stored=True):
        try:
            callbacks.remove_licence_popup_callback()
            Logger.info("Added file save licence callback")
        except RuntimeError:
            Logger.exception("Failed to add file save licence callback!")


def build_luna_hud():
    try:
        LunaHUD.create()
    except Exception:
        Logger.exception("Failed to create HUD")


def run():
    # Logging
    Logger.write_to_rotating_file(directories.LOG_FILE, level=30)
    Logger.info("Logging to file: {0}".format(directories.LOG_FILE))
    Logger.info("Current logging level: {0}".format(Logger.get_level(name=1)))

    # luna initialization
    open_port(lang="python")
    build_luna_menu()
    build_luna_hud()
    add_luna_callbacks()
