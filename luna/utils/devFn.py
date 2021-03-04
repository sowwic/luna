import sys
import pymel.core as pm

from luna import Logger
from luna.test import maya_unit_test


def run_unit_tests(*args):
    maya_unit_test.run_all_tests()


def unload_builder_modules(*args):
    for mod_name in sys.modules.keys():
        if mod_name.startswith("luna_builder"):
            del sys.modules[mod_name]
            Logger.debug("Unloaded module: {0}".format(mod_name))
    Logger.info("Unloaded builder modules")


def unload_configer_modules(*args):
    for mod_name in sys.modules.keys():
        if mod_name.startswith("luna_configer"):
            del sys.modules[mod_name]
            Logger.debug("Unloaded module: {0}".format(mod_name))
    Logger.info("Unloaded configer modules")


def unload_rig_modules(*args):
    for mod_name in sys.modules.keys():
        if mod_name.startswith("luna_rig"):
            del sys.modules[mod_name]
            Logger.debug("Unloaded module: {0}".format(mod_name))
    Logger.info("Unloaded luna rig modules")


def unload_luna_modules(*args):
    for mod_name in sys.modules.keys():
        if mod_name.startswith("luna"):
            del sys.modules[mod_name]
            Logger.debug("Unloaded module: {0}".format(mod_name))
    Logger.info("Unloaded luna modules")
