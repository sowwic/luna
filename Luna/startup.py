import pymel.core as pm
from Luna import Logger
from Luna.core.configFn import LunaConfig
from Luna.core.configFn import LunaVars
Logger.set_level(LunaConfig.get(LunaVars.logging_level, default=10))

try:
    from Luna.static import Directories
    from Luna.interface.menu import LunaMenu
    from Luna.interface.hud import LunaHud
except Exception as e:
    Logger.exception("Failed to import modules")


def open_port(lang="python"):
    port = LunaConfig.get(LunaVars.command_port, default=7221)
    if not pm.commandPort("127.0.0.1:{0}".format(port), n=1, q=1):
        try:
            pm.commandPort(name="127.0.0.1:{0}".format(port), stp=lang, echoOutput=True)
            Logger.info("Command port opened: {0} - {1}".format(lang.title(), port))
        except Exception as e:
            Logger.exception("Failed to open command port", exc_info=e)


def build_luna_menu():
    try:
        LunaMenu()
    except Exception as e:
        Logger.exception("Failed to build Luna menu", exc_info=e)


def build_luna_hud():
    try:
        LunaHud.create()
    except Exception:
        Logger.exception("Failed to create HUD")


def run():
    # Logging
    Logger.write_to_rotating_file(Directories.LOG_FILE, level=30)
    Logger.info("Logging to file: {0}".format(Directories.LOG_FILE))
    Logger.info("Current logging level: {0}".format(Logger.get_level(name=1)))

    # Luna initialization
    open_port(lang="python")
    build_luna_menu()
    build_luna_hud()
