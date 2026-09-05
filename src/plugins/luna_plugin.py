import os
from maya import cmds
from maya.api import OpenMaya

import luna
import luna_rig  # noqa: F401
from luna.static import directories
from luna.interface.hud import LunaHUD
from luna.interface.menu import LunaMenu
import luna.utils.devFn as devFn
import luna.interface.marking_menu as marking_menu
import luna.core.callbacks as callbacks
import luna_configer
import luna_builder
import luna_builder.editor.editor_conf as editor_conf

REGISTERED_CALLBACKS = []


def load_additional_plugins():
    if cmds.about(win64=True):
        system_dir = "win64"
    elif cmds.about(linux=True):
        system_dir = "linux"
    elif cmds.about(macOS=True):
        system_dir = "macOS"
    else:
        luna.Logger.error(
            f"Unable to load plugins for system: {cmds.about(operatingSystem=True)}"
        )
        return
    maya_version = cmds.about(version=True)
    plugins_dir = os.path.join(directories.PLUGINS_DIR_PATH, maya_version, system_dir)
    if not os.path.isdir(plugins_dir):
        return
    for file_name in os.listdir(plugins_dir):
        if not file_name.endswith(".mll"):
            continue
        full_path = os.path.join(plugins_dir, file_name)
        if cmds.pluginInfo(file_name, query=True, loaded=True):
            continue
        try:
            cmds.loadPlugin(full_path)
            luna.Logger.info(f"Loaded plugin: {file_name}")
        except Exception:
            luna.Logger.exception(f"Failed to load plugin: {file_name}")


def initialize_callbacks():
    if luna.Config.get(luna.LunaVars.callback_license, True):
        try:
            callback_id = callbacks.remove_license_popup_callback()
            REGISTERED_CALLBACKS.append(callback_id)
            luna.Logger.info("Added file save license callback")
        except RuntimeError:
            luna.Logger.exception("Failed to add file save license callback!")
            raise


def initializePlugin(mobject):
    vendor = "Dmitrii Shevchenko"
    version = luna.__version__
    # Init Config, Logger
    luna.Config.CACHED_DATA = luna.Config.load()
    luna.Logger.set_level(
        luna.Config.get(luna.LunaVars.logging_level, default=10, cached=True)
    )

    # Init logging
    luna.Logger.write_to_rotating_file(directories.LOG_FILE, level=40)
    luna.Logger.info(f"Logging to file: {directories.LOG_FILE}")
    luna.Logger.info(f"Current logging level: {luna.Logger.get_level(name=1)}")
    load_additional_plugins()
    editor_conf.load_plugins()
    # Command port
    devFn.open_port()

    # Init core
    try:
        OpenMaya.MFnPlugin(mobject, vendor, version)
        LunaMenu.create()
        LunaHUD.create()
        marking_menu.MarkingMenu.create()
        initialize_callbacks()
    except Exception:
        luna.Logger.exception("Failed to initialize luna plugin")
        raise


def uninitializePlugin(mobject):
    OpenMaya.MFnPlugin(mobject)
    try:
        luna.workspace.Project.exit()

        # Remove UI elements
        LunaMenu._delete_old()
        luna.Logger.info("Removed menu")
        LunaHUD.remove()
        luna.Logger.info("Removed HUD")
        marking_menu.MarkingMenu._delete_old()
        luna.Logger.info("Removed marking menu")

        # Remove PySide2 windows
        luna_builder.BuilderMainWindow.close_and_delete()
        luna_configer.MainDialog.close_and_delete()

        # Callbacks
        for callback_id in REGISTERED_CALLBACKS:
            OpenMaya.MMessage.removeCallback(callback_id)
        luna.Logger.info("Removed callbacks")

        # Python modules
        devFn.unload_builder_modules()
        devFn.unload_configer_modules()
        devFn.unload_rig_modules()
        devFn.unload_luna_modules()

    except Exception:
        luna.Logger.exception("Failed to fully uninitialize luna plugin")
        raise
