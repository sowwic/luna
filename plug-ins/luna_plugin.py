import pymel.core as pm
import pymel.api as pma

import luna
import luna_rig  # noqa: F401
from luna.static import directories
from luna.interface.hud import LunaHUD
from luna.interface.menu import LunaMenu
import luna.interface.marking_menu as marking_menu
import luna.utils.environFn as environFn
import luna.core.callbacks as callbacks

REGISTERED_CALLBACKS = []


def open_port(lang="python"):
    port = luna.Config.get(luna.LunaVars.command_port, stored=True)
    if not port:
        return
    if not pm.commandPort("127.0.0.1:{0}".format(port), n=1, q=1):
        try:
            pm.commandPort(name="127.0.0.1:{0}".format(port), stp="python", echoOutput=True)
            luna.Logger.info("Command port opened: Python - {0}".format(port))
        except Exception:
            luna.Logger.exception("Failed to open command port")


def initialize_callbacks():
    if luna.Config.get(luna.LunaVars.callback_licence, True, stored=True):
        try:
            callback_id = callbacks.remove_licence_popup_callback()
            REGISTERED_CALLBACKS.append(callback_id)
            luna.Logger.info("Added file save licence callback")
        except RuntimeError:
            luna.Logger.exception("Failed to add file save licence callback!")
            raise


def initializePlugin(mobject):
    vendor = "Dmitrii Shevchenko"
    version = luna.__version__
    # Init luna.Config
    environFn.store_config(luna.Config.load())
    luna.Logger.set_level(luna.Config.get(luna.LunaVars.logging_level, default=10, stored=True))

    # Init logging
    luna.Logger.write_to_rotating_file(directories.LOG_FILE, level=40)
    luna.Logger.info("Logging to file: {0}".format(directories.LOG_FILE))
    luna.Logger.info("Current logging level: {0}".format(luna.Logger.get_level(name=1)))
    # Command port
    open_port()

    # Init core
    try:
        pma.MFnPlugin(mobject, vendor, version)
        LunaMenu.create()
        LunaHUD.create()
        marking_menu.MarkingMenu.create()
        initialize_callbacks()
    except Exception:
        luna.Logger.exception("Failed to inialize luna plugin")
        raise


def uninitializePlugin(mobject):
    pma.MFnPlugin(mobject)
    try:
        LunaMenu._delete_old()
        luna.Logger.info("Removed menu")
        LunaHUD.remove()
        luna.Logger.info("Removed HUD")
        marking_menu.MarkingMenu._delete_old()
        luna.Logger.info("Removed marking menu")
        for callback_id in REGISTERED_CALLBACKS:
            pma.MMessage.removeCallback(callback_id)
        luna.Logger.info("Removed callbacks")

    except Exception:
        luna.Logger.exception("Failed to fully uninitialize luna plugin")
        raise
