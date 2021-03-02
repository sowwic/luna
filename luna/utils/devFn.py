import sys

from luna import Logger
from luna.test import maya_unit_test


def run_unit_tests(*args):
    maya_unit_test.run_all_tests()


def reload_rig_components(*args):
    """Reloads all modules located in in luna_rig.components package"""
    avoid_reload = set("luna_rig.core.meta, luna_rig.core.component")
    to_reload = set()
    for mod_name in sys.modules.keys():
        if "luna_rig.components" in mod_name and "pymel" not in mod_name:
            to_reload.add(mod_name)

    for mod_name in to_reload.difference(avoid_reload):
        mod = sys.modules.get(mod_name)
        if mod:
            reload(mod)
            Logger.info("Reloaded {0}".format(mod_name))


def reload_rig_functions(*args):
    avoid_reload = set("luna_rig.core.meta, luna_rig.core.component")
    to_reload = set()
    for mod_name in sys.modules.keys():
        if "luna_rig.functions" in mod_name and "pymel" not in mod_name:
            to_reload.add(mod_name)

    for mod_name in to_reload.difference(avoid_reload):
        mod = sys.modules.get(mod_name)
        if mod:
            reload(mod)
            Logger.info("Reloaded {0}".format(mod_name))


def unload_builder_modules(*args):
    for mod_name in sys.modules.keys():
        if mod_name.startswith("luna_builder"):
            del sys.modules[mod_name]
    Logger.info("Unloaded builder modules")


def unload_configer_modules(*args):
    for mod_name in sys.modules.keys():
        if mod_name.startswith("luna_configer"):
            del sys.modules[mod_name]
    Logger.info("Unloaded configer modules")


def unload_rig_modules(*args):
    for mod_name in sys.modules.keys():
        if mod_name.startswith("luna_rig"):
            del sys.modules[mod_name]
    Logger.info("Unloaded luna rig modules")


def unload_luna_modules(*args):
    for mod_name in sys.modules.keys():
        if mod_name.startswith("luna"):
            del sys.modules[mod_name]
    Logger.info("Unloaded luna modules")
