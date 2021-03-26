import os
import pymel.core as pm
import pymel.api as pma

import luna
import luna_rig  # noqa: F401
from luna.static import directories
from luna.interface.hud import LunaHUD
from luna.interface.menu import LunaMenu
import luna.utils.devFn as devFn
import luna.interface.marking_menu as marking_menu
import luna.utils.environFn as environFn
import luna.core.callbacks as callbacks
import luna_builder
import luna_configer

REGISTERED_CALLBACKS = []


def load_additional_plugins():
    if pm.about(win64=True):
        system_dir = "win64"
    elif pm.about(li=True):
        system_dir = "linux"
    elif pm.about(macOS=True):
        system_dir = "macOS"
    else:
        luna.Logger.error("Unable to load plugins for system: {0}".format(pm.about(os=True)))
        return
    maya_version = pm.about(version=True)
    plugins_dir = os.path.join(directories.PLUGINS_DIR_PATH, maya_version, system_dir)
    for file_name in os.listdir(plugins_dir):
        if not file_name.endswith(".mll"):
            continue
        full_path = os.path.join(plugins_dir, file_name)
        if pm.pluginInfo(file_name, q=True, loaded=True):
            continue
        try:
            pm.loadPlugin(full_path)
            luna.Logger.info("Loaded plugin: {0}".format(file_name))
        except Exception:
            luna.Logger.exception("Failed to load plugin: {0}".format(file_name))


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
    load_additional_plugins()
    # Command port
    devFn.open_port()

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
        # Remove UI elements
        LunaMenu._delete_old()
        luna.Logger.info("Removed menu")
        LunaHUD.remove()
        luna.Logger.info("Removed HUD")
        marking_menu.MarkingMenu._delete_old()
        luna.Logger.info("Removed marking menu")

        # Remove PySide2 windows
        luna_builder.MainDialog.close_and_delete()
        luna_configer.MainDialog.close_and_delete()

        # Callbacks
        for callback_id in REGISTERED_CALLBACKS:
            pma.MMessage.removeCallback(callback_id)
        luna.Logger.info("Removed callbacks")
        # Environ vars
        environFn.set_project_var(None)
        environFn.set_asset_var(None)
        environFn.set_character_var(None)
        environFn.store_config(None)

        # Python modules
        devFn.unload_builder_modules()
        devFn.unload_configer_modules()
        devFn.unload_rig_modules()
        devFn.unload_luna_modules()

    except Exception:
        luna.Logger.exception("Failed to fully uninitialize luna plugin")
        raise
