import sys
import pymel.core as pm
from maya import cmds

import luna
from luna.test import maya_unit_test


def run_unit_tests(*args):
    maya_unit_test.run_all_tests()


def unload_builder_modules(*args):
    for mod_name in list(sys.modules):
        if mod_name.startswith("luna_builder"):
            del sys.modules[mod_name]
            luna.Logger.debug("Unloaded module: {0}".format(mod_name))
    luna.Logger.info("Unloaded builder modules")


def unload_configer_modules(*args):
    for mod_name in list(sys.modules):
        if mod_name.startswith("luna_configer"):
            del sys.modules[mod_name]
            luna.Logger.debug("Unloaded module: {0}".format(mod_name))
    luna.Logger.info("Unloaded configer modules")


def unload_rig_modules(*args):
    for mod_name in list(sys.modules):
        if mod_name.startswith("luna_rig"):
            del sys.modules[mod_name]
            luna.Logger.debug("Unloaded module: {0}".format(mod_name))
    luna.Logger.info("Unloaded luna rig modules")


def unload_luna_modules(*args):
    for mod_name in list(sys.modules):
        if mod_name.startswith("luna"):
            del sys.modules[mod_name]
            luna.Logger.debug("Unloaded module: {0}".format(mod_name))
    luna.Logger.info("Unloaded luna modules")


def open_port(port=None):
    if not port:
        port = luna.Config.get(luna.LunaVars.command_port)
    if port < 0:
        return
    if not cmds.commandPort(":{0}".format(port), q=1):
        try:
            cmds.commandPort(name=":{0}".format(port))
            luna.Logger.info("Command port opened: Python - {0}".format(port))
        except Exception:
            luna.Logger.exception("Failed to open command port")
